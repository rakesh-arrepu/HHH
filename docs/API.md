# API

This document describes the backend API: REST auth endpoints and the GraphQL schema including CSRF and cookie semantics.

Base URL
- Local development: http://localhost:8000
- GraphQL endpoint: /graphql
- REST base (auth): /api/v1/auth

Security Overview
- Session cookies:
  - Access: ACCESS_COOKIE_NAME (default hhh_at) – short-lived, httpOnly, SameSite=lax, Secure in prod
  - Refresh: REFRESH_COOKIE_NAME (default hhh_rt) – longer-lived, httpOnly, SameSite=lax, Secure in prod
- CSRF:
  - CSRF cookie: CSRF_COOKIE_NAME (default hhh_csrf) – non-httpOnly, readable by JS
  - Header required for mutating methods (POST/PUT/PATCH/DELETE): CSRF_HEADER_NAME (default X-CSRF-Token)
  - Safe methods (GET/HEAD/OPTIONS) do not require CSRF header
- CORS:
  - Credentials enabled. Ensure origin allowlist includes your frontend DEV origin(s).

Error Response Format
- All API endpoints (REST + GraphQL) return standardized error envelopes:
  ```json
  {
    "code": "ERR_UNAUTHORIZED",
    "message": "Unauthorized",
    "details": {},
    "correlationId": "abc-123-def",
    "path": "/api/v1/auth/login",
    "timestamp": "2025-11-08T23:45:00.123456+00:00"
  }
  ```
- Common error codes: ERR_UNAUTHORIZED, ERR_FORBIDDEN, ERR_NOT_FOUND, ERR_VALIDATION, ERR_BAD_REQUEST
- GraphQL errors include this envelope in the `extensions` field

--------------------------------------------------------------------------------

REST: Auth Endpoints (/api/v1/auth)

Health
- GET /api/v1/auth/health
- Purpose: Liveness check. Also ensures a CSRF cookie is set for the client if missing.
- Response: { "status": "ok" }
- CSRF: Not required

Register
- POST /api/v1/auth/register
- Body:
  {
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe"
  }
- CSRF: Required – include X-CSRF-Token header matching hhh_csrf cookie
- Response:
  - 201 Created
  - Body:
    {
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "name": "John Doe"
      }
    }
  - Sets httpOnly cookies: hhh_at (access), hhh_rt (refresh)
- Errors:
  - 400/409 with detail message (validation/duplicate)

Login
- POST /api/v1/auth/login
- Body:
  {
    "email": "user@example.com",
    "password": "password123"
  }
- CSRF: Required – include X-CSRF-Token header matching hhh_csrf cookie
- Response:
  - 200 OK
  - Body:
    {
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "name": "John Doe"
      }
    }
  - Sets httpOnly cookies: hhh_at (access), hhh_rt (refresh)
- Errors:
  - 401 Invalid credentials

Refresh
- POST /api/v1/auth/refresh
- Body: none
- CSRF: Required – include X-CSRF-Token header matching hhh_csrf cookie
- Behavior: Reads refresh cookie, issues new access and refresh cookies (rotation)
- Response:
  - 200 OK
  - Body: { "status": "ok" }
- Errors:
  - 401 Missing/invalid refresh token

Logout
- POST /api/v1/auth/logout
- Body: none
- CSRF: Required – include X-CSRF-Token header
- Behavior: Clears access and refresh cookies
- Response: 204 No Content

Example: CSRF Flow with curl
1) Obtain CSRF cookie via health:
   curl -i -c cookies.txt http://localhost:8000/api/v1/auth/health

2) Extract CSRF value (hhh_csrf) from cookies.txt, then:
   CSRF=$(grep hhh_csrf cookies.txt | awk '{print $7}')
   curl -i -b cookies.txt -c cookies.txt \
     -H "Content-Type: application/json" \
     -H "X-CSRF-Token: $CSRF" \
     -d '{"email":"user@example.com","password":"password123","name":"User"}' \
     http://localhost:8000/api/v1/auth/register

--------------------------------------------------------------------------------

GraphQL API (/graphql)

Transport and CSRF
- Queries:
  - Use GET where possible (safe method, no CSRF header required)
