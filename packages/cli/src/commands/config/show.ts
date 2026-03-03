import {Command, Flags} from '@oclif/core'
import chalk from 'chalk'

import {getConfig} from '../../lib/config.js'
import {printJson} from '../../lib/output.js'

export default class ConfigShow extends Command {
  static description = 'Show current configuration'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(ConfigShow)
    const config = await getConfig()

    if (!config) {
      this.error('No configuration found. Run `plane-cli config init` first.', {exit: 1})
    }

    if (flags.json) {
      printJson({
        baseUrl: config.baseUrl,
        hasAccessToken: Boolean(config.accessToken),
        hasApiKey: Boolean(config.apiKey),
        workspace: config.workspace,
      })
      return
    }

    console.log(chalk.bold('\nConfiguration:'))
    console.log(chalk.gray('─'.repeat(40)))
    console.log(`Workspace: ${chalk.cyan(config.workspace)}`)
    console.log(`API URL: ${config.baseUrl}`)
    console.log(`Auth: ${config.apiKey ? chalk.green('API Key') : config.accessToken ? chalk.green('Access Token') : chalk.red('None')}`)

    if (config.defaults?.project) {
      console.log(`Default Project: ${config.defaults.project}`)
    }
  }
}
