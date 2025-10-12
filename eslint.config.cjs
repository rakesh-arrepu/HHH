const path = require('path');
const { createRequire } = require('module');

// Helper that tries a few resolution strategies so this config can be
// executed from the repository root (IDE) or from the frontend/ folder
// (CI step that runs `cd frontend && npm run lint`).
function tryRequireFromFrontend(relPath, pkgName) {
  // 1) Try explicit path relative to repository root (./frontend/node_modules/...)
  try {
    return require(relPath);
  } catch (e) {
    // ignore
  }

  // 2) Try to require by package name (normal resolution from this file)
  try {
    return require(pkgName);
  } catch (e) {
    // ignore
  }

  // 3) Try to require relative to process.cwd() (useful when eslint is
  // executed with CWD=frontend so node_modules are located there).
  try {
    const cwdPkgJson = path.join(process.cwd(), 'package.json');
    const cwdRequire = createRequire(cwdPkgJson);
    return cwdRequire(pkgName);
  } catch (e) {
    // ignore
  }

  return null;
}

const react = tryRequireFromFrontend('./frontend/node_modules/eslint-plugin-react', 'eslint-plugin-react');
const tsPlugin = tryRequireFromFrontend('./frontend/node_modules/@typescript-eslint/eslint-plugin', '@typescript-eslint/eslint-plugin');
const tsParser = (function () {
  const p = tryRequireFromFrontend('./frontend/node_modules/@typescript-eslint/parser', '@typescript-eslint/parser');
  if (p) return p;
  // last resort: use normal require which will throw with a helpful message
  return require('@typescript-eslint/parser');
})();

module.exports = [
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    ignores: ['node_modules/**', 'backend/**/.venv/**', 'backend/**/__pycache__/**'],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'module',
      parser: tsParser,
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    plugins: { react, '@typescript-eslint': tsPlugin },
    rules: {
      'react/react-in-jsx-scope': 'off',
      '@typescript-eslint/no-unused-vars': 'warn',
    },
    settings: {
      react: { version: 'detect' },
    },
  },
];
