# API Documentation
Base URL: `http://localhost:5000/api`
All protected endpoints require the `Authorization: Bearer <token>` header.

---

## 1. Authentication APIs

### `POST /auth/verify-firebase`
Exchanges a Firebase ID token for a system JWT.
- **Request:** `{ "id_token": "firebase_token_string", "role": "villager" }`
- **Response:** `200 OK` | `{ "access_token": "...", "user": { ... } }`

### `POST /auth/admin-login`
Standard username/password login for Admins.
- **Request:** `{ "mobile": "9999900000", "password": "..." }`
- **Response:** `200 OK` | `{ "access_token": "...", "user": { ... } }`

---

## 2. Complaint APIs (Villagers)

### `POST /complaints`
Submit a new complaint.
- **Headers:** `Authorization: Bearer <token>`
- **Request:** `multipart/form-data`
  - `title`: String
  - `description`: String
  - `location`: String
  - `category`: String (optional, AI classifier used if null)
  - `image`: File (optional)
- **Response:** `201 Created` | `{ "message": "Submitted", "complaint_id": 1 }`

### `GET /complaints`
Retrieve the logged-in user's complaints.
- **Response:** `200 OK` | `{ "data": [{...}] }`

---

## 3. Admin APIs

### `GET /admin/complaints`
List all complaints with pagination and filtering.
- **Query Params:** `page`, `per_page`, `status`, `category`
- **Response:** `200 OK` | `{ "complaints": [...], "pagination": {...} }`

### `PUT /admin/complaints/<id>/status`
Update complaint status.
- **Request:** `{ "status": "In Progress", "notes": "Worker dispatched" }`

### `POST /admin/complaints/<id>/assign`
Assign a worker to a complaint.
- **Request:** `{ "worker_id": 3, "notes": "Fix ASAP" }`

---

## 4. Worker APIs

### `GET /workers/tasks`
List assigned tasks for the logged-in worker.
- **Response:** `200 OK` | `{ "tasks": [...] }`

### `PUT /workers/tasks/<id>/progress`
Update task progress (upload resolution photo).
- **Request:** `multipart/form-data` | `status`: "Resolved", `image`: File, `notes`: String

---

## 5. Feedback & Survey APIs

### `POST /feedback`
Submit villager feedback for a resolved complaint.
- **Request:** `{ "complaint_id": 1, "rating": 5, "remarks": "Good job" }`

### `GET /admin/survey-insights`
Retrieve pre-loaded Gadepudi survey data.
- **Response:** `200 OK` | `{ "village": "Gadepudi", "insights": [...] }`
