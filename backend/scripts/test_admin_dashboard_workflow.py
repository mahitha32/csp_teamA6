"""
csp/backend/scripts/test_admin_dashboard_workflow.py
Phase 5: Complete Admin Dashboard Integration & Security Test Suite
Tests all 14 admin requirements, RBAC boundaries, and MySQL persistence.
"""

import os
import sys
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app, get_db

app = create_app("development")
client = app.test_client()

ADMIN_MOBILE = "9999900000"
ADMIN_PASSWORD = "Admin@123"

TEST_WORKER_MOBILE = "9888877777"
TEST_CITIZEN_MOBILE = "9777766666"

created_worker_ids = []
created_complaint_ids = []
created_citizen_ids = []
created_asset_ids = []


def cleanup():
    with app.app_context():
        db = get_db()
        with db.cursor() as cursor:
            for cid in created_complaint_ids:
                cursor.execute("DELETE FROM feedback WHERE complaint_id = %s", (cid,))
                cursor.execute("DELETE FROM assignments WHERE complaint_id = %s", (cid,))
                cursor.execute("DELETE FROM complaint_status_history WHERE complaint_id = %s", (cid,))
                cursor.execute("DELETE FROM complaints WHERE complaint_id = %s", (cid,))
            for aid in created_asset_ids:
                cursor.execute("DELETE FROM assets WHERE asset_id = %s", (aid,))
            for uid in created_citizen_ids:
                cursor.execute("DELETE FROM notifications WHERE user_id = %s", (uid,))
                cursor.execute("DELETE FROM users WHERE user_id = %s", (uid,))
            for wid in created_worker_ids:
                cursor.execute("DELETE FROM worker_profiles WHERE user_id = %s", (wid,))
                cursor.execute("DELETE FROM users WHERE user_id = %s", (wid,))
            cursor.execute("DELETE FROM users WHERE mobile IN (%s, %s)", (TEST_WORKER_MOBILE, TEST_CITIZEN_MOBILE))
        db.commit()


class TestAdminDashboardWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = app.app_context()
        cls.ctx.push()
        cleanup()

    @classmethod
    def tearDownClass(cls):
        cleanup()
        cls.ctx.pop()
        print("\n[CLEANUP] Test admin records cleaned up successfully.")

    # ─────────────────────────────────────────────────────────────
    # STEP 2: Admin Authentication & RBAC Access Barrier
    # ─────────────────────────────────────────────────────────────
    def test_01_admin_login_and_rbac_protection(self):
        print("\n--- 1. Testing Admin Authentication & RBAC Protection ---")
        # 1. Successful Admin Login
        res = client.post("/api/auth/admin-login", json={
            "mobile": ADMIN_MOBILE,
            "password": ADMIN_PASSWORD
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        admin_token = data["access_token"]
        self.assertIsNotNone(admin_token)
        self.assertEqual(data["user"]["role"], "admin")
        print(f"  [PASS] Admin authenticated: {data['user']['name']} (Role: admin)")

        # 2. Register citizen and attempt to access admin endpoints
        res = client.post("/api/auth/register", json={
            "name": "Intruder Citizen",
            "mobile": TEST_CITIZEN_MOBILE,
            "password": "Password@123",
            "village": "Vemavaram"
        })
        citizen_token = res.get_json()["data"]["access_token"]
        citizen_id = res.get_json()["data"]["user"]["user_id"]
        created_citizen_ids.append(citizen_id)

        # Citizen trying /api/admin/analytics -> 403 Forbidden
        res = client.get("/api/admin/analytics", headers={"Authorization": f"Bearer {citizen_token}"})
        self.assertEqual(res.status_code, 403)
        self.assertIn("Access denied", res.get_json()["message"])

        # Citizen trying /api/admin/complaints -> 403 Forbidden
        res = client.get("/api/admin/complaints", headers={"Authorization": f"Bearer {citizen_token}"})
        self.assertEqual(res.status_code, 403)

        # Citizen trying /api/workers -> 403 Forbidden
        res = client.get("/api/workers", headers={"Authorization": f"Bearer {citizen_token}"})
        self.assertEqual(res.status_code, 403)
        print("  [PASS] RBAC properly blocks non-admin users with 403 Forbidden")

        # 3. Unauthenticated request without token -> 401 Unauthorized
        res = client.get("/api/admin/analytics")
        self.assertEqual(res.status_code, 401)
        print("  [PASS] Unauthenticated access blocked with 401 Unauthorized")

    # ─────────────────────────────────────────────────────────────
    # STEP 3: Admin Overview / Dashboard Statistics
    # ─────────────────────────────────────────────────────────────
    def test_02_dashboard_overview_analytics(self):
        print("\n--- 2. Testing Dashboard Overview Analytics ---")
        res = client.post("/api/auth/admin-login", json={"mobile": ADMIN_MOBILE, "password": ADMIN_PASSWORD})
        admin_token = res.get_json()["data"]["access_token"]

        res = client.get("/api/admin/analytics", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["success"])
        analytics = body["data"]

        self.assertIn("summary", analytics)
        summary = analytics["summary"]
        self.assertIn("total", summary)
        self.assertIn("submitted", summary)
        self.assertIn("assigned", summary)
        self.assertIn("in_progress", summary)
        self.assertIn("resolved", summary)
        self.assertIn("avg_rating", summary)
        self.assertIn("avg_resolution_days", summary)

        self.assertIn("category_breakdown", analytics)
        self.assertIn("monthly_trend", analytics)
        self.assertIn("worker_performance", analytics)
        print(f"  [PASS] Live dashboard statistics verified: Total = {summary['total']}, Resolved = {summary['resolved']}")

    # ─────────────────────────────────────────────────────────────
    # STEP 4: Complaint Management (List, Search, Filter, Details)
    # ─────────────────────────────────────────────────────────────
    def test_03_complaint_management_and_filters(self):
        print("\n--- 3. Testing Complaint Management & Filters ---")
        # 1. Citizen submits a test complaint
        res = client.post("/api/auth/login", json={"mobile": TEST_CITIZEN_MOBILE, "password": "Password@123"})
        cit_token = res.get_json()["data"]["access_token"]

        res = client.post(
            "/api/complaints",
            headers={"Authorization": f"Bearer {cit_token}"},
            json={
                "title": "Low Water Pressure in Ward 4 Main Pipeline",
                "category": "Water Supply Problems",
                "description": "Pressure drop in pipeline since two days, taps running dry in morning.",
                "ward_id": 4,
                "location": "Near Overhead Tank, Vemavaram",
                "latitude": 16.4880,
                "longitude": 80.6450
            }
        )
        self.assertEqual(res.status_code, 201)
        cid = res.get_json()["data"]["complaint_id"]
        created_complaint_ids.append(cid)
        print(f"  [PASS] Test complaint submitted: {cid}")

        # 2. Admin retrieves complaint list
        res = client.post("/api/auth/admin-login", json={"mobile": ADMIN_MOBILE, "password": ADMIN_PASSWORD})
        admin_token = res.get_json()["data"]["access_token"]

        res = client.get("/api/admin/complaints", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(res.status_code, 200)
        complaints = res.get_json()["data"]["complaints"]
        self.assertTrue(any(c["complaint_id"] == cid for c in complaints))
        print("  [PASS] Admin complaint listing includes newly submitted complaint")

        # 3. Test Search Filter
        res = client.get(f"/api/admin/complaints?search={cid}", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(res.status_code, 200)
        search_results = res.get_json()["data"]["complaints"]
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]["complaint_id"], cid)
        print("  [PASS] Search by Complaint ID returns exact match")

        # 4. Test Category Filter
        res = client.get("/api/admin/complaints?category=Water Supply Problems", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(res.status_code, 200)
        cat_results = res.get_json()["data"]["complaints"]
        self.assertTrue(all(c["category"] == "Water Supply Problems" for c in cat_results))
        print("  [PASS] Category filter matches exact database category")

        # 5. Admin views single complaint details
        res = client.get(f"/api/complaints/{cid}", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(res.status_code, 200)
        detail = res.get_json()["data"]
        self.assertEqual(detail["complaint_id"], cid)
        self.assertEqual(detail["ward_id"], 4)
        print("  [PASS] Admin viewed complaint details and location coordinates")

    # ─────────────────────────────────────────────────────────────
    # STEP 5 & 6: Worker Management & Complaint Assignment
    # ─────────────────────────────────────────────────────────────
    def test_04_worker_management_and_assignment(self):
        print("\n--- 4. Testing Worker Management & Task Assignment ---")
        res = client.post("/api/auth/admin-login", json={"mobile": ADMIN_MOBILE, "password": ADMIN_PASSWORD})
        admin_token = res.get_json()["data"]["access_token"]

        # 1. Admin adds new worker
        res = client.post(
            "/api/workers",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "worker_name": "Kishore Water Engineer",
                "mobile": TEST_WORKER_MOBILE,
                "department": "Water Supply"
            }
        )
        self.assertEqual(res.status_code, 201)
        worker_id = res.get_json()["data"]["worker_id"]
        created_worker_ids.append(worker_id)
        print(f"  [PASS] Worker created in MySQL: ID = {worker_id}, Dept: Water Supply")

        # 2. Worker Listing
        res = client.get("/api/workers", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(res.status_code, 200)
        worker_list = res.get_json()["data"]["workers"]
        self.assertTrue(any(w["worker_id"] == worker_id for w in worker_list))
        print("  [PASS] Worker list contains newly added worker")

        # 3. Admin assigns complaint to worker
        target_cid = created_complaint_ids[0]
        res = client.post(
            f"/api/admin/complaints/{target_cid}/assign",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "worker_id": worker_id,
                "notes": "Inspect pipeline valve near overhead tank immediately"
            }
        )
        self.assertEqual(res.status_code, 200)
        print(f"  [PASS] Complaint {target_cid} assigned to worker {worker_id}")

        # 4. Verify in MySQL database
        db = get_db()
        with db.cursor() as cursor:
            # Check complaint status changed to 'Assigned'
            cursor.execute("SELECT status, worker_id FROM complaints WHERE complaint_id = %s", (target_cid,))
            c_row = cursor.fetchone()
            self.assertEqual(c_row["status"], "Assigned")
            self.assertEqual(c_row["worker_id"], worker_id)

            # Check assignment record
            cursor.execute("SELECT * FROM assignments WHERE complaint_id = %s AND is_current = 1", (target_cid,))
            a_row = cursor.fetchone()
            self.assertIsNotNone(a_row)
            self.assertEqual(a_row["worker_id"], worker_id)
            print("  [PASS] Assignment record and status update confirmed in MySQL")

        # 5. Verify notification sent to citizen
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (created_citizen_ids[0],))
            notif = cursor.fetchone()
            self.assertIsNotNone(notif)
            self.assertIn("Worker Assigned", notif["title"])
            print(f"  [PASS] Citizen notification generated: '{notif['title']}'")

    # ─────────────────────────────────────────────────────────────
    # STEP 7 & 8: GIS Map, Reports, and Status Transition
    # ─────────────────────────────────────────────────────────────
    def test_05_gis_map_and_reports(self):
        print("\n--- 5. Testing GIS Map, Status Management & Reports ---")
        res = client.post("/api/auth/admin-login", json={"mobile": ADMIN_MOBILE, "password": ADMIN_PASSWORD})
        admin_token = res.get_json()["data"]["access_token"]

        # 1. GIS Map GeoJSON
        res = client.get("/api/analytics_v2/gis_map", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(res.status_code, 200)
        geojson = res.get_json()["data"]["geojson"]
        self.assertEqual(geojson["type"], "FeatureCollection")
        self.assertTrue(len(geojson["features"]) >= 1)
        print(f"  [PASS] GeoJSON map features retrieved: {len(geojson['features'])} points mapped")

        # 2. Ward-wise Analytics
        res = client.get("/api/analytics_v2/ward_stats", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(res.status_code, 200)
        wards = res.get_json()["data"]["ward_stats"]
        self.assertTrue(len(wards) >= 1)
        print(f"  [PASS] Ward analytics retrieved for {len(wards)} wards")

        # 3. Survey Insights
        res = client.get("/api/admin/survey-insights", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(res.status_code, 200)
        survey = res.get_json()["data"]
        self.assertEqual(survey["village"], "Vemavaram")
        self.assertTrue(len(survey["insights"]) >= 1)
        print(f"  [PASS] Field survey insights verified: {survey['total_responses']} responses")

        # 4. Reports & CSV Export Query
        res = client.get("/api/admin/reports", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(res.status_code, 200)
        report_data = res.get_json()["data"]
        self.assertTrue(len(report_data["report"]) >= 1)
        print(f"  [PASS] Report generated with {report_data['total']} records from database")

        # 5. Status update to Resolved
        target_cid = created_complaint_ids[0]
        res = client.put(
            f"/api/admin/complaints/{target_cid}/status",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": "Resolved", "notes": "Pipeline valve replaced and pressure restored"}
        )
        self.assertEqual(res.status_code, 200)
        print("  [PASS] Admin updated complaint status to Resolved")

    # ─────────────────────────────────────────────────────────────
    # STEP 9: Asset Registry CRUD
    # ─────────────────────────────────────────────────────────────
    def test_06_asset_registry(self):
        print("\n--- 6. Testing Asset Registry ---")
        res = client.post("/api/auth/admin-login", json={"mobile": ADMIN_MOBILE, "password": ADMIN_PASSWORD})
        admin_token = res.get_json()["data"]["access_token"]

        test_asset_id = "AST-VEM-QA01"
        res = client.post(
            "/api/assets",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "asset_id": test_asset_id,
                "type": "Water Tank",
                "ward_id": 4,
                "location_lat": 16.4880,
                "location_lng": 80.6450,
                "status": "Active"
            }
        )
        self.assertEqual(res.status_code, 201)
        created_asset_ids.append(test_asset_id)
        print(f"  [PASS] Asset {test_asset_id} created in MySQL")

        res = client.get("/api/assets", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(res.status_code, 200)
        assets = res.get_json()["data"]["assets"]
        self.assertTrue(any(a["asset_id"] == test_asset_id for a in assets))
        print("  [PASS] Asset retrieved in registry listing")


if __name__ == "__main__":
    unittest.main()
