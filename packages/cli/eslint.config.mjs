import {includeIgnoreFile} from '@eslint/compat'
import oclif from 'eslint-config-oclif'
import prettier from 'eslint-config-prettier'
import path from 'node:path'
import {fileURLToPath} from 'node:url'

const gitignorePath = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '.gitignore')

export default [
  includeIgnoreFile(gitignorePath),
  ...oclif,
  prettier,
  {
    rules: {
      // API response fields use snake_case — can't control external API shape
      camelcase: 'off',
      // CLI tools legitimately use process.exit for non-zero exit codes
      'n/no-process-exit': 'off',
      // Allow fetch (globally available in Node 18+)
      'n/no-unsupported-features/node-builtins': ['error', {
        ignores: ['fetch'],
      }],
      'unicorn/no-process-exit': 'off',
    },
  },
  {
    files: ['test/**/*.ts'],
    languageOptions: {
      globals: {
        // Node 18+ fetch API globals available in test environment
        RequestInfo: 'readonly',
        RequestInit: 'readonly',
        Response: 'readonly',
      },
    },
    rules: {
      // Tests use any for mocks
      '@typescript-eslint/no-explicit-any': 'off',
      // Response/Request/fetch are Node 18+ globals — valid in test environment
      'n/no-unsupported-features/node-builtins': ['error', {
        ignores: ['fetch', 'Response', 'Request'],
      }],
    },
  },
]
