import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, formatDate, info, printJson} from '../../lib/output.js'

export default class CycleGet extends BaseCommand {
  static args = {
    id: Args.string({description: 'Cycle ID', required: true}),
  }
  static description = 'Get cycle details'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(CycleGet)
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Loading cycle...')
    try {
      const cycle = await api.getCycle(config.workspace, args.id)
      spinner.stop()

      if (flags.json) {
        printJson(cycle)
        return
      }

      info('Cycle Details:')
      console.log(`  ID:          ${cycle.id}`)
      console.log(`  Name:        ${cycle.name}`)
      console.log(`  Description: ${cycle.description || '-'}`)
      console.log(`  Project ID:  ${cycle.project_id}`)
      console.log(`  Start Date:  ${cycle.start_date ? formatDate(cycle.start_date) : '-'}`)
      console.log(`  End Date:    ${cycle.end_date ? formatDate(cycle.end_date) : '-'}`)
      console.log(`  Archived:    ${cycle.archived ? 'Yes' : 'No'}`)
      console.log(`  Created:     ${formatDate(cycle.created_at)}`)
      console.log(`  Updated:     ${formatDate(cycle.updated_at)}`)
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
