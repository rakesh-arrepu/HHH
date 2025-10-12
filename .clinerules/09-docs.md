# Documentation Rules – Project Docs, ADRs, API/Schema, Runbooks

These rules ensure documentation stays accurate, searchable, and useful for onboarding and future maintenance.

Sections
- General Documentation Principles
- Structure & Locations
- Change Management & PR Expectations
- API & GraphQL Docs
- Deployment & Ops Docs
- ADRs (Architecture Decision Records)
- Writing Standards

-------------------------------------------------------------------------------

General Documentation Principles
- Docs are part of the deliverable; update them in the same PR as the code change.
- Prefer small, targeted updates over large rewrites.
- Keep docs actionable: commands, paths, versions, code snippets.
- If something took >10 minutes to figure out, document it.

-------------------------------------------------------------------------------

Structure & Locations
- Top-level docs live under `/docs/`:
  - `/docs/API.md` – REST and GraphQL endpoint documentation (schemas, examples).
  - `/docs/DEPLOYMENT.md` – deploy instructions, environment assumptions.
  - `/docs/BACKUP_RESTORE.md` – backup schedule and restore runbook.
  - `/docs/DAILY_TRACKER_ARCHITECTURE_COMBINED.md` – architecture overview.
  - `/docs/PR_SPLIT_WORKSPACE_CHANGES.md` – PR splitting guidelines (if applicable).
- Code-Adjacent README files:
  - `/backend/README.md` – backend dev, test, migrations, local run.
  - `/frontend/README.md` – frontend dev, build, preview, lint.
- Cline Rules/Workflows:
  - `.clinerules/*.md` – active rules for this workspace.
  - `/workflows/*.md` – Cline workflows invokable via slash commands.

-------------------------------------------------------------------------------

Change Management & PR Expectations
- Any change that impacts developers or users must update the relevant docs:
  - UI/Workflow changes → frontend README or docs where appropriate.
  - API/GraphQL schema changes → `/docs/API.md`.
  - Config/env changes → `.env.example` and `/docs/DEPLOYMENT.md`.
  - DB changes → migration comments + `/docs/DEPLOYMENT.md` if ops steps change.
- PR must contain:
  - Summary of change and links to updated docs.
  - If no doc change is required, state explicitly why.

-------------------------------------------------------------------------------

API & GraphQL Docs
- REST:
  - For each endpoint: method, path, params, status codes, example request/response.
  - Include auth requirements and error envelope format.
- GraphQL:
  - Document types, queries, mutations, and important field-level auth notes.
  - Include example queries/mutations and typical error shapes.
- Keep `/docs/API.md` current with each schema or route change.

-------------------------------------------------------------------------------

Deployment & Ops Docs
- `/docs/DEPLOYMENT.md` must explain:
  - Environment variables and their purpose.
  - Dev vs staging vs production distinctions.
  - Build and run commands for frontend/backend.
  - Free-tier/provider specifics if relevant.
- `/docs/BACKUP_RESTORE.md`:
  - Backup cadence, storage location, retention.
  - Step-by-step restore drill (staging) and validation checks.

-------------------------------------------------------------------------------

ADRs (Architecture Decision Records)
- Use ADRs for decisions that affect architecture or long-term maintainability:
  - Major dependency swaps, database patterns, auth strategy changes, infra choices.
- Place ADRs under `/docs/adr/` as `YYYY-MM-DD-title.md` with:
  - Context/problem, considered options, decision, consequences.
- Reference ADRs in PRs where relevant.

-------------------------------------------------------------------------------

Writing Standards
- Prefer Markdown; include runnable code blocks where helpful.
- Use relative paths and exact commands tested locally.
- Date significant updates at top of doc when changing behavior or assumptions.
- Keep tone concise and technical; avoid ambiguity.
