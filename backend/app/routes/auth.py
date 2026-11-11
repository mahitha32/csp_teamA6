"""
app/routes/auth.py
Unified authentication routes for Citizens, Workers, and Admins.
Village Complaint Redressal System - Vemavaram Village

Roles:
  - citizen : Web registration/login OR Mobile Firebase Phone Auth
  - worker  : Created by admin, logs in with mobile + password
  - admin   : System admin, logs in with mobile + password
"""

import bcrypt
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from app import get_db
from app.services.firebase_service import verify_firebase_token
from app.utils.helpers import (
    validate_mobile, normalize_mobile,
    success_response, error_response
)

auth_bp = Blueprint("auth", __name__)


# ─────────────────────────────────────────────
# POST /api/auth/register
# Citizen web/app registration (mobile + password)
# ─────────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    data     = request.get_json(silent=True) or {}
    name     = data.get("name", "").strip()
    mobile   = normalize_mobile(data.get("mobile", "").strip())
    password = data.get("password", "").strip()
    village  = data.get("village", "Vemavaram").strip() or "Vemavaram"

    errors = []
    if not name:
        errors.append("Name is required")
    if not mobile:
        errors.append("Mobile number is required")
    elif not validate_mobile(mobile):
        errors.append("Invalid mobile number format")
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters")

    if errors:
        return error_response("Validation failed", 422, errors)

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT user_id FROM users WHERE mobile = %s", (mobile,))
        if cursor.fetchone():
            return error_response("A user with this mobile number already exists", 409)

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute(
            """INSERT INTO users (name, mobile, village, password_hash, role)
               VALUES (%s, %s, %s, %s, 'citizen')""",
            (name, mobile, village, hashed)
        )
        user_id = cursor.lastrowid
    db.commit()

    identity = {"user_id": user_id, "role": "citizen", "mobile": mobile}
    access_token  = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return success_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "user_id": user_id,
                "name": name,
                "mobile": mobile,
                "role": "citizen",
                "village": village,
            }
        },
        message="Registration successful",
        status_code=201
    )


# ─────────────────────────────────────────────
# POST /api/auth/login
# Citizen web/app login (mobile + password)
# ─────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def citizen_login():
    data     = request.get_json(silent=True) or {}
    mobile   = normalize_mobile(data.get("mobile", "").strip())
    password = data.get("password", "").encode("utf-8")

    if not mobile or not password:
        return error_response("Mobile and password are required")

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """SELECT * FROM users
               WHERE mobile = %s AND role IN ('citizen', 'villager') AND is_active = 1""",
            (mobile,)
        )
        user = cursor.fetchone()

    if not user:
        return error_response("Invalid credentials", 401)

    stored_hash = user["password_hash"].encode("utf-8")
    if not bcrypt.checkpw(password, stored_hash):
        return error_response("Invalid credentials", 401)

    role = "citizen"
    identity = {"user_id": user["user_id"], "role": role, "mobile": mobile}
    access_token  = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return success_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "user_id": user["user_id"],
                "name": user["name"],
                "mobile": mobile,
                "role": role,
                "village": user.get("village", "Vemavaram"),
            }
        },
        message="Login successful"
    )


# ─────────────────────────────────────────────
# POST /api/auth/worker-login
# Worker login with mobile & password
# ─────────────────────────────────────────────
@auth_bp.route("/worker-login", methods=["POST"])
def worker_login():
    data     = request.get_json(silent=True) or {}
    mobile   = normalize_mobile(data.get("mobile", "").strip())
    password = data.get("password", "").encode("utf-8")

    if not mobile or not password:
        return error_response("Mobile and password are required")

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """SELECT u.*, wp.department
               FROM users u
               LEFT JOIN worker_profiles wp ON u.user_id = wp.user_id
               WHERE u.mobile = %s AND u.role = 'worker' AND u.is_active = 1""",
            (mobile,)
        )
        worker = cursor.fetchone()

    if not worker:
        return error_response("Invalid worker credentials", 401)

    stored_hash = worker["password_hash"].encode("utf-8")
    if not bcrypt.checkpw(password, stored_hash):
        return error_response("Invalid worker credentials", 401)

    identity = {"user_id": worker["user_id"], "role": "worker", "mobile": mobile}
    access_token  = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return success_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "user_id": worker["user_id"],
                "name": worker["name"],
                "mobile": mobile,
                "role": "worker",
                "department": worker.get("department", "General Services"),
                "village": worker.get("village", "Vemavaram"),
            }
        },
        message="Worker login successful"
    )


