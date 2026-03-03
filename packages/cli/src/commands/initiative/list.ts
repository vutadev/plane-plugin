import {BaseCommand} from '../../base-command.js'
import {createSpinner, formatTable, info} from '../../lib/output.js'

export default class InitiativeList extends BaseCommand {
  static description = 'List initiatives'

  async run(): Promise<void> {
    const api = this.requireApi()
    const config = this.requireConfig()

    const spinner = createSpinner('Loading initiatives...')
    try {
      const {results} = await api.listInitiatives(config.workspace)
      spinner.stop()

      if (results.length === 0) {
        info('No initiatives found')
        return
      }

      const rows = results.map((i) => [
        i.id.slice(0, 8),
        i.name.slice(0, 35),
        i.created_at.slice(0, 10),
      ])

      console.log(formatTable(['ID', 'Name', 'Created'], rows))
    } catch (error) {
      spinner.stop()
      throw error
    }
  }
}
