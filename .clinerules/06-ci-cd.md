# CI/CD Rules – Pipelines, Quality Gates, Build/Release

These rules define the minimum quality bars and pipeline steps required to keep the repository healthy and deployable.

Sections
- Branching & Versioning
- Required Local Checks Pre-PR
- GitHub Actions (CI) – Required Jobs
- Build Artifacts & Caching
- Release & Deployment
- PR Review Checklist
- Failure Handling & Rollback

-------------------------------------------------------------------------------

Branching & Versioning
- Main is protected; only PRs with green checks may merge.
- Feature branches: `feat/*`, fixes: `fix/*`, chores: `chore/*`, docs: `docs/*`.
- Conventional commits preferred (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`).
- Tag releases semver (`vX.Y.Z`) when shipping.

-------------------------------------------------------------------------------

Required Local Checks Pre-PR
- Frontend:
  - `cd frontend && npm ci`
  - `npm run lint`
  - `npm run build`
  - Optional: `npm run preview` to verify assets/CSS load.
- Backend:
  - `cd backend && pip install -r requirements/dev.txt`
  - `pytest -q` (unit + optional integration)
  - Migrations current: `alembic upgrade head`
- Docs updated if API or schema changed.

-------------------------------------------------------------------------------

GitHub Actions (CI) – Required Jobs
- frontend-ci:
  - `npm ci`
  - `npm run lint`
  - `npm run build`
  - Cache: `~/.npm` and `frontend/node_modules/.vite` keyed by lockfile hash.
- backend-ci:
  - `pip install -r requirements/prod.txt`
  - `pytest -q`
  - Alembic: ensure migrations apply cleanly (`alembic upgrade head`) on ephemeral DB.
- security-ci (optional but recommended):
  - `pip install ruff` (or equivalent) + `ruff check .`
  - `npm audit --audit-level=moderate` (allow failures but log)
- Do not upload `dist/` or build outputs as artifacts unless needed (use caching instead).

-------------------------------------------------------------------------------

Build Artifacts & Caching
- Node cache: use lockfile hash and OS for cache key.
- Python cache: pip cache keyed by requirements/* content.
- Do not commit `.vite`, `dist/`, `app.db`, `.pytest_cache/`.
- If cache corrupt, CI must print cache bust hint.

-------------------------------------------------------------------------------

Release & Deployment
- Build must be reproducible from clean checkout:
  - `npm ci && npm run build` (frontend)
  - `pip install -r requirements/prod.txt && alembic upgrade head` (backend)
- Production configs/secrets must come from environment or secrets manager, never from repository.
- Keep `docs/DEPLOYMENT.md` updated for any environment changes.

-------------------------------------------------------------------------------

PR Review Checklist (Minimal)
- Code compiles/ builds; lint/type checks pass.
- Database changes include Alembic migrations and updated models.
- Security-sensitive code adheres to cookie/CSRF/CORS rules.
- UI: Tailwind v4 rules followed (postcss plugin, @import syntax, content).
- Docs and `.env.example` updated when config changes.

-------------------------------------------------------------------------------

Failure Handling & Rollback
- CI red: do not merge; fix forward.
- Migration issues:
  - Create new migration to correct; never edit applied migrations.
- Revert policy:
  - If production regression, revert merge via GitHub, create fix branch, add tests, re-merge.

-------------------------------------------------------------------------------

Notes
- Keep workflows small and fast; prefer caching over artifact passing.
- Ensure secrets are masked in CI logs; never print env content.