# ─────────────────────────────────────────────
# POST /api/auth/admin-login
# Admin login with mobile & password
# ─────────────────────────────────────────────
@auth_bp.route("/admin-login", methods=["POST"])
def admin_login():
    data     = request.get_json(silent=True) or {}
    raw_mobile = data.get("mobile", "").strip()
    mobile   = normalize_mobile(raw_mobile) if raw_mobile else ""
    email    = data.get("email", "").strip()
    password = data.get("password", "").encode("utf-8")

    if not password or (not mobile and not email):
        return error_response("Mobile or email and password are required")

    db = get_db()
    with db.cursor() as cursor:
        if mobile:
            cursor.execute(
                "SELECT * FROM users WHERE mobile = %s AND role = 'admin' AND is_active = 1",
                (mobile,)
            )
        else:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s AND role = 'admin' AND is_active = 1",
                (email,)
            )
        user = cursor.fetchone()

    if not user:
        return error_response("Invalid admin credentials", 401)

    stored_hash = user["password_hash"].encode("utf-8")
    if not bcrypt.checkpw(password, stored_hash):
        return error_response("Invalid admin credentials", 401)

    identity = {"user_id": user["user_id"], "role": "admin", "mobile": mobile}
    access_token  = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return success_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "user_id": user["user_id"],
                "name": user["name"],
                "mobile": mobile,
                "role": "admin",
                "village": user.get("village", "Vemavaram"),
            }
        },
        message="Admin login successful"
    )


# ─────────────────────────────────────────────
# POST /api/auth/firebase-login
# Verify Firebase Phone Auth ID token and return app JWT
# (Used by Flutter mobile application)
# ─────────────────────────────────────────────
@auth_bp.route("/firebase-login", methods=["POST"])
def firebase_login():
    data     = request.get_json(silent=True) or {}
    id_token = data.get("id_token", "").strip()
    name     = data.get("name", "").strip()

    if not id_token:
        return error_response("Firebase ID token is required")

    try:
        decoded = verify_firebase_token(id_token)
    except ValueError as e:
        return error_response(str(e), 401)

    phone = decoded.get("phone_number", "")
    if not phone:
        return error_response("Phone number not found in Firebase token", 400)

    mobile = normalize_mobile(phone)
    db = get_db()

    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE mobile = %s", (mobile,))
        user = cursor.fetchone()

        if not user:
            # Auto-register citizen on first Firebase login
            display_name = name or decoded.get("name") or f"Citizen_{mobile[-4:]}"
            dummy_hash = bcrypt.hashpw(b"firebase_auth_citizen", bcrypt.gensalt()).decode("utf-8")
            cursor.execute(
                """INSERT INTO users (name, mobile, village, password_hash, role)
                   VALUES (%s, %s, %s, %s, 'citizen')""",
                (display_name, mobile, "Vemavaram", dummy_hash)
            )
            db.commit()
            user_id = cursor.lastrowid
            role = "citizen"
            user_name = display_name
            village = "Vemavaram"
        else:
            user_id = user["user_id"]
            role = "citizen" if user["role"] == "villager" else user["role"]
            user_name = user["name"]
            village = user.get("village", "Vemavaram")

    identity = {"user_id": user_id, "role": role, "mobile": mobile}
    access_token  = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return success_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "user_id": user_id,
                "name": user_name,
                "mobile": mobile,
                "role": role,
                "village": village,
            }
        },
        message="Login successful"
    )


# ─────────────────────────────────────────────
# POST /api/auth/refresh
# Refresh access token
# ─────────────────────────────────────────────
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return success_response(data={"access_token": access_token}, message="Token refreshed")


# ─────────────────────────────────────────────
# PUT /api/auth/profile
# Update user profile (name, fcm_token)
# ─────────────────────────────────────────────
@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    identity = get_jwt_identity()
    user_id  = identity["user_id"]
    data     = request.get_json(silent=True) or {}
    name     = data.get("name", "").strip()
    fcm_token = data.get("fcm_token", "").strip()

    if not name and not fcm_token:
        return error_response("Nothing to update")

    db = get_db()
    with db.cursor() as cursor:
        if name and fcm_token:
            cursor.execute(
                "UPDATE users SET name=%s, fcm_token=%s WHERE user_id=%s",
                (name, fcm_token, user_id)
            )
        elif name:
            cursor.execute("UPDATE users SET name=%s WHERE user_id=%s", (name, user_id))
        else:
            cursor.execute("UPDATE users SET fcm_token=%s WHERE user_id=%s", (fcm_token, user_id))
    db.commit()

    return success_response(message="Profile updated successfully")


# ─────────────────────────────────────────────
# GET /api/auth/me
# Get current logged-in user profile
# ─────────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    identity = get_jwt_identity()
    user_id  = identity["user_id"]
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            """SELECT u.user_id, u.name, u.mobile, u.village, u.role, u.created_at,
                      wp.department
               FROM users u
               LEFT JOIN worker_profiles wp ON u.user_id = wp.user_id
               WHERE u.user_id = %s""",
            (user_id,)
        )
        user = cursor.fetchone()

    if not user:
        return error_response("User not found", 404)

    return success_response(data=user)
