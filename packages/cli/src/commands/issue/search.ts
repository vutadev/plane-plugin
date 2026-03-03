import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {formatTable, printJson, priorityColor, success} from '../../lib/output.js'

export default class IssueSearch extends BaseCommand {
  static args = {
    query: Args.string({description: 'Search query', required: true}),
  }
  static description = 'Search issues across projects'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({description: 'Limit to project'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(IssueSearch)
    const api = this.requireApi()
    const config = this.requireConfig()

    const results = await this.withSpinner('Searching issues...', () =>
      api.searchIssues(config.workspace, {
        project_id: flags.project,
        query: args.query,
      }),
    )

    if (flags.json) {
      printJson(results)
      return
    }

    if (results.length === 0) {
      success('No issues found matching your search')
      return
    }

    const rows = results.map((r) => [
      r.human_id,
      r.name.slice(0, 45),
      r.project_identifier,
      priorityColor(r.priority),
    ])

    console.log(formatTable(['ID', 'Title', 'Project', 'Priority'], rows))
    success(`Found ${results.length} issues matching "${args.query}"`)
  }
}
