import {Args, Command} from '@oclif/core'

import {createSpinner, info, success, warning} from '../../lib/output.js'
import {listSkills, updateSkill} from '../../lib/skill-manager.js'

export default class SkillUpdate extends Command {
  static args = {
    name: Args.string({
      description: 'Name of the skill to update (omit to update all)',
      required: false,
    }),
  }
  static description = 'Update installed Claude Code skills'
  static examples = [
    '<%= config.bin %> skill update',
    '<%= config.bin %> skill update plane',
  ]

  async run(): Promise<void> {
    const {args} = await this.parse(SkillUpdate)

    if (args.name) {
      const spinner = createSpinner(`Updating skill "${args.name}"...`)
      try {
        const result = await updateSkill(args.name)
        spinner.stop()
        success(`Updated skill "${result.name}" (${result.type})`)
        info(`Location: ${result.path}`)
      } catch (error) {
        spinner.stop()
        this.error(error instanceof Error ? error.message : String(error), {exit: 1})
      }
    } else {
      const skills = await listSkills()
      if (skills.length === 0) {
        info('No skills installed.')
        return
      }

      const results = await Promise.allSettled(
        skills.map(async (skill) => {
          const spinner = createSpinner(`Updating "${skill.name}"...`)
          try {
            await updateSkill(skill.name)
            spinner.stop()
            success(`Updated "${skill.name}"`)
          } catch (error) {
            spinner.stop()
            warning(`Failed to update "${skill.name}": ${error instanceof Error ? error.message : String(error)}`)
            throw error
          }
        }),
      )

      const updated = results.filter((r) => r.status === 'fulfilled').length
      const failed = results.filter((r) => r.status === 'rejected').length
      info(`Updated ${updated} skill(s)${failed > 0 ? `, ${failed} failed` : ''}`)
    }
  }
}
