import {Flags} from '@oclif/core'
import chalk from 'chalk'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, formatTable, info, printJson} from '../../lib/output.js'

export default class StateList extends BaseCommand {
  static description = 'List workflow states in a project'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({char: 'p', description: 'Project ID', required: true}),
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(StateList)
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Loading states...')
    try {
      const {results} = await api.listStates(config.workspace, flags.project)
      spinner.stop()

      if (flags.json) {
        printJson(results)
        return
      }

      if (results.length === 0) {
        info('No states found')
        return
      }

      const rows = results.map((s) => [
        s.id.slice(0, 8),
        s.name,
        s.group,
        chalk.hex(s.color)(s.color),
        s.default ? '\u2713' : '',
      ])

      console.log(formatTable(['ID', 'Name', 'Group', 'Color', 'Default'], rows))
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
