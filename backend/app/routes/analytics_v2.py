"""
app/routes/analytics_v2.py
Advanced Analytics for Wards and GIS Mapping
Village Complaint Redressal System - Vemavaram Village
"""

from flask import Blueprint
from flask_jwt_extended import jwt_required
from app import get_db
from app.utils.helpers import success_response

analytics_v2_bp = Blueprint("analytics_v2", __name__)


@analytics_v2_bp.route("/ward_stats", methods=["GET"])
@jwt_required()
def ward_stats():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT
                w.ward_id,
                w.name as ward_name,
                COUNT(c.complaint_id) as total_complaints,
                SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN c.status IN ('Submitted', 'Under Review', 'Assigned', 'In Progress') THEN 1 ELSE 0 END) as pending,
                COALESCE(AVG(DATEDIFF(c.resolved_at, c.created_at)), 0) as avg_resolution_time,
                COALESCE(AVG(f.rating), 0) as avg_satisfaction
            FROM wards w
            LEFT JOIN complaints c ON w.ward_id = c.ward_id
            LEFT JOIN feedback f ON c.complaint_id = f.complaint_id
            GROUP BY w.ward_id, w.name
            ORDER BY w.ward_id ASC
        """)
        stats = cursor.fetchall()
    return success_response(data={"ward_stats": stats})


@analytics_v2_bp.route("/gis_map", methods=["GET"])
@jwt_required()
def gis_map():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT c.complaint_id, c.category, c.status, c.priority,
                   c.latitude, c.longitude, c.location, c.created_at,
                   s.max_days_to_resolve,
                   CASE
                       WHEN c.status != 'Resolved' AND DATEDIFF(NOW(), c.created_at) > COALESCE(s.max_days_to_resolve, 7)
                       THEN 'Breached'
                       ELSE 'Normal'
                   END as sla_status
            FROM complaints c
            LEFT JOIN slas s ON c.category = s.category
            WHERE c.latitude IS NOT NULL AND c.longitude IS NOT NULL
        """)
        points = cursor.fetchall()

        features = []
        for p in points:
            try:
                lat = float(p["latitude"])
                lng = float(p["longitude"])
            except (ValueError, TypeError):
                continue

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "properties": {
                    "complaint_id": p["complaint_id"],
                    "category": p["category"],
                    "status": p["status"],
                    "priority": p["priority"],
                    "location": p.get("location", ""),
                    "sla_status": p.get("sla_status", "Normal")
                }
            })

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
    return success_response(data={"geojson": geojson})
