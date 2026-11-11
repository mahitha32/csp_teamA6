"""
app/routes/notifications.py
Notification routes — list, mark read, mark all read
Village Complaint Redressal System - Vemavaram Village
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
from app.utils.helpers import success_response, error_response

notifications_bp = Blueprint("notifications", __name__)


# GET /api/notifications
@notifications_bp.route("", methods=["GET"])
@jwt_required()
def list_notifications():
    identity = get_jwt_identity()
    user_id  = identity["user_id"]
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    offset   = (page - 1) * per_page

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as total FROM notifications WHERE user_id=%s", (user_id,))
        total = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) as unread FROM notifications WHERE user_id=%s AND is_read=0", (user_id,))
        unread = cursor.fetchone()["unread"]
        cursor.execute(
            """SELECT * FROM notifications WHERE user_id=%s
               ORDER BY created_at DESC LIMIT %s OFFSET %s""",
            (user_id, per_page, offset)
        )
        notifications = cursor.fetchall()

    return success_response(data={
        "notifications": notifications,
        "unread_count": unread,
        "total": total,
    })


# PUT /api/notifications/<id>/read
@notifications_bp.route("/<int:notif_id>/read", methods=["PUT"])
@jwt_required()
def mark_read(notif_id):
    identity = get_jwt_identity()
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "UPDATE notifications SET is_read=1 WHERE notification_id=%s AND user_id=%s",
            (notif_id, identity["user_id"])
        )
    db.commit()
    return success_response(message="Notification marked as read")


# PUT /api/notifications/read-all
@notifications_bp.route("/read-all", methods=["PUT"])
@jwt_required()
def mark_all_read():
    identity = get_jwt_identity()
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "UPDATE notifications SET is_read=1 WHERE user_id=%s", (identity["user_id"],)
        )
    db.commit()
    return success_response(message="All notifications marked as read")
