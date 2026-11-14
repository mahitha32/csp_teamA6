"""
config.py – Application configuration classes
Village Complaint Redressal System - Vemavaram Village
"""

import os
from dotenv import load_dotenv

# Explicitly load .env from the backend root directory
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(backend_dir, ".env"))


class Config:
    """Base configuration shared across all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", "vemavaram-csp-secret-key-change-in-prod")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "vemavaram-jwt-secret-change-in-prod")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 86400))     # 24 hours
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 2592000)) # 30 days

    # MySQL
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_NAME = os.getenv("DB_NAME", "vemavaram_csp")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_SSL_CA = os.getenv("DB_SSL_CA", None)
    DB_SSL_MODE = os.getenv("DB_SSL_MODE", None)

    # Cloudinary (image storage for complaints and resolution photos)
    CLOUDINARY_URL        = os.getenv("CLOUDINARY_URL", "")
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY    = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

    if CLOUDINARY_URL and not CLOUDINARY_CLOUD_NAME:
        import urllib.parse
        _c_parsed = urllib.parse.urlparse(CLOUDINARY_URL)
        CLOUDINARY_CLOUD_NAME = _c_parsed.hostname or ""
        CLOUDINARY_API_KEY    = _c_parsed.username or ""
        CLOUDINARY_API_SECRET = _c_parsed.password or ""

    # Firebase (Phone Auth token verification only — NOT used for image storage)
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")

    # OTP
    USE_REAL_OTP     = os.getenv("USE_REAL_OTP", "false").lower() == "true"
    OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", 10))
    OTP_MAX_ATTEMPTS   = int(os.getenv("OTP_MAX_ATTEMPTS", 3))

    # SMS Gateway (MSG91 — replace with your provider)
    MSG91_AUTH_KEY   = os.getenv("MSG91_AUTH_KEY", "")
    MSG91_TEMPLATE_ID = os.getenv("MSG91_TEMPLATE_ID", "")
    MSG91_SENDER_ID  = os.getenv("MSG91_SENDER_ID", "VEMVLG")

    # CORS — includes both local dev and production Vercel URL
    ALLOWED_ORIGINS = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://127.0.0.1:5500,https://complaintredressalsystem.vercel.app"
    ).split(",")

    VILLAGE_NAME = "Vemavaram"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DB_NAME = "vemavaram_csp_test"


config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
}
