import {promises as fs} from 'node:fs'
import {homedir} from 'node:os'
import {join} from 'node:path'

import {ConfigSchema, PlaneConfig} from '../types/config.js'

const CONFIG_FILE = '.planerc'

export function getConfigPath(): string {
  // Allow override for testing
  if (process.env.PLANE_CONFIG_PATH) {
    return process.env.PLANE_CONFIG_PATH
  }

  return join(homedir(), CONFIG_FILE)
}

export async function getConfig(): Promise<null | PlaneConfig> {
  // Check env vars first (they override file)
  const envConfig = getConfigFromEnv()

  // Then check config file
  const fileConfig = await getConfigFromFile()

  if (!envConfig && !fileConfig) return null

  // Merge: env overrides file
  const merged = {...fileConfig, ...envConfig} as PlaneConfig
  return ConfigSchema.parse(merged)
}

export async function saveConfig(config: PlaneConfig): Promise<void> {
  const path = getConfigPath()
  await fs.writeFile(path, JSON.stringify(config, null, 2), {mode: 0o600})
}

export async function hasConfig(): Promise<boolean> {
  try {
    const path = getConfigPath()
    await fs.access(path)
    return true
  } catch {
    return false
  }
}

function getConfigFromEnv(): null | Partial<PlaneConfig> {
  const apiKey = process.env.PLANE_API_KEY
  const accessToken = process.env.PLANE_ACCESS_TOKEN
  const workspace = process.env.PLANE_WORKSPACE_SLUG
  const baseUrl = process.env.PLANE_BASE_URL

  if (!apiKey && !accessToken && !workspace) return null

  return {
    ...(apiKey && {apiKey}),
    ...(accessToken && {accessToken}),
    ...(workspace && {workspace}),
    ...(baseUrl && {baseUrl}),
  }
}

async function getConfigFromFile(): Promise<null | PlaneConfig> {
  try {
    const path = getConfigPath()
    const content = await fs.readFile(path, 'utf8')
    return ConfigSchema.parse(JSON.parse(content))
  } catch {
    return null
  }
}
