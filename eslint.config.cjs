let react;
try {
  react = require('./frontend/node_modules/eslint-plugin-react');
} catch (e) {
  // fallback to normal resolution
  react = require('eslint-plugin-react');
}

module.exports = [
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'module',
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    plugins: { react },
    rules: {},
    settings: {
      react: { version: 'detect' },
    },
  },
];
