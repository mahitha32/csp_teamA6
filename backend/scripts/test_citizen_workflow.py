"""
csp/backend/scripts/test_citizen_workflow.py
Phase 4: Complete Citizen Website Integration Test Suite
Tests all 10 citizen workflows, edge cases, input validation, and MySQL persistence.
"""

import io
import json
import os
import sys
import unittest
import requests

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app, get_db

app = create_app("development")
client = app.test_client()

TEST_CITIZEN_MOBILE = "9988776655"
TEST_CITIZEN_PASSWORD = "Password@123"
TEST_CITIZEN_NAME = "Vemavaram Citizen QA"

TEST_OTHER_MOBILE = "9988776644"
TEST_OTHER_PASSWORD = "Password@456"

created_complaint_ids = []
created_user_ids = []
created_contact_ids = []


def cleanup():
    with app.app_context():
        db = get_db()
        with db.cursor() as cursor:
            for cid in created_complaint_ids:
                cursor.execute("DELETE FROM feedback WHERE complaint_id = %s", (cid,))
                cursor.execute("DELETE FROM assignments WHERE complaint_id = %s", (cid,))
                cursor.execute("DELETE FROM complaint_status_history WHERE complaint_id = %s", (cid,))
                cursor.execute("DELETE FROM complaints WHERE complaint_id = %s", (cid,))
            for uid in created_user_ids:
                cursor.execute("DELETE FROM notifications WHERE user_id = %s", (uid,))
                cursor.execute("DELETE FROM users WHERE user_id = %s", (uid,))
            cursor.execute("DELETE FROM users WHERE mobile IN (%s, %s)", (TEST_CITIZEN_MOBILE, TEST_OTHER_MOBILE))
            cursor.execute("DELETE FROM contact_messages WHERE email LIKE 'qa_test_%@vemavaram.org'")
        db.commit()


class TestCitizenIntegrationWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = app.app_context()
        cls.ctx.push()
        cleanup()

    @classmethod
    def tearDownClass(cls):
        cleanup()
        cls.ctx.pop()
        print("\n[CLEANUP] Test citizen data cleaned up cleanly.")

    # ─────────────────────────────────────────────────────────────
    # STEP 2: Contact Form Integration & Validation
    # ─────────────────────────────────────────────────────────────
    def test_01_contact_form_submission_and_validation(self):
        print("\n--- 1. Testing Contact Form (POST /api/contact) ---")
        # 1. Invalid payload (missing email)
        res = client.post("/api/contact", json={"name": "Ravi", "message": "Help"})
        self.assertEqual(res.status_code, 400)
        self.assertIn("Email address is required", res.get_json()["message"])

        # 2. Invalid payload (missing message)
        res = client.post("/api/contact", json={"name": "Ravi", "email": "ravi@vemavaram.org"})
        self.assertEqual(res.status_code, 400)

        # 3. Valid submission
        test_email = "qa_test_contact@vemavaram.org"
        res = client.post("/api/contact", json={
            "name": "Ravi Kumar",
            "email": test_email,
            "phone": "9876543210",
            "message": "Streetlight on Ward 2 Main Road is flickering."
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["success"])
        print("  [PASS] Contact form successfully validated and submitted")

        # 4. Verify in MySQL database
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM contact_messages WHERE email = %s", (test_email,))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["name"], "Ravi Kumar")
            self.assertEqual(row["phone"], "9876543210")
            print(f"  [PASS] Contact message verified in MySQL (ID: {row['message_id']})")

    # ─────────────────────────────────────────────────────────────
    # STEP 3: Dynamic Statistics Endpoint
    # ─────────────────────────────────────────────────────────────
    def test_02_public_statistics(self):
        print("\n--- 2. Testing Dynamic Statistics (GET /api/admin/public-stats) ---")
        res = client.get("/api/admin/public-stats")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["success"])
        stats = body["data"]

        self.assertIn("total_complaints", stats)
        self.assertIn("resolved_complaints", stats)
        self.assertIn("pending_complaints", stats)
        self.assertIn("avg_resolution_hours", stats)
        self.assertIn("citizen_satisfaction", stats)
        self.assertIn("active_citizens", stats)
        self.assertEqual(stats["village"], "Vemavaram")

        # Compare directly with live DB counts
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as c FROM complaints")
            db_total = cursor.fetchone()["c"]
            self.assertEqual(stats["total_complaints"], db_total)
        print(f"  [PASS] Live statistics match MySQL: Total Complaints = {stats['total_complaints']}, Village = {stats['village']}")

    # ─────────────────────────────────────────────────────────────
    # STEP 4: Citizen Registration & Login
    # ─────────────────────────────────────────────────────────────
    def test_03_citizen_registration_and_validation(self):
        print("\n--- 3. Testing Citizen Registration (POST /api/auth/register) ---")
        # 1. Validation failure: Short password
        res = client.post("/api/auth/register", json={
            "name": TEST_CITIZEN_NAME,
            "mobile": TEST_CITIZEN_MOBILE,
            "password": "123"
        })
        self.assertEqual(res.status_code, 422)

        # 2. Validation failure: Invalid mobile
        res = client.post("/api/auth/register", json={
            "name": TEST_CITIZEN_NAME,
            "mobile": "123",
            "password": TEST_CITIZEN_PASSWORD
        })
        self.assertEqual(res.status_code, 422)

        # 3. Successful registration
        res = client.post("/api/auth/register", json={
            "name": TEST_CITIZEN_NAME,
            "mobile": TEST_CITIZEN_MOBILE,
            "password": TEST_CITIZEN_PASSWORD,
            "village": "Vemavaram"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()["data"]
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["role"], "citizen")
        user_id = data["user"]["user_id"]
        created_user_ids.append(user_id)
        print(f"  [PASS] Citizen registered successfully: user_id = {user_id}")

        # 4. Duplicate registration conflict (409)
        res = client.post("/api/auth/register", json={
            "name": TEST_CITIZEN_NAME,
            "mobile": TEST_CITIZEN_MOBILE,
            "password": TEST_CITIZEN_PASSWORD
        })
        self.assertEqual(res.status_code, 409)
        print("  [PASS] Duplicate registration rejected with 409 Conflict")

    def test_04_citizen_login_and_auth_profile(self):
        print("\n--- 4. Testing Citizen Login & Profile (POST /api/auth/login, GET /api/auth/me) ---")
        # 1. Invalid credentials
        res = client.post("/api/auth/login", json={
            "mobile": TEST_CITIZEN_MOBILE,
            "password": "WrongPassword"
        })
        self.assertEqual(res.status_code, 401)

        # 2. Valid login
        res = client.post("/api/auth/login", json={
            "mobile": TEST_CITIZEN_MOBILE,
            "password": TEST_CITIZEN_PASSWORD
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        token = data["access_token"]
        refresh_token = data["refresh_token"]
        self.assertIsNotNone(token)
        print("  [PASS] Citizen logged in and received JWT token")

        # 3. GET /api/auth/me with Bearer token
        res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        user_info = res.get_json()["data"]
        self.assertEqual(user_info["mobile"], TEST_CITIZEN_MOBILE)
        self.assertEqual(user_info["role"], "citizen")
        print(f"  [PASS] Current user profile fetched: {user_info['name']} ({user_info['village']})")

        # 4. Unauthorized request without token
        res = client.get("/api/auth/me")
        self.assertEqual(res.status_code, 401)
        print("  [PASS] Unauthenticated access properly rejected (401)")

        # 5. Token refresh
        res = client.post("/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
        self.assertEqual(res.status_code, 200)
        new_token = res.get_json()["data"]["access_token"]
        self.assertIsNotNone(new_token)
        print("  [PASS] Token refreshed successfully")

    # ─────────────────────────────────────────────────────────────
    # STEP 5 & 6: Complaint Submission (with Image) and Tracking
    # ─────────────────────────────────────────────────────────────
    def test_05_complaint_submission_and_tracking(self):
        print("\n--- 5. Testing Complaint Submission & Public Tracking ---")
        # Login citizen to get token
        res = client.post("/api/auth/login", json={
            "mobile": TEST_CITIZEN_MOBILE,
            "password": TEST_CITIZEN_PASSWORD
        })
        token = res.get_json()["data"]["access_token"]

        # 1. Validation failure: Missing title
        res = client.post(
            "/api/complaints",
            headers={"Authorization": f"Bearer {token}"},
            data={"category": "Road Issues", "description": "Pothole", "location": "Ward 1"}
        )
        self.assertEqual(res.status_code, 422)

        # 2. Submit multipart complaint with simulated image file
        mock_image = (io.BytesIO(b"fake_image_bytes_for_testing"), "test_pothole.jpg")
        res = client.post(
            "/api/complaints",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "title": "Damaged Culvert on Canal Road",
                "category": "Drainage Problems",
                "description": "The canal culvert is broken causing water stagnation and safety risk.",
                "ward_id": "3",
                "location": "Canal Road near Vemavaram Temple",
                "image": mock_image
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 201)
        created = res.get_json()["data"]
        complaint_id = created["complaint_id"]
        created_complaint_ids.append(complaint_id)
        self.assertTrue(complaint_id.startswith("CMP"))
        print(f"  [PASS] Complaint registered: {complaint_id}, Priority: {created['smart_priority']}")

        # 3. Check complaint saved in MySQL
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM complaints WHERE complaint_id = %s", (complaint_id,))
            c_row = cursor.fetchone()
            self.assertIsNotNone(c_row)
            self.assertEqual(c_row["title"], "Damaged Culvert on Canal Road")
            self.assertEqual(c_row["status"], "Submitted")
            self.assertEqual(c_row["ward_id"], 3)
            print("  [PASS] Complaint row verified in MySQL database")

            # Check status history audit trail
            cursor.execute("SELECT * FROM complaint_status_history WHERE complaint_id = %s", (complaint_id,))
            h_row = cursor.fetchone()
            self.assertIsNotNone(h_row)
            self.assertEqual(h_row["new_status"], "Submitted")
            print("  [PASS] Status history record created in MySQL")

        # 4. Public Tracking (GET /api/complaints/track/<id>) without login
        res = client.get(f"/api/complaints/track/{complaint_id}")
        self.assertEqual(res.status_code, 200)
        track_data = res.get_json()["data"]
        self.assertEqual(track_data["complaint_id"], complaint_id)
        self.assertEqual(track_data["status"], "Submitted")
        self.assertEqual(track_data["location"], "Canal Road near Vemavaram Temple")
        self.assertEqual(len(track_data["status_history"]), 1)
        print(f"  [PASS] Public tracking endpoint verified for {complaint_id}")

        # 5. Public tracking with invalid ID
        res = client.get("/api/complaints/track/CMP9999999")
        self.assertEqual(res.status_code, 404)
        print("  [PASS] Invalid complaint ID returns 404 Not Found")

    # ─────────────────────────────────────────────────────────────
    # STEP 7: Citizen Dashboard & Authorization Checks
    # ─────────────────────────────────────────────────────────────
    def test_06_citizen_dashboard_and_security(self):
        print("\n--- 6. Testing Citizen Dashboard & Authorization ---")
        # 1. Login primary citizen
        res = client.post("/api/auth/login", json={
            "mobile": TEST_CITIZEN_MOBILE,
            "password": TEST_CITIZEN_PASSWORD
        })
        token = res.get_json()["data"]["access_token"]

        # Fetch citizen's complaints list
        res = client.get("/api/complaints", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        my_complaints = res.get_json()["data"]["complaints"]
        self.assertTrue(len(my_complaints) >= 1)
        print(f"  [PASS] Citizen dashboard loaded {len(my_complaints)} complaints")

        # 2. Register a second citizen to test authorization boundary
        res = client.post("/api/auth/register", json={
            "name": "Other Citizen",
            "mobile": TEST_OTHER_MOBILE,
            "password": TEST_OTHER_PASSWORD,
            "village": "Vemavaram"
        })
        other_user_id = res.get_json()["data"]["user"]["user_id"]
        created_user_ids.append(other_user_id)
        other_token = res.get_json()["data"]["access_token"]

        # Attempt to access primary citizen's complaint using other citizen's token (must return 403)
        target_cid = created_complaint_ids[0]
        res = client.get(f"/api/complaints/{target_cid}", headers={"Authorization": f"Bearer {other_token}"})
        self.assertEqual(res.status_code, 403)
        print("  [PASS] Cross-citizen access blocked with 403 Forbidden")

        # 3. Check notifications for primary citizen
        res = client.get("/api/notifications", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        notifs_data = res.get_json()["data"]
        self.assertTrue(len(notifs_data["notifications"]) >= 1)
        notif_id = notifs_data["notifications"][0]["notification_id"]
        print(f"  [PASS] Notification generated for citizen: '{notifs_data['notifications'][0]['title']}'")

        # Mark notification read
        res = client.put(f"/api/notifications/{notif_id}/read", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        print("  [PASS] Notification marked as read")

    # ─────────────────────────────────────────────────────────────
    # STEP 8: Status Progression to Resolved & Citizen Feedback
    # ─────────────────────────────────────────────────────────────
    def test_07_status_resolution_and_citizen_feedback(self):
        print("\n--- 7. Testing Resolution Progression & Citizen Feedback ---")
        target_cid = created_complaint_ids[0]

        # Login primary citizen
        res = client.post("/api/auth/login", json={
            "mobile": TEST_CITIZEN_MOBILE,
            "password": TEST_CITIZEN_PASSWORD
        })
        token = res.get_json()["data"]["access_token"]

        # 1. Cannot submit feedback while complaint is still 'Submitted'
        res = client.post(
            "/api/feedback",
            headers={"Authorization": f"Bearer {token}"},
            json={"complaint_id": target_cid, "rating": 5, "remarks": "Great work"}
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Feedback can only be submitted for resolved complaints", res.get_json()["message"])
        print("  [PASS] Pre-resolution feedback properly rejected (400)")

        # 2. Transition complaint status to 'Resolved' in MySQL
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """UPDATE complaints
                   SET status = 'Resolved', resolved_at = NOW()
                   WHERE complaint_id = %s""",
                (target_cid,)
            )
            cursor.execute(
                """INSERT INTO complaint_status_history
                   (complaint_id, old_status, new_status, changed_by, notes)
                   VALUES (%s, 'Submitted', 'Resolved', %s, 'Issue resolved by Vemavaram field team')""",
                (target_cid, created_user_ids[0])
            )
        db.commit()

        # 3. Submit valid citizen feedback (5 stars)
        res = client.post(
            "/api/feedback",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "complaint_id": target_cid,
                "rating": 5,
                "remarks": "Culvert repaired swiftly and debris cleared. Excellent work!"
            }
        )
        self.assertEqual(res.status_code, 201)
        print("  [PASS] Citizen submitted 5-star feedback successfully")

        # 4. Verify feedback in MySQL
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM feedback WHERE complaint_id = %s", (target_cid,))
            fb = cursor.fetchone()
            self.assertIsNotNone(fb)
            self.assertEqual(fb["rating"], 5)
            self.assertEqual(fb["remarks"], "Culvert repaired swiftly and debris cleared. Excellent work!")
            print("  [PASS] Feedback verified in MySQL database")

        # 5. Prevent duplicate feedback submission (409)
        res = client.post(
            "/api/feedback",
            headers={"Authorization": f"Bearer {token}"},
            json={"complaint_id": target_cid, "rating": 4}
        )
        self.assertEqual(res.status_code, 409)
        print("  [PASS] Duplicate feedback rejected with 409 Conflict")

        # 6. Check updated public tracking returns resolution and feedback
        res = client.get(f"/api/complaints/track/{target_cid}")
        self.assertEqual(res.status_code, 200)
        td = res.get_json()["data"]
        self.assertEqual(td["status"], "Resolved")
        self.assertIsNotNone(td["feedback"])
        self.assertEqual(td["feedback"]["rating"], 5)
        print("  [PASS] Public tracking displays resolution and citizen rating")


if __name__ == "__main__":
    unittest.main()
