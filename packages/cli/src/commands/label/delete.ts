import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, success} from '../../lib/output.js'

export default class LabelDelete extends BaseCommand {
  static args = {
    labelId: Args.string({description: 'Label ID', required: true}),
  }
  static description = 'Delete label'
  static flags = {
    confirm: Flags.boolean({description: 'Confirm destructive operation', required: true}),
    project: Flags.string({char: 'p', description: 'Project ID', required: true}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(LabelDelete)
    const api = this.requireApi()
    const config = this.requireConfig()

    if (!flags.confirm) {
      this.error('This is a destructive operation. Use --confirm to proceed.')
    }

    const spinner = createSpinner('Deleting label...')
    try {
      await api.deleteLabel(config.workspace, flags.project, args.labelId)
      spinner.stop()
      success(`Deleted label ${args.labelId}`)
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
