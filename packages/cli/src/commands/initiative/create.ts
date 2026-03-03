import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, printJson, success} from '../../lib/output.js'
import {promptConfirm, promptText} from '../../lib/prompts.js'

export default class InitiativeCreate extends BaseCommand {
  static description = 'Create initiative'
  static flags = {
    description: Flags.string({char: 'd', description: 'Description'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({char: 'n', description: 'Initiative name'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(InitiativeCreate)
    const api = this.requireApi()
    const config = this.requireConfig()

    const name = flags.name || (await promptText('Initiative name:'))

    let {description} = flags
    if (!description && !flags['no-input']) {
      const addDesc = await promptConfirm('Add description?')
      if (addDesc) {
        description = await promptText('Description:')
      }
    }

    const spinner = createSpinner('Creating initiative...')
    try {
      const initiative = await api.createInitiative(config.workspace, {
        description,
        name,
      })
      spinner.stop()

      if (flags.json) {
        printJson(initiative)
      } else {
        success(`Created initiative: ${initiative.name}`)
      }
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
