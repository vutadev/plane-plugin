import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, error, success} from '../../lib/output.js'

export default class CycleDelete extends BaseCommand {
  static args = {
    id: Args.string({description: 'Cycle ID', required: true}),
  }
  static description = 'Delete a cycle'
  static flags = {
    confirm: Flags.boolean({default: false, description: 'Confirm destructive operation'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(CycleDelete)

    // Destructive operation requires explicit confirmation
    if (!flags.confirm) {
      error('Destructive operation — pass --confirm to proceed.')
      process.exit(1)
    }

    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Deleting cycle...')
    try {
      await api.deleteCycle(config.workspace, args.id)
      spinner.stop()

      success(`Deleted cycle ${args.id}`)
    } catch (error_) {
      spinner.stop()
      throw error_
    }
  }
}
