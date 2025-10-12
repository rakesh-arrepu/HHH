# GraphQL Rules – Strawberry (Backend) + Apollo (Frontend)

These rules standardize our GraphQL schema, resolver, client usage, error handling, and performance practices.

Sections
- Schema Organization (Backend)
- Resolvers & Services
- Data Loading & N+1 Prevention
- Errors & Result Envelopes
- Pagination, Filtering, Sorting
- Security (AuthN/Z, Field-Level Considerations)
- Client (Apollo) Conventions
- Testing & Tooling
- Quality Gates

-------------------------------------------------------------------------------

Schema Organization (Backend)
- Location: `backend/src/api/graphql/schema.py`
  - Keep clear `Query` and `Mutation` roots; group fields by domain (users, groups, entries).
- Types
  - Use typed Strawberry types (`@strawberry.type`, `@strawberry.input`), not untyped dicts.
  - Model-to-type mapping should avoid leaking ORM internals; construct types explicitly.
- Modularity
  - Split schema into modules by feature if it grows, but keep a single import surface in `schema.py`.
- Introspection
  - Enabled in dev; restrict in production unless explicitly required (see Security rules).

-------------------------------------------------------------------------------

Resolvers & Services
- Thin resolvers
  - Resolvers should validate inputs and delegate domain logic to `backend/src/services/*`.
  - No DB sessions in resolvers; service layer handles persistence and transactions.
- Validation
  - Validate inputs at resolver boundary (types, constraints), raise typed domain errors for expected failures.
- Context
  - Extract auth/user context from request/session in a dedicated helper; do not re-parse in every resolver.

-------------------------------------------------------------------------------

Data Loading & N+1 Prevention
- Use DataLoader
  - Implement loaders in `backend/src/api/graphql/dataloaders.py`.
  - Batch DB calls per request for relational fields (e.g., entry -> user, group -> members).
- Patterns
  - Preload relations in service functions if batch loaders are insufficient.
  - Avoid `.all()` or repeated per-node queries inside loops.

-------------------------------------------------------------------------------

Errors & Result Envelopes
- Domain Errors
  - Represent expected domain failures (e.g., unauthorized, validation error) with typed error objects or consistent envelopes.
  - Return safe messages; avoid leaking stack traces or sensitive details.
- Unexpected Errors
  - Log (with correlation/request ID) and surface as generic errors to clients.
- Client Handling
  - Frontend must handle `graphQLErrors` and `networkError` in Apollo; show user-friendly toasts or inline messages.

-------------------------------------------------------------------------------

Pagination, Filtering, Sorting
- Pagination
  - Cursor or offset pagination as business needs dictate; keep consistent per domain.
  - Include `pageInfo` (hasNext/hasPrevious, cursors) for cursor-based.
- Filtering/Sorting
  - Validate filter/sort fields; whitelist allowed fields; default deterministic order.
- Limits
  - Enforce reasonable `limit` caps server-side to prevent abuse.

-------------------------------------------------------------------------------

Security (AuthN/Z, Field-Level Considerations)
- AuthN
  - Use JWT (httpOnly cookies) + CSRF protections per backend security rules.
- AuthZ
  - Check permissions in service layer for all protected resolvers.
  - Avoid accidental data leakage via nested relations; confirm permissions for related objects.
- PII
  - Mask/omit PII fields by default unless caller is authorized.

-------------------------------------------------------------------------------

Client (Apollo) Conventions
- Setup
  - Single client in `frontend/src/lib/apollo.ts`:
    - `HttpLink` with `${import.meta.env.VITE_API_URL}/graphql`
    - `credentials: 'include'` for cookie auth
    - `errorLink` to log GraphQL/network errors
    - `InMemoryCache` with defaults
  - Wrap app with `ApolloProvider` in `src/main.tsx`.
- Query/Mutation Files
  - Co-locate operations with features or group under `src/graphql/*` when shared.
  - Keep fragments in `src/graphql/fragments.ts`.
- UI States
  - All GraphQL-driven components must implement loading, error, and empty states.
  - Prefer optimistic UI where safe; rollback on failure.
- Env
  - Read API URL from `VITE_API_URL`; do not hardcode endpoints.

-------------------------------------------------------------------------------

Testing & Tooling
- Backend
  - Unit tests for service logic; integration tests for GraphQL endpoints.
  - Include tests for pagination, authz, and error envelopes.
- Frontend
  - Component tests for loading/error/empty; mock queries using Apollo testing utilities.
- Codegen (optional)
  - If adopted, configure GraphQL Code Generator to produce types/hooks; keep artifacts updated.

-------------------------------------------------------------------------------

Quality Gates
- Backend
  - `pytest` must pass; add tests for new schema fields and their auth rules.
- Frontend
  - `npm run build && npm run lint` must pass; ensure error states are covered.
- Docs
  - Update `docs/API.md` when schema changes impact API behavior or types.
