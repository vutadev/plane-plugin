import {BaseCommand} from '../../base-command.js'
import {createSpinner, formatTable, info} from '../../lib/output.js'

export default class WorkspaceMembers extends BaseCommand {
  static description = 'List workspace members'

  async run(): Promise<void> {
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Loading members...')
    try {
      const {results} = await api.listWorkspaceMembers(config.workspace)
      spinner.stop()

      if (results.length === 0) {
        info('No members found')
        return
      }

      const rows = results.map((m) => [
        m.display_name || m.email,
        m.email,
        m.role,
        m.status,
      ])

      console.log(formatTable(['Name', 'Email', 'Role', 'Status'], rows))
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
