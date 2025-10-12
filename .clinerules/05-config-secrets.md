# Configuration & Secrets Rules – Env Management, Secrets Hygiene, App Config

These rules standardize environment configuration across frontend, backend, CI/CD and Docker. They ensure secrets never leak and configuration is consistent across environments.

Sections
- Environment Files & Structure
- Frontend (Vite) Environment
- Backend (FastAPI) Environment
- Docker & Compose
- GitHub Actions & CI Secrets
- CORS, Cookies, Security Headers
- Secret Hygiene & Scanning
- Validation & Quality Gates

-------------------------------------------------------------------------------

Environment Files & Structure
- Do not commit real secrets. Only commit *.env.example templates.
- Required templates:
  - `backend/.env.example` – all backend vars (DB, JWT, CSRF, CORS, SENTRY).
  - `frontend/.env.example` – all frontend vars (VITE_API_URL, feature flags).
- Each developer should copy templates:
  - `cp backend/.env.example backend/.env`
  - `cp frontend/.env.example frontend/.env`
- Use explicit defaults in code only when safe for local dev (never for prod).
- Never embed secrets in code, client bundles, or Dockerfiles. Always read from env.

-------------------------------------------------------------------------------

Frontend (Vite) Environment
- Vite env prefix: only variables prefixed with `VITE_` are exposed to the client bundle.
  - Required: `VITE_API_URL` (default `http://localhost:8000`).
- Do NOT place secrets in `VITE_*` variables. These are publicly visible to end users.
- Access via: `import.meta.env.VITE_API_URL`.
- CORS: API URL must match backend dev server origin for cookie-based auth.
- Build-time only: Vite injects env at build-time; changes require rebuild/restart.

-------------------------------------------------------------------------------

Backend (FastAPI) Environment
- Backend env must include:
  - DB: `DATABASE_URL` (Postgres preferred; SQLite allowed for dev only).
  - JWT: `JWT_SECRET`, `JWT_ALG` (e.g., HS256), `ACCESS_TOKEN_EXPIRES`, `REFRESH_TOKEN_EXPIRES`.
  - CSRF: `CSRF_SECRET`, `CSRF_HEADER_NAME` (e.g., `X-CSRF-Token`).
  - CORS: `ALLOWED_ORIGINS` (comma-separated), `COOKIE_DOMAIN`, `SECURE_COOKIES` (true in prod).
  - Observability: `SENTRY_DSN` (optional).
- Do not default to permissive CORS in non-dev builds.
- Runtime validation: fail fast if required env vars are missing (raise at startup).

-------------------------------------------------------------------------------

Docker & Compose
- `docker/docker-compose.dev.yml`:
  - Mounts local project; loads `backend/.env` and `frontend/.env` with overrides.
  - Exposes backend on 8000, frontend on 5173 (or auto switch).
- `docker/docker-compose.prod.yml`:
  - Never bake secrets into images; pass via env or secrets manager.
  - Add healthchecks for API and DB.
- Build args vs env:
  - Build args for non-secret compile-time toggles.
  - Env for runtime-only sensitive values.

-------------------------------------------------------------------------------

GitHub Actions & CI Secrets
- Define secrets in repo settings (never commit):
  - `API_BASE_URL`, `PROD_DATABASE_URL`, `SENTRY_DSN`, `REGISTRY_TOKEN`, …
- CI steps:
  - Frontend: `npm ci`, `npm run build`.
  - Backend: `pip install -r requirements/prod.txt`, run tests, `alembic upgrade head` in integration envs.
- Mask secrets in logs; avoid echoing env content.

-------------------------------------------------------------------------------

CORS, Cookies, Security Headers
- CORS:
  - Dev: `ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174`
  - Prod: exact origins only (no `*`).
- Cookies:
  - `httpOnly`, `sameSite=lax` (or `strict`), `secure=true` in production.
  - Use `credentials: 'include'` in Apollo/clients.
- Security headers: enable sensible defaults (e.g., via middleware).

-------------------------------------------------------------------------------

Secret Hygiene & Scanning
- Git ignore:
  - Ignore `backend/.env`, `frontend/.env`, `.DS_Store`, `.vite`, `app.db`, `dist/`.
- Optional scanning:
  - Integrate secret scanners (e.g., `trufflehog`, `gitleaks`) in CI.
- Rotation:
  - Rotate compromised secrets immediately; reissue tokens and revoke old credentials.

-------------------------------------------------------------------------------

Validation & Quality Gates
- Local:
  - Frontend: `npm run build && npm run preview` – verify env injection and CSS.
  - Backend: `pytest` and a smoke GraphQL/REST call against `VITE_API_URL`.
- Pre-PR:
  - Confirm `*.env.example` updated when adding new config.
  - Confirm CORS and cookies settings are correct for target environment.
- Documentation:
  - Update `docs/DEPLOYMENT.md` and `docs/API.md` when env or security behavior changes.

-------------------------------------------------------------------------------

Appendix: Minimal Env Templates

frontend/.env.example
```
VITE_API_URL=http://localhost:8000
```

backend/.env.example (illustrative; keep real template in repo)
```
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/hhh
JWT_SECRET=change_me
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRES=900
REFRESH_TOKEN_EXPIRES=1209600
CSRF_SECRET=change_me
CSRF_HEADER_NAME=X-CSRF-Token
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
COOKIE_DOMAIN=localhost
SECURE_COOKIES=false
SENTRY_DSN=
