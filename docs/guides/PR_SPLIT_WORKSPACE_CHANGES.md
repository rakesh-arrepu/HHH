```markdown
PR: split/workspace-changes-2025-10-11 -> main

Title: Split previous large workspace commit into focused commits

Description:
- This pull request splits a previous monolithic commit (chore: add .gitignore and workspace change summary) into focused commits for easier review.

Commits included (local branch):
1) chore: add .gitignore to ignore local artifacts (app.db, .DS_Store, env files)
2) chore(api): add package markers for API and REST v1
3) feat(models): add BackupLog, GroupMember, and Role models
4) refactor(core): update config, database base, and security helpers
5) fix(models,services): update model definitions and auth service
6) chore(db): add alembic initial migration and update main and requirements
7) docs: add architecture & delivery docs, plus workspace change summary

Notes:
- Tests pass locally (backend tests ran successfully).
- I could not create the PR via CLI (gh not installed). Create it using the URL:
  https://github.com/rakesh-arrepu/HHH/pull/new/split/workspace-changes-2025-10-11

```