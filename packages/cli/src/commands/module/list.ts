import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {PlaneAPI} from '../../lib/api.js'
import {error, formatTable, printJson, success} from '../../lib/output.js'
import {promptSelect} from '../../lib/prompts.js'
import {PlaneConfig} from '../../types/config.js'

export default class ModuleList extends BaseCommand {
  static description = 'List modules in a project'
  static flags = {
    archived: Flags.boolean({description: 'Include archived modules'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({char: 'p', description: 'Project ID'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(ModuleList)
    const api = this.requireApi()
    const config = this.requireConfig()

    let projectId = flags.project
    if (!projectId && !flags['no-input']) {
      projectId = await this.promptForProject(api, config)
    }

    if (!projectId) {
      error('--project is required')
      process.exit(1)
    }

    const {results} = await this.withSpinner('Loading modules...', () =>
      api.listModules(config.workspace, projectId, flags.archived),
    )

    if (flags.json) {
      printJson(results)
      return
    }

    const rows = results.map((m) => [
      m.id.slice(0, 8),
      m.name.slice(0, 30),
      m.start_date || '-',
      m.target_date || '-',
      m.archived ? '✓' : '',
    ])

    console.log(formatTable(['ID', 'Name', 'Start', 'Target', 'Archived'], rows))
    success(`Found ${results.length} modules`)
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
