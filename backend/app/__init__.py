"""
app/__init__.py – Flask application factory
Village Complaint Redressal System - Vemavaram Village
"""

import os
import pymysql
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

from app.config import config_map

# Global database connection (reconnects automatically)
_db_connection = None


def get_db():
    """Return a live MySQL connection, reconnecting if needed."""
    global _db_connection
    try:
        if _db_connection is None or not _db_connection.open:
            raise Exception("Not connected")
        _db_connection.ping()
    except Exception:
        from flask import current_app
        cfg = current_app.config
        connect_kwargs = {
            "host": cfg["DB_HOST"],
            "port": cfg["DB_PORT"],
            "user": cfg["DB_USER"],
            "password": cfg["DB_PASSWORD"],
            "database": cfg["DB_NAME"],
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor,
            "autocommit": False,
        }
        ssl_config = {}
        if cfg.get("DB_SSL_CA"):
            ssl_config["ca"] = cfg["DB_SSL_CA"]
        elif cfg.get("DB_SSL_MODE") or ("tidbcloud.com" in str(cfg.get("DB_HOST", ""))):
            import certifi
            ssl_config["ca"] = certifi.where()

        if ssl_config:
            connect_kwargs["ssl"] = ssl_config

        _db_connection = pymysql.connect(**connect_kwargs)
    return _db_connection


def create_app(env: str = None) -> Flask:
    """Flask application factory."""
    env = env or os.getenv("FLASK_ENV", "development")
    config_class = config_map.get(env, config_map["development"])

    app = Flask(__name__)
    app.config.from_object(config_class)

    # JWT timedelta conversion
    app.config["JWT_ACCESS_TOKEN_EXPIRES"]  = timedelta(seconds=app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=app.config["JWT_REFRESH_TOKEN_EXPIRES"])

    # ── Extensions ──────────────────────────────────────────
    CORS(app, origins=app.config["ALLOWED_ORIGINS"], supports_credentials=True)
    jwt = JWTManager(app)

    # JWT identity serializer (ensures RFC 7519 sub claim is a valid string for PyJWT 2.x)
    import json
    import flask_jwt_extended.utils

    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        if isinstance(identity, dict):
            return json.dumps(identity)
        return str(identity)

    # Automatically deserialize JSON string back to dict when get_jwt_identity() is called
    orig_get_jwt_identity = flask_jwt_extended.utils.get_jwt_identity
    def safe_get_jwt_identity():
        val = orig_get_jwt_identity()
        if isinstance(val, str) and val.startswith("{") and val.endswith("}"):
            try:
                return json.loads(val)
            except Exception:
                return val
        return val

    flask_jwt_extended.utils.get_jwt_identity = safe_get_jwt_identity
    flask_jwt_extended.get_jwt_identity = safe_get_jwt_identity

    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return jsonify({"success": False, "message": "Authorization required", "reason": reason}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"success": False, "message": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"success": False, "message": "Invalid token", "reason": reason}), 422

    # ── Blueprints ───────────────────────────────────────────
    from app.routes.auth          import auth_bp
    from app.routes.complaints    import complaints_bp
    from app.routes.admin         import admin_bp
    from app.routes.workers       import workers_bp
    from app.routes.feedback      import feedback_bp
    from app.routes.notifications import notifications_bp
    from app.routes.analytics_v2  import analytics_v2_bp
    from app.routes.assets        import assets_bp
    from app.routes.reports       import reports_bp
    from app.routes.contact       import contact_bp

    app.register_blueprint(auth_bp,          url_prefix="/api/auth")
    app.register_blueprint(complaints_bp,    url_prefix="/api/complaints")
    app.register_blueprint(admin_bp,         url_prefix="/api/admin")
    app.register_blueprint(workers_bp,       url_prefix="/api/workers")
    app.register_blueprint(feedback_bp,      url_prefix="/api/feedback")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    app.register_blueprint(analytics_v2_bp,  url_prefix="/api/analytics_v2")
    app.register_blueprint(assets_bp,        url_prefix="/api/assets")
    app.register_blueprint(reports_bp,       url_prefix="/api/reports")
    app.register_blueprint(contact_bp,       url_prefix="/api/contact")

    # ── Health check ─────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return jsonify({
            "success": True,
            "message": "Vemavaram Village CSP API is running",
            "version": "2.0.0",
            "village": app.config["VILLAGE_NAME"],
        })

    # ── Global error handlers ────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "message": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "message": "Internal server error"}), 500

    return app
