# HHH – Priority Checklist (Backend, Frontend, Security, Docs, CI/CD)
Last updated: 2025-10-27

Sources: docs/API_IMPLEMENTATION_TRACKING.md, docs/FRONTEND_TASKS_TRACKER.md, docs/commits/*, current code.

Legend: P0 = Critical/Blocking, P1 = High, P2 = Nice-to-have

Quick refs
- GraphQL: backend/src/api/graphql/schema.py
- REST: backend/src/api/rest/v1/{analytics.py, backup.py, gdpr.py, roles.py, auth.py}
- Services: backend/src/services/{analytics.py, backup.py, gdpr.py, entry.py, group.py, notification.py, role.py}
- Frontend: frontend/src/{pages, components, lib/apollo.ts}
- Tests: backend/tests/{unit, integration}
- Tailwind/Vite: frontend/postcss.config.js, frontend/tailwind.config.js, frontend/vite.config.ts, frontend/src/index.css

## Next Sprint Plan (Oct 27, 2025)

P1 – High priority
- [ ] Standardize error envelopes (REST + GraphQL)
  - [ ] Define error envelope schema in docs/API.md: { code, message, details?, correlationId?, path?, timestamp }
  - [ ] Implement FastAPI exception handlers mapping backend/src/core/exceptions.py to envelope
  - [ ] Implement GraphQL error formatter to return envelope via extensions
  - [ ] Add tests for Unauthorized, Forbidden, ValidationError, NotFound (REST + GQL)
- [ ] Expand RBAC negative tests (analytics + audit logs)
  - [ ] GraphQL: globalAnalytics (Super Admin only); groupAnalytics (member/admin only); auditLogs (Super Admin only)
  - [ ] REST: /api/v1/analytics/global (Super Admin), /api/v1/analytics/group/:id (member/admin)
  - [ ] Negative cases cover unauthenticated, wrong role, wrong group
- [ ] Verify GDPR export completeness and delete semantics; add integration tests
  - [ ] Export includes: user profile, entries, group memberships, notifications (policy on audit logs)
  - [ ] Delete semantics: soft-delete/anonymization where required; no orphaned PII
  - [ ] Tests for export and delete flows; update docs/API.md
- [ ] API surface completeness in docs + Postman
  - [ ] API.md: list full GraphQL operations (me, myGroups, group, groups, myEntries, dailyProgress, streak, myNotifications, groupAnalytics, globalAnalytics, auditLogs, role management, GDPR, backups) with auth/role/CSRF notes
  - [ ] Postman: add roles (promote/demote), analytics (group/global), GDPR (export/delete), audit logs
- [ ] Rate limiting docs/tests/env config
  - [ ] Document 429 envelope and headers
  - [ ] Env-based configuration (limits/windows) and examples
  - [ ] Integration tests

P2 – Nice-to-have
- [x] REST audit logs endpoint implemented (GET /api/v1/audit/logs)
  - [ ] Document endpoint in docs/API.md and add to Postman collection
  - [ ] Add integration tests and RBAC negative tests
- [x] Rate limits implemented for GDPR export and backup trigger
  - [ ] Document 429 envelope and any headers in docs/API.md
  - [ ] Env configuration (limits/windows) with examples
  - [ ] Integration tests to verify 429 behavior

Acceptance for this sprint
- [ ] All above items implemented or tested as applicable
- [ ] Updated docs/API.md and Postman collection
- [ ] CI green on backend-ci and frontend-ci

## P0 – Critical
Backend
- [x] Enforce group access on REST GET /api/v1/analytics/group/{group_id} (member or group admin) in backend/src/api/rest/v1/analytics.py
- [x] Verify Super Admin enforcement on global/admin ops (globalAnalytics, flagEntry, unflagEntry, backup trigger/logs/stats) across GraphQL + REST
- [x] Stabilize CSRF + 2FA tests; ensure integration tests are active and passing
- [x] Add tests: Analytics (services + REST + GQL), Backup (trigger/logs/stats + GQL triggerBackup), GDPR (exportMyData/deleteMyAccount), Audit logs query

Frontendpr
- [x] Wire Dashboard components to live data with proper states:
  - components/dashboard/Analytics.tsx → groupAnalytics/globalAnalytics
  - components/dashboard/StreakCounter.tsx → Query.streak
  - components/dashboard/ProgressBar.tsx → Query.dailyProgress
  - Add loading/error/empty states per rules
- [x] QA gates: npm run lint && npm run build clean (fix TS/ESLint issues)

Documentation
- [x] Align docs/API_IMPLEMENTATION_TRACKING.md and docs/API.md with current code (Phase 6/7 implemented; list endpoints, types, auth constraints)

Ops
- [ ] Automated nightly backups schedule + PITR (production)
  - [ ] Nightly schedule (00:00 UTC) via cron/GitHub Actions calling POST /api/v1/backups/trigger with Super Admin credentials
  - [ ] PITR design for Postgres (WAL archiving to object storage; retention policy)
  - [ ] Update docs/ops/BACKUP_RESTORE.md with schedule, secrets, storage, retention, alerting, and restore drill steps

## P1 – High
Frontend
- [x] Complete loading/error for auth (Login/Register/2FA); ensure CSRF via lib/csrf.ts on REST
- [x] Ensure ErrorBoundary wraps routes and shows actionable messages
- [x] Tests: Dashboard analytics (mock Apollo), Groups flows (happy path), Auth forms (CSRF + cookies)
- [x] Tailwind v4 baseline verification:
  - [x] postcss.config.js uses {'@tailwindcss/postcss': {}}
  - [x] src/index.css has @import "tailwindcss" and visible body baseline styles
  - [x] tailwind.config.js content includes ./index.html and ./src/**/*.{js,ts,jsx,tsx}
  - [x] vite.config.ts sets css.postcss = './postcss.config.js'
