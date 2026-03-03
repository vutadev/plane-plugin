import {Args, Flags} from '@oclif/core'
import chalk from 'chalk'

import {BaseCommand} from '../../base-command.js'
import {resolveIssueId} from '../../lib/issue-resolver.js'
import {printJson, priorityColor} from '../../lib/output.js'

export default class IssueGet extends BaseCommand {
  static args = {
    id: Args.string({description: 'Issue ID, UUID, or PROJECT-123', required: true}),
  }
  static description = 'Get issue details (supports PROJECT-123 format)'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({description: 'Project ID (required if using UUID)'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(IssueGet)
    const api = this.requireApi()
    const config = this.requireConfig()

    const {issueId, projectId} = await resolveIssueId(
      api,
      config.workspace,
      args.id,
      flags.project,
    )

    const [issue, project] = await this.withSpinner('Loading issue...', () =>
      Promise.all([
        api.getIssue(config.workspace, projectId, issueId),
        api.getProject(config.workspace, projectId),
      ]),
    )

    if (flags.json) {
      printJson({...issue, human_id: `${project.identifier}-${issue.sequence_id}`})
      return
    }

    console.log(chalk.bold(`\n${project.identifier}-${issue.sequence_id}: ${issue.name}`))
    console.log(chalk.gray('─'.repeat(60)))
    console.log(`Priority: ${priorityColor(issue.priority)}`)
    console.log(`State: ${issue.state}`)
    console.log(`ID: ${issue.id}`)
    console.log(`Created: ${new Date(issue.created_at).toLocaleString()}`)
    if (issue.description_html) {
      console.log(`\nDescription:`)
      console.log(chalk.gray(this.stripHtml(issue.description_html)))
    }

    if (issue.assignees.length > 0) {
      console.log(`\nAssignees: ${issue.assignees.join(', ')}`)
    }

    if (issue.labels.length > 0) {
      console.log(`Labels: ${issue.labels.join(', ')}`)
    }
  }

  private stripHtml(html: string): string {
    return html
      .replaceAll(/<[^>]*>/g, ' ')
      .replaceAll(/\s+/g, ' ')
      .trim()
      .slice(0, 500)
  }
}
