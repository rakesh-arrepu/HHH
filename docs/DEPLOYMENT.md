# Deployment

This guide covers local development, environment configuration, production deployment, and CI for the HHH project.

Overview
- Frontend: Vite + React + TS (port 5173 by default)
- Backend: FastAPI + Strawberry GraphQL (port 8000 by default)
- DB: SQLite for local/dev by default; PostgreSQL recommended for production
- Auth: Cookie-based sessions (httpOnly access/refresh), CSRF protection (double-submit)
- GraphQL: Queries via GET, mutations via POST with CSRF header

Prerequisites
- Python 3.11
- Node.js 20.x and npm
- Recommended: virtualenv/pyenv
- Optional: Docker and docker-compose

Directory Layout (relevant)
- frontend/ – Vite app
- backend/ – FastAPI app
- docker/ – compose files
- docs/ – documentation

--------------------------------------------------------------------------------

Environment Variables

Frontend (Vite)
- File: frontend/.env.example
- Variables:
  - VITE_API_URL: Base URL for backend, default http://localhost:8000
- Usage:
  - Vite injects at build time; restart dev server after changes
  - Access via import.meta.env.VITE_API_URL

Backend (FastAPI)
- File: backend/.env.example
- Variables:
  - DATABASE_URL (e.g., sqlite:///./app.db for dev, or postgresql://user:pass@host:5432/db)
  - ENVIRONMENT (development|staging|production)
  - DEBUG (true|false)
  - JWT_SECRET, JWT_ALGORITHM (HS256), ACCESS_TOKEN_EXP_MINUTES (e.g., 15), REFRESH_TOKEN_EXP_DAYS (e.g., 7)
  - TOTP_ISSUER (e.g., DailyTracker)
  - CORS_ALLOW_ORIGINS (comma-separated, e.g., http://localhost:5173,http://localhost:5174)
  - CSRF_COOKIE_NAME (default hhh_csrf)
  - CSRF_HEADER_NAME (default X-CSRF-Token)
  - COOKIE_DOMAIN (e.g., localhost for dev, example.com for prod)
  - SECURE_COOKIES (false for dev, true for prod)
  - ACCESS_COOKIE_NAME (default hhh_at)
  - REFRESH_COOKIE_NAME (default hhh_rt)

Security Defaults
- Cookies:
  - httpOnly for session JWTs
  - SameSite=lax
  - Secure based on SECURE_COOKIES
  - Domain from COOKIE_DOMAIN; in tests/local mismatch, the domain may be omitted to ensure acceptance
- CSRF:
  - Non-httpOnly CSRF cookie (CSRF_COOKIE_NAME)
  - Header (CSRF_HEADER_NAME) must match cookie for all mutating requests (POST/PUT/PATCH/DELETE)
  - Safe methods (GET/HEAD/OPTIONS) do not require the CSRF header

--------------------------------------------------------------------------------

Local Development

1) Backend
- Setup venv and install dependencies:
  - cd backend
  - python3 -m venv .venv && source .venv/bin/activate
  - pip install -r requirements/dev.txt
- Configure env:
  - cp .env.example .env
  - Edit .env as needed (defaults are suitable for local dev)
- Run API:
  - uvicorn backend.main:app --reload --port 8000
- Notes:
  - On startup in dev, tables are created for SQLite (Base.metadata.create_all)
  - CSRF middleware set after CORS, before routers
  - Health endpoint: GET /api/v1/auth/health (also issues CSRF cookie if missing)

2) Frontend
- Install and run:
  - cd frontend
  - npm ci
  - npm run dev
- Ensure VITE_API_URL points to backend (http://localhost:8000 by default)
- Apollo client:
  - Sends credentials: 'include'
  - Uses GET for queries (no CSRF needed)
  - Adds X-CSRF-Token for non-Query operations using the hhh_csrf cookie

3) Testing
- Backend:
  - cd backend
  - pytest -q
  - Integration tests validate:
    - CSRF enforcement for REST and GraphQL
    - /auth register sets httpOnly cookies when CSRF header present
- Frontend:
  - cd frontend
  - npm run build (to verify builds)
  - npm run lint (ensure lint passes)

--------------------------------------------------------------------------------

Production Deployment

Backend
- Install prod dependencies:
  - pip install -r backend/requirements/prod.txt
- Environment:
  - Set DATABASE_URL to Postgres (e.g., postgresql://user:pass@host:5432/db)
  - SECURE_COOKIES=true
  - COOKIE_DOMAIN to your apex/subdomain as appropriate
  - CORS_ALLOW_ORIGINS to your exact frontend origin(s)
  - JWT_SECRET to a strong secret (do not commit secrets)
- DB Migrations:
  - alembic upgrade head
- Run server (example):
  - uvicorn backend.main:app --host 0.0.0.0 --port 8000
  - Place behind a reverse proxy (nginx/caddy); enable HTTPS
- Security notes:
  - SameSite=lax and Secure cookies on
  - Disable GraphQL introspection if required by environment
  - Restrict CORS origins explicitly (no wildcard with credentials)

Frontend
- Build:
  - cd frontend
  - npm ci && npm run build
- Serve:
  - Use a static hosting service or reverse proxy to serve dist/
  - Ensure VITE_API_URL at build-time matches backend origin
- Cookies/CSRF:
  - Ensure frontend and backend origins align with CORS and cookie domain

--------------------------------------------------------------------------------

Docker (optional)

- Dev compose:
  - docker/docker-compose.dev.yml mounts source and exposes backend and frontend
  - Typical usage:
    - docker compose -f docker/docker-compose.dev.yml up --build
- Prod compose:
  - docker/docker-compose.prod.yml (ensure secrets are injected via env/secrets manager)
  - Add healthchecks for API and DB

--------------------------------------------------------------------------------

CI

- Backend CI (.github/workflows/backend-ci.yml):
  - Setup Python 3.11
  - pip install -r backend/requirements/dev.txt
  - pytest -q (uses SQLite DATABASE_URL)
- Frontend CI (.github/workflows/frontend-ci.yml):
  - Setup Node 20
  - npm ci
  - npm run lint
  - npm run build

--------------------------------------------------------------------------------

Operational Considerations

- Backups:
  - Use pg_dump for Postgres backups (see docs/BACKUP_RESTORE.md)
  - Practice restore drills in staging
- Observability:
  - Consider Sentry/structured logs (redact PII)
- Security:
  - Rotate JWT secret if compromised; invalidate refresh tokens appropriately
  - Keep dependencies up to date; audit regularly

--------------------------------------------------------------------------------

Troubleshooting

- CSRF issues:
  - Check client has hhh_csrf cookie; for POST ensure X-CSRF-Token matches cookie
  - Ensure middleware order: CORS -> CSRF -> routers
- Cookies not set:
  - For dev, SECURE_COOKIES should be false; in prod set true
  - COOKIE_DOMAIN must match request host; otherwise cookies may be rejected
- CORS errors:
  - Validate CORS_ALLOW_ORIGINS includes exact frontend origin
  - Ensure credentials are enabled on both client and server
