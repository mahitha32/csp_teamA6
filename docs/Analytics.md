# Analytics Dashboard Documentation

## Overview
The analytics engine is designed to give the village administration a bird's-eye view of the redressal operation. It is accessible at the root (`/`) path of the React Admin dashboard.

## Key Metrics Tracked
The Flask backend aggregates data in the `/admin/analytics` endpoint to provide the following live indicators:

1. **Complaint Summary Counts**
   - Total All-Time Complaints
   - Pending Review (Submitted + Under Review)
   - In Progress (Assigned + Active)
   - Resolved
   - Resolution Rate (%)

2. **Performance Indicators**
   - **Average Resolution Time:** Calculated in days using `DATEDIFF(resolved_at, created_at)`.
   - **Average Villager Rating:** Aggregated from the `feedback` table (1-5 stars).

## Advanced Visualizations
The dashboard utilizes **Chart.js** to render advanced analytics:

### 1. Category Distribution (Pie Chart)
Displays the proportion of complaints across major categories (Roads, Water, Sanitation). This helps identify the most problematic infrastructure sectors in the village.

### 2. Monthly Complaint Trends (Line Chart)
A 12-month rolling trend line mapping the volume of incoming complaints. This helps in identifying seasonal issues (e.g., more drainage complaints during monsoon season).

### 3. Worker Performance Metrics (Grouped Bar Chart)
Contrasts the number of "Assigned" tasks vs "Resolved" tasks for the top 6 active maintenance workers. This ensures equitable distribution of labor and helps identify underperforming staff.

## Report Generation (Export Support)
The `/reports` module allows administrators to:
1. Filter live data by Date Range and Category.
2. View the tabular results.
3. **Export as CSV**: A custom JavaScript Blob generator creates an Excel-compatible `.csv` file format for offline archiving and printing for Panchayat meetings.
