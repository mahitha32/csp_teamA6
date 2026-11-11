# Entity Relationship Diagram (ERD)

The following Mermaid.js diagram illustrates the relationships and cardinalities between the entities in the Gadepudi Village CSP system.

```mermaid
erDiagram
    USERS {
        int user_id PK
        string name
        string mobile UK
        string role
        string fcm_token
    }

    COMPLAINTS {
        int complaint_id PK
        int user_id FK
        string title
        string category
        string status
        string priority
        int worker_id FK
    }

    ASSIGNMENTS {
        int assignment_id PK
        int complaint_id FK
        int worker_id FK
        string status
    }

    FEEDBACK {
        int feedback_id PK
        int complaint_id FK
        int user_id FK
        int rating
        string remarks
    }

    NOTIFICATIONS {
        int notification_id PK
        int user_id FK
        string title
        string body
    }

    SURVEY_DATA {
        int survey_id PK
        string village
        int total_responses
    }

    SURVEY_INSIGHTS {
        int insight_id PK
        int survey_id FK
        string category
        string severity
        int response_count
    }

    %% Relationships
    USERS ||--o{ COMPLAINTS : "files (villager)"
    USERS ||--o{ COMPLAINTS : "resolves (worker)"
    COMPLAINTS ||--o| ASSIGNMENTS : "has"
    USERS ||--o{ ASSIGNMENTS : "receives (worker)"
    COMPLAINTS ||--o| FEEDBACK : "receives"
    USERS ||--o{ FEEDBACK : "submits"
    USERS ||--o{ NOTIFICATIONS : "receives"
    SURVEY_DATA ||--o{ SURVEY_INSIGHTS : "contains"
```

## Cardinality Notes
- **Users to Complaints:** A villager (User) can submit **Zero or Many** complaints. A worker (User) can be assigned to **Zero or Many** complaints.
- **Complaints to Feedback:** A complaint can have **Zero or One** feedback record attached to it once resolved.
- **Complaints to Assignments:** An assignment acts as a junction/tracking table between Complaints and Workers for auditing purposes.