- Mutations:
  - Use POST and MUST include CSRF header X-CSRF-Token whose value equals the hhh_csrf cookie
- Cookies:
  - Access/refresh cookies are sent with requests (credentials: include)

Schema Summary

Query
- health: String
  - Returns "ok" for liveness
- entries_today(user_id: String!, group_id: String): [Entry!]!
  - Returns today's non-deleted entries for a user (optionally scoped by group)

Types
- enum SectionType { Health, Happiness, Hela }
- type Entry {
    id: ID!
    user_id: String!
    group_id: String!
    section_type: SectionType!
    content: String!
    entry_date: Date!
    edit_count: Int!
    is_flagged: Boolean!
    flagged_reason: String
  }

Mutations
- createEntry(input: CreateEntryInput!): Entry!
- updateEntry(id: ID!, input: UpdateEntryInput!): Entry!
- deleteEntry(id: ID!): Boolean!

Inputs
- input CreateEntryInput {
    user_id: String!
    group_id: String!
    section_type: SectionType!
    content: String!
    entry_date: Date
  }
- input UpdateEntryInput {
    content: String
    section_type: SectionType
  }

Examples

Query health (GET):
- GET /graphql?query=%7B%20health%20%7D
- Response:
  {
    "data": { "health": "ok" }
  }

Query entries_today (GET):
- GET /graphql?query=query%20(%24uid%3A%20String!)%7B%20entries_today(user_id%3A%20%24uid)%7B%20id%20content%20section_type%20%7D%7D&variables=%7B%22uid%22%3A%22USER_ID%22%7D

Mutation createEntry (POST) – requires CSRF header:
- POST /graphql
- Headers:
  - Content-Type: application/json
  - X-CSRF-Token: <value_of_hhh_csrf_cookie>
- Body:
  {
    "query": "mutation ($input: CreateEntryInput!) { createEntry(input: $input) { id content section_type } }",
    "variables": {
      "input": {
        "user_id": "USER_ID",
        "group_id": "GROUP_ID",
        "section_type": "Health",
        "content": "Walked 5k steps"
      }
    }
  }

--------------------------------------------------------------------------------

Cookie & CSRF Details

Cookies
- ACCESS_COOKIE_NAME (default hhh_at): httpOnly; short-lived access token
- REFRESH_COOKIE_NAME (default hhh_rt): httpOnly; refresh token; rotated on refresh
- Flags:
  - SameSite=lax
  - Secure: true in production (SECURE_COOKIES=true) and false for dev
  - Domain:
    - COOKIE_DOMAIN is used in production (e.g., example.com)
    - For local tests (testserver), cookie domain may be omitted to ensure acceptance

CSRF
- Cookie: hhh_csrf (readable by JS)
- Header: X-CSRF-Token must equal cookie value for mutating requests
- SAFE_METHODS (GET/HEAD/OPTIONS) do not require CSRF

Errors
- 400/409 – Bad Request / Conflict
- 401 – Unauthorized (e.g., invalid credentials/refresh token)
- 403 – CSRF validation failed
- 5xx – Internal Server Error

--------------------------------------------------------------------------------

REST: Backup Endpoints (/api/v1/backups)

Notes
- All backup endpoints require Super Admin privileges.
- CSRF header (X-CSRF-Token) is required for POST /trigger.
- Cookies: Send credentials (httpOnly cookies) with requests.

Trigger Backup
- POST /api/v1/backups/trigger
- Headers:
  - X-CSRF-Token: <value_of_hhh_csrf_cookie>
- Response (200 OK):
  {
    "success": true,
    "message": "Backup completed successfully",
    "backup_file": "backup_20250101_120000.sql",
    "backup_size": 123456,
    "backup_id": "uuid"
  }
- Errors:
  - 403 { "code": "ERR_SUPERADMIN_REQUIRED", "message": "Super Admin access required", "details": {"endpoint": "trigger"}, "correlationId": "...", "path": "/api/v1/backups/trigger", "timestamp": "..." }
  - 500 { "code": "ERR_BACKUP_FAILED", "message": "Backup failed: <details>", "details": {"endpoint": "trigger"}, "correlationId": "...", "path": "/api/v1/backups/trigger", "timestamp": "..." }

