import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, printJson, success} from '../../lib/output.js'
import {promptSelect, promptText} from '../../lib/prompts.js'

const COLORS = [
  {name: 'Red', value: '#ef4444'},
  {name: 'Orange', value: '#f97316'},
  {name: 'Yellow', value: '#eab308'},
  {name: 'Green', value: '#22c55e'},
  {name: 'Blue', value: '#3b82f6'},
  {name: 'Purple', value: '#8b5cf6'},
  {name: 'Pink', value: '#ec4899'},
  {name: 'Gray', value: '#6b7280'},
]

export default class LabelCreate extends BaseCommand {
  static description = 'Create a new label'
  static flags = {
    color: Flags.string({char: 'c', description: 'Hex color code'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({char: 'n', description: 'Label name'}),
    project: Flags.string({char: 'p', description: 'Project ID', required: true}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(LabelCreate)
    const api = this.requireApi()
    const config = this.requireConfig()

    const name = flags.name || (await promptText('Label name:'))
    let {color} = flags
    if (!color && !flags['no-input']) {
      color = await promptSelect('Choose color:', COLORS)
    }

    if (!color) {
      this.error('Color is required. Use --color or run without --no-input.')
    }

    const spinner = createSpinner('Creating label...')
    try {
      const label = await api.createLabel(config.workspace, flags.project, {color, name})
      spinner.stop()

      if (flags.json) {
        printJson(label)
      } else {
        success(`Created label: ${label.name}`)
      }
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
