import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, error, info, printJson, success} from '../../lib/output.js'
import {promptText} from '../../lib/prompts.js'

export default class ProjectCreate extends BaseCommand {
  static description = 'Create a new project'
  static flags = {
    description: Flags.string({description: 'Project description'}),
    identifier: Flags.string({description: 'Short identifier (e.g., MYPROJ)'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({description: 'Project name'}),
    network: Flags.integer({default: 2, description: 'Network type'}),
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(ProjectCreate)
    const api = this.requireApi()
    const config = this.requireConfig()

    // Interactive prompts for missing args
    let {name} = flags
    let {identifier} = flags

    if (!name && !flags['no-input']) {
      name = await promptText('Project name:')
    }

    if (!name) {
      error('Project name is required')
      process.exit(1)
    }

    if (!identifier && !flags['no-input']) {
      identifier = await promptText(
        'Project identifier (short code):',
        this.generateIdentifier(name),
      )
    }

    if (!identifier) {
      error('Project identifier is required')
      process.exit(1)
    }

    const data = {
      description: flags.description,
      identifier: identifier.toUpperCase(),
      name,
      network: flags.network,
    }

    const spinner = createSpinner('Creating project...')
    try {
      const project = await api.createProject(config.workspace, data)
      spinner.stop()

      if (flags.json) {
        printJson(project)
      } else {
        success(`Created project "${project.name}" (${project.identifier})`)
        info(`ID: ${project.id}`)
      }
    } catch (error_) {
      spinner.stop()
      throw error_
    }
  }

  private generateIdentifier(name: string): string {
    return name
      .toUpperCase()
      .replaceAll(/[^A-Z0-9]/g, '')
      .slice(0, 6)
  }
}
