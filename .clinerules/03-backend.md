# Backend Rules – FastAPI + Strawberry GraphQL + SQLAlchemy + Alembic

These rules must be satisfied for any backend changes. They codify our architecture, quality, and security standards.

Sections
- Service and API Layering
- GraphQL (Strawberry)
- REST APIs
- Models, ORM, and Migrations
- AuthN/AuthZ, Cookies, CSRF, CORS
- Background Tasks
- Observability & Errors
- Local Dev, Testing, and Tooling
- Quality Gates

-------------------------------------------------------------------------------

Service and API Layering
- Keep domain logic in `backend/src/services/*`.
- Keep persistence models in `backend/src/models/*`. Avoid application logic in model classes.
- API layers:
  - REST: `backend/src/api/rest/v1/*`
  - GraphQL: `backend/src/api/graphql/*`
  - Middlewares (CSRF, auth, rate-limit): `backend/src/api/middleware/*`
- No circular dependencies. Services may depend on models and utils, never on API layer.

-------------------------------------------------------------------------------

GraphQL (Strawberry)
- Schema placement: `backend/src/api/graphql/schema.py`. Keep clear Query/Mutation roots.
- Use DataLoader for N+1 prevention (`backend/src/api/graphql/dataloaders.py`).
- Resolver rules:
  - Keep resolver thin; delegate to service layer.
  - Validate inputs; propagate typed domain errors (wrap in GraphQL-friendly envelopes if needed).
- Error policy:
  - Operational errors should be typed and handled; unexpected exceptions should be logged and surfaced as generic errors.
- Pagination/filtering:
  - Prefer cursor/offset pagination as business needs dictate. Keep it consistent across types.
- Auth:
  - Read auth context from request/session; validate roles/permissions in services.

-------------------------------------------------------------------------------

REST APIs
- Versioned endpoints under `backend/src/api/rest/v1/`.
- Request/response validation via pydantic (if used) or explicit validation utilities in `backend/src/utils/validation.py`.
- Auth and RBAC checks in service layer; transport layer should be thin.

-------------------------------------------------------------------------------

Models, ORM, and Migrations
- SQLAlchemy models under `backend/src/models/*`:
  - Explicit constraints (nullable, unique, index).
  - Timestamps (`created_at`, `updated_at`) where relevant.
  - Enums or constrained strings for categorical fields.
- Migrations:
  - Every schema change => Alembic migration in `backend/alembic/versions/*`.
  - Never edit applied/merged migration scripts.
  - Maintain idempotent `upgrade`/`downgrade` with clear comments.
- Data integrity and performance:
  - Use partial indexes and unique constraints as business rules require.
  - Avoid expensive cascades or long transactions in hot paths.

-------------------------------------------------------------------------------

AuthN/AuthZ, Cookies, CSRF, CORS
- JWT access/refresh with httpOnly cookies; rotate/expire tokens correctly.
- CSRF protection on mutating endpoints; double-submit token or header-based patterns as implemented in `backend/src/api/middleware/csrf.py`.
- CORS: narrow origins outside of dev; no wildcard in non-dev.
- RBAC:
  - Roles and group memberships enforced in service layer.
  - Avoid role checks spread through resolvers/handlers; centralize in service functions.

-------------------------------------------------------------------------------

Background Tasks
- Avoid long-running schedulers in free-tier; prefer on-demand computations.
- If tasks are required:
  - Use fast, idempotent handlers (`backend/src/tasks/*`).
  - Keep any persistent scheduling minimal and documented.

-------------------------------------------------------------------------------

Observability & Errors
- Logging: use consistent structured logs for warnings/errors.
- Sentry (or equivalent) recommended for error telemetry; redact PII.
- Error handling:
  - Never swallow exceptions silently; convert expected errors to typed domain errors.

-------------------------------------------------------------------------------

Local Dev, Testing, and Tooling
- Common dev command:
  - `uvicorn backend.main:app --reload --port 8000`
- Tests: `pytest` at repo root or inside backend; include unit + integration where feasible.
- Type/lint (if configured): mypy/ruff; prefer fixing over suppressions.

-------------------------------------------------------------------------------

Quality Gates
- Required before PR merge:
  - Backend tests pass (`pytest`).
  - Type checks and linting pass (if configured).
- API additions:
  - Update `docs/API.md` and GraphQL schema documentation.
  - Add migrations for schema changes and update seed fixtures where needed.
- Security review for any changes related to auth/cookies/CSRF/CORS.
