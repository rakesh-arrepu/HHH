# /frontend-dev.md – Frontend Development Workflow (Vite + React + TS + Tailwind v4 + Apollo)

This workflow automates and documents the steps to develop, validate, and preview the frontend app. It encodes the active Cline Rules in `.clinerules/02-frontend.md` and `.clinerules/01-project-rules.md`.

Sections
- Prerequisites & Environment
- Tailwind v4/PostCSS sanity checks
- Install, Lint, Build
- Dev server (hot reload) and Production Preview
- CSS troubleshooting quick-fix
- Optional: Apollo/GraphQL smoke
- Success criteria

-------------------------------------------------------------------------------

## 1) Prerequisites & Environment

- Node 18+ recommended.
- Ensure env file exists (copied from template):
  ```bash
  cp -n frontend/.env.example frontend/.env 2>/dev/null || true
  ```
- Verify Vite API URL:
  - `frontend/.env` contains `VITE_API_URL=http://localhost:8000` (or your backend URL).

-------------------------------------------------------------------------------

## 2) Tailwind v4 / PostCSS sanity checks

These must match our rules:
- frontend/postcss.config.js must use the Tailwind v4 plugin:
  ```js
  module.exports = {
    plugins: { '@tailwindcss/postcss': {} },
  };
  ```
- frontend/src/index.css must import Tailwind v4:
  ```css
  @import "tailwindcss";
  /* baseline visible styles helpful for verification */
  :root { color-scheme: light; }
  body { background-color: #f9fafb; color: #111827; }
  ```
- frontend/tailwind.config.js must include:
  ```js
  module.exports = {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    theme: { extend: {} },
    plugins: []
  }
  ```
- frontend/vite.config.ts must point to PostCSS config:
  ```ts
  export default defineConfig({
    plugins: [react()],
    css: { postcss: './postcss.config.js' }
  })
  ```

If any mismatch, fix before proceeding.

-------------------------------------------------------------------------------

## 3) Install, Lint, Build

```bash
cd frontend
npm ci
npm run lint
npm run build
```

Expected:
- Lint passes with 0 errors (warnings acceptable if rule allows).
- Vite build succeeds and outputs `dist/assets/index-*.css` and `index-*.js`.

-------------------------------------------------------------------------------

## 4) Run Dev Server and Production Preview

- Dev server (hot reload):
  ```bash
  npm run dev
  # Open the printed local URL, e.g., http://localhost:5173
  ```
- Production preview (serves dist):
  ```bash
  # In a separate terminal
  npm run preview -- --port 5175
  # Open http://localhost:5175
  ```

Verify:
- Header/navigation shown
- Dashboard grid layout (Analytics / StreakCounter / ProgressBar) styled
- Baseline body background (light gray) and typography applied
- Forms (Login/Register/EntryForm) have Tailwind styling

-------------------------------------------------------------------------------

## 5) CSS troubleshooting quick-fix (use if styles are missing)

If you don’t see Tailwind styles:

- Confirm the plugin package is installed:
  ```bash
  cd frontend
  npm i -D @tailwindcss/postcss
  ```
- Ensure `postcss.config.js` exactly uses:
  ```js
  module.exports = { plugins: { '@tailwindcss/postcss': {} } };
  ```
- Clear Vite cache and force re-optimize:
  ```bash
  pkill -f "vite|vite preview" || true
  rm -rf node_modules/.vite
  npm run dev -- --force
  ```
- Hard-refresh the browser (Cmd+Shift+R on macOS)

-------------------------------------------------------------------------------

## 6) Optional: Apollo/GraphQL smoke

With backend running at `VITE_API_URL`:
- Confirm `frontend/src/lib/apollo.ts` uses:
  - `HttpLink` to `${import.meta.env.VITE_API_URL}/graphql`
  - `credentials: 'include'`
- Add a trivial query component and render on Dashboard (future step).
- Verify network calls succeed (200) and errorLink logs GraphQL errors to console in dev.

-------------------------------------------------------------------------------

## 7) Success criteria

- Dev server runs and renders styled UI (Tailwind v4 utility classes visible)
- Production preview serves compiled CSS bundle with styles applied
- Lint and build pass locally
- Env is correctly injected (Vite rebuild picks up `.env` changes)
- Navigation works (Dashboard, Groups, Profile, Admin, Login/Register)

-------------------------------------------------------------------------------

## References (Rules)

- `.clinerules/02-frontend.md` – Frontend rules (Tailwind v4, Vite config, Apollo)
- `.clinerules/01-project-rules.md` – Project-wide rules (quality gates, structure)

-------------------------------------------------------------------------------

## One-shot command set (copy/paste)

```bash
cd frontend \
&& npm ci \
&& npm run lint \
&& npm run build \
&& (npm run preview -- --port 5175 &> /dev/null &); sleep 1; echo "Preview on http://localhost:5175" \
&& pkill -f "vite|vite preview" || true \
&& rm -rf node_modules/.vite \
&& npm run dev -- --force
```

If CSS not applied, ensure:
- postcss.config.js uses @tailwindcss/postcss
- src/index.css contains `@import "tailwindcss"`
- tailwind.config.js includes ./index.html and ./src/**/*
