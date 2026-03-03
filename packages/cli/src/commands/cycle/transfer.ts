import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, success} from '../../lib/output.js'

export default class CycleTransfer extends BaseCommand {
  static args = {
    from: Args.string({description: 'Source cycle ID', required: true}),
    to: Args.string({description: 'Target cycle ID', required: true}),
  }
  static description = 'Transfer issues from one cycle to another'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
  }

  async run(): Promise<void> {
    const {args} = await this.parse(CycleTransfer)
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Transferring issues...')
    try {
      await api.transferCycleIssues(config.workspace, args.from, args.to)
      spinner.stop()

      success(`Transferred issues from cycle ${args.from} to ${args.to}`)
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
