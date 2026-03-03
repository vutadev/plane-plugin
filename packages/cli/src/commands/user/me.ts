import {Flags} from '@oclif/core'
import chalk from 'chalk'

import {BaseCommand} from '../../base-command.js'
import {createSpinner, printJson} from '../../lib/output.js'

export default class UserMe extends BaseCommand {
  static description = 'Get current user info'
  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(UserMe)
    const api = this.requireApi()

    const spinner = createSpinner('Loading user info...')
    try {
      const user = await api.getCurrentUser()
      spinner.stop()

      if (flags.json) {
        printJson(user)
        return
      }

      console.log(chalk.bold(user.display_name || user.email))
      console.log(`Email: ${user.email}`)
      console.log(`ID: ${user.id}`)
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
