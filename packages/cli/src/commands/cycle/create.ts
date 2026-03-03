import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, error, printJson, success} from '../../lib/output.js'
import {promptConfirm, promptSelect,promptText} from '../../lib/prompts.js'

export default class CycleCreate extends BaseCommand {
  static description = 'Create a new cycle (sprint)'
  static flags = {
    description: Flags.string({char: 'd', description: 'Description'}),
    end: Flags.string({description: 'End date (YYYY-MM-DD)'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({char: 'n', description: 'Cycle name'}),
    project: Flags.string({char: 'p', description: 'Project ID'}),
    start: Flags.string({description: 'Start date (YYYY-MM-DD)'}),
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(CycleCreate)
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
      error('--project is required')
      process.exit(1)
    }

    const name = flags.name || (await promptText('Cycle name:'))

    if (!name) {
      error('Cycle name is required')
      process.exit(1)
    }

    let startDate = flags.start
    let endDate = flags.end

    if (!flags['no-input'] && (!startDate || !endDate)) {
      const addDates = await promptConfirm('Set start/end dates?')
      if (addDates) {
        startDate = await promptText('Start date (YYYY-MM-DD):')
        endDate = await promptText('End date (YYYY-MM-DD):')
      }
    }

    const spinner = createSpinner('Creating cycle...')
    try {
      const cycle = await api.createCycle(config.workspace, projectId, {
        description: flags.description,
        end_date: endDate,
        name,
        start_date: startDate,
      })
      spinner.stop()

      if (flags.json) {
        printJson(cycle)
      } else {
        success(`Created cycle: ${cycle.name} (${cycle.id})`)
      }
    } catch (error_) {
      spinner.stop()
      throw error_
    }
  }
}

