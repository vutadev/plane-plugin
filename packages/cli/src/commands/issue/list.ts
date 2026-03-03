import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {PlaneAPI} from '../../lib/api.js'
import {error, formatTable, printJson, priorityColor, success} from '../../lib/output.js'
import {promptSelect} from '../../lib/prompts.js'
import {PlaneConfig} from '../../types/config.js'

export default class IssueList extends BaseCommand {
  static description = 'List issues in a project'
  static flags = {
    assignee: Flags.string({description: 'Filter by assignee ID'}),
    cycle: Flags.string({char: 'c', description: 'Filter by cycle ID'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    limit: Flags.integer({char: 'l', default: 50, description: 'Limit results'}),
    module: Flags.string({char: 'm', description: 'Filter by module ID'}),
    project: Flags.string({char: 'p', description: 'Project ID or identifier'}),
    state: Flags.string({description: 'Filter by state'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(IssueList)
    const api = this.requireApi()
    const config = this.requireConfig()

    // Get project - prompt if not provided
    let projectId = flags.project
    if (!projectId && !flags['no-input']) {
      projectId = await this.promptForProject(api, config)
    }

    if (!projectId) {
      error('--project is required')
      process.exit(1)
    }

    const {results} = await this.withSpinner('Loading issues...', () =>
      api.listIssues(config.workspace, projectId, {
        assignee: flags.assignee,
        cycle: flags.cycle,
        limit: flags.limit,
        module: flags.module,
        state: flags.state,
      }),
    )

    if (flags.json) {
      printJson(results)
      return
    }

    const project = await api.getProject(config.workspace, projectId)
    const rows = results.map((i) => [
      `${project.identifier}-${i.sequence_id}`,
      i.name.slice(0, 50),
      priorityColor(i.priority),
      i.state.slice(0, 15),
      i.assignees.length > 0 ? `${i.assignees.length} assigned` : '-',
    ])

    console.log(formatTable(['ID', 'Title', 'Priority', 'State', 'Assignees'], rows))
    success(`Found ${results.length} issues`)
  }

  private async promptForProject(api: PlaneAPI, config: PlaneConfig): Promise<string | undefined> {
    const projects = await api.listProjects(config.workspace)
    if (projects.results.length === 0) {
      error('No projects found')
      return undefined
    }

    return promptSelect(
      'Select project:',
      projects.results.map((p) => ({name: `${p.identifier} - ${p.name}`, value: p.id})),
    )
  }
}
