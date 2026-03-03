import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, success} from '../../lib/output.js'

export default class InitiativeDelete extends BaseCommand {
  static args = {
    initiativeId: Args.string({description: 'Initiative ID', required: true}),
  }
  static description = 'Delete initiative'
  static flags = {
    confirm: Flags.boolean({description: 'Confirm destructive operation', required: true}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(InitiativeDelete)
    const api = this.requireApi()
    const config = this.requireConfig()

    if (!flags.confirm) {
      this.error('This is a destructive operation. Use --confirm to proceed.')
    }

    const spinner = createSpinner('Deleting initiative...')
    try {
      await api.deleteInitiative(config.workspace, args.initiativeId)
      spinner.stop()
      success(`Deleted initiative ${args.initiativeId}`)
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
