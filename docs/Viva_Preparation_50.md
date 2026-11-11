# Viva Preparation Package (50 Questions)
**Gadepudi Smart Village Governance Platform**

## Section 1: Project Scope & CSP Impact (Q1-10)
1. **What is the primary problem this project solves?** It digitizes the manual grievance redressal system in Gadepudi, ensuring accountability via photo evidence and analytics.
2. **How does this relate to your CSP?** We conducted a physical survey to find baseline infrastructure issues, then built a digital system to track and solve them.
3. **What makes it "Smart"?** Geolocation tracking, AI-based priority routing, and automated escalation matrices.
4. **Who are the primary actors?** Villagers (users), Maintenance Workers (execution), and Panchayat Admins (oversight).
5. **How did the baseline survey influence the design?** The survey revealed water and drainage as critical issues, so we added a dedicated "Survey Insights" contrasting module.
6. **How do you handle illiterate users?** The app includes accessibility UI designs, and admins can manually input complaints at the Panchayat office.
7. **What is the "Community Impact Dashboard"?** A public-facing UI showing Development Scores to ensure total transparency between citizens and government.
8. **Why did you include an escalation matrix?** To prevent complaints from sitting in "Pending" forever; SLAs hold authorities accountable.
9. **How is Worker Efficiency calculated?** By dividing "Tasks Resolved" by "Tasks Assigned" and tracking average resolution days.
10. **What is the biggest challenge in rural deployment?** Internet connectivity and digital literacy.

## Section 2: Architecture & System Design (Q11-20)
11. **Explain the 3-tier architecture used.** Client (Flutter/React), Backend API (Flask), Data Layer (MySQL/Firebase).
12. **Why decouple the frontend and backend?** It allows us to build multiple clients (Web, Mobile) that consume the same central data source.
13. **Why use Firebase for Auth but MySQL for data?** Firebase provides highly secure, out-of-the-box OTP verification, while MySQL allows complex relational queries needed for the analytics dashboard.
14. **How do the Flutter app and Flask backend communicate?** Via RESTful HTTP API calls using JSON payloads.
15. **What is a JWT and how is it used here?** JSON Web Token. Flask issues it after verifying the Firebase login. It's sent in the header of every subsequent request to prove identity.
16. **Why store images in Firebase Storage instead of MySQL?** Databases are terrible for storing large binary files (BLOBs). Cloud storage is faster, cheaper, and optimized for CDN delivery.
17. **What is the purpose of the 'assignments' table?** It acts as a junction table to track the many-to-many relationship of complaints moving between different workers over time.
18. **How does the AI Classifier work?** It's a Python script that analyzes the complaint title and description against a keyword dictionary to suggest Categories and Priorities.
19. **What are Data Flow Diagrams (DFDs)?** Visual representations of how data moves from Villager input, through the API, into the DB, and out to the Admin Dashboard.
20. **Explain the difference between Unit and System testing in your project.** Unit testing checks a specific Flask function (like ID generation). System testing tests the whole flow (Submitting a complaint on Mobile and seeing it appear on Web).

## Section 3: Web Dashboard (React.js) (Q21-30)
21. **Why React instead of plain HTML/JS?** React uses a Virtual DOM for fast, dynamic updates, perfect for a live dashboard.
22. **What is Vite?** A modern, extremely fast build tool for React that replaces older tools like Webpack.
23. **How are the charts rendered?** Using the `Chart.js` library wrapped in `react-chartjs-2`.
24. **How does the interactive map work?** We use `react-leaflet` to render OpenStreetMap tiles and plot complaint GPS coordinates.
25. **Explain React Hooks used in this project.** `useState` for holding data (like complaint lists) and `useEffect` for fetching API data when a page loads.
26. **What is the AuthContext?** A React Context provider that wraps the app, ensuring the logged-in user state is available globally without prop-drilling.
27. **How do you handle routing?** Using `react-router-dom` to switch between Dashboard, Complaints, and Reports pages without reloading the browser.
28. **How does the CSV Export feature work?** It maps the JSON report data into comma-separated strings, creates a Blob, and forces the browser to download it.
29. **What happens if the API token expires?** Axios interceptors catch the 401 Unauthorized error and force a redirect to the login page.
30. **Why use CSS variables?** To create a consistent "Village Branding" design system where changing one primary color updates the entire app.

## Section 4: Backend API (Python Flask) (Q31-40)
31. **Why Flask instead of Django?** Flask is a micro-framework. It is lightweight and gives us total control over the API structure without unnecessary bloat.
32. **How does Flask connect to MySQL?** Using the `PyMySQL` driver configured in the application factory.
33. **Explain the `@jwt_required` decorator.** It intercepts the request, checks for a valid JWT in the headers, and blocks unauthorized access before the route logic runs.
34. **How do you handle File Uploads in Flask?** By reading `request.files`, validating the file type, and passing the binary data to the Firebase Admin SDK.
35. **What is CORS and why is it needed?** Cross-Origin Resource Sharing. It allows the React app (running on localhost:3000) to securely fetch data from the Flask API (running on localhost:5000).
36. **How are complaint IDs generated?** A custom Python utility fetches the current year and the total row count to format an ID like `CMP2026001`.
37. **What is SQL Injection and how did you prevent it?** An attack where malicious SQL is sent via inputs. We prevent it by using parameterized queries (`%s`) in PyMySQL.
38. **How does the backend calculate Analytics?** Using complex SQL `COUNT()`, `GROUP BY`, and `DATEDIFF()` queries.
39. **Explain the role of `.env` files.** They store sensitive secrets (DB passwords, Firebase keys) outside of the source code repository.
40. **How would you deploy this backend?** Using Gunicorn as the WSGI server on a platform like Render or AWS EC2.

## Section 5: Mobile App (Flutter) (Q41-50)
41. **Why use Flutter?** It allows us to compile native Android and iOS apps from a single Dart codebase.
42. **What is a StatefulWidget?** A UI component that has internal mutable state (e.g., a form where text changes as you type).
43. **How do you make HTTP requests in Flutter?** Using the `Dio` package for robust networking and interceptor support.
44. **How do you capture images?** Using the `image_picker` package to access the native device camera.
45. **How is geolocation handled?** Using the `geolocator` package to fetch latitude and longitude during complaint submission.
46. **What is SharedPreferences used for?** To store the JWT access token locally on the device so the user doesn't have to log in every time they open the app.
47. **Explain the layout of the Complaint Form.** A `SingleChildScrollView` containing a `Form` widget with various `TextFormField`s and a custom image upload container.
48. **How do you handle loading states?** By wrapping submission logic in `setState(() => _isLoading = true)` and showing a `CircularProgressIndicator` on the UI.
49. **How would you implement Push Notifications?** By integrating the `firebase_messaging` package and listening for background messages.
50. **How do you build the final APK?** By running `flutter build apk --release` in the terminal.
