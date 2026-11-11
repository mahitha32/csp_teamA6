"""
scripts/test_api_integration.py
Comprehensive End-to-End API and Database Integration Test Suite.
Tests all user flows with real MySQL operations.
"""

import sys
import os
import json

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app, get_db

app = create_app("development")
client = app.test_client()

passed_tests = []
failed_tests = []

def record(test_name, success, detail=""):
    if success:
        print(f"  [PASS] {test_name} {detail}")
        passed_tests.append(test_name)
    else:
        print(f"  [FAIL] {test_name}: {detail}")
        failed_tests.append((test_name, detail))

def run_tests():
    print("=" * 60)
    print("VEMAVARAM VILLAGE CSP - PHASE 3 INTEGRATION TEST SUITE")
    print("=" * 60)

    # 1. Health Check
    res = client.get("/api/health")
    data = res.get_json()
    record(
        "1. GET /api/health",
        res.status_code == 200 and data.get("village") == "Vemavaram",
        f"Status: {res.status_code}, Village: {data.get('village')}"
    )

    # 2. Admin Login
    res = client.post("/api/auth/admin-login", json={"mobile": "9999900000", "password": "Admin@123"})
    data = res.get_json() or {}
    admin_token = data.get("data", {}).get("access_token")
    record(
        "2. POST /api/auth/admin-login",
        res.status_code == 200 and admin_token is not None,
        f"Admin token received: {bool(admin_token)}"
    )

    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Admin Creates Worker Account
    worker_mobile = "9999911111"
    # Clean up existing test worker if re-running
    db = get_db()
    with db.cursor() as cur:
        cur.execute("DELETE FROM users WHERE mobile = %s", (worker_mobile,))
    db.commit()

    res = client.post(
        "/api/workers",
        headers=admin_headers,
        json={
            "worker_name": "Suresh Worker",
            "mobile": worker_mobile,
            "department": "Roads & Infrastructure",
            "password": "Worker@123"
        }
    )
    worker_data = res.get_json() or {}
    worker_id = worker_data.get("data", {}).get("worker_id")
    record(
        "3. POST /api/workers (Admin adds worker)",
        res.status_code == 201 and worker_id is not None,
        f"Worker ID created: {worker_id}"
    )

    # 4. Worker Login
    res = client.post(
        "/api/auth/worker-login",
        json={"mobile": worker_mobile, "password": "Worker@123"}
    )
    worker_login_data = res.get_json() or {}
    worker_token = worker_login_data.get("data", {}).get("access_token")
    record(
        "4. POST /api/auth/worker-login",
        res.status_code == 200 and worker_token is not None,
        f"Worker token received: {bool(worker_token)}"
    )
    worker_headers = {"Authorization": f"Bearer {worker_token}"}

    # 5. Citizen Registration
    citizen_mobile = "9888812345"
    with db.cursor() as cur:
        cur.execute("DELETE FROM users WHERE mobile = %s", (citizen_mobile,))
    db.commit()

    res = client.post(
        "/api/auth/register",
        json={
            "name": "Kavitha Citizen",
            "mobile": citizen_mobile,
            "password": "Citizen@123",
            "village": "Vemavaram"
        }
    )
    reg_data = res.get_json() or {}
    citizen_token = reg_data.get("data", {}).get("access_token")
    record(
        "5. POST /api/auth/register (Citizen registration)",
        res.status_code == 201 and citizen_token is not None,
        f"Status: {res.status_code}"
    )

    # 6. Citizen Login
    res = client.post(
        "/api/auth/login",
        json={"mobile": citizen_mobile, "password": "Citizen@123"}
    )
    login_data = res.get_json() or {}
    citizen_token = login_data.get("data", {}).get("access_token")
    citizen_user = login_data.get("data", {}).get("user", {})
    record(
        "6. POST /api/auth/login (Citizen login)",
        res.status_code == 200 and citizen_user.get("role") == "citizen",
        f"Role: {citizen_user.get('role')}"
    )
    citizen_headers = {"Authorization": f"Bearer {citizen_token}"}

    # 7. Citizen Submits Complaint
    res = client.post(
        "/api/complaints",
        headers=citizen_headers,
        json={
            "title": "Severe road damage near Vemavaram school",
            "category": "Road Issues",
            "description": "Large potholes making it difficult for school buses and cyclists to pass.",
            "location": "Near Zilla Parishad High School, Ward 1",
            "latitude": 16.321456,
            "longitude": 80.456123,
            "ward_id": 1
        }
    )
    complaint_data = res.get_json() or {}
    complaint_id = complaint_data.get("data", {}).get("complaint_id")
    record(
        "7. POST /api/complaints (Citizen registers complaint)",
        res.status_code == 201 and complaint_id is not None,
        f"Created Complaint ID: {complaint_id}, Priority: {complaint_data.get('data', {}).get('smart_priority')}"
    )

    # 8. Citizen Retrieves Complaint Details
    res = client.get(f"/api/complaints/{complaint_id}", headers=citizen_headers)
    c_detail = res.get_json() or {}
    record(
        f"8. GET /api/complaints/{complaint_id}",
        res.status_code == 200 and c_detail.get("data", {}).get("complaint_id") == complaint_id,
        f"Status: {c_detail.get('data', {}).get('status')}"
    )

    # 9. Admin Assigns Worker to Complaint
    res = client.post(
        f"/api/admin/complaints/{complaint_id}/assign",
        headers=admin_headers,
        json={"worker_id": worker_id, "notes": "Inspect and patch potholes urgently."}
    )
    assign_res = res.get_json() or {}
    record(
        f"9. POST /api/admin/complaints/{complaint_id}/assign",
        res.status_code == 200,
        assign_res.get("message", "")
    )

    # 10. Worker Views Assigned Tasks
    res = client.get("/api/workers/tasks", headers=worker_headers)
    tasks_data = res.get_json() or {}
    tasks = tasks_data.get("data", {}).get("tasks", [])
    found_task = any(t["complaint_id"] == complaint_id for t in tasks)
    record(
        "10. GET /api/workers/tasks (Worker sees assigned tasks)",
        res.status_code == 200 and found_task,
        f"Found assigned complaint in tasks list: {found_task} (Total: {len(tasks)})"
    )

    # 11. Worker Updates Task Status to In Progress
    res = client.put(
        f"/api/workers/tasks/{complaint_id}/progress",
        headers=worker_headers,
        json={"status": "In Progress", "notes": "Work crew arrived on site with materials."}
    )
    record(
        "11. PUT /api/workers/tasks/progress -> In Progress",
        res.status_code == 200,
        res.get_json().get("message", "")
    )

    # 12. Worker Completes Task and Updates Status to Resolved
    res = client.put(
        f"/api/workers/tasks/{complaint_id}/progress",
        headers=worker_headers,
        json={
            "status": "Resolved",
            "notes": "Potholes filled and compacted with asphalt. Road clear.",
            "resolution_image_url": "https://res.cloudinary.com/vemavaram/image/upload/v1/resolutions/pothole_repaired.jpg"
        }
    )
    record(
        "12. PUT /api/workers/tasks/progress -> Resolved",
        res.status_code == 200,
        res.get_json().get("message", "")
    )

    # 13. Citizen Submits Feedback on Resolved Complaint
    res = client.post(
        "/api/feedback",
        headers=citizen_headers,
        json={
            "complaint_id": complaint_id,
            "rating": 5,
            "remarks": "Prompt repair! Very happy with the resolution."
        }
    )
    record(
        "13. POST /api/feedback (Citizen rates resolution)",
        res.status_code == 201,
        res.get_json().get("message", "")
    )

    # 14. Public Contact Form Submission
    res = client.post(
        "/api/contact",
        json={
            "name": "Narayana Rao",
            "email": "narayana@example.com",
            "phone": "9876543210",
            "message": "When will the streetlights on East Ward be checked?"
        }
    )
    record(
        "14. POST /api/contact (Public website contact form)",
        res.status_code == 201,
        res.get_json().get("message", "")
    )

    # 15. Admin Views Contact Messages
    res = client.get("/api/contact", headers=admin_headers)
    contact_data = res.get_json() or {}
    messages = contact_data.get("data", {}).get("messages", [])
    found_contact = any(m["email"] == "narayana@example.com" for m in messages)
    record(
        "15. GET /api/contact (Admin reviews messages)",
        res.status_code == 200 and found_contact,
        f"Contact saved in MySQL: {found_contact} (Total: {len(messages)})"
    )

    # 16. Admin Analytics
    res = client.get("/api/admin/analytics", headers=admin_headers)
    analytics_data = res.get_json() or {}
    summary = analytics_data.get("data", {}).get("summary", {})
    record(
        "16. GET /api/admin/analytics",
        res.status_code == 200 and summary.get("resolved", 0) >= 1,
        f"Total: {summary.get('total')}, Resolved: {summary.get('resolved')}, Avg Rating: {summary.get('avg_rating')}"
    )

    # 17. Public Statistics (No Auth required)
    res = client.get("/api/admin/public-stats")
    pub_data = res.get_json() or {}
    p_stats = pub_data.get("data", {})
    record(
        "17. GET /api/admin/public-stats (Unauthenticated landing page)",
        res.status_code == 200 and p_stats.get("village") == "Vemavaram",
        f"Village: {p_stats.get('village')}, Total: {p_stats.get('total_complaints')}, Satisfaction: {p_stats.get('citizen_satisfaction')}%"
    )

    # 18. Cleanup test data
    print("\n--- Cleaning up test records ---")
    with db.cursor() as cur:
        # Delete feedback
        cur.execute("DELETE FROM feedback WHERE complaint_id = %s", (complaint_id,))
        # Delete assignments
        cur.execute("DELETE FROM assignments WHERE complaint_id = %s", (complaint_id,))
        # Delete status history
        cur.execute("DELETE FROM complaint_status_history WHERE complaint_id = %s", (complaint_id,))
        # Delete notifications
        cur.execute("DELETE FROM notifications WHERE user_id IN (%s, %s)", (citizen_user.get("user_id"), worker_id))
        # Delete complaints
        cur.execute("DELETE FROM complaints WHERE complaint_id = %s", (complaint_id,))
        # Delete contact messages from test
        cur.execute("DELETE FROM contact_messages WHERE email = 'narayana@example.com'")
        # Delete test worker & test citizen
        cur.execute("DELETE FROM users WHERE mobile IN (%s, %s)", (citizen_mobile, worker_mobile))
    db.commit()
    print("Test cleanup completed cleanly.")

    print("\n" + "=" * 60)
    print(f"RESULTS: {len(passed_tests)} PASSED, {len(failed_tests)} FAILED")
    print("=" * 60)

    if failed_tests:
        print("\nFailures:")
        for name, err in failed_tests:
            print(f"  - {name}: {err}")
        return False
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

