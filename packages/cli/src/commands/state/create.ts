import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, printJson, success} from '../../lib/output.js'
import {promptSelect, promptText} from '../../lib/prompts.js'

const STATE_GROUPS = [
  {name: 'Backlog', value: 'backlog'},
  {name: 'Unstarted', value: 'unstarted'},
  {name: 'Started', value: 'started'},
  {name: 'Completed', value: 'completed'},
  {name: 'Cancelled', value: 'cancelled'},
]

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

export default class StateCreate extends BaseCommand {
  static description = 'Create a new state'
  static flags = {
    color: Flags.string({char: 'c', description: 'Hex color code'}),
    group: Flags.string({char: 'g', description: 'State group', options: ['backlog', 'unstarted', 'started', 'completed', 'cancelled']}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({char: 'n', description: 'State name'}),
    project: Flags.string({char: 'p', description: 'Project ID', required: true}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(StateCreate)
    const api = this.requireApi()
    const config = this.requireConfig()

    const name = flags.name || (await promptText('State name:'))

    let {group} = flags
    if (!group && !flags['no-input']) {
      group = await promptSelect('State group:', STATE_GROUPS)
    }

    let {color} = flags
    if (!color && !flags['no-input']) {
      color = await promptSelect('Choose color:', COLORS)
    }

    if (!group || !color) {
      this.error('Group and color are required. Use --group and --color or run without --no-input.')
    }

    const spinner = createSpinner('Creating state...')
    try {
      const state = await api.createState(config.workspace, flags.project, {color, group, name})
      spinner.stop()

      if (flags.json) {
        printJson(state)
      } else {
        success(`Created state: ${state.name}`)
      }
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
