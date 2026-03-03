import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, printJson, success} from '../../lib/output.js'

export default class CycleArchive extends BaseCommand {
  static args = {
    id: Args.string({description: 'Cycle ID', required: true}),
  }
  static description = 'Archive a cycle'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(CycleArchive)
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Archiving cycle...')
    try {
      const cycle = await api.archiveCycle(config.workspace, args.id)
      spinner.stop()

      if (flags.json) {
        printJson(cycle)
      } else {
        success(`Archived cycle: ${cycle.name}`)
      }
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
