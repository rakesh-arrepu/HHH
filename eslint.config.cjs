let react;
try {
  react = require('./frontend/node_modules/eslint-plugin-react');
} catch (e) {
  // fallback to normal resolution
  react = require('eslint-plugin-react');
}

let tsPlugin;
try {
  tsPlugin = require('./frontend/node_modules/@typescript-eslint/eslint-plugin');
} catch (e) {
  tsPlugin = require('@typescript-eslint/eslint-plugin');
}
const tsParser = require('@typescript-eslint/parser');

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
