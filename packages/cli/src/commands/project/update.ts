import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {printJson, success} from '../../lib/output.js'
import {promptText} from '../../lib/prompts.js'

export default class ProjectUpdate extends BaseCommand {
  static args = {
    id: Args.string({description: 'Project ID', required: true}),
  }
  static description = 'Update project details'
  static flags = {
    description: Flags.string({description: 'New description'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({description: 'New project name'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(ProjectUpdate)
    const api = this.requireApi()
    const config = this.requireConfig()

    // Get current values
    const current = await api.getProject(config.workspace, args.id)

    // Interactive mode if no flags provided
    let {name} = flags
    let {description} = flags

    if (!name && !description && !flags['no-input']) {
      name = await promptText('Project name:', current.name)
      description = await promptText('Description:', current.description || '')
    }

    const data = {
      description: description ?? current.description,
      name: name ?? current.name,
    }

    const updated = await this.withSpinner('Updating project...', () =>
      api.updateProject(config.workspace, args.id, data),
    )

    success('Project updated')

    if (flags.json) {
      printJson(updated)
    }
  }
}
