import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, formatTable, info, printJson} from '../../lib/output.js'
import {promptSelect} from '../../lib/prompts.js'

export default class CycleList extends BaseCommand {
  static description = 'List cycles (sprints) in a project'
  static flags = {
    archived: Flags.boolean({description: 'Include archived cycles'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({char: 'p', description: 'Project ID'}),
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(CycleList)
    const api = this.requireApi()
    const config = this.requireConfig()

    let projectId = flags.project
    if (!projectId && !flags['no-input']) {
      const projects = await api.listProjects(config.workspace)
      projectId = await promptSelect(
        'Select project:',
        projects.results.map((p) => ({name: p.name, value: p.id})),
      )
    }

    if (!projectId) {
      this.error('--project is required')
    }

    const spinner = createSpinner('Loading cycles...')
    try {
      const {results} = await api.listCycles(config.workspace, projectId, flags.archived)
      spinner.stop()

      if (flags.json) {
        printJson(results)
        return
      }

      if (results.length === 0) {
        info('No cycles found')
        return
      }

      const rows = results.map((c) => [
        c.id.slice(0, 8),
        c.name.slice(0, 30),
        c.start_date || '-',
        c.end_date || '-',
        c.archived ? '✓' : '',
      ])

      console.log(formatTable(['ID', 'Name', 'Start', 'End', 'Archived'], rows))
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
