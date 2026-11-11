"""
app/routes/assets.py
Village Asset Registry CRUD
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app import get_db
from app.utils.helpers import success_response, error_response

assets_bp = Blueprint("assets", __name__)

@assets_bp.route("", methods=["GET"])
@jwt_required()
def list_assets():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT a.*, w.name as ward_name 
            FROM assets a 
            LEFT JOIN wards w ON a.ward_id = w.ward_id
        """)
        assets = cursor.fetchall()
    return success_response(data={"assets": assets})

@assets_bp.route("", methods=["POST"])
@jwt_required()
def create_asset():
    data = request.get_json()
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO assets (asset_id, type, ward_id, location_lat, location_lng, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['asset_id'], data['type'], data['ward_id'], data['location_lat'], data['location_lng'], data.get('status', 'Active')))
    db.commit()
    return success_response(message="Asset created successfully", status_code=201)
