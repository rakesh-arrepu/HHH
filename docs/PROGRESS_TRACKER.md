# HHH – Consolidated Project Progress Tracker

Last updated: 2025-11-08 23:23 (Asia/Calcutta)

Sources used (most recent wins on conflicts):
- docs/PRIORITY_CHECKLIST.md (2025-10-27)
- docs/FRONTEND_TASKS_TRACKER.md (2025-10-23)
- docs/API_IMPLEMENTATION_TRACKING.md (2025-10-22)
- README.md, backend/README.md, docs/DEPLOYMENT.md

Scope: Single source of truth listing Completed vs Pending across Backend/GraphQL, Frontend, API/Docs, Security/Rate Limiting, Ops/Backups, CI/CD, DB/Migrations, Docker/Deployment, Testing/Quality. Items are de-duplicated and normalized.

--------------------------------------------------------------------------------

Backend & GraphQL

Completed
- RBAC enforcement: group analytics membership checks; Super Admin gating on global/admin ops (GraphQL + REST).
- CSRF + 2FA tests stabilized; integration tests active and passing.
- Tests added: Analytics (services + REST + GraphQL), Backup (trigger/logs/stats incl. GQL triggerBackup), GDPR (exportMyData/deleteMyAccount), Audit logs query.
- Strawberry type-safety across resolvers; no dict passthroughs.
- DataLoader/preload patterns added to avoid N+1 (e.g., Group.members → User).
- Admin failure-path audit logging added.
- Analytics response shapes documented in docs/API.md.
- Standardized error envelopes (REST + GraphQL): FastAPI exception handlers mapping to envelope schema { code, message, details?, correlationId?, path?, timestamp }; GraphQL errors with extensions; comprehensive tests for Unauthorized, Forbidden, ValidationError, NotFound.

Pending
- Expand RBAC negative tests (analytics + audit logs): unauthenticated, wrong role, wrong group.
- Verify GDPR export dataset completeness and delete semantics; add integration tests and update docs/API.md.

--------------------------------------------------------------------------------

Frontend (Vite + React + TS + Tailwind v4 + Apollo)

Completed
- Routing/core layout in App.tsx with 404 fallback; Global ErrorBoundary across routes.
- Main pages scaffolded and routed (Dashboard, Groups, Profile, Admin, Auth).
- Apollo client configured (`src/lib/apollo.ts`) and ApolloProvider wrap.
- Groups flows wired to GraphQL with loading/error/empty states.
- Dashboard components wired to live data; lists with loading/error/empty states.
- Auth flows loading/error done; CSRF wiring via `lib/csrf.ts`.
- Tailwind v4 baseline verified:
  - postcss.config.js uses {'@tailwindcss/postcss': {}}.
  - src/index.css has `@import "tailwindcss";` and visible body baseline styles.
  - tailwind.config.js content includes ./index.html and ./src/**/*.{js,ts,jsx,tsx}.
  - vite.config.ts sets `css.postcss = './postcss.config.js'`.
- Lint/build clean (QA gates).
- Admin UI: analytics views, audit logs table, backup trigger/logs/stats.
- Tests baseline: Dashboard, Groups, Auth (Jest/RTL).
- Accessibility/responsive polish.
- Hygiene maintenance: removed unused components (Test.tsx), hooks (useNotifications.ts), pages (SignUp.tsx), utils (date.ts, timezone.ts), and empty directories.

Pending
- No critical FE blockers in latest priority doc.
- Keep hygiene backlog open: import hygiene, remove unused code, keep docs aligned with UI/API changes.

--------------------------------------------------------------------------------

API Surface & Documentation

Completed
- APIs implemented: 40/40, Phases 1–7 (per API_IMPLEMENTATION_TRACKING.md).
- docs/API.md updated with /api/v1/backups/stats and finalized analytics field shapes.
- Postman collection refreshed with CSRF header, cookies, and new endpoints.

Pending
- API surface completeness in docs + Postman:
  - Enumerate all GraphQL operations (me, myGroups, group, groups, myEntries, dailyProgress, streak, myNotifications, groupAnalytics, globalAnalytics, auditLogs, role management, GDPR, backups) with auth/role/CSRF notes.
  - Postman: add roles (promote/demote), analytics (group/global), GDPR (export/delete), audit logs.
- Document REST audit logs endpoint in docs/API.md and add to Postman.

--------------------------------------------------------------------------------

Security, Rate Limiting, and Compliance

Completed
- Rate limits implemented for GDPR export and backup trigger.

