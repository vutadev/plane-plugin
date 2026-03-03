import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {PlaneAPI} from '../../lib/api.js'
import {error, printJson, success} from '../../lib/output.js'
import {promptConfirm, promptSelect, promptText} from '../../lib/prompts.js'
import {PlaneConfig} from '../../types/config.js'

export default class ModuleCreate extends BaseCommand {
  static description = 'Create a new module'
  static flags = {
    description: Flags.string({char: 'd', description: 'Description'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({char: 'n', description: 'Module name'}),
    project: Flags.string({char: 'p', description: 'Project ID'}),
    start: Flags.string({description: 'Start date (YYYY-MM-DD)'}),
    target: Flags.string({description: 'Target date (YYYY-MM-DD)'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(ModuleCreate)
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

    const name = flags.name || (await promptText('Module name:'))
    const {description} = flags

    let startDate = flags.start
    let targetDate = flags.target

    if (!flags['no-input'] && (!startDate || !targetDate)) {
      const addDates = await promptConfirm('Set start/target dates?')
      if (addDates) {
        startDate = await promptText('Start date (YYYY-MM-DD):')
        targetDate = await promptText('Target date (YYYY-MM-DD):')
      }
    }

    const module = await this.withSpinner('Creating module...', () =>
      api.createModule(config.workspace, projectId, {
        description,
        name,
        start_date: startDate,
        target_date: targetDate,
      }),
    )

    if (flags.json) {
      printJson(module)
    } else {
      success(`Created module: ${module.name} (${module.id})`)
    }
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
