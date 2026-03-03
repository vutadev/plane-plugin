import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, formatTable, info, printJson} from '../../lib/output.js'

export default class IntakeList extends BaseCommand {
  static description = 'List intake items'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({char: 'p', description: 'Project ID', required: true}),
    status: Flags.string({description: 'Filter by status'}),
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(IntakeList)
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Loading intake items...')
    try {
      const {results} = await api.listIntake(config.workspace, flags.project, flags.status)
      spinner.stop()

      if (flags.json) {
        printJson(results)
        return
      }

      if (results.length === 0) {
        info('No intake items found')
        return
      }

      const rows = results.map((i) => [
        i.id.slice(0, 8),
        i.name.slice(0, 40),
        i.status,
        i.created_at.slice(0, 10),
      ])

      console.log(formatTable(['ID', 'Name', 'Status', 'Created'], rows))
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
