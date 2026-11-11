"""
test_e2e_full_lifecycle.py
End-to-End System Testing across Citizen, Worker, and Admin Workflows
Vemavaram Village Complaint Redressal System
"""

import sys
import os
import unittest
import io
import time

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app, get_db

class TestE2EFullLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.ctx = cls.app.app_context()
        cls.ctx.push()

        # Unique timestamps and credentials
        cls.ts = int(time.time())
        cls.citizen_mobile = f"988{cls.ts % 10000000:07d}"
        cls.citizen_name = f"Vemavaram Citizen {cls.ts % 1000}"
        cls.citizen_password = "CitizenPass@123"

        cls.worker_mobile = f"977{cls.ts % 10000000:07d}"
        cls.worker_name = f"Vemavaram Worker {cls.ts % 1000}"
        cls.worker_password = "WorkerPass@123"

        cls.admin_mobile = "9999900000"
        cls.admin_password = "Admin@123"

        # Shared lifecycle state
        cls.citizen_token = None
        cls.citizen_id = None
        cls.complaint_id = None
        cls.admin_token = None
        cls.worker_id = None
        cls.worker_token = None

    @classmethod
    def tearDownClass(cls):
        cls.ctx.pop()

    def test_01_citizen_registration_and_login(self):
        """Step 1: Citizen registers and authenticates."""
        reg_payload = {
            "name": self.citizen_name,
            "mobile": self.citizen_mobile,
            "password": self.citizen_password,
            "village": "Vemavaram"
        }
        res = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res.status_code, 201, f"Registration failed: {res.get_json()}")
        reg_data = res.get_json()
        self.assertTrue(reg_data.get("success"))
        self.assertEqual(reg_data["data"]["user"]["role"], "citizen")

        # Citizen login
        login_res = self.client.post("/api/auth/login", json={
            "mobile": self.citizen_mobile,
            "password": self.citizen_password
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.get_json()["data"]
        self.assertIn("access_token", data)
        TestE2EFullLifecycle.citizen_token = data["access_token"]
        TestE2EFullLifecycle.citizen_id = data["user"]["user_id"]

    def test_02_contact_submission(self):
        """Step 2: Citizen submits contact form query."""
        contact_payload = {
            "name": self.citizen_name,
            "email": f"citizen{self.ts}@example.com",
            "phone": self.citizen_mobile,
            "message": "Water pressure is fluctuating in Ward 2, Vemavaram."
        }
        res = self.client.post("/api/contact", json=contact_payload)
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.get_json().get("success"))

    def test_03_citizen_submits_complaint(self):
        """Step 3: Citizen reports complaint with category, ward, and image."""
        fake_image = (io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"), "leak_proof.png")
        data = {
            "title": "Severe Pipeline Leakage near North Tank",
            "category": "Water Supply Problems",
            "description": "Drinking water pipeline cracked near North water tank in Vemavaram.",
            "location": "North Water Tank Road, Ward 2",
            "ward_id": "2",
            "latitude": "16.4875",
            "longitude": "80.6441",
            "image": fake_image
        }
        res = self.client.post(
            "/api/complaints",
            data=data,
            content_type="multipart/form-data",
            headers={"Authorization": f"Bearer {TestE2EFullLifecycle.citizen_token}"}
        )
        self.assertEqual(res.status_code, 201, f"Complaint submission failed: {res.get_json()}")
        c_data = res.get_json()["data"]
        self.assertIn("complaint_id", c_data)
        TestE2EFullLifecycle.complaint_id = c_data["complaint_id"]
        self.assertTrue(c_data["complaint_id"].startswith("CMP"))

    def test_04_public_tracking(self):
        """Step 4: Public track endpoint shows submitted complaint status."""
        res = self.client.get(f"/api/complaints/track/{TestE2EFullLifecycle.complaint_id}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertEqual(data["complaint_id"], TestE2EFullLifecycle.complaint_id)
        self.assertEqual(data["status"], "Submitted")

    def test_05_admin_login_and_worker_creation(self):
        """Step 5: Admin logs in, verifies contact message, and provisions field worker."""
        res = self.client.post("/api/auth/admin-login", json={
            "mobile": self.admin_mobile,
            "password": self.admin_password
        })
        self.assertEqual(res.status_code, 200, f"Admin login failed: {res.get_json()}")
        admin_data = res.get_json()["data"]
        TestE2EFullLifecycle.admin_token = admin_data["access_token"]

        # Admin reads contact messages
        c_res = self.client.get("/api/contact", headers={"Authorization": f"Bearer {TestE2EFullLifecycle.admin_token}"})
        self.assertEqual(c_res.status_code, 200)

        # Admin creates field worker
        worker_payload = {
            "worker_name": self.worker_name,
            "mobile": self.worker_mobile,
            "password": self.worker_password,
            "department": "Water Supply",
        }
        w_res = self.client.post(
            "/api/workers",
            json=worker_payload,
            headers={"Authorization": f"Bearer {TestE2EFullLifecycle.admin_token}"}
        )
        self.assertEqual(w_res.status_code, 201, f"Worker creation failed: {w_res.get_json()}")
        TestE2EFullLifecycle.worker_id = w_res.get_json()["data"]["worker_id"]

    def test_06_admin_assigns_worker(self):
        """Step 6: Admin assigns worker to the complaint."""
        assign_payload = {
            "worker_id": TestE2EFullLifecycle.worker_id,
            "notes": "Please inspect pipeline and replace cracked valve at North Water Tank."
        }
        res = self.client.post(
            f"/api/admin/complaints/{TestE2EFullLifecycle.complaint_id}/assign",
            json=assign_payload,
            headers={"Authorization": f"Bearer {TestE2EFullLifecycle.admin_token}"}
        )
        self.assertEqual(res.status_code, 200, f"Assignment failed: {res.get_json()}")
        self.assertTrue(res.get_json().get("success"))

    def test_07_worker_login_and_tasks(self):
        """Step 7: Worker logs in with mobile + password and sees assigned task."""
        login_res = self.client.post("/api/auth/worker-login", json={
            "mobile": self.worker_mobile,
            "password": self.worker_password
        })
        self.assertEqual(login_res.status_code, 200, f"Worker login failed: {login_res.get_json()}")
        TestE2EFullLifecycle.worker_token = login_res.get_json()["data"]["access_token"]

        # Fetch worker tasks
        tasks_res = self.client.get(
            "/api/workers/tasks",
            headers={"Authorization": f"Bearer {TestE2EFullLifecycle.worker_token}"}
        )
        self.assertEqual(tasks_res.status_code, 200)
        tasks = tasks_res.get_json()["data"]["tasks"]
        task_ids = [t["complaint_id"] for t in tasks]
        self.assertIn(TestE2EFullLifecycle.complaint_id, task_ids)

    def test_08_worker_starts_work(self):
        """Step 8: Worker updates status to In Progress."""
        progress_res = self.client.put(
            f"/api/workers/tasks/{TestE2EFullLifecycle.complaint_id}/progress",
            json={"status": "In Progress", "notes": "On-site inspection started by pipeline crew."},
            headers={"Authorization": f"Bearer {TestE2EFullLifecycle.worker_token}"}
        )
        self.assertEqual(progress_res.status_code, 200)
        self.assertTrue(progress_res.get_json().get("success"))

    def test_09_enforce_resolution_proof_requirement(self):
        """Step 9: Security & validation: Attempting to resolve without photo and notes must fail."""
        # Attempt without photo and without notes
        res1 = self.client.put(
            f"/api/workers/tasks/{TestE2EFullLifecycle.complaint_id}/progress",
            json={"status": "Resolved"},
            headers={"Authorization": f"Bearer {TestE2EFullLifecycle.worker_token}"}
        )
        self.assertEqual(res1.status_code, 422, "Must reject resolution without proof photo and remarks!")

        # Attempt with notes only, no photo
        res2 = self.client.put(
            f"/api/workers/tasks/{TestE2EFullLifecycle.complaint_id}/progress",
            json={"status": "Resolved", "notes": "Fixed pipe."},
            headers={"Authorization": f"Bearer {TestE2EFullLifecycle.worker_token}"}
        )
        self.assertEqual(res2.status_code, 422, "Must reject resolution without resolution photo!")

    def test_10_worker_resolves_task_with_proof(self):
        """Step 10: Worker resolves task with mandatory photo evidence and remarks."""
        fake_resolution_image = (io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"), "fixed_pipeline.png")
        data = {
            "status": "Resolved",
            "notes": "Installed new heavy-duty valve and tested water pressure. Zero leakage verified.",
            "resolution_photo": fake_resolution_image
        }
        res = self.client.put(
            f"/api/workers/tasks/{TestE2EFullLifecycle.complaint_id}/progress",
            data=data,
            content_type="multipart/form-data",
            headers={"Authorization": f"Bearer {TestE2EFullLifecycle.worker_token}"}
        )
        self.assertEqual(res.status_code, 200, f"Resolution failed: {res.get_json()}")
        self.assertTrue(res.get_json().get("success"))

    def test_11_citizen_provides_feedback(self):
        """Step 11: Citizen rates resolution with 5 stars and remarks."""
        feedback_payload = {
            "complaint_id": TestE2EFullLifecycle.complaint_id,
            "rating": 5,
            "remarks": "Excellent response time! The water pressure is back to normal. Thank you Vemavaram Panchayat."
        }
        res = self.client.post(
            "/api/feedback",
            json=feedback_payload,
            headers={"Authorization": f"Bearer {TestE2EFullLifecycle.citizen_token}"}
        )
        self.assertEqual(res.status_code, 201, f"Feedback submission failed: {res.get_json()}")
        self.assertTrue(res.get_json().get("success"))

    def test_12_public_stats_and_analytics_reflect_progress(self):
        """Step 12: Public stats counter reflects real resolution count."""
        res = self.client.get("/api/admin/public-stats")
        self.assertEqual(res.status_code, 200)
        stats = res.get_json()["data"]
        self.assertIn("resolved_complaints", stats)
        self.assertIn("total_complaints", stats)
        self.assertGreater(stats["resolved_complaints"], 0)
        self.assertGreaterEqual(stats["total_complaints"], stats["resolved_complaints"])

    def test_13_security_role_based_access_control(self):
        """Step 13: Security RBAC checks - Citizens & Workers cannot access Admin endpoints."""
        # Citizen trying to access admin analytics -> 403
        c_res = self.client.get(
            "/api/admin/analytics",
            headers={"Authorization": f"Bearer {TestE2EFullLifecycle.citizen_token}"}
        )
        self.assertEqual(c_res.status_code, 403)

        # Worker trying to access admin analytics -> 403
        w_res = self.client.get(
            "/api/admin/analytics",
            headers={"Authorization": f"Bearer {TestE2EFullLifecycle.worker_token}"}
        )
        self.assertEqual(w_res.status_code, 403)

        # Unauthenticated request -> 401
        u_res = self.client.get("/api/admin/analytics")
        self.assertEqual(u_res.status_code, 401)

if __name__ == "__main__":
    unittest.main()
