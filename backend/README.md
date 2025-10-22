# Backend Development Guide

## Quick Start
```bash
cd backend
pip install -r requirements/dev.txt
cp .env.example .env  # Edit for your local setup (e.g., DATABASE_URL=sqlite:///app.db)
uvicorn main:app --reload --port 8000
```

## Testing
- Unit tests: Use in-memory SQLite with model metadata.
- Integration tests: Override `DATABASE_URL` to file-based SQLite (e.g., `sqlite:///./test_app.db`). Tables are auto-created via `Base.metadata.create_all` in test setup.
- Run all: `pytest -q`
- Run specific: `pytest tests/integration/test_auth_csrf.py -v`

## Migrations
Use Alembic for schema changes:
```bash
alembic revision -m "description"
alembic upgrade head
```

See docs/DEPLOYMENT.md for production setup.
