# HHH – Admin Usage Guide
Last updated: 2025-10-26

This guide explains how to use the Admin page to trigger database backups, view backup logs and stats, and inspect audit logs.

Overview
- Route: /admin
- Purpose: Administration console for backup management and audit visibility
- Data sources:
  - REST (cookie auth + CSRF):
    - POST ${API_URL}/api/v1/backups/trigger
    - GET ${API_URL}/api/v1/backups/logs
    - GET ${API_URL}/api/v1/backups/stats
  - GraphQL:
    - query AuditLogs(limit, offset)
- Permissions:
  - Backups: Super Admin
  - Audit Logs: Super Admin
  - Analytics section: Uses existing GraphQL queries (Global requires Super Admin, Group requires membership)

Prerequisites
- Backend running on http://localhost:8000
- Frontend running on http://localhost:5173
- frontend/.env contains:
  VITE_API_URL=http://localhost:8000
- You are logged in with a Super Admin account (required for backups and audit logs)
- Cookies enabled; CSRF token will be fetched automatically when needed

Sections

1) Backup Management
- Trigger Backup:
  - Click “Trigger Backup”
  - The app performs POST /api/v1/backups/trigger with credentials (cookies) and X-CSRF-Token
  - On success, a confirmation message displays and logs/stats refresh
- Refresh:
  - Click “Refresh” to GET /logs and /stats again
- Stats:
  - Total backups, successful/failed counts, aggregate size, and latest backup details
- Logs:
  - Table of recent backup operations with time, filename, size, and status

2) Audit Logs
- Displays latest audit log entries via GraphQL
- Columns: When, User, Action, Resource, IP
- Use “Refresh” to refetch data

Accessibility & Responsiveness
- Tables include captions and proper table headers
- Sections indicate busy state with aria-busy when loading
- Layout is responsive (Tailwind grid and utility classes)

Troubleshooting
- 401/403 errors:
  - Ensure your user is Super Admin
  - Check backend CORS and cookie settings (backend/.env -> CORS_ALLOW_ORIGINS, COOKIE_DOMAIN, SECURE_COOKIES)
- CSRF issues:
  - Ensure the CSRF cookie (hhh_csrf) is present; the app auto-fetches it via a safe GET when missing
- GraphQL errors:
  - See Apollo error logging (src/lib/apollo.ts)
  - Confirm VITE_API_URL matches backend origin
- Empty tables:
  - No backups performed yet or no audit events to show

Screenshots (placeholders)
- Admin – Backups: ./images/admin-backups.png
- Admin – Audit Logs: ./images/admin-audit-logs.png

Notes
- Backup storage in development may use local file copy (SQLite) or pg_dump (Postgres), per backend configuration
- In production, backups should be uploaded to object storage; current service cleans up temp files locally
