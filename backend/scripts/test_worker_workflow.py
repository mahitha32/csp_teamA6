"""
csp/backend/scripts/test_worker_workflow.py
Phase 6: Worker Module Comprehensive Test Suite
Validates worker authentication, task queue, status progression,
mandatory photo/remarks enforcement, and evidence upload.
"""

import io
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

WORKER_MOBILE = "9666655555"
WORKER_PASSWORD = "Worker@123"
WORKER_NAME = "Vemavaram Sanitation Worker"

CITIZEN_MOBILE = "9555544444"
CITIZEN_PASSWORD = "Citizen@123"

created_worker_ids = []
created_complaint_ids = []
created_citizen_ids = []


def cleanup():
    with app.app_context():
        db = get_db()
        with db.cursor() as cursor:
            for cid in created_complaint_ids:
                cursor.execute("DELETE FROM feedback WHERE complaint_id = %s", (cid,))
                cursor.execute("DELETE FROM assignments WHERE complaint_id = %s", (cid,))
                cursor.execute("DELETE FROM complaint_status_history WHERE complaint_id = %s", (cid,))
                cursor.execute("DELETE FROM complaints WHERE complaint_id = %s", (cid,))
            for uid in created_citizen_ids:
                cursor.execute("DELETE FROM notifications WHERE user_id = %s", (uid,))
                cursor.execute("DELETE FROM users WHERE user_id = %s", (uid,))
            for wid in created_worker_ids:
                cursor.execute("DELETE FROM worker_profiles WHERE user_id = %s", (wid,))
                cursor.execute("DELETE FROM users WHERE user_id = %s", (wid,))
            cursor.execute("DELETE FROM users WHERE mobile IN (%s, %s)", (WORKER_MOBILE, CITIZEN_MOBILE))
        db.commit()


class TestWorkerModuleWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = app.app_context()
        cls.ctx.push()
        cleanup()

    @classmethod
    def tearDownClass(cls):
        cleanup()
        cls.ctx.pop()
        print("\n[CLEANUP] Test worker records cleaned up cleanly.")

    def test_01_worker_setup_and_secure_login(self):
        print("\n--- 1. Testing Worker Creation & Secure Login ---")
        # 1. Admin logs in and creates worker
        res = client.post("/api/auth/admin-login", json={"mobile": ADMIN_MOBILE, "password": ADMIN_PASSWORD})
        self.assertEqual(res.status_code, 200)
        admin_token = res.get_json()["data"]["access_token"]

        res = client.post(
            "/api/workers",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "worker_name": WORKER_NAME,
                "mobile": WORKER_MOBILE,
                "department": "Drainage & Sanitation",
                "password": WORKER_PASSWORD
            }
        )
        self.assertEqual(res.status_code, 201)
        worker_id = res.get_json()["data"]["worker_id"]
        created_worker_ids.append(worker_id)
        print(f"  [PASS] Worker created in MySQL: ID {worker_id} ({WORKER_NAME})")

        # 2. Worker Login with wrong password -> 401
        res = client.post("/api/auth/worker-login", json={"mobile": WORKER_MOBILE, "password": "WrongPassword"})
        self.assertEqual(res.status_code, 401)
        print("  [PASS] Invalid worker credentials rejected (401)")

        # 3. Worker Login with valid credentials -> 200
        res = client.post("/api/auth/worker-login", json={"mobile": WORKER_MOBILE, "password": WORKER_PASSWORD})
        self.assertEqual(res.status_code, 200)
        worker_data = res.get_json()["data"]
        self.assertEqual(worker_data["user"]["role"], "worker")
        self.assertEqual(worker_data["user"]["department"], "Drainage & Sanitation")
        self.assertIsNotNone(worker_data["access_token"])
        print("  [PASS] Worker successfully authenticated via /api/auth/worker-login")

        # 4. Citizen trying to log in via worker endpoint -> rejected
        res = client.post("/api/auth/register", json={
            "name": "Normal Citizen",
            "mobile": CITIZEN_MOBILE,
            "password": CITIZEN_PASSWORD,
            "village": "Vemavaram"
        })
        cit_id = res.get_json()["data"]["user"]["user_id"]
        created_citizen_ids.append(cit_id)

        res = client.post("/api/auth/worker-login", json={"mobile": CITIZEN_MOBILE, "password": CITIZEN_PASSWORD})
        self.assertEqual(res.status_code, 401)
        print("  [PASS] Citizen account rejected from worker portal")

    def test_02_task_assignment_and_worker_queue(self):
        print("\n--- 2. Testing Task Assignment & Worker Task Queue ---")
        # 1. Citizen files a complaint
        res = client.post("/api/auth/login", json={"mobile": CITIZEN_MOBILE, "password": CITIZEN_PASSWORD})
        cit_token = res.get_json()["data"]["access_token"]

        res = client.post(
            "/api/complaints",
            headers={"Authorization": f"Bearer {cit_token}"},
            json={
                "title": "Clogged Drainage Canal Behind Vemavaram Primary Health Centre",
                "category": "Drainage Problems",
                "description": "Heavy monsoon silt clogging the canal. Water backing into streets.",
                "ward_id": 2,
                "location": "Behind PHC, Ward 2, Vemavaram"
            }
        )
        self.assertEqual(res.status_code, 201)
        cid = res.get_json()["data"]["complaint_id"]
        created_complaint_ids.append(cid)
        print(f"  [PASS] Complaint filed: {cid}")

        # 2. Admin assigns complaint to worker
        res = client.post("/api/auth/admin-login", json={"mobile": ADMIN_MOBILE, "password": ADMIN_PASSWORD})
        admin_token = res.get_json()["data"]["access_token"]

        worker_id = created_worker_ids[0]
        res = client.post(
            f"/api/admin/complaints/{cid}/assign",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"worker_id": worker_id, "notes": "Clear silt block immediately"}
        )
        self.assertEqual(res.status_code, 200)

        # 3. Worker checks assigned tasks
        res = client.post("/api/auth/worker-login", json={"mobile": WORKER_MOBILE, "password": WORKER_PASSWORD})
        worker_token = res.get_json()["data"]["access_token"]

        res = client.get("/api/workers/tasks", headers={"Authorization": f"Bearer {worker_token}"})
        self.assertEqual(res.status_code, 200)
        tasks = res.get_json()["data"]["tasks"]
        self.assertTrue(any(t["complaint_id"] == cid for t in tasks))
        print(f"  [PASS] Assigned complaint {cid} visible in worker task queue")

        # 4. Role check: Citizen cannot access worker task queue (403)
        res = client.get("/api/workers/tasks", headers={"Authorization": f"Bearer {cit_token}"})
        self.assertEqual(res.status_code, 403)
        print("  [PASS] Non-worker blocked from worker tasks queue (403)")

    def test_03_status_progression_and_mandatory_evidence(self):
        print("\n--- 3. Testing Status Progression & Mandatory Evidence Enforcement ---")
        cid = created_complaint_ids[0]

        res = client.post("/api/auth/worker-login", json={"mobile": WORKER_MOBILE, "password": WORKER_PASSWORD})
        worker_token = res.get_json()["data"]["access_token"]

        # 1. Update status to 'In Progress'
        res = client.put(
            f"/api/workers/tasks/{cid}/progress",
            headers={"Authorization": f"Bearer {worker_token}"},
            json={"status": "In Progress", "notes": "Excavation and cleaning crew deployed on site."}
        )
        self.assertEqual(res.status_code, 200)
        print("  [PASS] Task status updated to 'In Progress'")

        # 2. ATTEMPT RESOLUTION WITHOUT PHOTO -> Must Fail with 422 Unprocessable Entity
        res = client.put(
            f"/api/workers/tasks/{cid}/progress",
            headers={"Authorization": f"Bearer {worker_token}"},
            json={"status": "Resolved", "notes": "Completed drainage clean"}
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("Resolution evidence photograph is mandatory", res.get_json()["message"])
        print("  [PASS] Attempt to resolve without evidence photo rejected (422)")

        # 3. ATTEMPT RESOLUTION WITHOUT NOTES -> Must Fail with 422
        mock_photo = (io.BytesIO(b"fake_cleared_drain_photo_bytes"), "drain_cleared.jpg")
        res = client.put(
            f"/api/workers/tasks/{cid}/progress",
            headers={"Authorization": f"Bearer {worker_token}"},
            data={"status": "Resolved", "resolution_photo": mock_photo},
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("Completion remarks are mandatory", res.get_json()["message"])
        print("  [PASS] Attempt to resolve without completion remarks rejected (422)")

        # 4. VALID RESOLUTION WITH PHOTO EVIDENCE AND REMARKS
        mock_photo_valid = (io.BytesIO(b"fake_cleared_drain_photo_bytes_final"), "drain_cleared_proof.jpg")
        res = client.put(
            f"/api/workers/tasks/{cid}/progress",
            headers={"Authorization": f"Bearer {worker_token}"},
            data={
                "status": "Resolved",
                "notes": "Drainage canal desilted completely and water flow restored without obstruction.",
                "resolution_photo": mock_photo_valid
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 200)
        res_data = res.get_json()["data"]
        self.assertEqual(res_data["status"], "Resolved")
        self.assertIsNotNone(res_data["resolution_image_url"])
        print(f"  [PASS] Task marked Resolved with proof photograph: {res_data['resolution_image_url']}")

        # 5. Verify in MySQL database
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM complaints WHERE complaint_id = %s", (cid,))
            c_row = cursor.fetchone()
            self.assertEqual(c_row["status"], "Resolved")
            self.assertIsNotNone(c_row["resolved_at"])
            self.assertIsNotNone(c_row["resolution_image_url"])
            self.assertEqual(c_row["resolution_notes"], "Drainage canal desilted completely and water flow restored without obstruction.")
            print("  [PASS] Resolution evidence and timestamp verified in MySQL")

            # Check audit history trail
            cursor.execute("SELECT * FROM complaint_status_history WHERE complaint_id = %s ORDER BY history_id ASC", (cid,))
            history = cursor.fetchall()
            statuses = [h["new_status"] for h in history]
            self.assertIn("Submitted", statuses)
            self.assertIn("Assigned", statuses)
            self.assertIn("In Progress", statuses)
            self.assertIn("Resolved", statuses)
            print(f"  [PASS] Complete status audit trail confirmed in MySQL: {' -> '.join(statuses)}")


if __name__ == "__main__":
    unittest.main()

