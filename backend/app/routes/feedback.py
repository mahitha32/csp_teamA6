"""
app/routes/feedback.py
Feedback routes — submit and retrieve post-resolution ratings
Village Complaint Redressal System - Vemavaram Village
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
from app.utils.helpers import success_response, error_response

feedback_bp = Blueprint("feedback", __name__)


# ─────────────────────────────────────────────
# POST /api/feedback
# Submit rating + remarks after resolution
# ─────────────────────────────────────────────
@feedback_bp.route("", methods=["POST"])
@jwt_required()
def submit_feedback():
    identity     = get_jwt_identity()
    user_id      = identity["user_id"]
    data         = request.get_json(silent=True) or {}
    complaint_id = data.get("complaint_id", "").strip()
    rating       = data.get("rating")
    remarks      = data.get("remarks", "").strip()

    if not complaint_id:
        return error_response("complaint_id is required")
    if rating is None or not (1 <= int(rating) <= 5):
        return error_response("Rating must be between 1 and 5")

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM complaints WHERE complaint_id=%s AND user_id=%s",
            (complaint_id, user_id)
        )
        complaint = cursor.fetchone()
        if not complaint:
            return error_response("Complaint not found or access denied", 404)
        if complaint["status"] != "Resolved":
            return error_response("Feedback can only be submitted for resolved complaints", 400)

        cursor.execute(
            "SELECT feedback_id FROM feedback WHERE complaint_id=%s", (complaint_id,)
        )
        if cursor.fetchone():
            return error_response("Feedback already submitted for this complaint", 409)

        cursor.execute(
            """INSERT INTO feedback (complaint_id, user_id, rating, remarks)
               VALUES (%s,%s,%s,%s)""",
            (complaint_id, user_id, int(rating), remarks or None)
        )
    db.commit()
    return success_response(message="Thank you for your feedback!", status_code=201)


# ─────────────────────────────────────────────
# GET /api/feedback/<complaint_id>
# Get feedback for a complaint
# ─────────────────────────────────────────────
@feedback_bp.route("/<complaint_id>", methods=["GET"])
@jwt_required()
def get_feedback(complaint_id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM feedback WHERE complaint_id=%s", (complaint_id,)
        )
        fb = cursor.fetchone()
    if not fb:
        return error_response("No feedback found for this complaint", 404)
    return success_response(data=fb)


# ─────────────────────────────────────────────
# GET /api/feedback/summary
# Overall feedback stats (admin)
# ─────────────────────────────────────────────
@feedback_bp.route("/summary", methods=["GET"])
@jwt_required()
def feedback_summary():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """SELECT
                 COUNT(*) as total_feedback,
                 AVG(rating) as avg_rating,
                 SUM(CASE WHEN rating=5 THEN 1 ELSE 0 END) as five_star,
                 SUM(CASE WHEN rating=4 THEN 1 ELSE 0 END) as four_star,
                 SUM(CASE WHEN rating=3 THEN 1 ELSE 0 END) as three_star,
                 SUM(CASE WHEN rating=2 THEN 1 ELSE 0 END) as two_star,
                 SUM(CASE WHEN rating=1 THEN 1 ELSE 0 END) as one_star
               FROM feedback"""
        )
        summary = cursor.fetchone()
        cursor.execute(
            """SELECT f.rating, f.remarks, f.created_at,
                      c.complaint_id, c.title, c.category,
                      u.name as user_name
               FROM feedback f
               JOIN complaints c ON f.complaint_id=c.complaint_id
               JOIN users u ON f.user_id=u.user_id
               ORDER BY f.created_at DESC LIMIT 20"""
        )
        recent = cursor.fetchall()
    return success_response(data={"summary": summary, "recent_feedback": recent})
