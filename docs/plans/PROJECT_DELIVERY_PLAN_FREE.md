```markdown
# Daily Tracker – Free-Tier MVP Delivery Plan (Zero Cloud Spend)

Goal
- Deliver a functional MVP using only free-tier services or self-hosted on a personal machine, incurring $0/month infra cost during development and closed beta.
- Defer cost-incurring features (PITR, email-at-scale, sticky WebSockets, paid monitoring, custom domain) to a later paid phase.

Scope Guardrails (What’s In vs Deferred)

Included (no infra spend)
- Core domain: Users, Roles, Groups, GroupMembers, SectionEntries with same-day+2-edits rule, non-decreasing streaks
- Auth: argon2id password hashing, JWT access + refresh (short-lived), httpOnly cookies, CSRF protection
- RBAC: App-level + optional Postgres RLS (works fine on free Postgres; keep policies simple)
- UI: React + Vite + Tailwind + shadcn/ui, Apollo Client with GraphQL Code Generator
- GraphQL API: FastAPI + Strawberry, DataLoader, error handling
- Notifications: In-app notifications only (no emails)
- Scheduling: Avoid always-on schedulers; compute “reminders” and progress on-demand (e.g., on dashboard load) to bypass sleeping containers
- Backups: Manual or nightly pg_dump via GitHub Actions (free) to free object storage (Cloudflare R2/B2 free tier)
- Observability: Sentry free, basic logs; minimal Prometheus/Grafana optional on local only
- CI/CD: GitHub Actions free (public repo recommended for unlimited minutes)

Deferred to Paid Phase (because free tiers limit or break UX/SLAs)
- True Point-In-Time Recovery (PITR) (requires paid managed Postgres or self-operated WAL archiving with operational overhead)
- Email notifications at scale (free tiers too limited; deliver in-app first)
- WebSocket subscriptions in production (free PaaS sleeping breaks long-lived connections; start with polling/






```