# Backup & Restore

This runbook documents how to trigger, observe, and troubleshoot database backups for HHH across dev and production-like environments.

Scope
- Endpoints covered: /api/v1/backups/{trigger,logs,stats}
- Auth: Super Admin required for all backup endpoints
- CSRF: Required for POST /trigger
- Cookies: httpOnly cookies used; clients must send credentials

Prerequisites
- Super Admin user and valid session cookies (hhh_at, hhh_rt)
- CSRF cookie hhh_csrf and header X-CSRF-Token for mutating requests
- Dev DB defaults to SQLite; production should use Postgres

Endpoints

1) Trigger Backup (POST)
- Path: /api/v1/backups/trigger
- Auth: Super Admin
- CSRF: Required
- Response 200 example:
  {
    "success": true,
    "message": "Backup completed successfully",
    "backup_file": "backup_20250101_120000.sql",
    "backup_size": 123456,
    "backup_id": "uuid"
  }
- Errors:
  - 403: { "detail": "Super Admin access required", "error": { "code": "ERR_SUPERADMIN_REQUIRED", ... } }
  - 500: { "detail": "Backup failed: <details>", "error": { "code": "ERR_BACKUP_FAILED", ... } }

2) Backup Logs (GET)
- Path: /api/v1/backups/logs?limit=50&offset=0
- Auth: Super Admin
- Response 200 example:
  [
    {
      "id": "uuid",
      "backup_file": "backup_20250101_120000.sql",
      "backup_size": 123456,
      "status": "BackupStatus.SUCCESS",
      "created_at": "2025-01-01T12:00:00+00:00"
    }
  ]

3) Backup Stats (GET)
- Path: /api/v1/backups/stats
- Auth: Super Admin
- Response 200 example:
  {
    "total_backups": 10,
    "successful_backups": 9,
    "failed_backups": 1,
    "total_backup_size": 10485760,
    "latest_backup": {
      "file": "backup_20250101_120000.sql",
      "size": 123456,
      "created_at": "2025-01-01T12:00:00+00:00"
    }
  }

CSRF and Cookies – curl Examples

1) Obtain CSRF cookie (sets hhh_csrf)
curl -i -c cookies.txt "{{base_url}}/api/v1/auth/health"

2) Extract CSRF and trigger backup (Super Admin only)
CSRF=$(grep hhh_csrf cookies.txt | awk '{print $7}')
curl -i -b cookies.txt -c cookies.txt \
  -H "X-CSRF-Token: $CSRF" \
  -X POST "{{base_url}}/api/v1/backups/trigger"

3) Get logs
curl -i -b cookies.txt "{{base_url}}/api/v1/backups/logs?limit=50&offset=0"

4) Get stats
curl -i -b cookies.txt "{{base_url}}/api/v1/backups/stats"

Postman Collection
- Use docs/HHH_API.postman_collection.json
- Variables:
  - base_url (default http://localhost:8000)
  - csrf_token (set to value of hhh_csrf cookie)
- Requests included:
  - Backups – Trigger (POST, CSRF header required)
  - Backups – Logs (GET)
  - Backups – Stats (GET)
- Flow:
  1) Run Auth – Health to set CSRF cookie in your browser-client
  2) Set csrf_token variable to cookie value
  3) Execute Backups endpoints

Dev vs Production Behavior
- Dev (SQLite – default):
  - Backup uses file copy fallback to /tmp/backup_YYYYMMDD_HHMMSS.sql
  - File is removed after logging (simulates upload to cloud)
  - Logs recorded in backup_log table with status SUCCESS/FAILED
- Production (Postgres – recommended):
  - Uses pg_dump with flags: --no-owner --no-privileges --clean --if-exists --format=custom
  - Ensure pg_dump is available on the server/runner
  - Replace local file cleanup with upload to cloud storage in services/backup.py when integrating storage

Troubleshooting

Symptom: 403 Super Admin access required
- Ensure the requesting user has role SUPER_ADMIN
- Verify application session cookies are present (hhh_at/hhh_rt)
- If using curl, cookies.txt must contain a valid session

Symptom: 403 CSRF validation failed (on POST /trigger)
- Ensure X-CSRF-Token header is set and matches hhh_csrf cookie
- Fetch CSRF first via /api/v1/auth/health

Symptom: 500 Backup failed
- Check server logs for underlying error (e.g., pg_dump not installed, permission denied on /tmp)
- For SQLite dev:
  - Verify DB path exists and is readable
  - Ensure /tmp is writable

Symptom: Stats or Logs return 500
- Check DB connectivity and that migrations are up to date (alembic upgrade head)
- Inspect BackupLog table for inconsistent rows

Operational Notes
- CI runs alembic upgrade head to ensure migrations apply cleanly
- Optional security checks (ruff, pip-audit) are executed in CI and allowed to continue-on-error
- For real deployments, integrate cloud storage upload in services/backup.py and update this doc

Restore (Future Work)
- Dev (SQLite): Restore by copying a .sql/.db snapshot back into place
- Postgres: Use pg_restore for custom format files
- Detailed restore steps, environment-specific credentials, and safety checks will be added alongside storage integration

Contact and Ownership
- Backup service: backend/src/services/backup.py
- REST endpoints: backend/src/api/rest/v1/backup.py
- Models: backend/src/models/backup_log.py
- For incidents, capture logs and failing payloads (redact sensitive info) and open a ticket with steps to reproduce
