import {Args, Flags} from '@oclif/core'
import chalk from 'chalk'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, printJson, stripHtml} from '../../lib/output.js'

export default class PageGetProject extends BaseCommand {
  static args = {
    pageId: Args.string({description: 'Page ID', required: true}),
  }
  static description = 'Get a project page'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
    project: Flags.string({char: 'p', description: 'Project ID', required: true}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(PageGetProject)
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Loading page...')
    try {
      const page = await api.getProjectPage(config.workspace, flags.project, args.pageId)
      spinner.stop()

      if (flags.json) {
        printJson(page)
        return
      }

      console.log(chalk.bold(page.name))
      console.log(chalk.gray('\u2500'.repeat(60)))
      if (page.description_html) {
        console.log(stripHtml(page.description_html))
      }
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