Pending
- Rate limiting docs/tests/env config:
  - Document 429 envelope and headers.
  - Provide env-based configuration examples.
  - Add integration tests to verify 429 behavior.
- GDPR export/delete verification and tests (see Backend pending).

--------------------------------------------------------------------------------

Operations, Backups, and PITR

Completed
- Backup features implemented; stats usage and troubleshooting added to docs.

Pending
- Nightly backups schedule + PITR (production):
  - Nightly schedule (00:00 UTC) via cron/GitHub Actions calling POST /api/v1/backups/trigger with Super Admin credentials.
  - PITR design for Postgres (WAL archiving to object storage; retention policy).
  - Update docs/ops/BACKUP_RESTORE.md with schedule, secrets, storage, retention, alerting, and restore drill steps.

--------------------------------------------------------------------------------

CI/CD

Completed
- .github/workflows for FE/BE configured (FE: npm ci/lint/build; BE: pytest; alembic upgrade head; caches).
- Alembic migration step integrated in CI (upgrade head against ephemeral DB).
- Optional ruff/pip-audit security checks added.

Pending
- Sprint acceptance gate: CI green on backend-ci and frontend-ci (confirm latest runs).
- Housekeeping: ensure workflows exist in repo default branch and last run is green.

--------------------------------------------------------------------------------

Database & Migrations

Completed
- Alembic migration process established; step present in CI and docs.

Pending
- None explicitly flagged. Policy: each schema change must have an Alembic migration + tests + docs updates.

--------------------------------------------------------------------------------

Docker & Deployment

Completed
- Dev/prod compose files present; deployment guidance in docs/DEPLOYMENT.md (envs/CORS/cookies/security/CI).

Pending
- Ensure production configs:
  - Secure cookies true, exact CORS origins, HTTPS via reverse proxy.
  - Restrict GraphQL introspection where required by environment.
  - Secrets injected via env/secrets manager (not in images).

--------------------------------------------------------------------------------

Testing & Quality

Completed
- Backend: unit + integration coverage for Auth, Analytics, Backup, GDPR, CSRF flows.
- Frontend: Jest/RTL baseline for Dashboard, Groups, Auth.
- Lint/build pass locally.
- Error envelope tests: comprehensive REST + GraphQL error handling tests implemented and passing.
- RBAC negative tests: comprehensive coverage for analytics and audit logs (unauthenticated, wrong role, wrong group scenarios).

Pending
- Rate limit integration tests.

--------------------------------------------------------------------------------

Next Steps – Execution Order

1) Error envelope standardization end-to-end (FastAPI handlers + GraphQL formatter + tests + docs).
2) Expand RBAC negative tests for analytics and audit logs (REST + GraphQL).
3) GDPR export/delete verification (dataset completeness + semantics) with integration tests and docs.
4) Rate limiting documentation + env examples + 429 integration tests.
5) Automate nightly backups and define PITR strategy; update ops docs.
6) API surface/Postman completeness pass; include roles/analytics/GDPR/audit logs with auth/CSRF notes.
7) Sprint acceptance: ensure CI green on FE/BE and capture evidence.

--------------------------------------------------------------------------------

Acceptance Checklist (Sprint)

- [x] Error envelopes standardized and tested (REST + GQL).
- [x] RBAC negative tests expanded (analytics, audit logs).
- [x] GDPR export/delete verified with integration tests and docs updated.
- [ ] Rate limiting docs and integration tests complete.
- [ ] Nightly backups schedule live; PITR design documented.
- [x] API surface completeness in docs + Postman.
- [ ] CI green on backend-ci and frontend-ci.

## Pending Work Checklists by Section

Backend & GraphQL
- [x] Error envelopes standardized end-to-end
  - [x] Define envelope schema in docs/API.md: { code, message, details?, correlationId?, path?, timestamp }
  - [x] Implement FastAPI exception handlers mapping backend/src/core/exceptions.py → standardized envelope
  - [x] Implement GraphQL error formatter to surface envelope via extensions
  - [x] Add tests: Unauthorized, Forbidden, ValidationError, NotFound (REST + GraphQL)
  - [x] Update docs/API.md with envelope spec and examples
- [x] RBAC negative tests expanded
  - [x] GraphQL: negative tests for groupAnalytics (member/admin only), globalAnalytics (Super Admin only), auditLogs (Super Admin only)
  - [x] REST: negative tests for /api/v1/analytics/global (Super Admin) and /api/v1/analytics/group/:id (member/admin)
  - [x] Cover unauthenticated, wrong role, wrong group scenarios
