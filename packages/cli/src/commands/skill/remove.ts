import {Args, Command, Flags} from '@oclif/core'

import {success} from '../../lib/output.js'
import {promptConfirm} from '../../lib/prompts.js'
import {removeSkill} from '../../lib/skill-manager.js'

export default class SkillRemove extends Command {
  static args = {
    name: Args.string({description: 'Name of the skill to remove', required: true}),
  }
  static description = 'Remove an installed Claude Code skill'
  static examples = [
    '<%= config.bin %> skill remove plane',
    '<%= config.bin %> skill remove plane --force',
  ]
  static flags = {
    force: Flags.boolean({default: false, description: 'Skip confirmation prompt'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(SkillRemove)

    if (!flags.force) {
      const confirmed = await promptConfirm(`Remove skill "${args.name}"?`)
      if (!confirmed) {
        this.log('Cancelled.')
        return
      }
    }

    try {
      await removeSkill(args.name)
      success(`Removed skill "${args.name}"`)
    } catch (error) {
      this.error(error instanceof Error ? error.message : String(error), {exit: 1})
    }
  }
}
