import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, formatTable, info, printJson} from '../../lib/output.js'

export default class ProjectList extends BaseCommand {
  static description = 'List all projects in workspace'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(ProjectList)
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Loading projects...')
    try {
      const {results} = await api.listProjects(config.workspace)
      spinner.stop()

      if (flags.json) {
        printJson(results)
        return
      }

      if (results.length === 0) {
        info('No projects found')
        return
      }

      const rows = results.map((p) => [
        p.identifier,
        p.name,
        p.description?.slice(0, 40) || '-',
        p.id.slice(0, 8),
      ])

      console.log(formatTable(['ID', 'Name', 'Description', 'UUID'], rows))
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
