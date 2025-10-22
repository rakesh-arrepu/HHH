# API

This document describes the backend API: REST auth endpoints and the GraphQL schema including CSRF and cookie semantics.

Base URL
- Local development: http://localhost:8000
- GraphQL endpoint: /graphql
- REST base (auth): /api/v1/auth

Security Overview
- Session cookies:
  - Access: ACCESS_COOKIE_NAME (default hhh_at) – short-lived, httpOnly, SameSite=lax, Secure in prod
  - Refresh: REFRESH_COOKIE_NAME (default hhh_rt) – longer-lived, httpOnly, SameSite=lax, Secure in prod
- CSRF:
  - CSRF cookie: CSRF_COOKIE_NAME (default hhh_csrf) – non-httpOnly, readable by JS
  - Header required for mutating methods (POST/PUT/PATCH/DELETE): CSRF_HEADER_NAME (default X-CSRF-Token)
  - Safe methods (GET/HEAD/OPTIONS) do not require CSRF header
- CORS:
  - Credentials enabled. Ensure origin allowlist includes your frontend DEV origin(s).

--------------------------------------------------------------------------------

REST: Auth Endpoints (/api/v1/auth)

Health
- GET /api/v1/auth/health
- Purpose: Liveness check. Also ensures a CSRF cookie is set for the client if missing.
- Response: { "status": "ok" }
- CSRF: Not required

Register
- POST /api/v1/auth/register
- Body:
  {
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe"
  }
- CSRF: Required – include X-CSRF-Token header matching hhh_csrf cookie
- Response:
  - 201 Created
  - Body:
    {
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "name": "John Doe"
      }
    }
  - Sets httpOnly cookies: hhh_at (access), hhh_rt (refresh)
- Errors:
  - 400/409 with detail message (validation/duplicate)

Login
- POST /api/v1/auth/login
- Body:
  {
    "email": "user@example.com",
    "password": "password123"
  }
- CSRF: Required – include X-CSRF-Token header matching hhh_csrf cookie
- Response:
  - 200 OK
  - Body:
    {
      "user": {
        "id": "uuid",
        "email": "user@example.com",
        "name": "John Doe"
      }
    }
  - Sets httpOnly cookies: hhh_at (access), hhh_rt (refresh)
- Errors:
  - 401 Invalid credentials

Refresh
- POST /api/v1/auth/refresh
- Body: none
- CSRF: Required – include X-CSRF-Token header matching hhh_csrf cookie
- Behavior: Reads refresh cookie, issues new access and refresh cookies (rotation)
- Response:
  - 200 OK
  - Body: { "status": "ok" }
- Errors:
  - 401 Missing/invalid refresh token

Logout
- POST /api/v1/auth/logout
- Body: none
- CSRF: Required – include X-CSRF-Token header
- Behavior: Clears access and refresh cookies
- Response: 204 No Content

Example: CSRF Flow with curl
1) Obtain CSRF cookie via health:
   curl -i -c cookies.txt http://localhost:8000/api/v1/auth/health

2) Extract CSRF value (hhh_csrf) from cookies.txt, then:
   CSRF=$(grep hhh_csrf cookies.txt | awk '{print $7}')
   curl -i -b cookies.txt -c cookies.txt \
     -H "Content-Type: application/json" \
     -H "X-CSRF-Token: $CSRF" \
     -d '{"email":"user@example.com","password":"password123","name":"User"}' \
     http://localhost:8000/api/v1/auth/register

--------------------------------------------------------------------------------

GraphQL API (/graphql)

Transport and CSRF
- Queries:
  - Use GET where possible (safe method, no CSRF header required)
- Mutations:
  - Use POST and MUST include CSRF header X-CSRF-Token whose value equals the hhh_csrf cookie
- Cookies:
  - Access/refresh cookies are sent with requests (credentials: include)

Schema Summary

Query
- health: String
  - Returns "ok" for liveness
- entries_today(user_id: String!, group_id: String): [Entry!]!
  - Returns today's non-deleted entries for a user (optionally scoped by group)

Types
- enum SectionType { Health, Happiness, Hela }
- type Entry {
    id: ID!
    user_id: String!
    group_id: String!
    section_type: SectionType!
    content: String!
    entry_date: Date!
    edit_count: Int!
    is_flagged: Boolean!
    flagged_reason: String
  }

Mutations
- createEntry(input: CreateEntryInput!): Entry!
- updateEntry(id: ID!, input: UpdateEntryInput!): Entry!
- deleteEntry(id: ID!): Boolean!

Inputs
- input CreateEntryInput {
    user_id: String!
    group_id: String!
    section_type: SectionType!
    content: String!
    entry_date: Date
  }
- input UpdateEntryInput {
    content: String
    section_type: SectionType
  }

Examples

Query health (GET):
- GET /graphql?query=%7B%20health%20%7D
- Response:
  {
    "data": { "health": "ok" }
  }

Query entries_today (GET):
- GET /graphql?query=query%20(%24uid%3A%20String!)%7B%20entries_today(user_id%3A%20%24uid)%7B%20id%20content%20section_type%20%7D%7D&variables=%7B%22uid%22%3A%22USER_ID%22%7D

Mutation createEntry (POST) – requires CSRF header:
- POST /graphql
- Headers:
  - Content-Type: application/json
  - X-CSRF-Token: <value_of_hhh_csrf_cookie>
- Body:
  {
    "query": "mutation ($input: CreateEntryInput!) { createEntry(input: $input) { id content section_type } }",
    "variables": {
      "input": {
        "user_id": "USER_ID",
        "group_id": "GROUP_ID",
        "section_type": "Health",
        "content": "Walked 5k steps"
      }
    }
  }

--------------------------------------------------------------------------------

Cookie & CSRF Details

Cookies
- ACCESS_COOKIE_NAME (default hhh_at): httpOnly; short-lived access token
- REFRESH_COOKIE_NAME (default hhh_rt): httpOnly; refresh token; rotated on refresh
- Flags:
  - SameSite=lax
  - Secure: true in production (SECURE_COOKIES=true) and false for dev
  - Domain:
    - COOKIE_DOMAIN is used in production (e.g., example.com)
    - For local tests (testserver), cookie domain may be omitted to ensure acceptance

CSRF
- Cookie: hhh_csrf (readable by JS)
- Header: X-CSRF-Token must equal cookie value for mutating requests
- SAFE_METHODS (GET/HEAD/OPTIONS) do not require CSRF

Errors
- 400/409 – Bad Request / Conflict
- 401 – Unauthorized (e.g., invalid credentials/refresh token)
- 403 – CSRF validation failed
- 5xx – Internal Server Error

--------------------------------------------------------------------------------

Frontend Guidelines
- Apollo client:
  - Use credentials: 'include'
  - Use GET for queries
  - Attach X-CSRF-Token only for non-Query operations (from hhh_csrf cookie)
- REST calls (Login/Register/Refresh/Logout):
  - Use credentials: 'include'
  - Include X-CSRF-Token header for POST endpoints

--------------------------------------------------------------------------------

Notes
- Dev vs Prod:
  - Secure cookies and explicit COOKIE_DOMAIN should be used in production
  - CORS origins should be strictly controlled outside dev
- Migrations and DB:
  - In dev, SQLite may be used (default); in production Postgres is recommended
