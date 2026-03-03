import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, error, printJson, success} from '../../lib/output.js'

export default class CycleUpdate extends BaseCommand {
  static args = {
    id: Args.string({description: 'Cycle ID', required: true}),
  }
  static description = 'Update cycle details'
  static flags = {
    description: Flags.string({char: 'd', description: 'Description'}),
    end: Flags.string({description: 'End date (YYYY-MM-DD)'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({char: 'n', description: 'Cycle name'}),
    start: Flags.string({description: 'Start date (YYYY-MM-DD)'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(CycleUpdate)
    const api = this.requireApi()
    const config = this.requireConfig()

    // Check if at least one field is provided
    if (!flags.name && !flags.description && !flags.start && !flags.end) {
      error('At least one field to update is required')
      process.exit(1)
    }

    const spinner = createSpinner('Updating cycle...')
    try {
      const cycle = await api.updateCycle(config.workspace, args.id, {
        description: flags.description,
        end_date: flags.end,
        name: flags.name,
        start_date: flags.start,
      })
      spinner.stop()

      if (flags.json) {
        printJson(cycle)
      } else {
        success(`Updated cycle: ${cycle.name}`)
      }
    } catch (error_) {
      spinner.stop()
      throw error_
    }
  }
}
