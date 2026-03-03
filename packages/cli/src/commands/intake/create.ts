import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, printJson, success} from '../../lib/output.js'
import {promptConfirm, promptText} from '../../lib/prompts.js'

export default class IntakeCreate extends BaseCommand {
  static description = 'Create intake item'
  static flags = {
    description: Flags.string({char: 'd', description: 'Description'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({char: 'n', description: 'Intake title'}),
    project: Flags.string({char: 'p', description: 'Project ID', required: true}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(IntakeCreate)
    const api = this.requireApi()
    const config = this.requireConfig()

    const name = flags.name || (await promptText('Intake title:'))

    let {description} = flags
    if (!description && !flags['no-input']) {
      const addDesc = await promptConfirm('Add description?')
      if (addDesc) {
        description = await promptText('Description:')
      }
    }

    const spinner = createSpinner('Creating intake...')
    try {
      const intake = await api.createIntake(config.workspace, flags.project, {
        description_html: description,
        name,
      })
      spinner.stop()

      if (flags.json) {
        printJson(intake)
      } else {
        success(`Created intake: ${intake.name}`)
      }
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