- [x] Admin UI: analytics views, audit logs table, backup trigger/logs/stats wiring
- [x] Dashboard lists wired to live data with loading/empty/error states
- [x] Increase FE test coverage for Dashboard, Groups, Auth; validate Jest/RTL setup

Backend
- [x] Strawberry type-safety: ensure no dict passthroughs; resolvers return @strawberry.type instances consistently
- [x] Add DataLoader or preload patterns to avoid N+1 (e.g., Group.members → User)
- [ ] Standardize error envelopes
- [x] Add audit logging for admin failure paths
- [ ] Expand RBAC tests for analytics (GraphQL + REST) and auditLogs (negative cases)
- [x] Document analytics response shapes and parameters in docs/API.md with examples
- [ ] Verify GDPR export dataset completeness and delete semantics; add integration tests

CI/CD
- [x] Ensure .github/workflows for FE/BE exist (added) and configured (FE: npm ci/lint/build; BE: pytest; alembic upgrade head; caches). Mark pipelines green once run in GitHub.
- [x] Add Alembic migration step (alembic upgrade head) against ephemeral DB in CI if not present
- [x] Add optional ruff/pip-audit security checks

Documentation
- [x] Update docs/API.md to include /api/v1/backups/stats and finalize analytics field shapes
- [x] Refresh docs/HHH_API.postman_collection.json with CSRF header, cookies, and new endpoints
- [x] Update docs/ops/BACKUP_RESTORE.md with stats usage and troubleshooting
- [ ] API surface completeness in docs + Postman
- [ ] Rate limiting docs/tests/env config

## P2 – Nice-to-have
- [x] Accessibility and responsiveness polish (aria labels, keyboard nav, responsive layouts)
- [x] Usage docs/screenshots for Admin and Dashboard
- [x] Verify .env.example completeness for new features (frontend and backend)
- [x] REST audit logs endpoint implemented (GET /api/v1/audit/logs)
  - [ ] Document endpoint in docs/API.md and add to Postman
  - [ ] Add integration tests and RBAC negative tests
- [x] Rate limits implemented for GDPR export and backup trigger
  - [ ] Document 429 envelope and any headers in docs/API.md
  - [ ] Env configuration (limits/windows) with examples
  - [ ] Integration tests to verify 429 behavior
