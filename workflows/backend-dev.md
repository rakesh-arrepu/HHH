# /backend-dev.md – Backend Development Workflow (FastAPI + Strawberry + SQLAlchemy + Alembic)

This workflow encodes the backend rules in `.clinerules/03-backend.md`, `.clinerules/04-database.md`, `.clinerules/07-security.md`, and `.clinerules/06-ci-cd.md` to ensure consistent local dev, testing, and migrations.

Sections
- Prerequisites & Environment
- Install & Run (Dev)
- Lint/Type (optional) & Tests
- Migrations (Alembic) – create/apply/rollback
- Local Security Smoke & Observability
- Success Criteria

-------------------------------------------------------------------------------

## 1) Prerequisites & Environment

- Python 3.10+ recommended.
- Create/activate virtualenv:
  ```bash
  cd backend
  python -m venv .venv
  source .venv/bin/activate  # Windows: .venv\Scripts\activate
  ```
- Env file:
  ```bash
  cp -n .env.example .env 2>/dev/null || true
  # Edit .env with local DB credentials; for quick dev SQLite is allowed
  ```
- Recommended tooling available on PATH:
  - `uvicorn`, `alembic`, `pytest`
  - Optional linters: `ruff`, `mypy` (if configured)

-------------------------------------------------------------------------------

## 2) Install & Run (Dev)

Install dependencies:
```bash
cd backend
pip install -r requirements/dev.txt
```

Run API (reload on changes):
```bash
uvicorn backend.main:app --reload --port 8000
# Open http://localhost:8000/docs (REST) or /graphql (if GraphQL routing exposed)
```

Notes:
- API layers live under `backend/src/api/rest/v1/*` and `backend/src/api/graphql/*`.
- Services under `backend/src/services/*`, models `backend/src/models/*`.

-------------------------------------------------------------------------------

## 3) Lint/Type (optional) & Tests

Run tests:
```bash
cd backend
pytest -q
```

Optional lint/type (if configured):
```bash
ruff check .
mypy .
```

Expectations:
- Unit tests pass; add tests for services and API endpoints when changing behavior.
- Keep typing strict; avoid broad exceptions and silent failures.

-------------------------------------------------------------------------------

## 4) Migrations (Alembic)

Zero-drift policy: every schema change requires a migration under `backend/alembic/versions/*`.

Common commands:
```bash
# From backend/
alembic revision -m "add X to Y"                  # manual revision
alembic revision --autogenerate -m "sync models"  # autogenerate based on model diff
alembic upgrade head                              # apply latest
alembic downgrade -1                              # rollback a single step
```

Conventions:
- Filename format: `yyyymmddhhmmss_short_description.py`
- Include constraints, indexes, defaults in migration (not just models).
- For non-null on existing tables, prefer `server_default` and backfill when needed.
- Never edit applied/merged migrations; create a new one to correct.

-------------------------------------------------------------------------------

## 5) Local Security Smoke & Observability

Security quick-check:
- CSRF middleware enabled for mutating routes.
- Cookies `httpOnly` and `secure=true` in production builds.
- CORS:
  - Dev allowlist includes `http://localhost:5173` (and current port if different).
  - Non-dev: strict origin allowlist; never `*` with credentials.
- Avoid logging tokens/PII; redact sensitive fields.

Optional:
- Configure Sentry DSN via env for dev sampling (ensure PII scrubbing).

-------------------------------------------------------------------------------

## 6) Success Criteria

- API runs locally at `http://localhost:8000`, health endpoints OK.
- Tests pass (`pytest -q`).
- DB migrations apply cleanly (`alembic upgrade head`).
- No obvious security regressions (CORS, CSRF, cookies posture sane in dev).

-------------------------------------------------------------------------------

## One-shot local bring-up

```bash
cd backend \
&& python -m venv .venv && source .venv/bin/activate \
&& pip install -r requirements/dev.txt \
&& cp -n .env.example .env 2>/dev/null || true \
&& alembic upgrade head \
&& pytest -q \
&& uvicorn backend.main:app --reload --port 8000
```

-------------------------------------------------------------------------------

## References (Rules)

- `.clinerules/03-backend.md` – Backend rules (layering, GraphQL/REST, testing)
- `.clinerules/04-database.md` – DB/migrations rules (naming, performance, lifecycle)
- `.clinerules/07-security.md` – Security posture (CSRF, CORS, cookies, headers)
- `.clinerules/06-ci-cd.md` – CI jobs and local checks
