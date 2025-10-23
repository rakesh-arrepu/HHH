module.exports = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx'],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest'
  },
  setupFilesAfterEnv: ['<rootDir>/src/test/setupTests.ts'],
  moduleNameMapper: {
    '\\.(css|less|scss)$': 'identity-obj-proxy'
  },
  testPathIgnorePatterns: ['/node_modules/', '/dist/'],
};
