# Security Rules – Auth, Cookies, CSRF, CORS, Headers, Dependency Hygiene

This rule set standardizes security posture across frontend, backend, infra, and CI. It must be followed for any change that touches authentication, authorization, data access, network boundaries, or secrets.

Sections
- Authentication & Session
- Authorization & RBAC
- CSRF, CORS, and Cookies
- Input Validation & Output Encoding
- Secrets & Configuration
- Dependency & Supply Chain
- Transport & Headers
- Logging, Privacy, and Telemetry
- Operational Security & QA

-------------------------------------------------------------------------------

Authentication & Session
- Identity:
  - Primary auth: username/email + password (argon2id on backend).
  - Optional 2FA (TOTP) flows must be additive and backward-compatible.
- Tokens:
  - Short-lived Access JWT + Refresh JWT stored in httpOnly cookies.
  - Rotate refresh tokens on use; invalidate on password reset or logout.
- Session binding:
  - Couple session to user-agent and IP heuristics (tunable) if necessary.
  - Enforce max concurrent sessions per user if business allows.
- Session invalidation:
  - Provide logout-all-sessions endpoint.
  - Blacklist/rotate refresh tokens on password change, 2FA enablement, and account lockout.

-------------------------------------------------------------------------------

Authorization & RBAC
- RBAC:
  - Evaluate all protected actions (REST/GraphQL) in service layer using roles/groups.
  - Consolidate permission checks (avoid spreading across resolvers/handlers).
- Least privilege:
  - Default deny; escalate privileges explicitly per action.
- Multi-tenancy (if applicable):
  - Scope queries and mutations by tenant boundaries.
  - Ensure tenant IDs are validated and not user-controlled blindly.

-------------------------------------------------------------------------------

CSRF, CORS, and Cookies
- CSRF:
  - Use double-submit or header-based token (`X-CSRF-Token`) on mutating requests.
  - Validate token server-side on POST/PUT/PATCH/DELETE.
- CORS:
  - Dev: allow `http://localhost:5173` (or currently active port).
  - Non-dev: explicit origin allowlist; never `*` with credentials.
- Cookies:
  - `httpOnly`, `sameSite=lax` (or `strict`), `secure=true` in production.
  - Limit cookie scope to specific paths where possible; prefix cookie names consistently (e.g., `hhh_at`, `hhh_rt`).

-------------------------------------------------------------------------------

Input Validation & Output Encoding
- Backend:
  - Validate all inputs (REST/GraphQL) before processing (pydantic/explicit validators).
  - Avoid passing raw user input to queries; use parameterized queries only.
- Frontend:
  - Validate forms with client-side rules for UX; never rely on client-only validation.
- Output:
  - Sanitize/encode any user-generated content rendered in UI. Avoid `dangerouslySetInnerHTML`.

-------------------------------------------------------------------------------

Secrets & Configuration
- No secrets in repo or client bundle.
- .env:
  - Frontend: only `VITE_*` (non-sensitive); backend: `.env` not committed.
- Key rotation:
  - Plan for JWT secret rotation. Document in DEPLOYMENT.md.
- Config checks:
  - Fail fast if any required env is missing at startup (backend).

-------------------------------------------------------------------------------

Dependency & Supply Chain
- Dependencies:
  - Keep up-to-date; remediate high/critical quickly.
  - Frontend: `npm audit --audit-level=moderate` during CI (log-only unless breaking).
  - Backend: pin versions in requirements files; optional `pip-audit` in CI.
- Lockfiles:
  - Commit lockfiles; CI caches keyed by lockfile hash.
- Build integrity:
  - Reproducible builds from clean checkout enforced by CI scripts.

-------------------------------------------------------------------------------

Transport & Headers
- TLS:
  - Enforce HTTPS in all environments beyond local dev.
- Security headers (backend middleware/reverse-proxy):
  - HSTS (prod), X-Content-Type-Options, X-Frame-Options/Frame-Ancestors as needed, Referrer-Policy, Content-Security-Policy (tune for app).
- GraphQL introspection:
  - Allowed in dev only; restrict in production unless explicitly required.

-------------------------------------------------------------------------------

Logging, Privacy, and Telemetry
- Logging:
  - Structured logs; avoid logging tokens, secrets, or PII.
  - Redact sensitive fields consistently (central utility).
- Telemetry:
  - Optional Sentry DSN from env; ensure PII scrubbing and sampling in production.
- Auditing:
  - Record sensitive actions in `backend/src/models/audit.py` (user changes, role modifications).

-------------------------------------------------------------------------------

Operational Security & QA
- Backups:
  - Nightly pg_dump to object storage (R2/B2). Test monthly restores.
- Admin:
  - Protect admin endpoints/routes; do not expose admin-only data to regular users.
- QA:
  - Security smoke checklist before release:
    - Cookies flags (secure/httpOnly/sameSite) verified in browser.
    - CORS origin set correctly for environment.
    - CSRF token present and validated on mutations.
    - No sensitive logs in server output.
    - Production GraphQL introspection policy set as per environment.
