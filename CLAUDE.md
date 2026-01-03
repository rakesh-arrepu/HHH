# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Daily Tracker (HHH) is a monorepo app for tracking Health, Happiness, and Hela (Money) entries in groups with role-based access control, streak tracking, and analytics.

## Commands

### Development
```bash
# Backend (from repo root with venv activated)
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000

# Frontend
cd frontend && npm run dev

# Both via Docker
make dev
```

### Testing
```bash
# Backend tests
cd backend && pytest -q

# Frontend tests
cd frontend && npm run test

# Full test suite
make test
```

### Linting & Build
```bash
# Frontend (must pass before PR)
cd frontend && npm run lint && npm run build

# Backend linting (if configured)
ruff check backend/
```

### Database Migrations (Alembic)
```bash
cd backend
alembic revision -m "description"           # Create migration
alembic revision --autogenerate -m "sync"   # Auto-generate from model diff
alembic upgrade head                        # Apply migrations
alembic downgrade -1                        # Rollback one step
```

## Architecture

### Backend (FastAPI + Strawberry GraphQL + SQLAlchemy)
```
backend/
├── main.py                    # FastAPI app entry
├── src/
│   ├── api/
│   │   ├── graphql/          # Strawberry schema, resolvers, dataloaders
│   │   ├── rest/v1/          # REST endpoints
│   │   └── middleware/       # Auth, CSRF, rate limiting
│   ├── services/             # Business logic (auth, entry, group, analytics, etc.)
│   ├── models/               # SQLAlchemy models (user, group, entry, role, etc.)
│   ├── core/                 # Config, DB session
│   └── utils/                # Validation, helpers
├── alembic/                  # Database migrations
└── tests/
```

### Frontend (Vite + React 18 + TypeScript + Tailwind v4 + Apollo)
```
frontend/
├── src/
│   ├── pages/               # Dashboard, Groups, Profile, Admin
│   ├── components/          # Feature-organized: auth, entries, groups, dashboard, common
│   ├── graphql/             # Queries, mutations, fragments
│   ├── lib/                 # Apollo client setup, constants
│   ├── hooks/               # Custom React hooks
│   └── types/               # TypeScript types
├── postcss.config.js        # Must use @tailwindcss/postcss for v4
├── tailwind.config.js       # content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}']
└── vite.config.ts           # Must reference postcss config via css.postcss
```

## Key Conventions

### Tailwind v4 (Critical)
- Use `@import "tailwindcss";` in index.css (not legacy `@tailwind` directives)
- PostCSS plugin: `{ '@tailwindcss/postcss': {} }`
- Vite must explicitly point to postcss.config.js

### GraphQL
- Schema: `backend/src/api/graphql/schema.py`
- Use DataLoader for N+1 prevention
- Apollo client in `frontend/src/lib/apollo.ts` with `credentials: 'include'`
- Handle loading/error/empty states in all GraphQL components

### Database
- Every schema change requires an Alembic migration
- Never edit merged migrations; create new ones
- Use soft deletes via `deleted_at` column
- Partial unique indexes: `WHERE deleted_at IS NULL`

### Auth & Security
- JWT access/refresh with httpOnly cookies
- CSRF protection on mutating endpoints
- CORS: narrow origins (no wildcard with credentials)
- RBAC enforced in service layer, not resolvers

### Environment Variables
- Backend: `backend/.env` (copy from `.env.example`)
- Frontend: `frontend/.env` with `VITE_API_URL=http://localhost:8000`
- Never commit real secrets; only commit `.env.example` templates

## Domain Model

- **Users**: Have roles (User, Group Admin, Super Admin), belong to multiple groups
- **Groups**: Have timezone, admin, members with per-group streak tracking
- **Entries**: Three section types (Health, Happiness, Hela), max 2 edits/day, same-day only
- **Streaks**: Non-resetting, increment only when all 3 sections completed for a day

## Quality Gates (Before PR)
- `npm run build` and `npm run lint` pass (frontend)
- `pytest` passes (backend)
- Migrations apply cleanly
- Update docs/API.md for schema changes
