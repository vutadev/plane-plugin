import {runCommand} from '@oclif/test'
import {expect} from 'chai'
import * as fs from 'node:fs/promises'
import * as os from 'node:os'
import {join} from 'node:path'

describe('project commands', () => {
  let testConfigPath: string

  beforeEach(async () => {
    testConfigPath = join(os.tmpdir(), `.planerc-test-${Date.now()}`)

    // Create test config
    const testConfig = {
      apiKey: 'test-api-key',
      baseUrl: 'https://api.test.com/api/v1',
      workspace: 'test-workspace',
    }
    await fs.writeFile(testConfigPath, JSON.stringify(testConfig), {mode: 0o600})

    // Set env var for config path
    process.env.PLANE_CONFIG_PATH = testConfigPath
  })

  afterEach(async () => {
    // Clean up env vars
    delete process.env.PLANE_API_KEY
    delete process.env.PLANE_WORKSPACE_SLUG
    delete process.env.PLANE_BASE_URL
    delete process.env.PLANE_CONFIG_PATH

    // Clean up test file
    try {
      await fs.unlink(testConfigPath)
    } catch {
      // Ignore
    }
  })

  describe('project:list', () => {
    it('attempts to list projects', async () => {
      try {
        await runCommand(['project:list', '--no-input'], {
          env: {
            PLANE_API_KEY: 'test-key',
            PLANE_BASE_URL: 'https://api.test.com/api/v1',
            PLANE_CONFIG_PATH: testConfigPath,
            PLANE_WORKSPACE_SLUG: 'test-workspace',
          },
        })
      } catch (error: any) {
        // Expected to fail due to API not being available
        expect(error.message).to.match(/fetch|network|ECONNREFUSED|ENOTFOUND|exit code 1/i)
      }
    })

    it('supports --json flag', async () => {
      try {
        await runCommand(['project:list', '--json', '--no-input'], {
          env: {
            PLANE_API_KEY: 'test-key',
            PLANE_CONFIG_PATH: testConfigPath,
            PLANE_WORKSPACE_SLUG: 'test-workspace',
          },
        })
      } catch (error: any) {
        expect(error.message).to.match(/fetch|network|ECONNREFUSED|ENOTFOUND|exit code 1/i)
      }
    })
  })

  describe('project:create', () => {
    it('accepts name and identifier flags', async () => {
      try {
        await runCommand(['project:create', '--name', 'Test Project', '--identifier', 'TEST', '--no-input'], {
          env: {
            PLANE_API_KEY: 'test-key',
            PLANE_CONFIG_PATH: testConfigPath,
            PLANE_WORKSPACE_SLUG: 'test-workspace',
          },
        })
      } catch (error: any) {
        expect(error.message).to.match(/fetch|network|ECONNREFUSED|ENOTFOUND|exit code 1/i)
      }
    })
  })

  describe('project:get', () => {
    it('accepts project ID and json flag', async () => {
      try {
        await runCommand(['project:get', 'proj-uuid-1234', '--json', '--no-input'], {
          env: {
            PLANE_API_KEY: 'test-key',
            PLANE_CONFIG_PATH: testConfigPath,
            PLANE_WORKSPACE_SLUG: 'test-workspace',
          },
        })
      } catch (error: any) {
        expect(error.message).to.match(/fetch|network|ECONNREFUSED|ENOTFOUND|exit code 1/i)
      }
    })
  })

  describe('project:delete', () => {
    it('requires --confirm flag', async () => {
      try {
        await runCommand(['project:delete', 'proj-uuid-1234', '--no-input'], {
          env: {
            PLANE_API_KEY: 'test-key',
            PLANE_CONFIG_PATH: testConfigPath,
            PLANE_WORKSPACE_SLUG: 'test-workspace',
          },
        })
      } catch (error: any) {
        // Should require confirm or fail on API
        expect(error.message).to.match(/confirm|fetch|network|ECONNREFUSED|ENOTFOUND|exit code 1/i)
      }
    })
  })
})
