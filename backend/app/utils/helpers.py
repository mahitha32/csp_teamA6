"""
app/utils/helpers.py — Common helper functions
Village Complaint Redressal System - Vemavaram Village
"""

import re
from datetime import datetime


def validate_mobile(mobile: str) -> bool:
    """Validate Indian mobile number (10 digits, optionally prefixed with +91)."""
    mobile = mobile.strip().replace(" ", "")
    pattern = r"^(?:\+91)?[6-9]\d{9}$"
    return bool(re.match(pattern, mobile))


def normalize_mobile(mobile: str) -> str:
    """Normalize mobile to 10-digit format without country code."""
    mobile = mobile.strip().replace(" ", "")
    if mobile.startswith("+91"):
        mobile = mobile[3:]
    elif mobile.startswith("91") and len(mobile) == 12:
        mobile = mobile[2:]
    return mobile


def success_response(data=None, message="Success", status_code=200):
    """Standard success response."""
    resp = {"success": True, "message": message}
    if data is not None:
        resp["data"] = data
    return resp, status_code


def error_response(message="An error occurred", status_code=400, errors=None):
    """Standard error response."""
    resp = {"success": False, "message": message}
    if errors:
        resp["errors"] = errors
    return resp, status_code


def paginate_query(cursor, query: str, params: tuple, page: int, per_page: int):
    """Execute a paginated query and return (items, total_count)."""
    # Count total
    count_query = f"SELECT COUNT(*) as total FROM ({query}) as sub"
    cursor.execute(count_query, params)
    total = cursor.fetchone()["total"]

    # Fetch page
    offset = (page - 1) * per_page
    cursor.execute(f"{query} LIMIT %s OFFSET %s", params + (per_page, offset))
    items = cursor.fetchall()

    return items, total


def serialize_datetime(obj):
    """JSON serializer for datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def format_complaint_id(year: int, seq: int) -> str:
    """Format complaint ID: CMP2026001."""
    return f"CMP{year}{str(seq).zfill(3)}"
