import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {success} from '../../lib/output.js'

export default class ModuleRemoveIssue extends BaseCommand {
  static args = {
    moduleId: Args.string({description: 'Module ID', required: true}),
  }
  static description = 'Remove an issue from a module'
  static flags = {
    issue: Flags.string({description: 'Issue ID to remove', required: true}),
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({char: 'p', description: 'Project ID'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(ModuleRemoveIssue)
    const api = this.requireApi()
    const config = this.requireConfig()

    let projectId = flags.project
    if (!projectId) {
      const module = await api.getModule(config.workspace, args.moduleId)
      projectId = module.project_id
    }

    await this.withSpinner('Removing issue...', () =>
      api.removeIssueFromModule(config.workspace, projectId, args.moduleId, flags.issue),
    )

    success('Issue removed from module')
  }
}
