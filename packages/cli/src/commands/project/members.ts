import {Args, Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {formatTable, printJson} from '../../lib/output.js'

export default class ProjectMembers extends BaseCommand {
  static args = {
    id: Args.string({description: 'Project ID', required: true}),
  }
  static description = 'List project members'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(ProjectMembers)
    const api = this.requireApi()
    const config = this.requireConfig()

    const members = await this.withSpinner('Loading members...', () =>
      api.listProjectMembers(config.workspace, args.id),
    )

    if (flags.json) {
      printJson(members)
      return
    }

    const rows = members.map((m) => [
      m.display_name || m.email,
      m.role,
      m.email,
    ])

    console.log(formatTable(['Name', 'Role', 'Email'], rows))
  }
}
