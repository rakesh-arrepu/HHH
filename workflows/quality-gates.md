# /quality-gates.md – Unified Local Quality Gates (FE/BE/DB/Security)

Run this workflow before opening a PR. It enforces the core checks encoded in `.clinerules/`:
- Frontend: lint + build (+ preview optional)
- Backend: migrations apply + tests
- Security: optional scanners
- Artifacts/caches sanity

Sections
- Preflight
- Frontend Checks (Vite + TS + Tailwind v4)
- Backend Checks (FastAPI + Alembic + Tests)
- Optional Security Scans
- Artifacts/Caches Sanity
- Success Criteria
- One-shot command set

-------------------------------------------------------------------------------

## 1) Preflight

Ensure env templates are copied (safe no-op if already present):
```bash
cp -n frontend/.env.example frontend/.env 2>/dev/null || true
cp -n backend/.env.example backend/.env 2>/dev/null || true
```

-------------------------------------------------------------------------------

## 2) Frontend Checks (Vite + TS + Tailwind v4)

```bash
cd frontend
npm ci
npm run lint
npm run build
# Optional production preview (new terminal)
npm run preview -- --port 5175
```

Verify:
- Build succeeds and emits `dist/assets/index-*.css` and JS bundle.
- CSS renders in preview (Tailwind v4 via @tailwindcss/postcss).
- If CSS missing, use `/frontend-dev.md` troubleshooting section.

-------------------------------------------------------------------------------

## 3) Backend Checks (FastAPI + Alembic + Tests)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate 2>/dev/null || true
pip install -r requirements/dev.txt
alembic upgrade head
pytest -q
```

Verify:
- Migrations apply cleanly on a fresh DB.
- Tests pass.
- Optionally smoke-run API:
  ```bash
  uvicorn backend.main:app --reload --port 8000
  # Visit http://localhost:8000/docs or /graphql
  ```

-------------------------------------------------------------------------------

## 4) Optional Security Scans

(These do not block local dev but should be observed and triaged)
```bash
# Python
pip install ruff && ruff check .

# Node
npm audit --audit-level=moderate || true
```

-------------------------------------------------------------------------------

## 5) Artifacts/Caches Sanity

- Do not commit:
  - `.vite/`, `dist/`, `app.db`, `.pytest_cache/`, `backend/.env`, `frontend/.env`
- If FE dev server shows stale styling:
  ```bash
  pkill -f "vite|vite preview" || true
  rm -rf frontend/node_modules/.vite
  (cd frontend && npm run dev -- --force)
  ```

-------------------------------------------------------------------------------

## 6) Success Criteria

- Frontend: `npm run lint` and `npm run build` pass.
- Backend: `alembic upgrade head` and `pytest -q` pass.
- No critical findings from optional scanners.
- Env and configs adhere to `.clinerules/` (Tailwind v4 plugin, Vite -> postcss.config, etc.).

-------------------------------------------------------------------------------

## 7) One-shot Command Set

```bash
# Frontend
cd frontend \
&& npm ci \
&& npm run lint \
&& npm run build \
&& (npm run preview -- --port 5175 &> /dev/null &); sleep 1; echo "Preview on http://localhost:5175"

# Backend
cd ../backend \
&& (python -m venv .venv && source .venv/bin/activate) || source .venv/bin/activate \
&& pip install -r requirements/dev.txt \
&& alembic upgrade head \
&& pytest -q
```

-------------------------------------------------------------------------------

## References (Rules)

- `.clinerules/01-project-rules.md` – General standards and gates
- `.clinerules/02-frontend.md` – Tailwind v4 + Vite specifics
- `.clinerules/03-backend.md` – Layering, GraphQL/REST, testing
- `.clinerules/04-database.md` – Migrations policy
- `.clinerules/06-ci-cd.md` – CI jobs and pre-PR checks
- `.clinerules/07-security.md` – Security posture
