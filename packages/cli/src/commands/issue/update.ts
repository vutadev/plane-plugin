import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {resolveIssueId} from '../../lib/issue-resolver.js'
import {info, printJson, success} from '../../lib/output.js'
import {promptConfirm, promptSelect, promptText} from '../../lib/prompts.js'

export default class IssueUpdate extends BaseCommand {
  static args = {
    id: Args.string({description: 'Issue ID, UUID, or PROJECT-123', required: true}),
  }
  static description = 'Update an issue'
  static flags = {
    'clear-description': Flags.boolean({description: 'Clear the description'}),
    description: Flags.string({char: 'd', description: 'Description'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({char: 'n', description: 'Issue title'}),
    priority: Flags.string({
      description: 'Priority',
      options: ['urgent', 'high', 'medium', 'low', 'none'],
    }),
    project: Flags.string({description: 'Project ID (required if using UUID)'}),
    state: Flags.string({description: 'State ID'}),
    ...BaseCommand.baseFlags,
  }

  // eslint-disable-next-line complexity
  async run(): Promise<void> {
    const {args, flags} = await this.parse(IssueUpdate)
    const api = this.requireApi()
    const config = this.requireConfig()

    const {issueId, projectId} = await resolveIssueId(
      api,
      config.workspace,
      args.id,
      flags.project,
    )

    // Get current issue to show in prompts
    let currentIssue = null
    if (!flags['no-input']) {
      currentIssue = await this.withSpinner('Loading issue...', () =>
        api.getIssue(config.workspace, projectId, issueId),
      )
    }

    // Build update data
    const updateData: {
      description_html?: string
      name?: string
      priority?: 'high' | 'low' | 'medium' | 'none' | 'urgent'
      state?: string
    } = {}

    // Name
    if (flags.name) {
      updateData.name = flags.name
    } else if (!flags['no-input'] && currentIssue) {
      const newName = await promptText('Issue title:', currentIssue.name)
      if (newName !== currentIssue.name) {
        updateData.name = newName
      }
    }

    // Description
    if (flags['clear-description']) {
      updateData.description_html = ''
    } else if (flags.description) {
      updateData.description_html = flags.description
    } else if (!flags['no-input'] && currentIssue) {
      const currentDesc = currentIssue.description_html
        ? this.stripHtml(currentIssue.description_html)
        : ''
      const changeDesc = await promptConfirm('Change description?')
      if (changeDesc) {
        const newDesc = await promptText('Description:', currentDesc)
        updateData.description_html = newDesc
      }
    }

    // Priority
    if (flags.priority) {
      updateData.priority = flags.priority as 'high' | 'low' | 'medium' | 'none' | 'urgent'
    } else if (!flags['no-input'] && currentIssue) {
      const newPriority = await promptSelect('Priority:', [
        {name: 'Urgent', value: 'urgent'},
        {name: 'High', value: 'high'},
        {name: 'Medium', value: 'medium'},
        {name: 'Low', value: 'low'},
        {name: 'None', value: 'none'},
      ])
      if (newPriority !== currentIssue.priority) {
        updateData.priority = newPriority
      }
    }

    // State
    if (flags.state) {
      updateData.state = flags.state
    } else if (!flags['no-input'] && currentIssue) {
      const states = await api.listStates(config.workspace, projectId)
      const newState = await promptSelect(
        'State:',
        states.results.map((s) => ({name: s.name, value: s.id})),
      )
      if (newState !== currentIssue.state_id) {
        updateData.state = newState
      }
    }

    // Check if there are any updates
    if (Object.keys(updateData).length === 0) {
      info('No changes to apply')
      return
    }

    const issue = await this.withSpinner('Updating issue...', () =>
      api.updateIssue(config.workspace, projectId, issueId, updateData),
    )

    if (flags.json) {
      printJson(issue)
    } else {
      success(`Updated issue ${args.id}`)
      info(`ID: ${issue.id}`)
    }
  }

  private stripHtml(html: string): string {
    return html
      .replaceAll(/<[^>]*>/g, ' ')
      .replaceAll(/\s+/g, ' ')
      .trim()
      .slice(0, 200)
  }
}