- [x] GDPR export/delete verification
  - [x] Export includes: user profile, entries, group memberships, notifications (policy on audit logs)
  - [x] Delete semantics: soft-delete/anonymization where required; no orphaned PII
  - [x] Integration tests for export and delete flows
  - [x] Update docs/API.md with datasets and delete behavior

Frontend (Vite + React + TS + Tailwind v4 + Apollo)
- [x] Hygiene/maintenance backlog
  - [x] Review import hygiene across components/pages
  - [x] Remove unused code and dead files
  - [x] Update docs for new UI/API changes as they land

API Surface & Documentation
- [x] Enumerate all GraphQL operations in docs/API.md with auth/role/CSRF notes
  - [x] me
  - [x] myGroups
  - [x] group
  - [x] groups
  - [x] myEntries
  - [x] dailyProgress
  - [x] streak
  - [x] myNotifications
  - [x] groupAnalytics
  - [x] globalAnalytics
  - [x] auditLogs
  - [x] role management (promote/demote)
  - [x] GDPR (export/delete)
  - [x] backups (trigger/logs/stats)
- [x] Postman collection completeness
  - [x] Roles: promote/demote
  - [x] Analytics: group/global
  - [x] GDPR: export/delete
  - [x] Audit logs
- [x] Document REST audit logs endpoint in docs/API.md and add to Postman

Security, Rate Limiting, and Compliance
- [ ] Rate limiting documentation and tests
  - [ ] Document 429 envelope and any relevant headers
  - [ ] Provide env-based configuration examples
  - [ ] Add integration tests verifying 429 behavior
- [ ] GDPR export/delete verification (see Backend & GraphQL)

Operations, Backups, and PITR
- [ ] Nightly backups automation (production)
  - [ ] GitHub Actions/cron at 00:00 UTC calling POST /api/v1/backups/trigger
  - [ ] Use Super Admin credentials stored securely as repo/org secrets
- [ ] PITR design for Postgres
  - [ ] Enable WAL archiving to object storage
  - [ ] Define retention policy and storage lifecycle rules
- [ ] Update docs/ops/BACKUP_RESTORE.md
  - [ ] Nightly schedule and triggering mechanism
  - [ ] Secrets management and storage location
  - [ ] Retention policy and alerting
  - [ ] Restore drill steps and validation checklist

CI/CD
- [ ] Confirm latest runs are green on backend-ci and frontend-ci
- [ ] Ensure workflows exist on default branch and caches function correctly
- [ ] Capture evidence (links/screenshots) in PR or release notes

Database & Migrations
- [ ] No pending items currently
  - [ ] Enforce policy: every schema change has an Alembic migration + tests + docs updates

Docker & Deployment
- [ ] Production configuration hardening
  - [ ] SECURE_COOKIES=true in prod and cookie domain set correctly
  - [ ] Exact CORS origins (no wildcard with credentials)
  - [ ] HTTPS via reverse proxy; disable GraphQL introspection where required
  - [ ] Secrets provided via env/secrets manager; not baked into images

Testing & Quality
- [ ] Expand RBAC negative tests (analytics, audit logs)
- [ ] Add rate limit integration tests

--------------------------------------------------------------------------------

Maintenance Notes

- Update this tracker when completing items; keep bullets concise and actionable.
- Prefer linking to PRs or commits in future updates for traceability.
- When conflicts arise, prefer the most recent dated doc as primary source and reconcile here.

## Minimal Folder Analysis (Based on code review on 03/01/2026)

### Completed in Minimal

- Basic user authentication (register, login, logout, get me) using session cookies
- Group management: create group, list groups, list members, add member by email, remove member
- Entry management: get entries for group and date, create or update entry for section (health, happiness, hela)
- Analytics: streak calculation for group, history for last 30 days with completed sections
- Frontend: Routing for dashboard, history, groups, login, register
- Dashboard UI: Group selection, entry cards for sections, save entries, streak display, progress bar
- History UI: Group selection, stats (complete/partial days, rate), 30-day calendar grid with color coding
- API client in frontend for all endpoints
- Database models for users, groups, group_members, entries
- FastAPI app with CORS configuration

### Pending in Minimal (inferred from code and missing features)

- CSRF protection (configured but not implemented in code)
- 2FA (mentioned in comment but not implemented)
- Error standardization and envelopes
- RBAC and roles
- Admin interfaces
- Notifications
- Global analytics
- GDPR features (export/delete data)
- Backups
- Rate limiting
- Testing (no tests in minimal)
- GraphQL (using REST)
- Production configurations (secure cookies, etc., partially there)
- And other advanced features from main project
