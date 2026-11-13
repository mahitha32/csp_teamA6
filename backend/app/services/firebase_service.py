"""
app/services/firebase_service.py
Firebase Phone Auth token verification ONLY.
Image storage has moved to Cloudinary (see image_service.py).
Village Complaint Redressal System - Vemavaram Village
"""

import os
from flask import current_app

_firebase_initialized = False


def _init_firebase():
    """
    Initialize Firebase Admin SDK once per process.
    Only needed for phone-auth token verification (mobile app flow).
    If the credentials file is missing, phone auth will fail gracefully.
    """
    global _firebase_initialized
    if _firebase_initialized:
        return

    try:
        import firebase_admin
        from firebase_admin import credentials
        import json
    except ImportError:
        raise RuntimeError(
            "firebase_admin package is not installed. Install it with: pip install firebase-admin"
        )

    # 1. Check for inline JSON string in environment variable
    raw_json = os.getenv("FIREBASE_CREDENTIALS_JSON") or current_app.config.get("FIREBASE_CREDENTIALS_JSON")
    if raw_json:
        try:
            cred_dict = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
            cred = credentials.Certificate(cred_dict)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            return
        except Exception as e:
            raise ValueError(f"Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")

    # 2. Check for credentials file path
    cred_path = current_app.config.get(
        "FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json"
    )
    if not os.path.exists(cred_path):
        raise FileNotFoundError(
            f"Firebase credentials file not found at '{cred_path}'. "
            "Phone authentication via Firebase will not work. "
            "See docs/Firebase_Setup_Guide.md for setup instructions. "
            "Citizens can still use mobile+password login via /api/auth/login."
        )

    cred = credentials.Certificate(cred_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    _firebase_initialized = True


def verify_firebase_token(id_token: str) -> dict:
    """
    Verify a Firebase Auth ID token (used by the Flutter mobile app).
    Returns the decoded token dict containing uid, phone_number, etc.
    Raises ValueError with a human-readable message on failure.
    """
    _init_firebase()
    try:
        from firebase_admin import auth
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        if "ExpiredIdTokenError" in type(e).__name__:
            raise ValueError("Firebase token has expired. Please sign in again.")
        elif "InvalidIdTokenError" in type(e).__name__:
            raise ValueError("Invalid Firebase token.")
        else:
            raise ValueError(f"Token verification failed: {str(e)}")


def send_fcm_push(token: str, title: str, body: str) -> bool:
    """
    Send a Firebase Cloud Messaging push notification.
    Non-fatal — returns False if Firebase is not configured.
    """
    try:
        _init_firebase()
        from firebase_admin import messaging
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
        )
        messaging.send(message)
        return True
    except Exception as e:
        if current_app:
            current_app.logger.warning(f"[FCM] Push notification failed (non-fatal): {e}")
        return False
