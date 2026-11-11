# Database Documentation & Implementation Guide

## Overview
The Gadepudi Village Complaint Redressal System relies on a relational MySQL database (`grampur_csp`). The schema is fully normalized and supports role-based access, comprehensive complaint tracking, survey data insights, and worker assignments.

## 1. Schema Initialization
The database schema script is located at `backend/migrations/schema.sql`.

To initialize the database, execute:
```sql
CREATE DATABASE IF NOT EXISTS grampur_csp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE grampur_csp;
-- Execute the contents of schema.sql here
```

## 2. Table Structures & Foreign Keys

### `users`
Stores villagers, workers, and administrators.
- `user_id` (PK)
- `mobile` (Unique, Indexed)
- `role` (ENUM: villager, worker, admin)
- `fcm_token` (Push notification token)

### `complaints`
Central entity for the system.
- `complaint_id` (PK)
- `user_id` (FK -> users.user_id)
- `category` (ENUM: Road, Water, Lighting, Sanitation, etc.)
- `status` (ENUM: Submitted, Under Review, Assigned, In Progress, Resolved, Rejected)
- `priority` (ENUM: Low, Medium, High, Critical)
- `worker_id` (FK -> users.user_id)

### `assignments`
Tracks task delegation to workers.
- `assignment_id` (PK)
- `complaint_id` (FK -> complaints.complaint_id)
- `worker_id` (FK -> users.user_id)
- `status` (ENUM: Pending, Accepted, Completed)

### `feedback`
Post-resolution feedback from villagers.
- `feedback_id` (PK)
- `complaint_id` (FK -> complaints.complaint_id)
- `rating` (INT 1-5)

### `notifications`
System alerts for users.
- `notification_id` (PK)
- `user_id` (FK -> users.user_id)
- `title`, `body`

### `survey_data`
Village insight metrics gathered during the CSP survey phase.
- `survey_id` (PK)
- `village` (e.g., 'Gadepudi')
- `total_households_surveyed`

### `survey_insights`
Specific problems identified during the survey.
- `insight_id` (PK)
- `survey_id` (FK -> survey_data.survey_id)
- `category`
- `severity` (Critical, High, Medium)

## 3. Sample Test Data Insertion
Below is the SQL script to inject sample data for testing.

```sql
INSERT INTO users (name, mobile, password_hash, role) VALUES 
('Admin User', '9999900000', 'hashed_pw', 'admin'),
('Ramesh (Villager)', '9876543210', 'hashed_pw', 'villager'),
('Suresh (Worker)', '8765432109', 'hashed_pw', 'worker');

INSERT INTO complaints (user_id, title, description, location, category, status, priority) VALUES 
(2, 'Broken Water Pipe', 'Pipe leaking near temple', 'Main Road', 'Water Supply Problems', 'Submitted', 'High'),
(2, 'Streetlight out', 'Dark alley near school', 'School Road', 'Streetlight Issues', 'Resolved', 'Medium');

INSERT INTO feedback (complaint_id, user_id, rating, remarks) VALUES 
(2, 2, 5, 'Fixed very quickly, thank you.');

INSERT INTO survey_data (village, total_households_surveyed, total_responses, survey_year) VALUES 
('Gadepudi', 500, 350, 2026);

INSERT INTO survey_insights (survey_id, category, description, response_count, severity) VALUES 
(1, 'Water Supply Problems', 'Irregular drinking water supply in South Ward', 120, 'High'),
(1, 'Drainage Problems', 'Open drains causing mosquito breeding', 210, 'Critical');
```
