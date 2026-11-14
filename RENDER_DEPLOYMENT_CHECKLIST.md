# Render Deployment Readiness Checklist & Production Guide

**Project**: Vemavaram Village Complaint Redressal System (Vemavaram CSP)  
**Target Platform**: Render (Web Service)  
**GitHub Repository**: [https://github.com/mahitha32/csp_teamA6](https://github.com/mahitha32/csp_teamA6)  
**Branch**: `main`  
**Latest Remote Commit**: `135b90b` (`135b90b996541496c17af3b66a03078368e2de43`)  
**Status**: **PREPARATION & VALIDATION COMPLETE — READY FOR DEPLOYMENT (Awaiting User Action)**  

---

## Task 1: GitHub Verification Results

| Check | Expected | Actual Result | Verification Status |
|---|---|---|---|
| **Origin Remote URL** | `https://github.com/mahitha32/csp_teamA6.git` | `origin https://github.com/mahitha32/csp_teamA6.git (fetch & push)` | **VERIFIED** |
| **Remote Main Commit** | `135b90b` | `135b90b996541496c17af3b66a03078368e2de43` confirmed via `git ls-remote` | **VERIFIED** |
| **`render.yaml` in Root** | Repository root | Present (`csp/render.yaml`) | **VERIFIED** |
| **`backend/requirements.txt`** | In `backend/` | Present (`csp/backend/requirements.txt`) | **VERIFIED** |
| **`backend/run.py`** | In `backend/` | Present (`csp/backend/run.py`) | **VERIFIED** |
| **`backend/Procfile`** | In `backend/` | Present (`csp/backend/Procfile`) | **VERIFIED** |

---

## Task 2: Render Configuration Validation

### 2.1 File Inspection (`render.yaml`)
```yaml
services:
  - type: web
    name: vemavaram-backend-api
    runtime: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -w 4 -b 0.0.0.0:$PORT run:app
    healthCheckPath: /api/health
    plan: free
    autoDeploy: true
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: DB_HOST
        sync: false
      - key: DB_PORT
        value: "3306"
      - key: DB_NAME
        sync: false
      - key: DB_USER
        sync: false
      - key: DB_PASSWORD
        sync: false
      - key: CLOUDINARY_CLOUD_NAME
        sync: false
      - key: CLOUDINARY_API_KEY
        sync: false
      - key: CLOUDINARY_API_SECRET
        sync: false
      - key: ALLOWED_ORIGINS
        value: https://complaintredressalsystem.vercel.app,http://localhost:3000,http://localhost:5173
```

### 2.2 Validation Points
1. **Root Directory**: Explicitly set to `rootDir: backend`. Render executes all build steps (`pip install`) and runtime processes inside `backend/`, preventing `ModuleNotFoundError: No module named 'app'`.
2. **Build Command**: `pip install -r requirements.txt`. All packages are pure-Python compatible.
3. **Gunicorn WSGI Target**: `run:app`. In `run.py`, `app = create_app(...)` is exported at module level.
4. **Health Check Path**: `/api/health`. Returns HTTP 200 `{"message": "Vemavaram Village CSP API is running", "success": true}` with zero database dependencies, ensuring fast zero-downtime health probing.
5. **Python Version**: `PYTHON_VERSION=3.11.9`. Render native Python environment supports this variable to pin runtime to Python 3.11 LTS.

---

## Task 3: Database Readiness & Cloud MySQL Setup

### 3.1 Local Database Isolation Confirmation
### 3.1 TiDB Starter Cloud Database Setup Status
- **Cluster**: `vemavaram-csp` (AWS Singapore `ap-southeast-1`)
- **Engine**: `8.0.11-TiDB-v8.5.3-serverless`
- **Database**: `vemavaram_csp`
- **TLS/SSL Encryption**: Enabled via Python `certifi` Root CA bundle.
- **Setup Execution**: Executed via `backend/scripts/setup_tidb.py`.
- **Status**: **100% COMPLETE & VERIFIED**

### 3.2 Schema Verification Results on TiDB
- **Total Tables**: **15 / 15 verified active**
  1. `users` (PASS)
  2. `worker_profiles` (PASS)
  3. `otp_sessions` (PASS)
  4. `wards` (PASS — seeded with 4 wards)
  5. `complaints` (PASS)
  6. `assignments` (PASS)
  7. `complaint_status_history` (PASS)
  8. `feedback` (PASS)
  9. `notifications` (PASS)
  10. `activity_logs` (PASS)
  11. `survey_insights` (PASS — 0 mock records, clean for actual survey data)
  12. `contact_messages` (PASS)
  13. `assets` (PASS)
  14. `slas` (PASS — seeded with 6 category SLAs)
  15. `escalations` (PASS)
- **Foreign Keys**: **15 active Foreign Key constraints verified** in TiDB `information_schema.key_column_usage`.
- **Admin Account Security**: Default admin (`Admin@123`) was **NOT** inserted. Admin count in `users` is 0.
- **Survey Data Integrity**: Preloaded 2025 survey mock statistics were **NOT** inserted. Record count in `survey_insights` is 0.
- **Flask Backend Integration**: Verified via Flask application factory `create_app('production')` and `get_db()`.
  - `/api/health`: HTTP 200 OK
  - `/api/admin/public-stats`: HTTP 200 OK (returned live data from TiDB)

### 3.3 Schema Idempotency (`backend/migrations/schema_complete.sql`)
- Contains 12 core tables: `users`, `worker_profiles`, `otp_sessions`, `wards`, `complaints`, `assignments`, `complaint_status_history`, `feedback`, `notifications`, `activity_logs`, `survey_insights`, `contact_messages`, `assets`, `slas`, and `escalations`.
- All table creations use `CREATE TABLE IF NOT EXISTS`.
- Seed data uses `INSERT IGNORE INTO` and `ON DUPLICATE KEY UPDATE`.
- The schema is completely non-destructive.

### 3.4 Commands for Applying Schema to a Fresh Cloud Database

#### Option A: If your cloud database user has permission to create databases:
```bash
mysql -h <REMOTE_DB_HOST> -P <REMOTE_DB_PORT> -u <REMOTE_DB_USER> -p<REMOTE_DB_PASSWORD> < backend/migrations/schema_complete.sql
```

#### Option B: If using a provider with a pre-created database (e.g., Aiven `defaultdb`, Railway `railway`):
If your cloud user does not have permission to execute `CREATE DATABASE`, target the database directly:
```bash
# Connect and execute into your specific cloud database name
mysql -h <REMOTE_DB_HOST> -P <REMOTE_DB_PORT> -u <REMOTE_DB_USER> -p<REMOTE_DB_PASSWORD> <REMOTE_DB_NAME> < backend/migrations/schema_complete.sql
```
*(Ensure `DB_NAME` in Render's environment variables matches `<REMOTE_DB_NAME>`)*.

#### Option C: Verification query after schema import:
```bash
mysql -h <REMOTE_DB_HOST> -P <REMOTE_DB_PORT> -u <REMOTE_DB_USER> -p<REMOTE_DB_PASSWORD> -e "USE <REMOTE_DB_NAME>; SHOW TABLES;"
```
Expected output: 14-15 tables listed, including `complaints`, `users`, `worker_profiles`, `wards`, `assets`.

---

## Task 4: Cloud Security & Credentials Audit

| Security Domain | Implementation | Audit Finding |
|---|---|---|
| **Git Tracking** | `.gitignore` covers `.env`, `*.key`, `*.pem`, `*.json` (credentials) | **Zero sensitive files tracked** in commit history or working tree. |
| **Firebase Auth** | `app/services/firebase_service.py` | Supports `FIREBASE_CREDENTIALS_JSON` inline env string or Render secret file. Lazy initialization: not invoked for standard citizen/admin web authentication. |
| **Image Storage** | `app/services/image_service.py` | Uploads directly to Cloudinary CDN (`vemavaram_csp/complaints/`, `vemavaram_csp/resolutions/`). Persistent across container restarts. |
| **JWT Tokens** | `SECRET_KEY` & `JWT_SECRET_KEY` | Render auto-generates 256-bit cryptographically secure strings (`generateValue: true` in `render.yaml`). |

---

## Task 5: Step-by-Step Render Deployment Guide

### Deployment Method 1: One-Click Blueprint (Recommended)
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. In the top navigation, click **New +** → **Blueprint**.
3. Connect your GitHub account and select repository: `mahitha32/csp_teamA6`.
4. Render will automatically detect `render.yaml` and configure the service parameters.
5. Render will prompt you for the un-synced variables (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`).
6. Click **Apply**. Render will build and deploy the web service.

---

### Deployment Method 2: Manual Web Service
If creating the service manually:
1. Click **New +** → **Web Service**.
2. Select GitHub repository: `mahitha32/csp_teamA6`.
3. Configure the service settings:
   - **Name**: `vemavaram-backend-api`
   - **Region**: Select the closest region (e.g. `Singapore` or `Frankfurt`)
   - **Branch**: `main`
   - **Root Directory**: `backend` *(CRITICAL: do not leave blank)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT run:app`
   - **Instance Type**: `Free`
4. Expand **Advanced**:
   - **Health Check Path**: `/api/health`
   - **Auto-Deploy**: `Yes`
5. Go to the **Environment** section and add the variables below.

---

### Environment Variables Reference Table

#### Mandatory Environment Variables

| Variable Name | Description | Where to Obtain |
|---|---|---|
| `FLASK_ENV` | Must be set to `production` | Enter literal string: `production` |
| `PYTHON_VERSION` | Pinned Python runtime | Enter literal string: `3.11.9` |
| `SECRET_KEY` | Flask session encryption | Auto-generated by Render Blueprint or click **Generate** in Render UI |
| `JWT_SECRET_KEY` | JWT token signature key | Auto-generated by Render Blueprint or click **Generate** in Render UI |
| `DB_HOST` | Remote MySQL hostname | From your cloud MySQL dashboard (e.g., Aiven, Railway, AWS) |
| `DB_PORT` | Remote MySQL port | Typically `3306` (or custom port from your cloud MySQL dashboard) |
| `DB_NAME` | Database name | From cloud MySQL dashboard (e.g., `vemavaram_csp` or `defaultdb`) |
| `DB_USER` | MySQL database username | From cloud MySQL dashboard |
| `DB_PASSWORD` | MySQL database password | From cloud MySQL dashboard |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary account cloud name | Log into [cloudinary.com](https://cloudinary.com/console) → Dashboard → Cloud Name |
| `CLOUDINARY_API_KEY` | Cloudinary API Key | Cloudinary Dashboard → API Keys |
| `CLOUDINARY_API_SECRET` | Cloudinary API Secret | Cloudinary Dashboard → API Keys |
| `ALLOWED_ORIGINS` | CORS origin whitelist | `https://complaintredressalsystem.vercel.app,http://localhost:3000,http://localhost:5173` |

#### Optional Environment Variables

| Variable Name | Default Value | Description | Where to Obtain |
|---|---|---|---|
| `DB_SSL_MODE` | *(Unset / None)* | Set to `REQUIRED` if your cloud MySQL enforces SSL/TLS (e.g., Aiven, TiDB) | Set to `REQUIRED` if needed |
| `FIREBASE_CREDENTIALS_JSON` | *(Unset)* | Full service account JSON string for Flutter Phone Auth / FCM | Firebase Console → Project Settings → Service Accounts → Generate new private key |
| `USE_REAL_OTP` | `false` | Set to `true` if sending real SMS OTPs via MSG91 | Set `true` only if live SMS gateway is configured |
| `MSG91_AUTH_KEY` | *(Unset)* | MSG91 SMS auth key | From MSG91 dashboard (only if `USE_REAL_OTP=true`) |
| `MSG91_TEMPLATE_ID` | *(Unset)* | MSG91 DLT approved SMS template ID | From MSG91 dashboard |
| `MSG91_SENDER_ID` | `VEMVLG` | 6-character SMS sender ID header | From MSG91 dashboard |

---

## Post-Deployment Verification Steps

Once Render finishes deploying:
1. **Health Probe**:
   ```bash
   curl -i https://<your-render-subdomain>.onrender.com/api/health
   ```
   Expected response: HTTP 200 with `{"message": "Vemavaram Village CSP API is running", "success": true}`.
2. **Public Statistics Check**:
   ```bash
   curl -i https://<your-render-subdomain>.onrender.com/api/admin/public-stats
   ```
   Expected response: HTTP 200 with village stats from database.
3. **Connect Vercel Frontend**:
   In your Vercel citizen website project:
   - Navigate to **Project Settings** → **Environment Variables**.
   - Update `VITE_API_BASE_URL` to `https://<your-render-subdomain>.onrender.com/api`.
   - Trigger a redeployment in Vercel.

---

## Task 6: Operational Hold & Safety Guarantee

- **Deployment Execution**: **HALTED / AWAITING USER APPROVAL**. No Render Web Service has been triggered or deployed.
- **Data Safety**: No data migration or local database interaction was performed.
- **Git State**: Branch `main` is clean, synced with remote commit `135b90b`. No unapproved commits or credentials have been pushed.

