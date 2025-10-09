const react = require('eslint-plugin-react');

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
