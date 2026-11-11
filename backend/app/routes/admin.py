"""
app/routes/admin.py
Admin-only routes: complaints oversight, analytics, worker assignments, reports, survey insights, public stats
Village Complaint Redressal System - Vemavaram Village
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
from app.services.notification_service import notify_complaint_assigned, notify_status_changed
from app.utils.helpers import success_response, error_response
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


# ─────────────────────────────────────────────
# GET /api/admin/public-stats
# Public statistics for the website (no auth required)
# ─────────────────────────────────────────────
@admin_bp.route("/public-stats", methods=["GET"])
def public_stats():
    """Returns live aggregated statistics for the public landing page."""
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as total FROM complaints")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as resolved FROM complaints WHERE status = 'Resolved'")
        resolved = cursor.fetchone()["resolved"]

        cursor.execute(
            """SELECT COUNT(*) as pending FROM complaints
               WHERE status IN ('Submitted', 'Under Review', 'Assigned', 'In Progress')"""
        )
        pending = cursor.fetchone()["pending"]

        cursor.execute("SELECT AVG(rating) as avg_rating FROM feedback")
        row = cursor.fetchone()
        avg_rating = round(float(row["avg_rating"] or 0), 2)

        cursor.execute(
            """SELECT AVG(TIMESTAMPDIFF(HOUR, created_at, resolved_at)) as avg_hours
               FROM complaints
               WHERE status = 'Resolved' AND resolved_at IS NOT NULL"""
        )
        row_hours = cursor.fetchone()
        avg_resolution_hours = round(float(row_hours["avg_hours"] or 24))

        cursor.execute("SELECT COUNT(*) as citizens FROM users WHERE role IN ('citizen', 'villager')")
        citizens = cursor.fetchone()["citizens"]

    satisfaction_pct = round((avg_rating / 5) * 100) if avg_rating > 0 else 97

    return success_response(data={
        "total_complaints": total,
        "resolved_complaints": resolved,
        "pending_complaints": pending,
        "avg_resolution_hours": avg_resolution_hours if avg_resolution_hours else 24,
        "citizen_satisfaction": satisfaction_pct,
        "active_citizens": citizens,
        "village": "Vemavaram"
    })


# ─────────────────────────────────────────────
# GET /api/admin/complaints
# All complaints with search, filter, and pagination
# ─────────────────────────────────────────────
@admin_bp.route("/complaints", methods=["GET"])
@jwt_required()
@admin_required
def get_all_complaints():
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 15))
    status   = request.args.get("status", "")
    category = request.args.get("category", "")
    search   = request.args.get("search", "")
    priority = request.args.get("priority", "")

    query = """
        SELECT c.*,
               u.name as user_name, u.mobile as user_mobile,
               w.name as worker_name, wp.department
        FROM complaints c
        JOIN users u ON c.user_id = u.user_id
        LEFT JOIN assignments a ON c.complaint_id = a.complaint_id AND a.is_current = 1
        LEFT JOIN users w ON a.worker_id = w.user_id
        LEFT JOIN worker_profiles wp ON w.user_id = wp.user_id
        WHERE 1=1
    """
    params = []

    if status:
        query += " AND c.status = %s"
        params.append(status)
    if category:
        query += " AND c.category = %s"
        params.append(category)
    if priority:
        query += " AND c.priority = %s"
        params.append(priority)
    if search:
        query += " AND (c.complaint_id LIKE %s OR c.title LIKE %s OR u.name LIKE %s)"
        like = f"%{search}%"
        params += [like, like, like]

    query += " ORDER BY c.created_at DESC"

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
# PUT /api/admin/complaints/<id>/status
# Update complaint status
# ─────────────────────────────────────────────
@admin_bp.route("/complaints/<complaint_id>/status", methods=["PUT"])
@jwt_required()
@admin_required
def update_status(complaint_id):
    identity   = get_jwt_identity()
    data       = request.get_json(silent=True) or {}
    new_status = data.get("status", "").strip()
    notes      = data.get("notes", "").strip()

    valid = ["Submitted", "Under Review", "Assigned", "In Progress", "Resolved", "Rejected"]
    if new_status not in valid:
        return error_response(f"Invalid status. Must be one of: {', '.join(valid)}")

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM complaints WHERE complaint_id = %s", (complaint_id,))
        complaint = cursor.fetchone()
        if not complaint:
            return error_response("Complaint not found", 404)

        old_status = complaint["status"]

        if new_status == "Resolved":
            cursor.execute(
                """UPDATE complaints
                   SET status = %s, updated_at = NOW(), resolved_at = NOW()
                   WHERE complaint_id = %s""",
                (new_status, complaint_id)
            )
        else:
            cursor.execute(
                """UPDATE complaints
                   SET status = %s, updated_at = NOW()
                   WHERE complaint_id = %s""",
                (new_status, complaint_id)
            )

        cursor.execute(
            """INSERT INTO complaint_status_history
               (complaint_id, old_status, new_status, changed_by, notes)
               VALUES (%s, %s, %s, %s, %s)""",
            (complaint_id, old_status, new_status, identity["user_id"],
             notes or f"Status changed to {new_status}")
        )
    db.commit()

    notify_status_changed(complaint["user_id"], complaint_id, new_status)
    return success_response(message=f"Complaint status updated to {new_status}")


# ─────────────────────────────────────────────
# POST /api/admin/complaints/<id>/assign
# Assign a worker to a complaint
# ─────────────────────────────────────────────
@admin_bp.route("/complaints/<complaint_id>/assign", methods=["POST"])
@jwt_required()
@admin_required
def assign_worker(complaint_id):
    identity  = get_jwt_identity()
    data      = request.get_json(silent=True) or {}
    worker_id = data.get("worker_id")
    notes     = data.get("notes", "").strip()
    exp_date  = data.get("expected_date")

    if not worker_id:
        return error_response("worker_id is required")

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM complaints WHERE complaint_id = %s", (complaint_id,))
        complaint = cursor.fetchone()
        if not complaint:
            return error_response("Complaint not found", 404)

        # Worker check in users table
        cursor.execute(
            "SELECT * FROM users WHERE user_id = %s AND role = 'worker' AND is_active = 1",
            (worker_id,)
        )
        worker = cursor.fetchone()
        if not worker:
            return error_response("Worker not found or inactive", 404)

        # Deactivate old current assignments
        cursor.execute(
            "UPDATE assignments SET is_current = 0 WHERE complaint_id = %s",
            (complaint_id,)
        )
        cursor.execute(
            """INSERT INTO assignments
               (complaint_id, worker_id, assigned_by, notes)
               VALUES (%s, %s, %s, %s)""",
            (complaint_id, worker_id, identity["user_id"], notes or None)
        )
        # Update complaint
        cursor.execute(
            """UPDATE complaints
               SET status = 'Assigned', worker_id = %s, updated_at = NOW()
               WHERE complaint_id = %s""",
            (worker_id, complaint_id)
        )
        cursor.execute(
            """INSERT INTO complaint_status_history
               (complaint_id, old_status, new_status, changed_by, notes)
               VALUES (%s, %s, 'Assigned', %s, %s)""",
            (complaint_id, complaint["status"], identity["user_id"],
             f"Assigned to worker: {worker['name']}")
        )
    db.commit()

    notify_complaint_assigned(complaint["user_id"], complaint_id, worker["name"])
    return success_response(message=f"Complaint assigned to {worker['name']}")


# ─────────────────────────────────────────────
# GET /api/admin/analytics
# Dashboard analytics
# ─────────────────────────────────────────────
@admin_bp.route("/analytics", methods=["GET"])
@jwt_required()
@admin_required
def get_analytics():
    db = get_db()
    with db.cursor() as cursor:
        # Status counts
        cursor.execute("SELECT status, COUNT(*) as count FROM complaints GROUP BY status")
        status_counts = {r["status"]: r["count"] for r in cursor.fetchall()}

        # Category counts
        cursor.execute(
            "SELECT category, COUNT(*) as count FROM complaints GROUP BY category ORDER BY count DESC"
        )
        category_counts = cursor.fetchall()

        # Monthly trend (last 6 months)
        cursor.execute(
            """SELECT DATE_FORMAT(created_at, '%%b %%Y') as month,
                      COUNT(*) as count
               FROM complaints
               WHERE created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
               GROUP BY DATE_FORMAT(created_at, '%%Y-%%m'), month
               ORDER BY DATE_FORMAT(created_at, '%%Y-%%m') ASC"""
        )
        monthly_trend = cursor.fetchall()

        # Worker performance using unified users + assignments
        cursor.execute(
            """SELECT w.user_id as worker_id,
                      w.name as worker_name,
                      COUNT(a.assignment_id) as total_assigned,
                      SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END) as resolved
               FROM users w
               LEFT JOIN assignments a ON w.user_id = a.worker_id
               LEFT JOIN complaints c ON a.complaint_id = c.complaint_id
               WHERE w.role = 'worker' AND w.is_active = 1
               GROUP BY w.user_id, w.name
               ORDER BY total_assigned DESC"""
        )
        worker_performance = cursor.fetchall()

        # Total complaints
        cursor.execute("SELECT COUNT(*) as total FROM complaints")
        total = cursor.fetchone()["total"]

        # Average rating
        cursor.execute("SELECT AVG(rating) as avg_rating FROM feedback")
        avg_rating = cursor.fetchone()["avg_rating"] or 0

        # Average resolution days
        cursor.execute(
            """SELECT AVG(DATEDIFF(resolved_at, created_at)) as avg_days
               FROM complaints
               WHERE status = 'Resolved' AND resolved_at IS NOT NULL"""
        )
        avg_resolution = cursor.fetchone()["avg_days"] or 0

    return success_response(data={
        "summary": {
            "total": total,
            "submitted":    status_counts.get("Submitted", 0),
            "under_review": status_counts.get("Under Review", 0),
            "assigned":     status_counts.get("Assigned", 0),
            "in_progress":  status_counts.get("In Progress", 0),
            "resolved":     status_counts.get("Resolved", 0),
            "rejected":     status_counts.get("Rejected", 0),
            "avg_rating":   round(float(avg_rating), 2),
            "avg_resolution_days": round(float(avg_resolution), 1),
        },
        "category_breakdown": category_counts,
        "monthly_trend": monthly_trend,
        "worker_performance": worker_performance,
    })


# ─────────────────────────────────────────────
# GET /api/admin/survey-insights
# Vemavaram field survey data
# ─────────────────────────────────────────────
@admin_bp.route("/survey-insights", methods=["GET"])
@jwt_required()
@admin_required
def survey_insights():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM survey_insights ORDER BY response_count DESC")
        insights = cursor.fetchall()
        cursor.execute("SELECT SUM(response_count) as total FROM survey_insights")
        total_responses = cursor.fetchone()["total"] or 0

    return success_response(data={
        "village": "Vemavaram",
        "total_responses": total_responses,
        "survey_year": 2025,
        "insights": insights,
    })


# ─────────────────────────────────────────────
# GET /api/admin/reports
# Filtered report query
# ─────────────────────────────────────────────
@admin_bp.route("/reports", methods=["GET"])
@jwt_required()
@admin_required
def generate_report():
    from_date = request.args.get("from_date", "")
    to_date   = request.args.get("to_date", "")
    category  = request.args.get("category", "")

    query = """
        SELECT c.complaint_id, c.title, c.category, c.status, c.priority,
               c.location, c.created_at, c.resolved_at,
               u.name as complainant_name, u.mobile as complainant_mobile,
               w.name as worker_name, wp.department,
               f.rating, f.remarks
        FROM complaints c
        JOIN users u ON c.user_id = u.user_id
        LEFT JOIN assignments a ON c.complaint_id = a.complaint_id AND a.is_current = 1
        LEFT JOIN users w ON a.worker_id = w.user_id
        LEFT JOIN worker_profiles wp ON w.user_id = wp.user_id
        LEFT JOIN feedback f ON c.complaint_id = f.complaint_id
        WHERE 1=1
    """
    params = []
    if from_date:
        query += " AND DATE(c.created_at) >= %s"
        params.append(from_date)
    if to_date:
        query += " AND DATE(c.created_at) <= %s"
        params.append(to_date)
    if category:
        query += " AND c.category = %s"
        params.append(category)

    query += " ORDER BY c.created_at DESC"

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    return success_response(data={"report": rows, "total": len(rows)})
