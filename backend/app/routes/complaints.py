"""
app/routes/complaints.py
Complaint CRUD routes for citizens & workers
Village Complaint Redressal System - Vemavaram Village
"""

from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
from app.services.image_service import upload_image
from app.services.ai_classifier import classify_complaint
from app.services.notification_service import notify_complaint_received
from app.utils.helpers import success_response, error_response, format_complaint_id

complaints_bp = Blueprint("complaints", __name__)

VALID_CATEGORIES = [
    "Road Issues",
    "Streetlight Issues",
    "Water Supply Problems",
    "Drainage Problems",
    "Garbage Collection Issues",
    "Sanitation Issues",
]

STATUS_FLOW = ["Submitted", "Under Review", "Assigned", "In Progress", "Resolved", "Rejected"]


def _generate_complaint_id(cursor) -> str:
    year = datetime.now().year
    cursor.execute(
        "SELECT COUNT(*) as cnt FROM complaints WHERE complaint_id LIKE %s",
        (f"CMP{year}%",)
    )
    seq = cursor.fetchone()["cnt"] + 1
    return format_complaint_id(year, seq)


# ─────────────────────────────────────────────
# POST /api/complaints
# Create a new complaint (with optional Cloudinary image upload)
# ─────────────────────────────────────────────
@complaints_bp.route("", methods=["POST"])
@jwt_required()
def create_complaint():
    identity = get_jwt_identity()
    user_id = identity["user_id"]

    # Support both JSON and multipart/form-data
    if request.content_type and "multipart/form-data" in request.content_type:
        title       = request.form.get("title", "").strip()
        category    = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        location    = request.form.get("location", "").strip()
        latitude    = request.form.get("latitude")
        longitude   = request.form.get("longitude")
        ward_id     = request.form.get("ward_id")
        image_file  = request.files.get("image")
    else:
        data        = request.get_json(silent=True) or {}
        title       = data.get("title", "").strip()
        category    = data.get("category", "").strip()
        description = data.get("description", "").strip()
        location    = data.get("location", "").strip()
        latitude    = data.get("latitude")
        longitude   = data.get("longitude")
        ward_id     = data.get("ward_id")
        image_file  = None

    errors = []
    if not title:
        errors.append("Title is required")
    if not description:
        errors.append("Description is required")
    if not location:
        errors.append("Location is required")
    if category and category not in VALID_CATEGORIES:
        errors.append(f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}")

    if errors:
        return error_response("Validation failed", 422, errors)

    # AI category and priority classification
    ai_result = classify_complaint(title, description)
    ai_suggestion = ai_result["category"]
    smart_priority = ai_result["priority"]

    if not category:
        category = ai_suggestion or VALID_CATEGORIES[0]

    # Upload image to Cloudinary if provided
    image_url = None
    if image_file and image_file.filename:
        try:
            image_bytes = image_file.read()
            image_url = upload_image(image_bytes, image_file.filename, folder="complaints")
        except Exception as e:
            return error_response(f"Image upload failed: {str(e)}", 500)

    db = get_db()
    with db.cursor() as cursor:
        complaint_id = _generate_complaint_id(cursor)
        cursor.execute(
            """INSERT INTO complaints
               (complaint_id, user_id, title, category, description,
                image_url, ai_category_suggestion, location, latitude, longitude,
                ward_id, status, priority)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Submitted', %s)""",
            (complaint_id, user_id, title, category, description,
             image_url, ai_suggestion, location, latitude or None, longitude or None,
             ward_id or None, smart_priority)
        )
        # Record status history audit trail
        cursor.execute(
            """INSERT INTO complaint_status_history
               (complaint_id, old_status, new_status, changed_by, notes)
               VALUES (%s, NULL, 'Submitted', %s, 'Complaint submitted by citizen')""",
            (complaint_id, user_id)
        )
    db.commit()

    # Trigger notification
    notify_complaint_received(user_id, complaint_id)

    return success_response(
        data={
            "complaint_id": complaint_id,
            "category": category,
            "ai_suggestion": ai_suggestion,
            "smart_priority": smart_priority,
            "image_url": image_url,
        },
        message="Complaint submitted successfully",
        status_code=201
    )


# ─────────────────────────────────────────────
# GET /api/complaints
# List logged-in user's complaints (paginated)
# ─────────────────────────────────────────────
@complaints_bp.route("", methods=["GET"])
@jwt_required()
def list_complaints():
    identity = get_jwt_identity()
    user_id  = identity["user_id"]
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    status   = request.args.get("status", "")
    category = request.args.get("category", "")

    query = "SELECT * FROM complaints WHERE user_id = %s"
    params = [user_id]

    if status:
        query += " AND status = %s"
        params.append(status)
    if category:
        query += " AND category = %s"
        params.append(category)

    query += " ORDER BY created_at DESC"

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) as total FROM ({query}) sub", params)
        total = cursor.fetchone()["total"]

        offset = (page - 1) * per_page
        cursor.execute(f"{query} LIMIT %s OFFSET %s", params + [per_page, offset])
        complaints = cursor.fetchall()

    return success_response(data={
        "complaints": complaints,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page if per_page else 1
        }
    })


