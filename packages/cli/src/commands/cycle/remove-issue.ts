import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, success} from '../../lib/output.js'

export default class CycleRemoveIssue extends BaseCommand {
  static args = {
    cycleId: Args.string({description: 'Cycle ID', required: true}),
    issueId: Args.string({description: 'Issue ID', required: true}),
  }
  static description = 'Remove an issue from a cycle'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({char: 'p', description: 'Project ID'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(CycleRemoveIssue)
    const api = this.requireApi()
    const config = this.requireConfig()

    let projectId = flags.project
    if (!projectId) {
      const cycle = await api.getCycle(config.workspace, args.cycleId)
      projectId = cycle.project_id
    }

    const spinner = createSpinner('Removing issue from cycle...')
    try {
      await api.removeIssueFromCycle(config.workspace, projectId, args.cycleId, args.issueId)
      spinner.stop()

      success(`Removed issue ${args.issueId} from cycle`)
    } catch (error_) {
      spinner.stop()
      throw error_
    }
  }
}
