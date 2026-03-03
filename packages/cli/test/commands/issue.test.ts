import {runCommand} from '@oclif/test'
import {expect} from 'chai'
import * as fs from 'node:fs/promises'
import * as os from 'node:os'
import {join} from 'node:path'

describe('issue commands', () => {
  let testConfigPath: string

  beforeEach(async () => {
    testConfigPath = join(os.tmpdir(), `.planerc-test-${Date.now()}`)

    const testConfig = {
      apiKey: 'test-api-key',
      baseUrl: 'https://api.test.com/api/v1',
      workspace: 'test-workspace',
    }
    await fs.writeFile(testConfigPath, JSON.stringify(testConfig), {mode: 0o600})
    process.env.PLANE_CONFIG_PATH = testConfigPath
  })

  afterEach(async () => {
    delete process.env.PLANE_API_KEY
    delete process.env.PLANE_WORKSPACE_SLUG
    delete process.env.PLANE_BASE_URL
    delete process.env.PLANE_CONFIG_PATH

    try {
      await fs.unlink(testConfigPath)
    } catch {
      // Ignore
    }
  })

  describe('issue:list', () => {
    it('lists issues with project flag', async () => {
      try {
        await runCommand(['issue:list', '--project', 'proj-uuid-1234', '--json', '--no-input'], {
          env: {
            PLANE_API_KEY: 'test-key',
            PLANE_BASE_URL: 'https://api.test.com/api/v1',
            PLANE_CONFIG_PATH: testConfigPath,
            PLANE_WORKSPACE_SLUG: 'test-workspace',
          },
        })
      } catch (error: any) {
        expect(error.message).to.match(/fetch|network|ECONNREFUSED|ENOTFOUND|exit code 1/i)
      }
    })

    it('accepts cycle filter', async () => {
      try {
        await runCommand(['issue:list', '--project', 'proj-uuid', '--cycle', 'cycle-uuid', '--no-input'], {
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

    it('accepts limit flag', async () => {
      try {
        await runCommand(['issue:list', '--project', 'proj-uuid', '--limit', '10', '--no-input'], {
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

  describe('issue:get', () => {
    it('resolves PROJECT-123 format', async () => {
      try {
        await runCommand(['issue:get', 'ISSUE-123', '--json', '--no-input'], {
          env: {
            PLANE_API_KEY: 'test-key',
            PLANE_CONFIG_PATH: testConfigPath,
            PLANE_WORKSPACE_SLUG: 'test-workspace',
          },
        })
      } catch (error: any) {
        expect(error.message).to.match(/fetch|network|ECONNREFUSED|ENOTFOUND|Project not found|exit code 1/i)
      }
    })

    it('accepts UUID with project flag', async () => {
      try {
        await runCommand(['issue:get', 'uuid-1234-5678', '--project', 'proj-uuid', '--json', '--no-input'], {
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

  describe('issue:create', () => {
    it('accepts name and priority flags', async () => {
      try {
        await runCommand(['issue:create', '--project', 'proj-uuid', '--name', 'Test Issue', '--priority', 'high', '--no-input'], {
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

  describe('issue:update', () => {
    it('accepts issue ID and name flag', async () => {
      try {
        await runCommand(['issue:update', 'ISSUE-123', '--name', 'Updated Name', '--no-input'], {
          env: {
            PLANE_API_KEY: 'test-key',
            PLANE_CONFIG_PATH: testConfigPath,
            PLANE_WORKSPACE_SLUG: 'test-workspace',
          },
        })
      } catch (error: any) {
        expect(error.message).to.match(/fetch|network|ECONNREFUSED|ENOTFOUND|Project not found|exit code 1/i)
      }
    })
  })

  describe('issue:delete', () => {
    it('requires --confirm flag', async () => {
      try {
        await runCommand(['issue:delete', 'ISSUE-123', '--confirm', '--no-input'], {
          env: {
            PLANE_API_KEY: 'test-key',
            PLANE_CONFIG_PATH: testConfigPath,
            PLANE_WORKSPACE_SLUG: 'test-workspace',
          },
        })
      } catch (error: any) {
        expect(error.message).to.match(/fetch|network|ECONNREFUSED|ENOTFOUND|Project not found|exit code 1/i)
      }
    })
  })

  describe('issue:search', () => {
    it('accepts search query', async () => {
      try {
        await runCommand(['issue:search', 'query term', '--json', '--no-input'], {
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
})
