# CSP Project Presentation Package

This document contains materials for a 15-slide Viva presentation, an executive summary, and a live demo script for your final evaluation.

---

## 1. Executive Summary & Synopsis
**Project Title:** Gadepudi Village Complaint Redressal System
**Domain:** E-Governance & Rural Development
**Tech Stack:** Flutter (Mobile), React.js (Web), Python/Flask (API), MySQL (DB), Firebase (Auth/Storage)

**Synopsis:** This project digitizes the civic grievance redressal mechanism for Gadepudi village. It replaces a manual, opaque paper-based system with a transparent digital pipeline. Villagers report issues with photos via a mobile app; Panchayat administrators monitor, analyze, and assign these tasks via a web dashboard; and maintenance workers prove resolution by uploading completion photos. 

---

## 2. 15-Slide Viva Presentation Content

**Slide 1: Title Slide**
- Project Title, Student Name, Guide Name, Institution.

**Slide 2: Introduction**
- What is the project? A localized e-governance platform for Gadepudi Village.

**Slide 3: Problem Statement**
- Manual paper tracking. Lost complaints. No accountability for workers. No data for administrators.

**Slide 4: Objectives**
- Digitize reporting, enforce accountability via photos, provide analytics, integrate field survey data.

**Slide 5: Field Survey Insights (Baseline)**
- Surveyed 500 households in Gadepudi.
- Top issues found: Drainage (60%), Water Supply (34%).

**Slide 6: Proposed System**
- 3 distinct portals: Villager App, Worker App, Admin Dashboard.

**Slide 7: System Architecture**
- Diagram showing Flutter -> Flask API -> MySQL & Firebase.

**Slide 8: Key Features - Villager**
- OTP Login, Photo Uploads, Status Tracking, 5-Star Feedback.

**Slide 9: Key Features - Administrator**
- Live Analytics Dashboard, Worker Assignment, CSV Export, Survey Contrasting.

**Slide 10: Key Features - Worker**
- Digital Task Roster, Mandatory Resolution Photo Upload.

**Slide 11: Database Design (ERD)**
- Brief look at Users, Complaints, Assignments, Feedback tables.

**Slide 12: Professional Enhancements**
- Automated AI Categorization (stub), Firebase Cloud Storage integration.

**Slide 13: Results & Impact**
- Transparent governance, measured worker performance, data-driven budgeting for the Panchayat.

**Slide 14: Future Scope**
- Local language support (Telugu), IoT automated complaints.

**Slide 15: Conclusion & Q&A**
- Summary statement and open floor for faculty questions.

---

## 3. Demo Script (Evaluation Day)

**Step 1: The Villager (Mobile App)**
* "I am a villager in Gadepudi. I see a broken water pipe."
* *Action:* Open Flutter app, login with OTP.
* *Action:* Create a complaint, take a picture of the "pipe", submit.

**Step 2: The Administrator (Web Dashboard)**
* "I am the Panchayat Secretary. I log into my web dashboard."
* *Action:* Open React Dashboard. Show the new pending complaint.
* *Action:* Show the Analytics page highlighting Water Supply issues.
* *Action:* Go back to complaints, assign "Worker Suresh" to the task.

**Step 3: The Worker (Mobile App)**
* "I am Worker Suresh. I get a notification."
* *Action:* Log into Flutter app as worker. See assigned task.
* *Action:* Click "Update Progress", upload a photo of the "fixed pipe", mark as Resolved.

**Step 4: The Conclusion (Web Dashboard / Villager)**
* *Action:* Show the Admin dashboard updating live to 'Resolved'.
* *Action:* Show the Villager app receiving a notification asking for a 1-5 star rating.

---

## 4. Evaluation Talking Points & Anticipated Questions

**Q1: Why did you use Flask instead of Node.js?**
*Answer:* Flask was chosen because Python is excellent for data processing, and it leaves room to easily integrate Machine Learning models in the future (like the AI classification feature we planned for).

**Q2: How do you handle villagers without smartphones?**
*Answer:* The Admin Dashboard has a feature to manually enter complaints. A villager can walk into the Panchayat office, and a clerk can register it on their behalf.

**Q3: Why use Firebase just for Auth and Storage instead of the whole database?**
*Answer:* We wanted a highly relational SQL database (MySQL) to easily write complex analytical queries (like worker performance vs complaint category), which is harder to do in NoSQL databases like Firestore.
