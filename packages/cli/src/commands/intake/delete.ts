import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, success} from '../../lib/output.js'

export default class IntakeDelete extends BaseCommand {
  static args = {
    intakeId: Args.string({description: 'Intake ID', required: true}),
  }
  static description = 'Delete intake'
  static flags = {
    confirm: Flags.boolean({description: 'Confirm destructive operation', required: true}),
    project: Flags.string({char: 'p', description: 'Project ID', required: true}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(IntakeDelete)
    const api = this.requireApi()
    const config = this.requireConfig()

    if (!flags.confirm) {
      this.error('This is a destructive operation. Use --confirm to proceed.')
    }

    const spinner = createSpinner('Deleting intake...')
    try {
      await api.deleteIntake(config.workspace, flags.project, args.intakeId)
      spinner.stop()
      success(`Deleted intake ${args.intakeId}`)
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
