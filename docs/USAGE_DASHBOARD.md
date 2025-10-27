# HHH – Dashboard Usage Guide
Last updated: 2025-10-26

This guide explains how to use the Dashboard in the HHH app, including data sources, required permissions, UI states, and troubleshooting.

Overview
- Route: /dashboard
- Purpose: Daily overview with analytics, streak, and progress
- Data sources (GraphQL):
  - Query.globalAnalytics and groupAnalytics (components/dashboard/Analytics.tsx)
  - Query.streak (components/dashboard/StreakCounter.tsx)
  - Query.dailyProgress (components/dashboard/ProgressBar.tsx)
- Auth: Login required. Cookies are used for session auth. CSRF is handled on mutating requests; dashboard queries are reads.

Quick Start
1) Start backend (FastAPI + Strawberry GraphQL) on http://localhost:8000
2) Start frontend (Vite) on http://localhost:5173
3) Ensure frontend/.env contains:
   VITE_API_URL=http://localhost:8000
4) Visit http://localhost:5173/dashboard

Features
1) Analytics
   - Global analytics (Super Admin only) and group analytics (if member/admin of a group)
   - Shows daily/weekly/monthly aggregates per current implementation
   - Handles loading, empty, and error states per project rules

2) Streak Counter
   - Displays current streak (consecutive days) from Query.streak
   - Loading and empty states included

3) Daily Progress
   - Shows daily completion percentage from Query.dailyProgress
   - Visual progress bar with loading and empty states

Permissions
- Global analytics: Super Admin required
- Group analytics: Group member or group admin
- Streak and daily progress: Authenticated user

Troubleshooting
- 401/403 errors:
  - Ensure you are logged in and have the right role/permissions
  - Check backend CORS and cookies settings (backend/.env -> CORS_ALLOW_ORIGINS, SECURE_COOKIES, COOKIE_DOMAIN)
- GraphQL errors:
  - See frontend Apollo error logging (src/lib/apollo.ts errorLink)
  - Verify VITE_API_URL matches backend origin and credentials include is set
- Empty states:
  - Data may legitimately be empty (no entries yet). Check with seeded data.

Screenshots (placeholders)
- Dashboard Overview: ./images/dashboard-overview.png
- Analytics Widget: ./images/dashboard-analytics.png
- Streak + Progress: ./images/dashboard-streak-progress.png

Notes
- UI built with Tailwind v4; responsive across breakpoints
- Accessibility: components include proper aria- props, loading/empty/error states
- For contributing/testing details, see frontend/README.md and docs/FRONTEND_TASKS_TRACKER.md
