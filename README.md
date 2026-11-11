# Smart Complaint Redressal System for Village Issues (Vemavaram Village)

[![Backend Tests](https://img.shields.io/badge/Backend_Tests-46%20Passed-brightgreen)](backend/scripts/)
[![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479a1?logo=mysql)](https://mysql.com/)
[![React](https://img.shields.io/badge/React-18-61dafb?logo=react)](https://react.dev/)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569b?logo=flutter)](https://flutter.dev/)

An end-to-end, multi-tier Digital Governance and Smart Village Complaint Redressal System engineered for **Vemavaram Village**, Krishna District, Andhra Pradesh.

- **Live Citizen Portal**: [https://complaintredressalsystem.vercel.app/](https://complaintredressalsystem.vercel.app/)
- **Citizen Portal Repository**: [https://github.com/mahitha32/0-review.git](https://github.com/mahitha32/0-review.git)
- **Main System Repository**: [https://github.com/mahitha32/csp_teamA6.git](https://github.com/mahitha32/csp_teamA6.git)

---

## 📌 Problem Statement

In rural communities like Vemavaram, civic grievances (such as water pipeline bursts, malfunctioning streetlights, uncollected waste, clogged drainage, and road hazards) are typically reported through informal, unrecorded, or manual channels. This leads to:
1. Lack of traceability and transparent status tracking for villagers.
2. Delayed administrative escalation and SLA breaches.
3. Inability to verify whether fieldwork was legitimately completed.
4. Absence of centralized geospatial and ward-level civic analytics.

---

## 🎯 Objectives

- **Citizen Empowerment**: Provide accessible digital channels (web and mobile) for villagers to submit complaints with photo evidence and GPS coordinates.
- **Strict Accountability & Evidence Enforcement**: Field workers are policy-mandated to upload photographic proof of the completed work and closing remarks before an issue can be marked "Resolved".
- **Dynamic Administrative Oversight**: Equip the Vemavaram Panchayat with live SLA alert monitoring, interactive GIS village mapping, worker assignment, and citizen satisfaction ratings.
- **Relational Integrity**: Unified user management across Citizens, Field Workers, and Administrators backed by MySQL 8.0.

---

## 🏗️ Architecture & Modules

The platform is designed around four decoupled, interoperable tiers:

```
                            ┌────────────────────────────────────────┐
                            │    Citizen Website (React + Vite)     │
                            │   https://complaintredressalsystem...  │
                            └───────────────────┬────────────────────┘
                                                │ REST API (HTTPS)
┌────────────────────────────────┐              ▼              ┌────────────────────────────────┐
│   Admin Dashboard (React 18)   │ ──► ┌───────────────────┐ ◄── │    Mobile App (Flutter)        │
│   • GIS Village Map (Leaflet)  │     │  Flask REST API   │     │    • Citizen Complaint Filing  │
│   • Live SLA Alert Tracker     │     │   (Python 3.12)   │     │    • Field Worker Task Flow    │
│   • Worker & Task Management   │     └─────────┬─────────┘     │    • Geolocation & Evidence    │
└────────────────────────────────┘               │               └────────────────────────────────┘
                                                 │
                                ┌────────────────┴────────────────┐
                                ▼                                 ▼
                     ┌─────────────────────┐           ┌─────────────────────┐
                     │   MySQL 8.0 Database │           │ Cloudinary Storage  │
                     │  (15 Relational     │           │ (Complaint & Proof  │
                     │   Tables, Triggers) │           │  Photographs)       │
                     └─────────────────────┘           └─────────────────────┘
```

### 1. Flask REST API (`backend/`)
- Unified JWT role-based access control (`citizen`, `worker`, `admin`) with PyJWT 2.x string serialization.
- Automated priority scoring (Critical, High, Medium, Low) and keyword-based category resolution.
- Public tracking endpoint (`GET /api/complaints/track/<id>`) allowing unauthenticated status lookup.
- Cloudinary photo upload service with local storage fallback (`/static/uploads/`).
- Automated notifications generated on submission, assignment, and resolution.
- Contact form processing directly into MySQL.

### 2. Admin Dashboard (`admin_dashboard/`)
- Real-time statistics: Total, Pending, Assigned, In Progress, Resolved complaints.
- Live SLA Breach Warning System with countdown timers and overdue indicators.
- Interactive Leaflet GIS village map with custom status-colored pins and popup metadata.
- Ward-wise analytics across Wards 1 to 5 (`GET /api/analytics_v2/ward_stats`).
- Asset Registry for village infrastructure (Water tanks, borewells, transformers).
- CSV report generator exporting live database complaint records.

### 3. Field Worker Module (Web Modal & Flutter App)
- Secure mobile + password worker authentication (`POST /api/auth/worker-login`).
- Real-time assigned task list (`GET /api/workers/tasks`).
- Status progression: `Assigned` → `In Progress` → `Resolved`.
- **Mandatory Policy Check**: The backend strictly validates that both resolution photo evidence and closing remarks exist when updating to `Resolved`. Requests without both are rejected with HTTP 422 Unprocessable Entity.

### 4. Flutter Mobile Application (`mobile_app/`)
- Citizen reporting with camera image capture and GPS coordinates.
- Tabbed citizen & field worker login flow.
- Offline-ready SQLite sync queue architecture (`sync_service.dart`).
- Post-resolution 1-to-5 star citizen feedback rating.

---

## 💻 Technology Stack

| Domain | Technologies |
| :--- | :--- |
| **Backend Engine** | Python 3.12, Flask 3.0, Gunicorn 22.0, Werkzeug, PyMySQL, bcrypt, Flask-JWT-Extended |
| **Database** | MySQL 8.0 (15 Relational Tables with Foreign Keys, Cascades, Indexes, and Audit Triggers) |
| **Media Storage** | Cloudinary API (with Local Static Storage Fallback) |
| **Admin Frontend** | React 18, Vite, Chart.js, React-Chartjs-2, Leaflet 1.9, React-Leaflet 4.2, Axios |
| **Mobile App** | Flutter 3.x, Dart, Dio, SharedPreferences, ImagePicker, Geolocator |
| **Test Suites** | Pytest, Python `unittest` (46 Automated Integration & E2E Tests, 100% Pass) |

---

## 📂 Project Structure

```
csp/
├── .gitignore                          # Root ignore covering secrets, dependencies, & builds
├── README.md                           # Master system documentation
│
├── admin_dashboard/                    # React + Vite Administration Portal
│   ├── .env.example                    # Safe environment template
│   ├── .gitignore                      # Ignore for admin node_modules & dist
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js                  # Proxy configuration to Flask backend
│   └── src/
│       ├── api/api.js                  # Axios client with JWT interceptor
│       ├── context/AuthContext.jsx     # Admin authentication & RBAC guard
│       └── pages/                      # Dashboard, Complaints, Workers, Map, Reports
│
├── backend/                            # Flask REST API Tier
│   ├── .env.example                    # Safe environment template with variable docs
│   ├── .gitignore                      # Ignore for Python cache, .env, and uploads
│   ├── Procfile                        # Production WSGI runner for Render/Railway
│   ├── run.py                          # Flask entrypoint (development & Gunicorn callable)
│   ├── requirements.txt                # Pinned production Python dependencies
│   ├── app/
│   │   ├── __init__.py                 # Application factory & CORS configuration
│   │   ├── config.py                   # Environment config loader
│   │   ├── routes/                     # auth, complaints, admin, workers, feedback, contact
│   │   ├── services/                   # image_service (Cloudinary), ai_service, notification
│   │   └── utils/                      # decorators, helpers, validation
│   ├── migrations/                     # schema_complete.sql (15 relational tables + seeds)
│   └── scripts/                        # Automated test suites (46 total tests)
│       ├── test_api_integration.py
│       ├── test_citizen_workflow.py
│       ├── test_admin_dashboard_workflow.py
│       ├── test_worker_workflow.py
│       └── test_e2e_full_lifecycle.py
│
├── mobile_app/                         # Flutter Cross-Platform Mobile Client
│   ├── .gitignore                      # Standard Flutter ignore rules
│   ├── pubspec.yaml                    # Flutter dependencies (Dio, Riverpod, ImagePicker)
│   └── lib/
│       ├── main.dart
│       ├── core/network/api_client.dart# Multi-environment loopback & token interceptor
│       └── features/                   # auth, complaints, worker, feedback, profile
│
└── docs/                               # 24 Detailed System Architecture & Viva Documents
```

---

## ⚙️ Local Setup Instructions

### 1. Prerequisites
- **Python**: Version 3.10 to 3.12 installed
- **Node.js**: Version 18.x or 20.x installed
- **MySQL Server**: Version 8.0 running on `localhost:3306`
- **Flutter SDK**: Version 3.16+ (optional, for mobile app development)

---

### 2. Database Setup (MySQL)
1. Open your MySQL client (MySQL Workbench, HeidiSQL, or CLI):
   ```sql
   CREATE DATABASE vemavaram_csp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. Execute the complete schema migration:
   ```bash
   mysql -u root -p vemavaram_csp < backend/migrations/schema_complete.sql
   ```
3. This creates all 15 relational tables and seeds the initial Administrator account (`admin@vemavaram.gov.in` / `9999900000`), default wards, and SLA categories.

---

### 3. Backend Setup (Flask API)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your MySQL root password and optional Cloudinary credentials.
5. Run automated validation tests to verify the setup:
   ```bash
   python scripts/test_e2e_full_lifecycle.py
   ```
   *(All 13 lifecycle tests should report `OK`)*
6. Start the API server:
   ```bash
   python run.py
   ```
   The backend API will run at `http://127.0.0.1:5000` (`http://127.0.0.1:5000/api/health`).

---

### 4. Admin Dashboard Setup (React + Vite)
1. Navigate to the admin dashboard directory:
   ```bash
   cd ../admin_dashboard
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Configure environment file:
   ```bash
   cp .env.example .env
   ```
4. Start the Vite development server:
   ```bash
   npm run dev
   ```
5. Open your browser at `http://localhost:3000` (or `http://localhost:5173`).
   - **Login**: Mobile: `9999900000` | Password: `Admin@123`

---

### 5. Flutter Mobile App Setup
1. Navigate to the mobile application directory:
   ```bash
   cd ../mobile_app
   ```
2. Fetch Flutter packages:
   ```bash
   flutter pub get
   ```
3. Run on connected Android Emulator or Physical Device:
   ```bash
   flutter run
   ```
   *(Note: The `api_client.dart` automatically connects to `http://10.0.2.2:5000/api` on Android emulators and `http://127.0.0.1:5000/api` on desktop).*

---

## 🔐 Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `FLASK_ENV` | Environment mode (`development` or `production`) | `development` |
| `SECRET_KEY` | Flask session cryptographic secret | `generate_random_hex_string` |
| `JWT_SECRET_KEY` | JWT token signature secret | `generate_random_jwt_secret` |
| `DB_HOST` | MySQL hostname | `localhost` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_NAME` | Database schema name | `vemavaram_csp` |
| `DB_USER` | MySQL database user | `root` |
| `DB_PASSWORD` | MySQL user password | `your_mysql_password` |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary account name | `your_cloud_name` |
| `CLOUDINARY_API_KEY` | Cloudinary API Key | `your_api_key` |
| `CLOUDINARY_API_SECRET` | Cloudinary API Secret | `your_api_secret` |
| `ALLOWED_ORIGINS` | Comma-separated CORS whitelist | `https://complaintredressalsystem.vercel.app,http://localhost:5173` |

### Admin Dashboard (`admin_dashboard/.env`)

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `VITE_API_URL` | API base endpoint | `http://localhost:5000/api` (dev) or `/api` (prod) |

---

## 🌐 Production Deployment Overview

1. **Database**: Host on managed MySQL (e.g., Aiven, Railway, AWS RDS, PlanetScale). Execute `schema_complete.sql`.
2. **Backend**:
   - Host on Render, Railway, or VPS.
   - Set Build Command: `pip install -r requirements.txt`.
   - Set Start Command: `gunicorn run:app` (or use included `Procfile`).
   - Add environment variables (`DB_HOST`, `DB_PASSWORD`, `JWT_SECRET_KEY`, `CLOUDINARY_*`).
   - Update `ALLOWED_ORIGINS` to include the production frontend domain.
3. **Citizen Website**: Deployed on Vercel (`https://complaintredressalsystem.vercel.app/`). Update `VITE_API_URL` in Vercel settings to your cloud backend domain.
4. **Admin Dashboard**: Deploy to Vercel/Netlify. Set `VITE_API_URL` to your cloud backend URL.

---

## 👥 Project Information & Attribution

- **Project**: Community Service Project (CSP)
- **Institution**: Seshadri Rao Gudlavalleru Engineering College (SRGEC)
- **District**: Krishna District, Andhra Pradesh
- **Target Community**: Vemavaram Village

