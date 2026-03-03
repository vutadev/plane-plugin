import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {error, success} from '../../lib/output.js'

export default class ModuleDelete extends BaseCommand {
  static args = {
    moduleId: Args.string({description: 'Module ID', required: true}),
  }
  static description = 'Delete a module'
  static flags = {
    confirm: Flags.boolean({default: false, description: 'Confirm destructive operation'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(ModuleDelete)
    const api = this.requireApi()
    const config = this.requireConfig()

    if (!flags.confirm) {
      error('Destructive operation — pass --confirm to proceed.')
      process.exit(1)
    }

    await this.withSpinner('Deleting module...', () =>
      api.deleteModule(config.workspace, args.moduleId),
    )

    success('Module deleted')
  }
}
