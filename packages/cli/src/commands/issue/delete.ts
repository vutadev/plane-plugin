import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {resolveIssueId} from '../../lib/issue-resolver.js'
import {error, success} from '../../lib/output.js'

export default class IssueDelete extends BaseCommand {
  static args = {
    id: Args.string({description: 'Issue ID, UUID, or PROJECT-123', required: true}),
  }
  static description = 'Delete an issue'
  static flags = {
    confirm: Flags.boolean({default: false, description: 'Confirm destructive operation'}),
    project: Flags.string({description: 'Project ID (required if using UUID)'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(IssueDelete)

    // Destructive operation requires explicit confirmation
    if (!flags.confirm) {
      error('Destructive operation — pass --confirm to proceed.')
      process.exit(1)
    }

    const api = this.requireApi()
    const config = this.requireConfig()

    const {issueId, projectId} = await resolveIssueId(
      api,
      config.workspace,
      args.id,
      flags.project,
    )

    await this.withSpinner('Deleting issue...', () =>
      api.deleteIssue(config.workspace, projectId, issueId),
    )

    success(`Deleted issue ${args.id}`)
  }
}
