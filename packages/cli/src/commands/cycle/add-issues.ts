import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, error, success} from '../../lib/output.js'
import {promptMultiSelect} from '../../lib/prompts.js'

export default class CycleAddIssues extends BaseCommand {
  static args = {
    cycleId: Args.string({description: 'Cycle ID', required: true}),
  }
  static description = 'Add issues to a cycle'
  static flags = {
    issues: Flags.string({description: 'Comma-separated issue IDs'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({char: 'p', description: 'Project ID'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(CycleAddIssues)
    const api = this.requireApi()
    const config = this.requireConfig()

    let projectId = flags.project
    if (!projectId) {
      const cycle = await api.getCycle(config.workspace, args.cycleId)
      projectId = cycle.project_id
    }

    let issueIds = flags.issues?.split(',')
    if (!issueIds && !flags['no-input']) {
      const {results: issues} = await api.listIssues(config.workspace, projectId)
      issueIds = await promptMultiSelect(
        'Select issues to add:',
        issues.map((i) => ({name: `${i.sequence_id}: ${i.name.slice(0, 40)}`, value: i.id})),
      )
    }

    if (!issueIds || issueIds.length === 0) {
      error('No issues selected')
      process.exit(1)
    }

    const spinner = createSpinner(`Adding ${issueIds.length} issues...`)
    try {
      await api.addIssuesToCycle(config.workspace, projectId, args.cycleId, issueIds)
      spinner.stop()

      success(`Added ${issueIds.length} issues to cycle`)
    } catch (error_) {
      spinner.stop()
      throw error_
    }
  }
}
