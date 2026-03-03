import {Args, Flags} from '@oclif/core'

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

export default class LabelUpdate extends BaseCommand {
  static args = {
    labelId: Args.string({description: 'Label ID', required: true}),
  }
  static description = 'Update label'
  static flags = {
    color: Flags.string({char: 'c', description: 'New hex color code'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({char: 'n', description: 'New label name'}),
    project: Flags.string({char: 'p', description: 'Project ID', required: true}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(LabelUpdate)
    const api = this.requireApi()
    const config = this.requireConfig()

    let {name} = flags
    let {color} = flags

    if (!name && !color && !flags['no-input']) {
      const {results} = await api.listLabels(config.workspace, flags.project)
      const label = results.find((l) => l.id === args.labelId)
      if (!label) {
        this.error(`Label ${args.labelId} not found`)
      }

      name = await promptText('Label name:', label.name)
      color = await promptSelect('Choose color:', COLORS)
    }

    const spinner = createSpinner('Updating label...')
    try {
      const label = await api.updateLabel(config.workspace, flags.project, args.labelId, {
        color,
        name,
      })
      spinner.stop()

      if (flags.json) {
        printJson(label)
      } else {
        success(`Updated label: ${label.name}`)
      }
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
