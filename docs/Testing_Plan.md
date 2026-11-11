# Testing Plan & Scenarios

To ensure the reliability of the Gadepudi Village CSP system, a comprehensive testing strategy combining Unit, Integration, and System testing must be executed.

## 1. Unit Testing Plan
- **Backend:** Use `pytest` to test isolated utility functions (e.g., JWT token generation, password hashing).
- **Frontend:** Use `Jest` for testing React component rendering (e.g., Sidebar visibility based on auth state).
- **Mobile:** Use Flutter's built-in `test` package for widget testing and API client parsing logic.

## 2. Integration Testing Plan
Verify interactions between subsystems.
- **Flask <-> MySQL:** Ensure ORM/SQL queries correctly fetch joined data (e.g., Complaints + Assigned Worker Names).
- **Flask <-> Firebase:** Test the ID Token verification flow using mock tokens.
- **Flutter <-> Flask:** Ensure HTTP 401 Unauthorized responses correctly trigger the token refresh/logout flow in the mobile app.

## 3. System & User Acceptance Testing (UAT)
Simulate real-world end-to-end usage.

### 20 Realistic Test Cases

| TC ID | Module | Scenario | Expected Result | Pass/Fail |
|-------|--------|----------|-----------------|-----------|
| TC01 | Auth | Villager attempts to login with 9-digit mobile | Frontend validates and blocks request | |
| TC02 | Auth | Villager enters correct OTP | Successful login, JWT issued, routed to Home | |
| TC03 | Auth | Admin attempts login with invalid password | API returns 401 Unauthorized, UI shows error toast | |
| TC04 | Complaint | Villager submits text-only complaint | Success. AI classifies category automatically. | |
| TC05 | Complaint | Villager attaches 5MB image to complaint | Firebase upload succeeds, complaint record contains URL | |
| TC06 | Complaint | Villager submits complaint without location | UI blocks submission (Required field) | |
| TC07 | Dashboard | Admin loads Dashboard Analytics | Charts render correctly with live DB data | |
| TC08 | Dashboard | Admin filters complaints by "Road Issues" | Table only displays Road-related complaints | |
| TC09 | Dashboard | Admin assigns Worker A to Complaint X | Assignment table updates, Worker A receives notification | |
| TC10 | Dashboard | Admin attempts to assign Deactivated Worker | Dropdown hides deactivated workers / API rejects | |
| TC11 | Dashboard | Admin changes status to "In Progress" | Status updates in DB, Villager receives FCM notification | |
| TC12 | WorkerApp | Worker logs in, views assigned tasks | Only assigned tasks for that specific worker ID are shown | |
| TC13 | WorkerApp | Worker marks task as "Resolved" without photo | UI blocks submission (Evidence required) | |
| TC14 | WorkerApp | Worker uploads resolution photo and saves | Task marked Completed, Admin UI updates immediately | |
| TC15 | Feedback | Villager views resolved complaint | Rating UI (1-5 stars) becomes visible | |
| TC16 | Feedback | Villager submits 1-star rating with remarks | Feedback saved to DB, Admin Dashboard average drops | |
| TC17 | Reports | Admin selects Date Range Jan 1 to Jan 31 | Only complaints within range are fetched | |
| TC18 | Reports | Admin clicks "Export CSV" | Browser downloads a valid, properly formatted CSV file | |
| TC19 | Survey | Admin navigates to Survey Insights | Baseline data for Gadepudi is displayed accurately | |
| TC20 | System | Token expires while villager is active | API Client intercepts 401, attempts silent refresh, or redirects to login | |
