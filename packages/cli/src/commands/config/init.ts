import {Command, Flags} from '@oclif/core'

import {hasConfig, saveConfig} from '../../lib/config.js'
import {info, success, warning} from '../../lib/output.js'
import {promptAccessToken, promptApiKey, promptConfirm, promptWorkspace} from '../../lib/prompts.js'

export default class ConfigInit extends Command {
  static description = 'Initialize Plane CLI configuration'
  static flags = {
    'access-token': Flags.string({description: 'Plane access token (alternative to API key)'}),
    'api-key': Flags.string({description: 'Plane API key'}),
    'base-url': Flags.string({default: 'https://api.plane.so/api/v1', description: 'Plane API base URL'}),
    force: Flags.boolean({default: false, description: 'Overwrite existing config'}),
    'no-input': Flags.boolean({default: false, description: 'Disable interactive prompts'}),
    workspace: Flags.string({description: 'Workspace slug'}),
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(ConfigInit)

    // Check if config already exists
    if (!flags.force && await hasConfig()) {
      this.error('Configuration already exists. Use --force to overwrite.', {exit: 1})
    }

    // Get API key or access token
    let apiKey = flags['api-key']
    let accessToken = flags['access-token']

    if (!apiKey && !accessToken && !flags['no-input']) {
      const useApiKey = await promptConfirm('Use API key? (No for access token)', true)
      if (useApiKey) {
        apiKey = await promptApiKey()
      } else {
        accessToken = await promptAccessToken()
      }
    }

    // Get workspace
    let {workspace} = flags
    if (!workspace && !flags['no-input']) {
      workspace = await promptWorkspace()
    }

    if (!workspace) {
      this.error('Workspace is required', {exit: 1})
    }

    if (!apiKey && !accessToken) {
      this.error('API key or access token is required', {exit: 1})
    }

    // Save config
    const config = {
      accessToken,
      apiKey,
      baseUrl: flags['base-url'],
      currentProfile: 'default',
      workspace,
    }

    await saveConfig(config)
    success('Configuration saved to ~/.planerc')
    info(`Workspace: ${workspace}`)
    info(`API URL: ${flags['base-url']}`)
    warning('Keep your API key secure!')
  }
}