# ─────────────────────────────────────────────
# GET /api/complaints/<id>
# Get complaint details
# ─────────────────────────────────────────────
@complaints_bp.route("/<complaint_id>", methods=["GET"])
@jwt_required()
def get_complaint(complaint_id):
    identity = get_jwt_identity()
    user_id  = identity["user_id"]
    role     = identity["role"]

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM complaints WHERE complaint_id = %s", (complaint_id,))
        complaint = cursor.fetchone()

    if not complaint:
        return error_response("Complaint not found", 404)

    # Citizens can only view their own complaints; workers and admins can view any
    if role in ("citizen", "villager") and complaint["user_id"] != user_id:
        return error_response("Access denied", 403)

    with db.cursor() as cursor:
        # Status history
        cursor.execute(
            """SELECT csh.*, u.name as changed_by_name
               FROM complaint_status_history csh
               JOIN users u ON csh.changed_by = u.user_id
               WHERE csh.complaint_id = %s
               ORDER BY csh.changed_at ASC""",
            (complaint_id,)
        )
        history = cursor.fetchall()

        # Assignment info joining unified users + worker_profiles
        cursor.execute(
            """SELECT a.*, u.name as worker_name, u.mobile as worker_mobile,
                      wp.department
               FROM assignments a
               JOIN users u ON a.worker_id = u.user_id
               LEFT JOIN worker_profiles wp ON u.user_id = wp.user_id
               WHERE a.complaint_id = %s AND a.is_current = 1""",
            (complaint_id,)
        )
        assignment = cursor.fetchone()

        # Feedback
        cursor.execute(
            "SELECT * FROM feedback WHERE complaint_id = %s", (complaint_id,)
        )
        feedback = cursor.fetchone()

    complaint["status_history"] = history
    complaint["assignment"] = assignment
    complaint["feedback"] = feedback

    return success_response(data=complaint)


# ─────────────────────────────────────────────
# GET /api/complaints/track/<complaint_id>
# Public complaint status tracker by ID (no auth required)
# ─────────────────────────────────────────────
@complaints_bp.route("/track/<complaint_id>", methods=["GET"])
def track_complaint_public(complaint_id):
    complaint_id = complaint_id.strip()
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """SELECT complaint_id, title, category, description, location,
                      ward_id, status, priority, image_url, resolution_image_url, resolution_notes,
                      created_at, resolved_at
               FROM complaints WHERE complaint_id = %s""",
            (complaint_id,)
        )
        complaint = cursor.fetchone()

    if not complaint:
        return error_response(f"Complaint ID '{complaint_id}' not found. Please verify the ID and try again.", 404)

    with db.cursor() as cursor:
        # Status history timeline
        cursor.execute(
            """SELECT csh.old_status, csh.new_status, csh.notes, csh.changed_at
               FROM complaint_status_history csh
               WHERE csh.complaint_id = %s
               ORDER BY csh.changed_at ASC""",
            (complaint_id,)
        )
        history = cursor.fetchall()

        # Assignment info (sanitized for public view: only department and assignment notes)
        cursor.execute(
            """SELECT a.assignment_id, a.notes as assignment_notes, a.assigned_at,
                      wp.department
               FROM assignments a
               JOIN users u ON a.worker_id = u.user_id
               LEFT JOIN worker_profiles wp ON u.user_id = wp.user_id
               WHERE a.complaint_id = %s AND a.is_current = 1""",
            (complaint_id,)
        )
        assignment = cursor.fetchone()

        # Public feedback summary if available
        cursor.execute(
            "SELECT rating, remarks, created_at FROM feedback WHERE complaint_id = %s",
            (complaint_id,)
        )
        feedback = cursor.fetchone()

    complaint["status_history"] = history
    complaint["assignment"] = assignment
    complaint["feedback"] = feedback

    return success_response(data=complaint)


# ─────────────────────────────────────────────
# GET /api/complaints/categories
# List all valid complaint categories
# ─────────────────────────────────────────────
@complaints_bp.route("/categories", methods=["GET"])
def get_categories():
    return success_response(data={"categories": VALID_CATEGORIES})


# ─────────────────────────────────────────────
# POST /api/complaints/classify
# AI helper: Suggest category and priority
# ─────────────────────────────────────────────
@complaints_bp.route("/classify", methods=["POST"])
@jwt_required()
def classify():
    data = request.get_json(silent=True) or {}
    suggestion = classify_complaint(
        data.get("title", ""), data.get("description", "")
    )
    return success_response(data=suggestion)
