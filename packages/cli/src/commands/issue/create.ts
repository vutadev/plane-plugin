import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {PlaneAPI} from '../../lib/api.js'
import {info, success} from '../../lib/output.js'
import {promptConfirm, promptSelect, promptText} from '../../lib/prompts.js'
import {PlaneConfig} from '../../types/config.js'
import {Project} from '../../types/plane.js'

export default class IssueCreate extends BaseCommand {
  static description = 'Create a new issue'
  static flags = {
    assignees: Flags.string({description: 'Comma-separated assignee IDs'}),
    description: Flags.string({char: 'd', description: 'Description'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    labels: Flags.string({description: 'Comma-separated label IDs'}),
    name: Flags.string({char: 'n', description: 'Issue title'}),
    priority: Flags.string({
      description: 'Priority',
      options: ['urgent', 'high', 'medium', 'low', 'none'],
    }),
    project: Flags.string({char: 'p', description: 'Project ID'}),
    state: Flags.string({description: 'Initial state'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(IssueCreate)
    const api = this.requireApi()
    const config = this.requireConfig()

    // Interactive wizard if minimal args
    const data = await this.buildIssueData(flags, api, config)

    const issue = await this.withSpinner('Creating issue...', () =>
      api.createIssue(config.workspace, data.projectId, {
        assignees: data.assignees,
        description_html: data.description,
        labels: data.labels,
        name: data.name,
        priority: data.priority as 'high' | 'low' | 'medium' | 'none' | 'urgent',
        state: data.state,
      }),
    )

    if (flags.json) {
      import('../../lib/output.js').then(({printJson}) => {
        printJson(issue)
      })
    } else {
      success(`Created issue ${data.project.identifier}-${issue.sequence_id}`)
      info(`ID: ${issue.id}`)
    }
  }

  private async buildIssueData(
    flags: {
      assignees?: string
      description?: string
      json?: boolean
      labels?: string
      name?: string
      'no-input'?: boolean
      priority?: string
      project?: string
      state?: string
    },
    api: PlaneAPI,
    config: PlaneConfig,
  ): Promise<{
    assignees?: string[]
    description?: string
    labels?: string[]
    name: string
    priority: string
    project: Project
    projectId: string
    state?: string
  }> {
    // Select project
    let projectId = flags.project

    if (!projectId) {
      const projects = await api.listProjects(config.workspace)
      projectId = await promptSelect(
        'Select project:',
        projects.results.map((p) => ({name: p.name, value: p.id})),
      )
    }

    const project: Project = await api.getProject(config.workspace, projectId)

    // Title
    let {name} = flags
    if (!name && !flags['no-input']) {
      name = await promptText('Issue title:')
    }

    if (!name) {
      throw new Error('Issue title is required')
    }

    // Description (optional)
    let {description} = flags
    if (!description && !flags['no-input']) {
      const addDesc = await promptConfirm('Add description?')
      if (addDesc) {
        description = await promptText('Description:')
      }
    }

    // Priority
    let {priority} = flags
    if (!priority && !flags['no-input']) {
      priority = await promptSelect('Priority:', [
        {name: 'Urgent', value: 'urgent'},
        {name: 'High', value: 'high'},
        {name: 'Medium', value: 'medium'},
        {name: 'Low', value: 'low'},
        {name: 'None', value: 'none'},
      ])
    }

    // State
    let {state} = flags
    if (!state && !flags['no-input']) {
      const states = await api.listStates(config.workspace, projectId)
      state = await promptSelect(
        'State:',
        states.results.map((s) => ({name: s.name, value: s.id})),
      )
    }

    return {
      assignees: flags.assignees?.split(','),
      description,
      labels: flags.labels?.split(','),
      name,
      priority: priority || 'none',
      project,
      projectId,
      state,
    }
  }
}