Backup Logs
- GET /api/v1/backups/logs?limit=50&offset=0
- Response (200 OK):
  [
    {
      "id": "uuid",
      "backup_file": "backup_20250101_120000.sql",
      "backup_size": 123456,
      "status": "BackupStatus.SUCCESS",
      "created_at": "2025-01-01T12:00:00+00:00"
    }
  ]
- Errors:
  - 403 { "code": "ERR_SUPERADMIN_REQUIRED", "message": "Super Admin access required", "details": {"endpoint": "logs"}, "correlationId": "...", "path": "/api/v1/backups/logs", "timestamp": "..." }
  - 500 { "code": "ERR_BACKUP_LOGS_FAILED", "message": "Failed to retrieve backup logs: <details>", "details": {"endpoint": "logs"}, "correlationId": "...", "path": "/api/v1/backups/logs", "timestamp": "..." }

Backup Stats
- GET /api/v1/backups/stats
- Response (200 OK):
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
- Errors:
  - 403 { "code": "ERR_SUPERADMIN_REQUIRED", "message": "Super Admin access required", "details": {"endpoint": "stats"}, "correlationId": "...", "path": "/api/v1/backups/stats", "timestamp": "..." }
  - 500 { "code": "ERR_BACKUP_STATS_FAILED", "message": "Failed to retrieve backup stats: <details>", "details": {"endpoint": "stats"}, "correlationId": "...", "path": "/api/v1/backups/stats", "timestamp": "..." }

REST: Audit Logs Endpoints (/api/v1/audit)

Notes
- All audit log endpoints require Super Admin privileges.
- CSRF header (X-CSRF-Token) is required for POST operations (none currently).
- Cookies: Send credentials (httpOnly cookies) with requests.

Get Audit Logs
- GET /api/v1/audit/logs?limit=50&offset=0&userId=user123&action=login&resourceType=user
- Response (200 OK):
  ```json
  [
    {
      "id": "uuid",
      "user_id": "user123",
      "action": "login",
      "resource_type": "auth",
      "resource_id": "user123",
      "metadata": "{\"device\": \"mobile\"}",
      "ip_address": "192.168.1.1",
      "created_at": "2025-01-01T12:00:00+00:00"
    }
  ]
  ```
- Query Parameters:
  - `limit` (int, default 50, max 100): Number of logs to return
  - `offset` (int, default 0): Pagination offset
  - `userId` (string, optional): Filter by user ID
  - `action` (string, optional): Filter by action type
  - `resourceType` (string, optional): Filter by resource type
- Errors:
  - 403 { "code": "ERR_SUPERADMIN_REQUIRED", "message": "Super Admin access required", "details": {"endpoint": "audit.logs"}, "correlationId": "...", "path": "/api/v1/audit/logs", "timestamp": "..." }
  - 500 { "code": "ERR_AUDIT_LOGS_FAILED", "message": "Failed to retrieve audit logs: <details>", "details": {"endpoint": "audit.logs"}, "correlationId": "...", "path": "/api/v1/audit/logs", "timestamp": "..." }

--------------------------------------------------------------------------------

Analytics Response Shapes (GraphQL)

Group Analytics
- Query: groupAnalytics(groupId: String!, startDate?: Date, endDate?: Date): GroupAnalyticsResult
- Shape:
  {
    "group_id": "uuid",
    "period": { "start": "2025-01-01", "end": "2025-01-31" },
    "member_count": 12,
    "total_entries": 345,
    "active_users": 8,
    "avg_streak": 4.2,
    "daily_activity": [
      { "date": "2025-01-01", "entries": 12 }
    ]
  }

Global Analytics
- Query: globalAnalytics(startDate?: Date, endDate?: Date): GlobalAnalyticsResult (Super Admin only)
- Shape:
  {
    "period": { "start": "2025-01-01", "end": "2025-01-31" },
    "total_users": 120,
    "total_groups": 15,
    "total_entries": 1200,
    "new_users": 10,
    "active_users": 75,
    "active_groups": 9,
    "engagement_rate": 0.62
  }

GDPR Compliance Endpoints (/graphql)

