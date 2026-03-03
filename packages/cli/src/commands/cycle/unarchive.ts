import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, printJson, success} from '../../lib/output.js'

export default class CycleUnarchive extends BaseCommand {
  static args = {
    id: Args.string({description: 'Cycle ID', required: true}),
  }
  static description = 'Unarchive a cycle'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(CycleUnarchive)
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Unarchiving cycle...')
    try {
      const cycle = await api.unarchiveCycle(config.workspace, args.id)
      spinner.stop()

      if (flags.json) {
        printJson(cycle)
      } else {
        success(`Unarchived cycle: ${cycle.name}`)
      }
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
