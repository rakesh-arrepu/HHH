# /db-migration.md – Database Migration Workflow (SQLAlchemy + Alembic)

This workflow encodes rules from:
- `.clinerules/04-database.md` – DB & Migrations
- `.clinerules/03-backend.md` – Backend layering & GraphQL
- `.clinerules/06-ci-cd.md` – CI gates for migrations

Use this when changing models or DB schema. It ensures zero drift, safe operations, and clear documentation.

Sections
- Prereqs & Environment
- Plan the Change
- Create/Autogenerate Migration
- Review & Edit Migration (constraints/indexes/defaults)
- Apply & Test Locally
- Rollback Strategy
- Update Code & Docs
- Pre-PR Checklist
- One-shot command set

-------------------------------------------------------------------------------

## 1) Prereqs & Environment

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
cp -n .env.example .env 2>/dev/null || true
```

Ensure Alembic is configured (already in `backend/alembic/`):
- `alembic.ini` present and env points to `backend/src/core/database.py` engine.

-------------------------------------------------------------------------------

## 2) Plan the Change

- Identify the feature or bug driving the change.
- Decide model-level changes in `backend/src/models/*`.
- Decide migration impact:
  - Columns: add/drop/alter (nullability, defaults)
  - Constraints: unique, foreign keys
  - Indexes: simple/compound/partial
  - Backfills: data migrations (guarded and idempotent)
- Consider non-blocking changes and backwards-compatibility.

-------------------------------------------------------------------------------

## 3) Create / Autogenerate Migration

Option A – Manual scaffold:
```bash
cd backend
alembic revision -m "add <thing> to <table>"
```

Option B – Autogenerate from model diffs:
```bash
cd backend
# Ensure models are updated first
alembic revision --autogenerate -m "sync models: <summary>"
```

Conventions:
- Filename: `yyyymmddhhmmss_short_description.py`
- Message at top must clearly state intent/risk.

-------------------------------------------------------------------------------

## 4) Review & Edit Migration

Open the new file in `backend/alembic/versions/*.py` and ensure:

- Include constraints, indexes, defaults inside the migration (not only models).
- For existing populated tables, add `server_default` when introducing non-nullable columns.
- Add indexes reflecting actual query patterns (consider EXPLAIN once applied).
- For partial indexes (Postgres), ensure correct `postgresql_where` condition.
- If foreign keys are added, set reasonable `ondelete` policy aligned to business need.
- For data backfill, use safe/guarded operations and keep them idempotent.
- Add comments describing intent & potential risks.

Example (sketch):
```python
def upgrade():
    # add column with server_default to avoid failing on existing rows
    op.add_column('entries', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false'))
    # add index to speed frequent queries
    op.create_index('ix_entries_user_created_at', 'entries', ['user_id', 'created_at'])

def downgrade():
    op.drop_index('ix_entries_user_created_at', table_name='entries')
    op.drop_column('entries', 'is_archived')
```

-------------------------------------------------------------------------------

## 5) Apply & Test Locally

Apply:
```bash
cd backend
alembic upgrade head
```

Run tests/smoke:
```bash
pytest -q
# Optionally run API smoke
uvicorn backend.main:app --reload --port 8000
# Exercise endpoints/GraphQL with the new schema
```

Verify:
- App loads & key flows still work.
- New constraints/indexes present (check DB).
- Backfill completed (verify data shape).

-------------------------------------------------------------------------------

## 6) Rollback Strategy

Test rollback:
```bash
cd backend
alembic downgrade -1
# Optionally re-upgrade to ensure both directions are valid
alembic upgrade head
```

Ensure downgrade path is safe & idempotent.

-------------------------------------------------------------------------------

## 7) Update Code & Docs

- Update SQLAlchemy models in `backend/src/models/*` to match migration.
- Update services if logic depends on new fields/constraints.
- Update docs:
  - `/docs/API.md` if schema changes impact API behavior or types.
  - Add notes to `/docs/DEPLOYMENT.md` if operations needed.
- If GraphQL schema changed, ensure resolvers/types updated accordingly and add tests.

-------------------------------------------------------------------------------

## 8) Pre-PR Checklist

- [ ] Migration file authored with clear comments and safe defaults.
- [ ] Models updated to match migration and vice versa.
- [ ] `alembic upgrade head` applies cleanly.
- [ ] `pytest -q` passes locally.
- [ ] Downgrade path tested (`alembic downgrade -1`).
- [ ] Docs updated (`/docs/API.md` etc.).
- [ ] CI will run alembic upgrade in ephemeral DB (per .clinerules/06-ci-cd.md).

-------------------------------------------------------------------------------

## 9) One-shot command set (copy/paste)

```bash
cd backend \
&& source .venv/bin/activate 2>/dev/null || (python -m venv .venv && source .venv/bin/activate) \
&& pip install -r requirements/dev.txt \
&& cp -n .env.example .env 2>/dev/null || true \
&& alembic revision --autogenerate -m "sync models: <summary>" \
&& alembic upgrade head \
&& pytest -q
```

-------------------------------------------------------------------------------

## References (Rules)

- `.clinerules/04-database.md`
- `.clinerules/03-backend.md`
- `.clinerules/06-ci-cd.md`
- `.clinerules/07-security.md`
