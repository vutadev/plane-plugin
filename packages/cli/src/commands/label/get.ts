import {Args, Flags} from '@oclif/core'
import chalk from 'chalk'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, printJson} from '../../lib/output.js'

export default class LabelGet extends BaseCommand {
  static args = {
    labelId: Args.string({description: 'Label ID', required: true}),
  }
  static description = 'Get label details'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({char: 'p', description: 'Project ID', required: true}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(LabelGet)
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Loading label...')
    try {
      const {results} = await api.listLabels(config.workspace, flags.project)
      const label = results.find((l) => l.id === args.labelId)

      if (!label) {
        this.error(`Label ${args.labelId} not found`)
      }

      spinner.stop()

      if (flags.json) {
        printJson(label)
        return
      }

      console.log(chalk.bold(label.name))
      console.log(chalk.gray('\u2500'.repeat(40)))
      console.log(`ID: ${label.id}`)
      console.log(`Color: ${chalk.hex(label.color)(label.color)}`)
      console.log(`Project: ${label.project_id}`)
      console.log(`Created: ${label.created_at}`)
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
