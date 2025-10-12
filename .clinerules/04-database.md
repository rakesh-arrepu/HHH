# Database Rules – SQLAlchemy + Alembic (PostgreSQL-first, SQLite dev allowed)

These rules standardize our schema evolution, modeling, and data integrity practices across environments.

Sections
- Engines & Environments
- Migrations (Alembic)
- Modeling Conventions (SQLAlchemy)
- Constraints, Indexes, and Performance
- Data Integrity & Lifecycle
- Seeds/Fixtures
- Testing Database
- Backup/Restore & Maintenance

-------------------------------------------------------------------------------

Engines & Environments
- Default DB: PostgreSQL (Neon/Supabase for free tier). SQLite may be used for local quick dev but parity must be maintained.
- Read connection settings from env only (no hardcoding):
  - backend/.env.example must contain all required DB vars.
  - Never check real secrets into VCS.
- Connection management:
  - Use a single session factory; avoid long-lived sessions in request handlers.
  - Prefer scoped/session contexts in async/REST/GraphQL layers.

-------------------------------------------------------------------------------

Migrations (Alembic)
- Every schema change MUST have an Alembic migration under backend/alembic/versions/*.
- Zero drift policy:
  - Do not modify applied/merged migrations.
  - For changes, generate a new migration.
- Migration authoring:
  - Use explicit Upgrade/Downgrade with comments describing intent and risk.
  - Include constraints, indexes, defaults inside the migration (not only in models).
  - Add server_default for non-nullable columns on existing populated tables when possible.
- Naming conventions:
  - Filenames: yyyymmddhhmmss_short_description.py
  - Revisions should include a meaningful message at the top.
- Review checklist:
  - Backward compatible where feasible.
  - Non-blocking operations (avoid table locks for long durations).
  - Index creation concurrent on Postgres when appropriate.
  - Data backfill steps included where necessary.
- Commands (typical):
  - Create: alembic revision -m "add X to Y"
  - Autogenerate: alembic revision --autogenerate -m "sync models"
  - Apply: alembic upgrade head
  - Rollback: alembic downgrade -1

-------------------------------------------------------------------------------

Modeling Conventions (SQLAlchemy)
- Tables:
  - snake_case table names; singular or plural consistently (prefer plural for collections e.g., users, groups).
  - Include created_at (UTC), updated_at (UTC) timestamps where relevant.
  - Soft-delete column when policy required (deleted_at or is_deleted).
- Columns:
  - Explicit nullable/unique/index where relevant.
  - Use enum types or constrained strings for categorical fields.
  - Text vs. JSONB (PG): choose JSONB for structured dynamic data; index with GIN when queried.
  - Foreign Keys: always define FK constraints with ondelete behavior; align with business expectations.
- Relationships:
  - Avoid lazy=joined by default; use DataLoader (GraphQL) or explicit joins in services to prevent N+1.
- Validation:
  - Business rules at service layer; DB constraints for integrity (unique, not-null).
- Defaults:
  - Prefer server-side defaults in migrations for durable behavior across languages/services.

-------------------------------------------------------------------------------

Constraints, Indexes, and Performance
- Unique constraints: enforce business uniqueness (e.g., email per tenant).
- Partial/Conditional indexes: use when selective subsets are frequently queried (e.g., is_deleted = false).
- Compound indexes: add when queries filter on multiple columns.
- Query patterns:
  - Add indexes only after confirming query patterns (analyze with EXPLAIN on PG).
  - Avoid wildcards LIKE leading % without special indexes.
- Migrations must include index/constraint creation (not only models).

-------------------------------------------------------------------------------

Data Integrity & Lifecycle
- Referential integrity via FKs; avoid silent cascades on hot paths (use explicit deletes or soft-delete policies).
- Soft delete:
  - Add deleted_at or is_deleted.
  - Update queries and unique constraints to respect soft-delete semantics.
- Auditing:
  - For important actions, use backend/src/models/audit.py and service-layer logging patterns.

-------------------------------------------------------------------------------

Seeds/Fixtures
- Dev seeds:
  - backend/scripts/seed_data.py may load minimal fixtures for local dev only.
  - Never run in production; guard with explicit environment checks.
- Test fixtures:
  - Fixture data must be deterministic and idempotent.
  - Keep seeded user credentials non-sensitive; rotate/change in different envs.

-------------------------------------------------------------------------------

Testing Database
- Use a separate test DB (schema or database name suffix _test).
- Tests should:
  - Run migrations fresh before integration tests.
  - Use transactions/rollbacks or per-test schema teardown.
  - Avoid relying on global mutable state between tests.

-------------------------------------------------------------------------------

Backup/Restore & Maintenance
- Backups:
  - For free-tier: nightly pg_dump via GitHub Actions to R2/B2 (see docs/BACKUP_RESTORE.md).
  - Ensure size limits; apply lifecycle rules on buckets.
- Restore drills:
  - Monthly manual restore into a staging DB to validate backups.
- Maintenance:
  - Vacuum/Analyze (PG) per provider defaults; monitor query performance for hotspots.

-------------------------------------------------------------------------------

Quality Gates for DB Changes
- PR includes:
  - Migration script(s) with clear comments.
  - Updated models reflecting migration.
  - Tests updated/added when schema affects behavior.
  - Docs update if API/GraphQL schema impacted.
- Manual verification:
  - Apply migrations locally.
  - Run pytest + backend smoke API tests.
  - Sanity-check EXPLAIN plans for new critical queries.
