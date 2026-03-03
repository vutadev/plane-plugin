import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {error, success} from '../../lib/output.js'
import {promptMultiSelect} from '../../lib/prompts.js'

export default class ModuleAddIssues extends BaseCommand {
  static args = {
    moduleId: Args.string({description: 'Module ID', required: true}),
  }
  static description = 'Add issues to a module'
  static flags = {
    issues: Flags.string({description: 'Comma-separated issue IDs'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({char: 'p', description: 'Project ID'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(ModuleAddIssues)
    const api = this.requireApi()
    const config = this.requireConfig()

    let projectId = flags.project
    if (!projectId) {
      const module = await api.getModule(config.workspace, args.moduleId)
      projectId = module.project_id
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

    await this.withSpinner(`Adding ${issueIds.length} issues...`, () =>
      api.addIssuesToModule(config.workspace, projectId, args.moduleId, issueIds),
    )

    success(`Added ${issueIds.length} issues to module`)
  }
}
