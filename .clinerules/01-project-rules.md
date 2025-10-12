# HHH – Project Cline Rules (Workspace Rules)

This repository uses Cline Rules and Workflows to standardize development, reduce regressions, and speed up repetitive tasks. These rules are active for this workspace and should guide all code changes.

Contents
- General Principles
- Frontend (Vite + React + TS + Tailwind v4 + Apollo)
- Backend (FastAPI + Strawberry GraphQL)
- Database & Migrations (SQLAlchemy + Alembic)
- Configuration & Secrets
- CI/CD & Quality Gates
- Security & Compliance
- GraphQL Conventions
- Documentation Standards
- Commit/PR Hygiene

Note: Workflows to automate these rules are placed under /workflows and can be invoked via slash commands, e.g. /frontend-dev.md

-------------------------------------------------------------------------------

General Principles
- Keep changes focused; avoid mixed concerns (e.g., styling + schema change in same PR).
- Prefer typed and validated boundaries (TS/py right at the edge).
- All new code must compile/build locally and pass lint/type checks before PR.
- Prefer smallest diff that accomplishes the outcome; defer refactors to dedicated PRs.
- Ensure idempotent scripts and reproducible workflow steps.

-------------------------------------------------------------------------------

Frontend Rules (Vite + React + TypeScript + Tailwind v4 + Apollo)
- Tooling
  - Use Vite for dev/build. Entry file is frontend/index.html (root-level).
  - Tailwind v4:
    - postcss.config.js must use the Tailwind v4 plugin:
      plugins: { '@tailwindcss/postcss': {} }
    - Import Tailwind via src/index.css: @import "tailwindcss";
    - Tailwind content must include index.html and src/**/*.{js,ts,jsx,tsx}.
    - Vite must explicitly reference ./postcss.config.js via vite.config.ts css.postcss.
  - CSS baseline:
    - src/index.css should include visible baseline styles for body to verify CSS load.
    - Avoid ad-hoc CSS resets; rely on Tailwind preflight via v4 import.
- Routing
  - Use React Router; define routes in App.tsx (or central router).
  - Keep routes shallow; lazy-load heavy pages/components where needed.
- Apollo Client
  - Provide a single Apollo client (src/lib/apollo.ts) and wrap app in ApolloProvider.
  - Read GraphQL endpoint from VITE_API_URL and use credentials: 'include' for cookie-based auth.
  - Centralize GraphQL fragments in src/graphql/fragments.ts and co-locate queries with features.
- State/UI
  - Prefer functional components with hooks.
  - Keep UI responsive (Tailwind classes) and accessible (labels, aria- props).
  - Add loading/empty/error states to all user-facing lists and mutation flows.
- Quality Commands (must pass before PR)
  - npm run build
  - npm run lint

-------------------------------------------------------------------------------

Backend Rules (FastAPI + Strawberry)
- Structure
  - Keep services under backend/src/services/* and model logic in backend/src/models/*.
  - API layers:
    - REST under backend/src/api/rest/v1/*
    - GraphQL schema under backend/src/api/graphql/*
  - Middlewares for auth, rate limit, CSRF under backend/src/api/middleware/*
- Auth & Security
  - JWT access/refresh with httpOnly cookies and CSRF protections.
  - Enforce RBAC via roles and group membership checks in service layer.
- Background Tasks
  - Prefer on-demand computations for free tier; avoid reliance on long-running schedulers.
- Quality
  - Add unit tests for services and integration tests for API endpoints.
  - Ensure typing; avoid silent excepts and broad exception handling.
- Run/Dev (typical)
  - uvicorn backend.main:app --reload --port 8000

-------------------------------------------------------------------------------

Database & Migrations (SQLAlchemy + Alembic)
- Migrations
  - Every schema change must have an Alembic migration under backend/alembic/versions/*.
  - No direct schema drift; never modify existing migration scripts after they’ve been merged.
- Modeling
  - Use explicit nullable/unique/index constraints.
  - Add created_at/updated_at timestamps where relevant.
  - Prefer enums or constrained strings for categorical data.
- Data Integrity
  - Enforce soft delete policies where required.
  - Add partial indexes and uniqueness as business rules dictate.
- Seed/Fixtures
  - Use backend/scripts/seed_data.py only for local/dev bootstrap; never for production.

-------------------------------------------------------------------------------

Configuration & Secrets
- Environment Variables
  - Frontend: VITE_API_URL (default: http://localhost:8000).
  - Backend: keep secrets in backend/.env (excluded from VCS); provide .env.example.
- Do not hardcode secrets or environment-specific URLs in code.
- All developer machines should copy *.env.example to *.env and adjust.

-------------------------------------------------------------------------------

CI/CD & Quality Gates
- Mandatory local checks before PR:
  - Frontend: npm run lint && npm run build
  - Backend: run tests (pytest) and mypy/ruff if configured.
- Keep GitHub Actions green; do not merge red pipelines.
- Avoid committing local artifacts (DB files, .DS_Store, .vite cache, etc.)

-------------------------------------------------------------------------------

Security & Compliance
- Cookies must be httpOnly and secure in production, with CSRF protection for mutating requests.
- CORS: narrowly scoped origins in non-dev environments.
- Input validation: use pydantic/validation on backend; zod/yup (or custom) on frontend.
- Keep dependencies up to date; address vulnerabilities surfaced by audit tools.

-------------------------------------------------------------------------------

GraphQL Conventions
- Schema
  - Keep schema under backend/src/api/graphql/schema.py, with clear delineation of Query/Mutation types.
  - Use DataLoader for N+1 sensitive fields.
  - Return typed errors in a consistent envelope when appropriate.
- Client
  - Co-locate queries/mutations with features or shared in src/graphql/* when reusable.
  - Always handle loading/error states.
  - Prefer optimistic UI for fast feedback when safe.

-------------------------------------------------------------------------------

Documentation Standards
- Update docs/API.md for new endpoints or schema changes.
- For non-trivial changes, update docs/DEPLOYMENT.md or docs/BACKUP_RESTORE.md if relevant.
- Consider ADRs in docs/ for major decisions (DB schema patterns, auth, infra changes).

-------------------------------------------------------------------------------

Commit/PR Hygiene
- Commits: Conventional style where possible (feat:, fix:, chore:, docs:, refactor:).
- PRs:
  - Include summary, screenshots (for UI), and test notes.
  - Link to related issues.
  - Keep diffs minimal; follow the rules in this document.

-------------------------------------------------------------------------------

Activation Notes
- Cline reads all Markdown files in .clinerules/. Add additional rule files (e.g. 02-frontend.md) as needed.
- Use the Workflows tab and slash commands (e.g., /frontend-dev.md) to run defined workflows.
