import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {printJson, success} from '../../lib/output.js'

export default class ModuleUnarchive extends BaseCommand {
  static args = {
    moduleId: Args.string({description: 'Module ID', required: true}),
  }
  static description = 'Unarchive a module'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(ModuleUnarchive)
    const api = this.requireApi()
    const config = this.requireConfig()

    const module = await this.withSpinner('Unarchiving module...', () =>
      api.unarchiveModule(config.workspace, args.moduleId),
    )

    if (flags.json) {
      printJson(module)
    } else {
      success(`Unarchived module: ${module.name}`)
    }
  }
}
