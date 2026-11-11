"""
app/routes/workers.py
Worker management routes (admin) + worker task self-service routes
Village Complaint Redressal System - Vemavaram Village
"""

import bcrypt
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
from app.services.image_service import upload_image
from app.utils.helpers import success_response, error_response, normalize_mobile, validate_mobile
from app.utils.decorators import admin_required

workers_bp = Blueprint("workers", __name__)

DEPARTMENTS = [
    "Roads & Infrastructure",
    "Electrical & Streetlights",
    "Water Supply",
    "Drainage & Sanitation",
    "Waste Management",
    "General Services",
]


# ─────────────────────────────────────────────
# GET /api/workers
# List all workers (admin only)
# ─────────────────────────────────────────────
@workers_bp.route("", methods=["GET"])
@jwt_required()
@admin_required
def list_workers():
    department = request.args.get("department", "")
    is_active  = request.args.get("is_active")

    query = """
        SELECT u.user_id as worker_id,
               u.name as worker_name,
               u.mobile,
               u.is_active,
               u.created_at,
               COALESCE(wp.department, 'General Services') as department,
               wp.employee_id
        FROM users u
        LEFT JOIN worker_profiles wp ON u.user_id = wp.user_id
        WHERE u.role = 'worker'
    """
    params = []

    if department:
        query += " AND wp.department = %s"
        params.append(department)
    if is_active is not None and is_active != "":
        query += " AND u.is_active = %s"
        params.append(int(is_active))

    query += " ORDER BY u.name ASC"

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, params)
        workers = cursor.fetchall()

    return success_response(data={"workers": workers, "departments": DEPARTMENTS})


# ─────────────────────────────────────────────
# POST /api/workers
# Add a new worker account & profile (admin only)
# ─────────────────────────────────────────────
@workers_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
def create_worker():
    data = request.get_json(silent=True) or {}
    name       = data.get("worker_name", "").strip()
    mobile     = normalize_mobile(data.get("mobile", "").strip())
    department = data.get("department", "").strip()
    password   = data.get("password", "Worker@123").strip()

    if not name:
        return error_response("Worker name is required")
    if not mobile:
        return error_response("Mobile number is required")
    if not validate_mobile(mobile):
        return error_response("Invalid mobile number format")
    if department not in DEPARTMENTS:
        return error_response(f"Invalid department. Must be one of: {', '.join(DEPARTMENTS)}")

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT user_id FROM users WHERE mobile = %s", (mobile,))
        if cursor.fetchone():
            return error_response("A user or worker with this mobile number already exists", 409)

        # 1. Create worker record in users table
        cursor.execute(
            """INSERT INTO users (name, mobile, village, password_hash, role)
               VALUES (%s, %s, 'Vemavaram', %s, 'worker')""",
            (name, mobile, hashed)
        )
        user_id = cursor.lastrowid

        # 2. Create worker profile record
        cursor.execute(
            """INSERT INTO worker_profiles (user_id, department)
               VALUES (%s, %s)""",
            (user_id, department)
        )
    db.commit()

    return success_response(
        data={"worker_id": user_id, "user_id": user_id},
        message="Worker added successfully. Default credentials: mobile and password 'Worker@123'",
        status_code=201
    )


# ─────────────────────────────────────────────
# PUT /api/workers/<id>
# Update worker details (admin only)
# ─────────────────────────────────────────────
@workers_bp.route("/<int:worker_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_worker(worker_id):
    data = request.get_json(silent=True) or {}
    name       = data.get("worker_name", "").strip()
    mobile     = normalize_mobile(data.get("mobile", "").strip()) if data.get("mobile") else ""
    department = data.get("department", "").strip()
    is_active  = data.get("is_active")

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE user_id = %s AND role = 'worker'", (worker_id,))
        worker = cursor.fetchone()
        if not worker:
            return error_response("Worker not found", 404)

        # Update users table
        user_updates = []
        user_params  = []
        if name:
            user_updates.append("name = %s")
            user_params.append(name)
        if mobile:
            user_updates.append("mobile = %s")
            user_params.append(mobile)
        if is_active is not None:
            user_updates.append("is_active = %s")
            user_params.append(int(is_active))

        if user_updates:
            cursor.execute(
                f"UPDATE users SET {', '.join(user_updates)} WHERE user_id = %s",
                user_params + [worker_id]
            )

        # Update worker_profiles table
        if department:
            if department not in DEPARTMENTS:
                return error_response(f"Invalid department. Must be one of: {', '.join(DEPARTMENTS)}")
            cursor.execute(
                """INSERT INTO worker_profiles (user_id, department)
                   VALUES (%s, %s)
                   ON DUPLICATE KEY UPDATE department = VALUES(department)""",
                (worker_id, department)
            )

    db.commit()
    return success_response(message="Worker updated successfully")


# ─────────────────────────────────────────────
# GET /api/workers/tasks
# List tasks assigned to the logged-in worker
# ─────────────────────────────────────────────
@workers_bp.route("/tasks", methods=["GET"])
@jwt_required()
def get_worker_tasks():
    identity = get_jwt_identity()
    user_id  = identity["user_id"]
    role     = identity["role"]

    if role not in ("worker", "admin"):
        return error_response("Access denied. Workers only.", 403)

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """SELECT c.*,
                      u.name as citizen_name, u.mobile as citizen_mobile,
                      a.assigned_at, a.notes as assignment_notes
               FROM assignments a
               JOIN complaints c ON a.complaint_id = c.complaint_id
               JOIN users u ON c.user_id = u.user_id
               WHERE a.worker_id = %s AND a.is_current = 1
               ORDER BY
                 FIELD(c.status, 'In Progress', 'Assigned', 'Under Review', 'Resolved', 'Rejected'),
                 c.created_at DESC""",
            (user_id,)
        )
        tasks = cursor.fetchall()

    return success_response(data={"tasks": tasks})


