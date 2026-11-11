# Firebase Setup Guide
## Gadepudi Village CSP

This project uses Firebase for **Authentication (Phone OTP)** and **Cloud Storage (Image Uploads)**.
Follow these steps to set up a new Firebase project and connect it to your backend and Flutter app.

### 1. Create a Firebase Project
1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Click **Add project**.
3. Name your project (e.g., `gadepudi-csp`) and click **Continue**.
4. Disable Google Analytics (optional but recommended for simple setups) and click **Create project**.

### 2. Enable Authentication
1. In the Firebase console, go to **Build > Authentication**.
2. Click **Get Started**.
3. Go to the **Sign-in method** tab.
4. Enable **Phone** authentication.
5. (Optional) Add a test phone number and verification code to test login without real SMS.

### 3. Enable Cloud Storage
1. In the Firebase console, go to **Build > Storage**.
2. Click **Get Started**.
3. Start in **Test mode** (or configure security rules to allow read/write).
4. Click **Next** and choose a Cloud Storage location, then click **Done**.

### 4. Setup Backend API (Python Flask)
The backend requires a Service Account Key to verify Firebase tokens and upload images.

1. In the Firebase console, go to **Project settings** (gear icon) > **Service accounts**.
2. Click **Generate new private key**.
3. Save the downloaded JSON file as `firebase_credentials.json` inside the `backend/` folder.
4. In your `.env` file, set:
   ```env
   FIREBASE_CREDENTIALS_PATH=firebase_credentials.json
   FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
   ```
   *Note: You can find the storage bucket name in the Storage section (e.g., `gs://gadepudi-csp.appspot.com`). Remove the `gs://` prefix.*

### 5. Setup Flutter App
1. Install the Firebase CLI: `npm install -g firebase-tools`
2. Log in to Firebase: `firebase login`
3. Install the FlutterFire CLI: `dart pub global activate flutterfire_cli`
4. In your `mobile_app/` directory, run:
   ```bash
   flutterfire configure
   ```
5. Select your newly created Firebase project.
6. This command will automatically generate `lib/firebase_options.dart` and configure your Android/iOS projects.
7. Uncomment the Firebase initialization code in `lib/main.dart`:
   ```dart
   await Firebase.initializeApp(
     options: DefaultFirebaseOptions.currentPlatform,
   );
   ```

You are now fully connected to Firebase!
