import {Command, Flags} from '@oclif/core'

import {PlaneAPI} from './lib/api.js'
import {createSpinner} from './lib/output.js'
import {PlaneConfig} from './types/config.js'

export abstract class BaseCommand extends Command {
  static baseFlags = {
    'no-input': Flags.boolean({
      default: false,
      description: 'Disable interactive prompts',
    }),
  }
static enableJsonFlag = true
protected api!: PlaneAPI
  protected configData!: PlaneConfig

  async init(): Promise<void> {
    await super.init()
    const {getConfig} = await import('./lib/config.js')
    const config = await getConfig()

    if (!config) {
      this.error('No configuration found. Run `plane-cli config init` first.', {exit: 1})
    }

    this.configData = config

    if (config.apiKey || config.accessToken) {
      this.api = new PlaneAPI(config)
    }
  }

  protected requireApi(): PlaneAPI {
    this.requireConfig()
    if (!this.api) {
      this.error('API client not initialized. Check your API key or access token.', {exit: 1})
    }

    return this.api
  }

  protected requireConfig(): PlaneConfig {
    if (!this.configData) {
      this.error('No configuration found. Run `plane-cli config init` first.', {exit: 1})
    }

    return this.configData
  }

  /** Run an async operation with a spinner, ensuring it stops on error. */
  protected async withSpinner<T>(message: string, fn: () => Promise<T>): Promise<T> {
    const spinner = createSpinner(message)
    try {
      const result = await fn()
      spinner.stop()
      return result
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
