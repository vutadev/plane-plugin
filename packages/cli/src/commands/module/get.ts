import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {printJson, success} from '../../lib/output.js'

export default class ModuleGet extends BaseCommand {
  static args = {
    moduleId: Args.string({description: 'Module ID', required: true}),
  }
  static description = 'Get module details'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(ModuleGet)
    const api = this.requireApi()
    const config = this.requireConfig()

    const module = await this.withSpinner('Loading module...', () =>
      api.getModule(config.workspace, args.moduleId),
    )

    if (flags.json) {
      printJson(module)
      return
    }

    success(`Module: ${module.name}`)
    console.log(`  ID: ${module.id}`)
    console.log(`  Description: ${module.description || '-'}`)
    console.log(`  Start date: ${module.start_date || '-'}`)
    console.log(`  Target date: ${module.target_date || '-'}`)
    console.log(`  Archived: ${module.archived ? 'Yes' : 'No'}`)
  }
}
