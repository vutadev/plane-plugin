import {Flags} from '@oclif/core'
import chalk from 'chalk'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, formatTable, info, printJson} from '../../lib/output.js'

export default class LabelList extends BaseCommand {
  static description = 'List labels in a project'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({char: 'p', description: 'Project ID', required: true}),
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(LabelList)
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Loading labels...')
    try {
      const {results} = await api.listLabels(config.workspace, flags.project)
      spinner.stop()

      if (flags.json) {
        printJson(results)
        return
      }

      if (results.length === 0) {
        info('No labels found')
        return
      }

      const rows = results.map((l) => [
        l.id.slice(0, 8),
        l.name,
        chalk.hex(l.color)(`\u25A0 ${l.color}`),
      ])

      console.log(formatTable(['ID', 'Name', 'Color'], rows))
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
