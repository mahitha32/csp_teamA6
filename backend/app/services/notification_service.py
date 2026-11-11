"""
app/services/notification_service.py
In-app notification creation + Firebase Cloud Messaging (FCM) push
Village Complaint Redressal System - Vemavaram Village
"""

from flask import current_app
from app import get_db


def create_notification(user_id: int, title: str, message: str,
                         notif_type: str = "general", complaint_id: str = None):
    """
    Insert a notification into the DB and (optionally) send FCM push.
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO notifications
                   (user_id, complaint_id, title, message, type)
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, complaint_id, title, message, notif_type)
            )
            # Fetch FCM token for push notification
            cursor.execute("SELECT fcm_token FROM users WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()
        db.commit()

        # Send FCM push if token exists
        if row and row.get("fcm_token"):
            _send_fcm_push(row["fcm_token"], title, message)

    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Notification error: {e}")


def notify_complaint_received(user_id: int, complaint_id: str):
    create_notification(
        user_id,
        title="✅ Complaint Received",
        message=f"Your complaint {complaint_id} has been submitted successfully. We'll review it shortly.",
        notif_type="complaint_received",
        complaint_id=complaint_id
    )


def notify_complaint_assigned(user_id: int, complaint_id: str, worker_name: str):
    create_notification(
        user_id,
        title="👷 Worker Assigned",
        message=f"Complaint {complaint_id} has been assigned to {worker_name}. Work will begin soon.",
        notif_type="complaint_assigned",
        complaint_id=complaint_id
    )


def notify_status_changed(user_id: int, complaint_id: str, new_status: str):
    status_messages = {
        "Under Review": "Your complaint is under review by the Panchayat office.",
        "Assigned": "A worker has been assigned to your complaint.",
        "In Progress": "Work has started on your complaint.",
        "Resolved": "🎉 Your complaint has been resolved! Please provide feedback.",
        "Rejected": "Your complaint could not be processed. Contact the Panchayat office for details.",
    }
    msg = status_messages.get(new_status, f"Your complaint status is now: {new_status}")
    create_notification(
        user_id,
        title=f"📋 Status Update: {new_status}",
        message=f"{complaint_id} — {msg}",
        notif_type="status_changed",
        complaint_id=complaint_id
    )


def _send_fcm_push(token: str, title: str, body: str):
    """
    Send FCM push notification via Firebase Admin SDK.
    Requires firebase_admin to be initialized.
    """
    try:
        from firebase_admin import messaging
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
        )
        messaging.send(message)
    except Exception as e:
        current_app.logger.warning(f"FCM push failed (non-fatal): {e}")
