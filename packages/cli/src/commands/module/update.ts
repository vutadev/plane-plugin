import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {printJson, success} from '../../lib/output.js'

export default class ModuleUpdate extends BaseCommand {
  static args = {
    moduleId: Args.string({description: 'Module ID', required: true}),
  }
  static description = 'Update module details'
  static flags = {
    description: Flags.string({char: 'd', description: 'Description'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({char: 'n', description: 'Module name'}),
    start: Flags.string({description: 'Start date (YYYY-MM-DD)'}),
    target: Flags.string({description: 'Target date (YYYY-MM-DD)'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(ModuleUpdate)
    const api = this.requireApi()
    const config = this.requireConfig()

    const module = await this.withSpinner('Updating module...', () =>
      api.updateModule(config.workspace, args.moduleId, {
        description: flags.description,
        name: flags.name,
        start_date: flags.start,
        target_date: flags.target,
      }),
    )

    if (flags.json) {
      printJson(module)
    } else {
      success(`Updated module: ${module.name}`)
    }
  }
}
