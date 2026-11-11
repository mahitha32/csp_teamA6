# Use Case Diagrams

This document outlines the interactions between the system actors (Villager, Worker, Administrator) and the system processes.

```mermaid
usecaseDiagram
    actor Villager as "Villager"
    actor Worker as "Maintenance Worker"
    actor Admin as "Village Administrator"

    package "Gadepudi CSP System" {
        usecase "Login via OTP" as UC1
        usecase "Submit Complaint" as UC2
        usecase "Upload Photo Evidence" as UC3
        usecase "Track Complaint Status" as UC4
        usecase "Submit Rating/Feedback" as UC5

        usecase "View Assigned Tasks" as UC6
        usecase "Update Task Progress" as UC7
        usecase "Upload Resolution Photo" as UC8

        usecase "View Dashboard Analytics" as UC9
        usecase "Manage Complaints" as UC10
        usecase "Assign Worker to Task" as UC11
        usecase "View Survey Insights" as UC12
        usecase "Generate Reports" as UC13
    }

    Villager --> UC1
    Villager --> UC2
    Villager --> UC3
    Villager --> UC4
    Villager --> UC5

    Worker --> UC1
    Worker --> UC6
    Worker --> UC7
    Worker --> UC8

    Admin --> UC1
    Admin --> UC9
    Admin --> UC10
    Admin --> UC11
    Admin --> UC12
    Admin --> UC13
```

## Actor Descriptions

### 1. Villager
The primary end-user residing in Gadepudi Village. They use the mobile application to log issues they face in the village infrastructure.

### 2. Maintenance Worker
Employed by the village administration (Panchayat). They use the mobile app to receive daily task assignments and prove resolution by uploading photos.

### 3. Administrator
Village authorities (e.g., Sarpanch, Panchayat Secretary). They use the secure web dashboard to oversee the entire redressal operation, delegate work, and analyze long-term trends against survey data.
