import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, success} from '../../lib/output.js'

export default class StateDelete extends BaseCommand {
  static args = {
    stateId: Args.string({description: 'State ID', required: true}),
  }
  static description = 'Delete a state'
  static flags = {
    confirm: Flags.boolean({description: 'Confirm destructive operation', required: true}),
    project: Flags.string({char: 'p', description: 'Project ID', required: true}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(StateDelete)
    const api = this.requireApi()
    const config = this.requireConfig()

    if (!flags.confirm) {
      this.error('This is a destructive operation. Use --confirm to proceed.')
    }

    const spinner = createSpinner('Deleting state...')
    try {
      await api.deleteState(config.workspace, flags.project, args.stateId)
      spinner.stop()
      success(`Deleted state ${args.stateId}`)
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
