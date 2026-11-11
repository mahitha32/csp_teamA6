"""
app/routes/contact.py
Contact form submission & management - saves messages to contact_messages table
Village Complaint Redressal System - Vemavaram Village
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
from app.utils.helpers import success_response, error_response
from app.utils.decorators import admin_required

contact_bp = Blueprint("contact", __name__)


# ─────────────────────────────────────────────
# POST /api/contact
# Public: Submit a message from the website contact form
# ─────────────────────────────────────────────
@contact_bp.route("", methods=["POST"])
def submit_contact():
    data = request.get_json(silent=True) or {}
    name    = data.get("name", "").strip()
    email   = data.get("email", "").strip()
    phone   = data.get("phone", "").strip()
    message = data.get("message", "").strip()

    if not name:
        return error_response("Name is required")
    if not email:
        return error_response("Email address is required")
    if not message:
        return error_response("Message is required")

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """INSERT INTO contact_messages (name, email, phone, message)
               VALUES (%s, %s, %s, %s)""",
            (name, email, phone or None, message)
        )
    db.commit()

    return success_response(
        message="Thank you! Your message has been received. The Vemavaram Village administration will reach out soon.",
        status_code=201
    )


# ─────────────────────────────────────────────
# GET /api/contact
# Admin: List submitted contact messages
# ─────────────────────────────────────────────
@contact_bp.route("", methods=["GET"])
@jwt_required()
@admin_required
def list_contacts():
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    offset   = (page - 1) * per_page

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as total FROM contact_messages")
        total = cursor.fetchone()["total"]

        cursor.execute(
            """SELECT * FROM contact_messages
               ORDER BY created_at DESC
               LIMIT %s OFFSET %s""",
            (per_page, offset)
        )
        messages = cursor.fetchall()

    return success_response(data={
        "messages": messages,
        "total": total,
        "page": page,
        "per_page": per_page
    })


# ─────────────────────────────────────────────
# PUT /api/contact/<id>/read
# Admin: Mark message as read
# ─────────────────────────────────────────────
@contact_bp.route("/<int:message_id>/read", methods=["PUT"])
@jwt_required()
@admin_required
def mark_contact_read(message_id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "UPDATE contact_messages SET is_read = 1 WHERE message_id = %s",
            (message_id,)
        )
    db.commit()
    return success_response(message="Message marked as read")

