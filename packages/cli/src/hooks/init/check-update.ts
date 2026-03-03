import {Hook} from '@oclif/core'
import chalk from 'chalk'

import {getLatestVersion} from '../../lib/npm.js'

const ONE_DAY_MS = 24 * 60 * 60 * 1000

const hook: Hook<'init'> = async function ({config}) {
  // Only check once per day
  const lastCheck = process.env.PLANE_CLI_LAST_UPDATE_CHECK
  const now = Date.now()
  if (lastCheck && now - Number.parseInt(lastCheck, 10) < ONE_DAY_MS) {
    return
  }

  try {
    const latest = await getLatestVersion(config.name)
    const current = config.version
    if (latest && latest !== current) {
      console.log(chalk.yellow(`\nUpdate available: ${current} → ${latest}`))
      console.log(chalk.gray(`Run: npm install -g ${config.name}\n`))
    }

    process.env.PLANE_CLI_LAST_UPDATE_CHECK = String(now)
  } catch {
    // Silently fail - not critical
  }
}

export default hook
