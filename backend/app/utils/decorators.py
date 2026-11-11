"""
app/utils/decorators.py – Route decorator utilities
Village Complaint Redressal System - Vemavaram Village
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request


def roles_required(*roles):
    """Decorator: restrict access to users with specified roles."""
    # Normalize roles: if citizen is allowed, accept villager as well for backward compatibility
    allowed_roles = set(roles)
    if "citizen" in allowed_roles:
        allowed_roles.add("villager")

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            role = identity.get("role")

            if role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "message": f"Access denied. Required roles: {', '.join(roles)}"
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Shortcut: admin-only route."""
    return roles_required("admin")(fn)


def worker_required(fn):
    """Shortcut: worker or admin route."""
    return roles_required("worker", "admin")(fn)


def citizen_required(fn):
    """Shortcut: citizen or admin route."""
    return roles_required("citizen", "admin")(fn)
