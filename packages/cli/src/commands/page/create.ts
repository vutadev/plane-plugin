import {Flags} from '@oclif/core'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, printJson, success} from '../../lib/output.js'
import {promptConfirm, promptText} from '../../lib/prompts.js'

export default class PageCreate extends BaseCommand {
  static description = 'Create a page'
  static flags = {
    description: Flags.string({char: 'd', description: 'Page content (HTML)'}),
    json: Flags.boolean({description: 'Output as JSON'}),
    name: Flags.string({char: 'n', description: 'Page title'}),
    project: Flags.string({char: 'p', description: 'Project ID (omit for workspace page)'}),
    ...BaseCommand.baseFlags,
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(PageCreate)
    const api = this.requireApi()
    const config = this.requireConfig()

    const name = flags.name || (await promptText('Page title:'))

    let {description} = flags
    if (!description && !flags['no-input']) {
      const addDesc = await promptConfirm('Add content?')
      if (addDesc) {
        description = await promptText('Content (HTML):')
      }
    }

    const spinner = createSpinner('Creating page...')
    try {
      const page = await (flags.project ? api.createProjectPage(config.workspace, flags.project, {
          description_html: description,
          name,
        }) : api.createWorkspacePage(config.workspace, {
          description_html: description,
          name,
        }));
      spinner.stop()

      if (flags.json) {
        printJson(page)
      } else {
        success(`Created page: ${page.name}`)
      }
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