# ─────────────────────────────────────────────
# PUT /api/workers/tasks/<complaint_id>/progress
# Worker: update status and upload resolution evidence photo
# ─────────────────────────────────────────────
@workers_bp.route("/tasks/<complaint_id>/progress", methods=["PUT"])
@jwt_required()
def update_progress(complaint_id):
    identity = get_jwt_identity()
    role     = identity["role"]
    user_id  = identity["user_id"]

    if role not in ("worker", "admin"):
        return error_response("Access denied. Workers only.", 403)

    # Multipart form for image upload or JSON
    data = {}
    if request.content_type and "multipart/form-data" in request.content_type:
        new_status = request.form.get("status", "").strip()
        notes      = request.form.get("notes", "").strip()
        photo      = request.files.get("resolution_photo")
        json_url   = request.form.get("resolution_image_url", "").strip()
    else:
        data       = request.get_json(silent=True) or {}
        new_status = data.get("status", "").strip()
        notes      = data.get("notes", "").strip()
        photo      = None
        json_url   = data.get("resolution_image_url", "").strip()

    valid = ["In Progress", "Resolved"]
    if new_status and new_status not in valid:
        return error_response(f"Worker can update status to: {', '.join(valid)}")

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM complaints WHERE complaint_id = %s", (complaint_id,))
        complaint = cursor.fetchone()
        if not complaint:
            return error_response("Complaint not found", 404)

        # Mandatory Resolution Photograph & Completion Remarks Validation for Resolved Status
        if new_status == "Resolved":
            if not notes:
                return error_response("Completion remarks are mandatory to mark a task as Resolved", 422)
            has_photo = bool((photo and photo.filename) or json_url or complaint.get("resolution_image_url"))
            if not has_photo:
                return error_response("Resolution evidence photograph is mandatory to mark a task as Resolved", 422)

    resolution_url = json_url or None
    if photo and photo.filename:
        try:
            resolution_url = upload_image(photo.read(), photo.filename, folder="resolutions")
        except Exception as e:
            return error_response(f"Resolution photo upload failed: {str(e)}", 500)

    with db.cursor() as cursor:
        updates = []
        params  = []
        if new_status:
            updates.append("status = %s")
            params.append(new_status)
        if resolution_url:
            updates.append("resolution_image_url = %s")
            params.append(resolution_url)
        if notes:
            updates.append("resolution_notes = %s")
            params.append(notes)
        if new_status == "Resolved":
            updates.append("resolved_at = NOW()")

        if updates:
            cursor.execute(
                f"UPDATE complaints SET {', '.join(updates)}, updated_at = NOW() WHERE complaint_id = %s",
                params + [complaint_id]
            )
            if new_status:
                cursor.execute(
                    """INSERT INTO complaint_status_history
                       (complaint_id, old_status, new_status, changed_by, notes)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (complaint_id, complaint["status"], new_status, user_id,
                     notes or f"Updated by worker: {new_status}")
                )
    db.commit()

    if new_status:
        from app.services.notification_service import notify_status_changed
        notify_status_changed(complaint["user_id"], complaint_id, new_status)

    return success_response(
        data={"complaint_id": complaint_id, "status": new_status, "resolution_image_url": resolution_url},
        message="Task progress updated successfully"
    )
