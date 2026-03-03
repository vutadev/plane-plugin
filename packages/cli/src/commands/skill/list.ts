import {Command, Flags} from '@oclif/core'

import {formatTable, info, printJson} from '../../lib/output.js'
import {listSkills} from '../../lib/skill-manager.js'

export default class SkillList extends Command {
  static description = 'List installed Claude Code skills'
  static examples = [
    '<%= config.bin %> skill list',
    '<%= config.bin %> skill list --json',
  ]
  static flags = {
    json: Flags.boolean({default: false, description: 'Output as JSON'}),
  }

  async run(): Promise<void> {
    const {flags} = await this.parse(SkillList)

    const skills = await listSkills()

    if (skills.length === 0) {
      info('No skills installed. Use "plane skill install" to install one.')
      return
    }

    if (flags.json) {
      printJson(skills)
      return
    }

    const table = formatTable(
      ['Name', 'Description', 'Type', 'Path'],
      skills.map((s) => [s.name, s.description, s.type, s.path]),
    )

    this.log(table)
  }
}
