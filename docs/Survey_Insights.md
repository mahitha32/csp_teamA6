# Village Survey Insights Module

## Overview
A core requirement of the Community Service Project (CSP) is to conduct a field survey before building a solution. The Gadepudi Village Survey revealed structural deficits in local administration reporting.

This module permanently anchors the field survey data into the live administrative dashboard. This allows the Panchayat to contrast **what villagers claimed during the survey** vs **what is actually being reported live**.

## Key Survey Metrics
*(As populated in the database `survey_data` and `survey_insights` tables)*

- **Target Location:** Gadepudi Village
- **Total Households Surveyed:** 500
- **Total Respondents:** 350 (70% coverage)
- **Survey Year:** 2026

## Most Common Problems Identified (Baseline)
During the manual physical survey, the following major issues were flagged by respondents:

| Category | Description | Affected Households | Percentage | Severity |
|----------|-------------|---------------------|------------|----------|
| Drainage Problems | Open drains causing mosquito breeding | 210 | 60% | Critical |
| Water Supply | Irregular drinking water supply | 120 | 34% | High |
| Streetlights | Broken lights causing safety issues at night | 85 | 24% | Medium |
| Roads | Potholes on the main transit road | 60 | 17% | Medium |

*(Note: Households could select multiple issues)*

## Dashboard Integration
The React Admin Dashboard features a dedicated `/survey` route.
This page fetches the baseline data from the `/admin/survey-insights` API and displays it using graphical progress bars, severity badges, and affected household counts.

**Utility for Authorities:**
If the live complaint dashboard suddenly shows 100 "Water Supply" complaints, the administration can look at the Survey Insights to realize this was a known "High" severity issue during the baseline survey, indicating that previous temporary fixes failed and a permanent infrastructure upgrade is required.
