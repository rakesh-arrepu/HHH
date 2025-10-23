# Frontend Tasks Tracker

Central place to track all tasks, status, and key info for UI/Frontend development.
_Last updated: 2025-10-23_

---

## Table of Contents

- [Chunk 1: Routing & Core Layout](#chunk-1-routing--core-layout)
- [Chunk 2: Main Feature Pages](#chunk-2-main-feature-pages)
- [Chunk 3: Apollo Client Setup](#chunk-3-apollo-client-setup)
- [Chunk 4: Group Feature Components](#chunk-4-group-feature-components)
- [Chunk 5: Loading, Error, and Empty States](#chunk-5-loading-error-and-empty-states)
- [Chunk 6: Frontend QA Gates](#chunk-6-frontend-qa-gates)
- [Chunk 7: Accessibility & UX](#chunk-7-accessibility--ux)
- [Chunk 8: 404 Fallback & Edge Cases](#chunk-8-404-fallback--edge-cases)
- [Chunk 9: Frontend Tests](#chunk-9-frontend-tests)
- [Chunk 10: Tailwind Baseline & Styling](#chunk-10-tailwind-baseline--styling)
- [Chunk 11: Other/Backlog](#chunk-11-otherbacklog)

---

## Chunk 1: Routing & Core Layout

**Description:** Setup & manage React Router in `App.tsx`, core page skeletons, shared layout (Header, ErrorBoundary).
- **Status:** ✅ Done
- **Files:** `frontend/src/App.tsx`, `frontend/src/components/common/Header.tsx`, `frontend/src/components/common/ErrorBoundary.tsx`
- **Open points:** Add 404 fallback route (see Chunk 8)

---

## Chunk 2: Main Feature Pages

**Description:** Implement and route Dashboard, Groups, Profile, Admin, Login, Register, and SignUp pages.
- **Status:** ✅ Done (routes/page skeletons); Features under active development
- **Files:** `frontend/src/pages/`
- **Notes:** Review per-feature completeness as per each component/route

---

## Chunk 3: Apollo Client Setup

**Description:** Configure Apollo Client (`src/lib/apollo.ts`), wrap app with `ApolloProvider` in `src/main.tsx`, ensure VITE_API_URL/credentials.
- **Status:** ✅ Done
- **Files:** `frontend/src/lib/apollo.ts`, `frontend/src/main.tsx`
- **Checklist:**
  - [x] Apollo instance configured per rules
  - [x] ApolloProvider wraps App

---

## Chunk 4: Group Feature Components

**Description:** Build & wire `GroupList`, `GroupManagement`, `MemberList`, for group features, with full UI flows.
- **Status:** ✅ Done
- **Files:** `frontend/src/components/groups/`, `frontend/src/pages/Groups.tsx`
- **Checklist:**
  - [x] Component skeletons exist
  - [x] Complete GraphQL data wiring
  - [x] Add necessary loading/error/empty states

---

## Chunk 5: Loading, Error, and Empty States

**Description:** Add user-facing loading, empty, and error states for all lists, forms, and mutation flows.
- **Status:** ⏳ Partially done; group flows complete, dashboard stats need API/state, review others
- **Files:** `frontend/src/components/`, per-page
- **Checklist:**
  - [ ] Dashboard analytics/stats (Analytics, StreakCounter, ProgressBar) wired with real API data & UI state (loading/error/empty)
  - [ ] Dashboard lists
  - [x] Groups lists/forms
  - [ ] Auth flows
  - [ ] Global error boundary catches UI failures

---

## Chunk 6: Frontend QA Gates

**Description:** Ensure all quality gates for PR: `npm run lint`, `npm run build` pass cleanly.
- **Status:** ⏳ To do (ensure zero errors)
- **Files:** `frontend/package.json`
- **Checklist:**
  - [ ] Lint clean
  - [ ] Build clean

---

## Chunk 7: Accessibility & UX

**Description:** Add/verify accessible labels, aria-*, keyboard navigation, responsive layouts, and UX polish.
- **Status:** ⏳ Planned
- **Files:** all FE components/pages
- **Checklist:**
  - [ ] Accessible forms/components
  - [ ] Responsive layouts

---

## Chunk 8: 404 Fallback & Edge Cases

**Description:** Add route/page for 404 (unknown/not found) and handle navigation edge cases.
- **Status:** ✅ Done
- **Files:** `frontend/src/App.tsx`
- **Checklist:**
  - [x] Implement <Route path="*" ... /> with fallback UI

---

## Chunk 9: Frontend Tests

**Description:** Add minimal unit/component tests for key UI features.
- **Status:** ⏳ To do
- **Files:** tbd
- **Checklist:**
  - [ ] Add tests infra (Jest/React Testing Library or preferred)
  - [ ] Cover key pages/components

---

## Chunk 10: Tailwind Baseline & Styling

**Description:** Ensure baseline Tailwind styles, body styling in `src/index.css`, consistent use of v4.
- **Status:** ⏳ To do (verify and confirm)
- **Files:** `frontend/postcss.config.js`, `frontend/src/index.css`, `frontend/tailwind.config.js`
- **Checklist:**
  - [ ] Baseline visible body styles in index.css
  - [ ] V4 plugin in postcss.config.js
  - [ ] Tailwind config content correct

---

## Chunk 12: Backend Strawberry Dict Return Types Bug

**Description:** Refactor all `-> dict` return types for GraphQL (groupAnalytics, globalAnalytics, exportMyData, triggerBackup) to use proper `@strawberry.type` wrappers, as required by Strawberry GraphQL.
- **Status:** 🚧 In progress
- **Checklist:**
  - [ ] Identify all affected resolver return types in backend/src/api/graphql/schema.py
  - [ ] Create missing `@strawberry.type` wrappers for each field
  - [ ] Update resolver signatures and return statements to use types
  - [ ] Confirm backend boot with no errors
  - [ ] Resume server up/testing flows for FE/BE
  - [ ] Document fix/result

---

## Chunk 11: Other/Backlog

**Description:** Track any newly identified tasks, reusable refactors, code hygiene, doc updates, etc.
- **Status:** 📋 Open
- **Examples:**
  - [ ] Review import hygiene
  - [ ] Remove unused code
  - [ ] Update docs for new UI/API changes

---

_This document to be updated as progress is made or new chunks appear._
