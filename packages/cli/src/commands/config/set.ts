import {Args, Command} from '@oclif/core'

import {getConfig, saveConfig} from '../../lib/config.js'
import {success} from '../../lib/output.js'

export default class ConfigSet extends Command {
  static args = {
    key: Args.string({
      description: 'Config key (workspace, apiKey, accessToken, baseUrl, defaults.project)',
      required: true,
    }),
    value: Args.string({
      description: 'Config value',
      required: true,
    }),
  }
  static description = 'Set a configuration value'

  async run(): Promise<void> {
    const {args} = await this.parse(ConfigSet)
    const config = await getConfig()

    if (!config) {
      this.error('No configuration found. Run `plane-cli config init` first.', {exit: 1})
    }

    const {key, value} = args

    // Handle nested keys like defaults.project
    if (key.includes('.')) {
      const parts = key.split('.')
      let current: Record<string, unknown> = config as unknown as Record<string, unknown>
      for (let i = 0; i < parts.length - 1; i++) {
        if (!current[parts[i]]) {
          current[parts[i]] = {}
        }

        current = current[parts[i]] as Record<string, unknown>
      }

      current[parts.at(-1)!] = value
    } else if (key === 'apiKey' || key === 'accessToken' || key === 'baseUrl' || key === 'workspace') {
      // Handle top-level keys
      ;(config as unknown as Record<string, string>)[key] = value
    } else {
      this.error(`Unknown config key: ${key}`, {exit: 1})
    }

    await saveConfig(config)
    success(`Set ${key} = ${key.includes('Key') || key.includes('Token') ? '***' : value}`)
  }
}