Data Export
- GraphQL Mutation: exportMyData
- Purpose: Export all user data in GDPR-compliant JSON format
- Authentication: Required (user's own data only)
- Response:
  ```json
  {
    "success": true,
    "data": "{\"export_timestamp\": \"...\", \"user_profile\": {...}, \"entries\": [...], \"group_memberships\": [...], \"notifications\": [...], \"audit_logs\": [...], \"data_summary\": {...}}",
    "message": "Data exported successfully"
  }
  ```
- Exported Dataset:
  - User profile: id, email, name, role, timestamps, 2FA status
  - All entries: content, metadata, timestamps
  - Group memberships: group details, join dates, streaks
  - Notifications: all notification data
  - Audit logs: user activity history (retained for compliance)
  - Summary statistics

Account Deletion
- GraphQL Mutation: deleteMyAccount(confirm: Boolean!)
- Purpose: Soft delete user account and anonymize associated data per GDPR
- Authentication: Required (user's own account only)
- Requires explicit confirmation (confirm: true)
- Deletion Semantics:
  - User account: soft deleted, PII anonymized (email → deleted-{id}@anonymous.local, name → [DELETED USER])
  - Entries: soft deleted, content anonymized to [DELETED]
  - Group memberships: soft deleted
  - Notifications: soft deleted
  - Audit logs: retained but anonymized (PII removed, metadata updated for compliance tracking)
- Response:
  ```json
  {
    "success": true,
    "message": "Account soft-deleted and anonymized per GDPR. Processed X records. User data anonymized, audit logs retained for compliance."
  }
  ```
- Note: Deletion is irreversible for user data, but audit logs may be retained for legal/compliance purposes

GraphQL Operations Reference (/graphql)

All mutations require CSRF protection via X-CSRF-Token header. Queries are safe operations and do not require CSRF.

**Queries:**

- **health**: String
  - Auth: None required
  - CSRF: Not applicable (safe operation)
  - Returns server health status

- **me**: User
  - Auth: Any authenticated user
  - CSRF: Not applicable (safe operation)
  - Returns current user profile

- **myGroups**: [Group]
  - Auth: Any authenticated user
  - CSRF: Not applicable (safe operation)
  - Returns groups where user is a member

- **group(id: String!)**: Group
  - Auth: None required (public group info)
  - CSRF: Not applicable (safe operation)
  - Returns group details by ID

- **groups(limit?: Int, offset?: Int)**: [Group]
  - Auth: None required
  - CSRF: Not applicable (safe operation)
  - Returns paginated list of all groups

- **entries_today(user_id: String!, group_id?: String)**: [Entry]
  - Auth: None required (takes user_id as parameter)
  - CSRF: Not applicable (safe operation)
  - Returns today's entries for specified user

- **myEntries(groupId?: String, limit?: Int, offset?: Int)**: [Entry]
  - Auth: Any authenticated user (returns user's own entries)
  - CSRF: Not applicable (safe operation)
  - Returns paginated user's entries, optionally filtered by group

- **entry(id: String!)**: Entry
  - Auth: None required
  - CSRF: Not applicable (safe operation)
  - Returns entry details by ID

- **dailyProgress(date: Date!, groupId?: String)**: DailyProgress
  - Auth: Any authenticated user (user's own progress)
  - CSRF: Not applicable (safe operation)
  - Returns daily progress summary for authenticated user

- **streak(groupId?: String)**: Int
  - Auth: Any authenticated user (user's own streak)
  - CSRF: Not applicable (safe operation)
  - Returns current streak count for authenticated user

- **myNotifications(limit?: Int, offset?: Int)**: [Notification]
  - Auth: Any authenticated user (user's own notifications)
  - CSRF: Not applicable (safe operation)
  - Returns paginated user's notifications

- **groupAnalytics(groupId: String!, startDate?: Date, endDate?: Date)**: GroupAnalyticsResult
  - Auth: Group member or admin only
  - CSRF: Not applicable (safe operation)
  - Returns analytics for specified group (member/admin access required)

- **globalAnalytics(startDate?: Date, endDate?: Date)**: GlobalAnalyticsResult
  - Auth: Super Admin only
  - CSRF: Not applicable (safe operation)
  - Returns global system analytics (Super Admin required)

- **auditLogs(limit?: Int, offset?: Int, userId?: String, action?: String, resourceType?: String)**: [AuditLog]
  - Auth: Super Admin only
  - CSRF: Not applicable (safe operation)
  - Returns paginated audit logs (Super Admin required)

**Mutations:**

- **enable2fa**: String (provisioning URI)
  - Auth: Super Admin only
  - CSRF: Required
  - Enables 2FA for Super Admin account

- **verify2fa(totp_code: String!)**: Boolean
  - Auth: Super Admin only
  - CSRF: Required
  - Verifies 2FA TOTP code and enables 2FA

- **create_entry(input: CreateEntryInput!)**: Entry
  - Auth: None required (takes user_id in input)
  - CSRF: Required
  - Creates new entry

- **update_entry(id: String!, input: UpdateEntryInput!)**: Entry
  - Auth: None required
  - CSRF: Required
  - Updates existing entry

- **delete_entry(id: String!)**: Boolean
  - Auth: None required
  - CSRF: Required
  - Soft deletes entry

- **promoteToGroupAdmin(userId: String!, groupId: String!)**: MutationResponse
  - Auth: Group admin permissions required
  - CSRF: Required
  - Promotes user to group admin

- **demoteToUser(userId: String!, groupId: String!)**: MutationResponse
  - Auth: Group admin permissions required
  - CSRF: Required
  - Demotes user from group admin to regular member

- **softDeleteUser(userId: String!, confirm: Boolean!)**: MutationResponse
  - Auth: Super Admin only
  - CSRF: Required
  - Soft deletes user account (admin action on other users)

- **createGroup(name: String!, description?: String, timezone?: String)**: Group
  - Auth: Any authenticated user
  - CSRF: Required
  - Creates new group with user as admin

- **updateGroup(id: String!, name?: String, description?: String, timezone?: String)**: Group
  - Auth: Group admin permissions required
  - CSRF: Required
  - Updates group details

- **addGroupMember(groupId: String!, userId: String!)**: GroupMember
  - Auth: Group admin permissions required
  - CSRF: Required
  - Adds user to group

- **removeGroupMember(groupId: String!, userId: String!, confirm: Boolean!)**: MutationResponse
  - Auth: Group admin permissions required
  - CSRF: Required
  - Removes user from group

- **restoreEntry(id: String!)**: Entry
  - Auth: Entry owner permissions required
  - CSRF: Required
  - Restores soft-deleted entry

- **markNotificationRead(id: String!)**: Notification
  - Auth: User's own notification
  - CSRF: Required
  - Marks notification as read

- **markAllNotificationsRead**: MutationResponse
  - Auth: Any authenticated user
  - CSRF: Required
  - Marks all user's notifications as read

- **flagEntry(entryId: String!, reason: String!)**: Entry
  - Auth: Super Admin only
  - CSRF: Required
  - Flags entry for moderation

- **unflagEntry(entryId: String!)**: Entry
  - Auth: Super Admin only
  - CSRF: Required
  - Removes flag from entry

- **exportMyData**: ExportResult
  - Auth: Any authenticated user (user's own data)
  - CSRF: Required
  - Exports user's complete data for GDPR compliance

- **deleteMyAccount(confirm: Boolean!)**: MutationResponse
  - Auth: Any authenticated user (user's own account)
  - CSRF: Required
  - Soft deletes user's own account (GDPR right to erasure)

- **triggerBackup**: BackupResult
  - Auth: Super Admin only
  - CSRF: Required
  - Triggers database backup

- **signUp(input: SignUpInput!)**: SignUpPayload
  - Auth: None required
  - CSRF: Required
  - User registration

--------------------------------------------------------------------------------

Frontend Guidelines
- Apollo client:
  - Use credentials: 'include'
  - Use GET for queries
  - Attach X-CSRF-Token only for non-Query operations (from hhh_csrf cookie)
- REST calls (Login/Register/Refresh/Logout):
  - Use credentials: 'include'
  - Include X-CSRF-Token header for POST endpoints

--------------------------------------------------------------------------------

Notes
- Dev vs Prod:
  - Secure cookies and explicit COOKIE_DOMAIN should be used in production
  - CORS origins should be strictly controlled outside dev
- Migrations and DB:
  - In dev, SQLite may be used (default); in production Postgres is recommended
