import {expect} from 'chai'
import * as fs from 'node:fs/promises'
import * as os from 'node:os'
import {join} from 'node:path'

describe('config', () => {
  let testConfigPath: string

  beforeEach(async () => {
    testConfigPath = join(os.tmpdir(), `.planerc-test-${Date.now()}`)
  })

  afterEach(async () => {
    // Clean up env vars
    delete process.env.PLANE_API_KEY
    delete process.env.PLANE_ACCESS_TOKEN
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

  it('returns null when no config exists', async () => {
    // Import fresh module to avoid caching
    process.env.PLANE_CONFIG_PATH = testConfigPath
    const {getConfig} = await import('../../src/lib/config.js')

    const config = await getConfig()
    expect(config).to.be.null
  })

  it('loads config from file', async () => {
    const testConfig = {
      apiKey: 'test-api-key',
      baseUrl: 'https://api.plane.so/api/v1',
      workspace: 'test-workspace',
    }
    await fs.writeFile(testConfigPath, JSON.stringify(testConfig), {mode: 0o600})

    process.env.PLANE_CONFIG_PATH = testConfigPath
    const {getConfig} = await import('../../src/lib/config.js')

    const config = await getConfig()
    expect(config).to.not.be.null
    expect(config?.workspace).to.equal('test-workspace')
    expect(config?.apiKey).to.equal('test-api-key')
  })

  it('env vars override file config', async () => {
    const fileConfig = {apiKey: 'file-key', workspace: 'file-workspace'}
    await fs.writeFile(testConfigPath, JSON.stringify(fileConfig), {mode: 0o600})

    process.env.PLANE_CONFIG_PATH = testConfigPath
    process.env.PLANE_API_KEY = 'env-api-key'

    const {getConfig} = await import('../../src/lib/config.js')
    const config = await getConfig()

    expect(config?.apiKey).to.equal('env-api-key')
    expect(config?.workspace).to.equal('file-workspace')
  })

  it('saveConfig writes config to file', async () => {
    process.env.PLANE_CONFIG_PATH = testConfigPath

    const testConfig = {
      apiKey: 'test-api-key',
      workspace: 'test-workspace',
    }

    const {saveConfig} = await import('../../src/lib/config.js')
    await saveConfig(testConfig)

    const content = await fs.readFile(testConfigPath, 'utf8')
    const saved = JSON.parse(content)
    expect(saved.workspace).to.equal('test-workspace')
    expect(saved.apiKey).to.equal('test-api-key')
  })

  it('uses access token when api key not provided', async () => {
    process.env.PLANE_CONFIG_PATH = testConfigPath
    process.env.PLANE_ACCESS_TOKEN = 'env-access-token'
    process.env.PLANE_WORKSPACE_SLUG = 'env-workspace'

    const {getConfig} = await import('../../src/lib/config.js')
    const config = await getConfig()
    expect(config?.accessToken).to.equal('env-access-token')
    expect(config?.workspace).to.equal('env-workspace')
  })

  it('getConfigPath respects PLANE_CONFIG_PATH', async () => {
    process.env.PLANE_CONFIG_PATH = testConfigPath

    const {getConfigPath} = await import('../../src/lib/config.js')
    const path = getConfigPath()
    expect(path).to.equal(testConfigPath)
  })
})
