import {Args, Flags} from '@oclif/core'
import chalk from 'chalk'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, printJson,stripHtml} from '../../lib/output.js'

export default class PageGetWorkspace extends BaseCommand {
  static args = {
    pageId: Args.string({description: 'Page ID', required: true}),
  }
  static description = 'Get a workspace page'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(PageGetWorkspace)
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Loading page...')
    try {
      const page = await api.getWorkspacePage(config.workspace, args.pageId)
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
