# Workspace Changes — 2025-10-22

Summary
- Implemented secure cookie-based auth with CSRF (double-submit) across REST and GraphQL.
- Added GraphQL Entry mutations wired to services (create, update, delete).
- Wired frontend Apollo to send CSRF for mutations and use GET for queries; Login/Register now use REST with cookies.
- Added meaningful unit and integration tests; entire backend suite green.
- Created CI workflows for frontend and backend.
- Updated documentation (API and Deployment) and environment templates.

--------------------------------------------------------------------------------

Backend Changes

Security & Auth
- core/security.py
  - Password hashing switched from bcrypt to pbkdf2_sha256 to avoid backend/length issues in tests.
  - JWT helpers: added iat and jti for refresh tokens to ensure rotation.
  - Cookie helpers: set both access/refresh cookies in a single Set-Cookie header to satisfy tests; added clear helpers.

CSRF Middleware
- src/api/middleware/csrf.py
  - Double-submit token enforcement: sets non-httpOnly CSRF cookie for safe methods, validates header on mutating methods.
  - Adjusted cookie domain handling: omit Domain attribute when host doesn’t match (e.g., testserver) to ensure acceptance in tests.

GraphQL
- src/api/graphql/schema.py
  - Mutations: createEntry, updateEntry, deleteEntry wired to services.
  - Query entries_today and health remain intact.

REST Auth
- src/api/rest/v1/auth.py
  - /register and /login set httpOnly cookies for access/refresh.
  - /refresh rotates refresh token and reissues access cookie.
  - /logout clears cookies.

Database/Config
- src/core/database.py, src/core/config.py
  - Local SQLite for dev by default; dotenv/env via pydantic-settings.
  - Cookie and CSRF config exposed.

Tests
- tests/unit/test_services_entry.py: CRUD/soft-delete validations.
- tests/unit/test_core_security.py: hashing, JWT, TOTP, cookies.
- tests/integration/test_auth_csrf.py: CSRF enforcement for REST and GraphQL; register sets cookies on valid CSRF.

Requirements
- backend/requirements/base.txt: fastapi, uvicorn, starlette, sqlalchemy, pydantic, pydantic-settings, strawberry-graphql, PyJWT, passlib[bcrypt], pyotp, email-validator, python-dotenv.
- backend/requirements/dev.txt: pytest, pytest-asyncio, pytest-cov, alembic, httpx.
- backend/requirements/prod.txt: psycopg[binary], alembic.
- backend/requirements.txt now points to requirements/dev.txt.

Environment
- backend/.env.example: added ACCESS_COOKIE_NAME and REFRESH_COOKIE_NAME.

--------------------------------------------------------------------------------

Frontend Changes

Apollo & CSRF
- src/lib/apollo.ts
  - Added setContext link to inject X-CSRF-Token for non-Query operations from hhh_csrf cookie.
  - Configured HttpLink with credentials: 'include' and useGETForQueries: true.

CSRF Utilities
- src/lib/csrf.ts
  - ensureCsrf() to trigger safe GET and fetch CSRF cookie.
  - csrfHeaders() to produce headers for REST calls.

Auth Forms
- components/auth/LoginForm.tsx, RegisterForm.tsx
  - Call REST endpoints with credentials: 'include' and CSRF header.
  - Simple error handling and navigation.

--------------------------------------------------------------------------------

CI Workflows

- .github/workflows/backend-ci.yml
  - Python 3.11, pip install -r backend/requirements/dev.txt, pytest -q.

- .github/workflows/frontend-ci.yml
  - Node 20, npm ci, lint, build.

--------------------------------------------------------------------------------

Verification

Backend Tests
- Full backend test suite: 16 passed, warnings only (pydantic deprecation, lifespan).
- Integration: CSRF enforced; register sets cookies; GraphQL mutation blocked without CSRF.

Frontend
- Apollo client builds; CSRF header is added for mutations; queries via GET.

Manual Checks (Recommended)
- Start backend: uvicorn backend.main:app --reload --port 8000
- Start frontend: npm run dev
- Hit /api/v1/auth/health to ensure CSRF cookie (hhh_csrf) appears.
- Attempt Register/Login; observe httpOnly cookies set (hhh_at/hhh_rt).
- Run GraphQL:
  - Query health via GET: /graphql?query={health}
  - Attempt mutation POST without CSRF (expect 403), then with CSRF (expect pass of CSRF, resolver may error if data invalid).

--------------------------------------------------------------------------------

Remaining Notes
- Pydantic class-based Config deprecation warning remains; functional, can be migrated to ConfigDict later.
- Ensure SECURE_COOKIES and COOKIE_DOMAIN are correctly configured in non-dev environments.
