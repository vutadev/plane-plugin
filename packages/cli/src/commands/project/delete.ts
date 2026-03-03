import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {error, info, success} from '../../lib/output.js'
import {promptConfirm} from '../../lib/prompts.js'

export default class ProjectDelete extends BaseCommand {
  static args = {
    id: Args.string({description: 'Project ID', required: true}),
  }
  static description = 'Delete a project'
  static flags = {
    confirm: Flags.boolean({description: 'Confirm deletion (required)', required: true}),
    force: Flags.boolean({default: false, description: 'Skip confirmation prompt'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(ProjectDelete)
    const api = this.requireApi()
    const config = this.requireConfig()

    if (!flags.confirm) {
      error('Deletion requires --confirm flag')
      process.exit(1)
    }

    if (!flags.force && !flags['no-input']) {
      const confirmed = await promptConfirm(
        `Are you sure you want to delete project ${args.id}? This cannot be undone.`,
      )
      if (!confirmed) {
        info('Cancelled')
        return
      }
    }

    await api.deleteProject(config.workspace, args.id)
    success(`Deleted project ${args.id}`)
  }
}
