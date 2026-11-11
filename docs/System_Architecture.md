# System Architecture

The Gadepudi Village Complaint Redressal System follows a decoupled, service-oriented architecture.

```mermaid
graph TD
    subgraph "Client Tier"
        VillagerApp[Flutter App\nVillager Interface]
        WorkerApp[Flutter App\nWorker Interface]
        AdminWeb[React SPA\nAdmin Dashboard]
    end

    subgraph "API Gateway / Backend Tier"
        Flask[Flask Backend API]
        AuthSvc[Auth Service\nJWT & Decorators]
        AISvc[AI Service\nComplaint Classifier]
        FCM[FCM Service\nPush Notifications]
    end

    subgraph "Data & Cloud Services Tier"
        MySQL[(MySQL Database\ngrampur_csp)]
        FBAuth[Firebase Authentication\nPhone OTP]
        FBStore[Firebase Cloud Storage\nImage Hosting]
    end

    %% Flows
    VillagerApp -- HTTP REST --> Flask
    WorkerApp -- HTTP REST --> Flask
    AdminWeb -- HTTP REST --> Flask

    Flask <--> AuthSvc
    Flask <--> AISvc
    Flask -- Write/Read --> MySQL
    Flask -- Send --> FCM

    VillagerApp -- Token Auth --> FBAuth
    Flask -- Verify Token --> FBAuth

    Flask -- Upload/URL --> FBStore

    classDef frontend fill:#0ea5e9,stroke:#0284c7,stroke-width:2px,color:#fff;
    classDef backend fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff;
    classDef db fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff;

    class VillagerApp,WorkerApp,AdminWeb frontend;
    class Flask,AuthSvc,AISvc,FCM backend;
    class MySQL,FBAuth,FBStore db;
```

## Flow Descriptions
1. **Authentication Flow:** Flutter app sends phone number to Firebase Auth. User receives OTP. Flutter sends resulting ID Token to Flask Backend. Flask verifies with Firebase Admin SDK and issues a custom JWT.
2. **Complaint Submission Flow:** Villager submits data via Flutter. Flask receives request, saves image to Firebase Storage, queries AI Classifier if category is missing, and saves record to MySQL.
3. **Notification Flow:** When Admin updates a status or assigns a worker, Flask inserts a record into MySQL `notifications` and triggers Firebase Cloud Messaging (FCM) to push the alert to the target device.
