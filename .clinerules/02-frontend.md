# Frontend Rules – Vite + React + TypeScript + Tailwind v4 + Apollo

These rules must be satisfied for any frontend changes. They encode the fixes and conventions we validated in this project.

Sections
- Tooling & Project Layout
- Tailwind v4 & PostCSS
- Vite Config
- Routing & Pages
- Apollo Client & GraphQL
- UI/UX & Accessibility
- Quality Gates
- Local Dev & Preview

-------------------------------------------------------------------------------

Tooling & Project Layout
- Use Vite for dev/build. Entry file is frontend/index.html (root-level).
- Use TypeScript + React 18 function components.
- Keep UI by feature:
  - pages/* for pages
  - components/* for shared or feature components
  - hooks/* for custom hooks
  - lib/* for setup (apollo, constants, validation)
  - graphql/* for fragments and shared artifacts
- Do not introduce Create React App tooling or webpack. Stick to Vite.

-------------------------------------------------------------------------------

Tailwind v4 & PostCSS
- Only Tailwind v4 plugin via PostCSS (no legacy @tailwind directives).
- Required files:
  1) frontend/postcss.config.js
     plugins: { '@tailwindcss/postcss': {} }
  2) frontend/src/index.css
     @import "tailwindcss";
     Add visible baseline styles in body to verify load.
  3) frontend/tailwind.config.js
     content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}']
- Do not install tailwindcss/forms or other v3-era plugins unless explicitly needed.

-------------------------------------------------------------------------------

Vite Config
- frontend/vite.config.ts must point to PostCSS config:
  export default defineConfig({
    plugins: [react()],
    css: { postcss: './postcss.config.js' }
  })
- Do not add custom CSS preprocessors unless a rule file authorizes them.

-------------------------------------------------------------------------------

Routing & Pages
- Use React Router. Define routes centrally in App.tsx (or a router module).
- Keep routes shallow and lazy-load heavy routes where applicable.
- Header must expose nav for main sections (Dashboard, Groups, Profile, Admin, Auth).
- Include 404 fallback page for invalid routes in future iteration.

-------------------------------------------------------------------------------

Apollo Client & GraphQL
- Provide a single Apollo client (src/lib/apollo.ts) with:
  - HttpLink using `${import.meta.env.VITE_API_URL}/graphql`
  - credentials: 'include' for cookie auth
  - errorLink to log GraphQL/network errors
  - InMemoryCache
- Wrap app in ApolloProvider in src/main.tsx.
- Centralize fragments in src/graphql/fragments.ts.
- Co-locate queries/mutations with the feature using them or in shared folders when reused.
- Handle loading/error states in all GraphQL-driven components.

-------------------------------------------------------------------------------

UI/UX & Accessibility
- Use Tailwind utility classes for responsiveness.
- Ensure form fields have accessible labels and aria-* where appropriate.
- Provide loading, empty, and error states across:
  - Dashboard lists
  - Entries (create/list)
  - Groups (list/manage)
  - Auth flows (login/register)
- Prefer headless/accessibility-first components (e.g., @headlessui/react) when needed.

-------------------------------------------------------------------------------

Quality Gates
- The following must pass locally before PR:
  - npm run build (Vite build must succeed)
  - npm run lint (no errors; warnings acceptable only if rule allows)
- Keep TypeScript strict; address types over suppressing them.
- Do not push .vite cache or dist outputs.

-------------------------------------------------------------------------------

Local Dev & Preview
- Start dev server:
  npm run dev
  - If port conflict, allow Vite to switch. Confirm port in terminal and open in browser.
- Production preview:
  npm run build && npm run preview
  - Confirm CSS bundle generated under dist/assets and styles render.

-------------------------------------------------------------------------------

Gotchas (Lessons Learned)
- Tailwind v4 requires @tailwindcss/postcss plugin; do not use legacy tailwindcss in postcss.config.js.
- Use @import "tailwindcss"; not @tailwind base/components/utilities for v4.
- Ensure Vite points to postcss.config.js via css.postcss or config may be ignored.
