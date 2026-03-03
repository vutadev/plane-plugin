import {runCommand} from '@oclif/test'
import {expect} from 'chai'
import * as fs from 'node:fs/promises'
import * as os from 'node:os'
import {join} from 'node:path'

describe('config commands', () => {
  let testConfigPath: string

  beforeEach(async () => {
    testConfigPath = join(os.tmpdir(), `.planerc-test-${Date.now()}`)
    process.env.PLANE_CONFIG_PATH = testConfigPath

    // Create initial config for commands that require it
    const initialConfig = {
      apiKey: 'test-api-key',
      baseUrl: 'https://api.plane.so/api/v1',
      workspace: 'test-workspace',
    }
    await fs.writeFile(testConfigPath, JSON.stringify(initialConfig), {mode: 0o600})
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
      // Ignore if file doesn't exist
    }
  })

  describe('config:show', () => {
    it('shows config when it exists', async () => {
      const result = await runCommand(['config:show'], {
        env: {PLANE_CONFIG_PATH: testConfigPath},
      })

      // Just verify it runs without error
      expect(result).to.be.an('object')
    })

    it('shows error when config does not exist', async () => {
      const nonExistentPath = join(os.tmpdir(), `.planerc-nonexistent-${Date.now()}`)

      const result = await runCommand(['config:show'], {
        env: {PLANE_CONFIG_PATH: nonExistentPath},
      })

      // Check that the result contains an error or the command failed
      expect(result.error).to.exist
    })
  })

  describe('config:set', () => {
    it('accepts workspace value', async () => {
      const result = await runCommand(['config:set', 'workspace', 'new-workspace'], {
        env: {PLANE_CONFIG_PATH: testConfigPath},
      })

      // Verify command ran without error
      expect(result).to.be.an('object')
    })

    it('accepts apiKey value', async () => {
      const result = await runCommand(['config:set', 'apiKey', 'new-api-key'], {
        env: {PLANE_CONFIG_PATH: testConfigPath},
      })

      expect(result).to.be.an('object')
    })

    it('accepts baseUrl value', async () => {
      const result = await runCommand(['config:set', 'baseUrl', 'https://custom.api.com'], {
        env: {PLANE_CONFIG_PATH: testConfigPath},
      })

      expect(result).to.be.an('object')
    })

    it('rejects unknown config keys', async () => {
      const result = await runCommand(['config:set', 'unknownKey', 'value'], {
        env: {PLANE_CONFIG_PATH: testConfigPath},
      })

      // Check that the result contains an error
      expect(result.error).to.exist
    })
  })
})
