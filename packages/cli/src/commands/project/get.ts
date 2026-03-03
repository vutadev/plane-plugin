import {Args, Flags} from '@oclif/core'
import chalk from 'chalk'

import {BaseCommand} from '../../base-command.js'
import {printJson} from '../../lib/output.js'

export default class ProjectGet extends BaseCommand {
  static args = {
    id: Args.string({description: 'Project ID or identifier', required: true}),
  }
  static description = 'Get project details'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(ProjectGet)
    const api = this.requireApi()
    const config = this.requireConfig()

    const project = await this.withSpinner('Loading project...', () =>
      api.getProject(config.workspace, args.id),
    )

    if (flags.json) {
      printJson(project)
      return
    }

    console.log(chalk.bold('\n' + project.name))
    console.log(chalk.gray('─'.repeat(50)))
    console.log(`Identifier: ${chalk.cyan(project.identifier)}`)
    console.log(`ID: ${project.id}`)
    console.log(`Description: ${project.description || '-'}`)
    console.log(`Created: ${new Date(project.created_at).toLocaleString()}`)
  }
}
