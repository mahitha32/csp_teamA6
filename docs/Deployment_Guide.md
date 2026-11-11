# Deployment Guide

This guide covers how to deploy the entire Gadepudi CSP system to a production-ready state.

## 1. Database (MySQL) Setup
1. Provision a MySQL database (e.g., AWS RDS, DigitalOcean Managed DB, or local server).
2. Run the initialization script: `mysql -h <host> -u <user> -p < migrations/schema.sql`
3. Ensure the database user has full CRUD permissions on the `grampur_csp` schema.

## 2. Flask Backend Deployment (Render / Heroku)
The Python backend is production-ready via Gunicorn.
1. Clone the repository to your host.
2. Ensure `requirements.txt` includes `gunicorn`.
3. Create a `.env` file on your server (or add Environment Variables in your hosting provider):
   ```env
   FLASK_ENV=production
   DB_HOST=your_mysql_host
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=grampur_csp
   FIREBASE_CREDENTIALS_PATH=firebase_credentials.json
   ```
4. Place the `firebase_credentials.json` (from Firebase Console > Service Accounts) in the backend directory.
5. Start the server:
   ```bash
   gunicorn --bind 0.0.0.0:8000 run:app
   ```

## 3. React Admin Dashboard Deployment (Vercel / Netlify)
The Admin Dashboard is built with Vite.
1. Navigate to `admin_dashboard/`
2. Create a `.env.production` file:
   ```env
   VITE_API_URL=https://your-flask-backend.com/api
   ```
3. Run the build command:
   ```bash
   npm install
   npm run build
   ```
4. Deploy the `dist/` folder to any static hosting provider (Vercel, Netlify, GitHub Pages, or an Nginx server).
5. Ensure "Single Page App" routing is enabled on the server (redirect all `404`s to `index.html`).

## 4. Flutter Mobile App Deployment (Android APK)
1. Ensure Firebase is fully configured (`flutterfire configure`).
2. Update the `ApiClient.baseUrl` in `lib/core/network/api_client.dart` to point to your live Flask backend URL (remove the `10.0.2.2` loopback).
3. Build the release APK:
   ```bash
   flutter build apk --release
   ```
4. The generated APK will be located at `build/app/outputs/flutter-apk/app-release.apk`.
5. This APK can be distributed directly to villagers or published to the Google Play Store.

## 5. Firebase Requirements
Ensure the following are active in your Firebase Console:
- **Authentication:** Phone Sign-in provider enabled.
- **Storage:** A bucket is provisioned and Security Rules allow authenticated users to `write`.
- **Cloud Messaging (FCM):** Enabled for push notifications.
