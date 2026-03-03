import {Args, Command, Flags} from '@oclif/core'

import {createSpinner, info, success} from '../../lib/output.js'
import {discoverSkillDir, installFromGit, installFromLocal} from '../../lib/skill-manager.js'

export default class SkillInstall extends Command {
  static args = {
    source: Args.string({
      description: 'Skill source: local path or github:user/repo (default: current directory)',
      required: false,
    }),
  }
  static description = 'Install a Claude Code skill'
  static examples = [
    '<%= config.bin %> skill install',
    '<%= config.bin %> skill install ./path/to/skill',
    '<%= config.bin %> skill install github:user/repo',
  ]
  static flags = {
    force: Flags.boolean({default: false, description: 'Overwrite existing skill'}),
  }

  async run(): Promise<void> {
    const {args, flags} = await this.parse(SkillInstall)
    const {source} = args

    const isGit = source?.startsWith('github:') || source?.startsWith('https://') || source?.endsWith('.git')

    const spinner = createSpinner(isGit ? `Cloning and installing skill...` : 'Installing skill...')

    try {
      if (isGit) {
        const result = await installFromGit(source!, {force: flags.force})
        spinner.stop()
        success(`Installed skill "${result.name}" (copied from git)`)
        info(`Location: ${result.path}`)
      } else {
        const baseDir = source || process.cwd()
        const skillDir = await discoverSkillDir(baseDir)
        const result = await installFromLocal(skillDir, {force: flags.force})
        spinner.stop()
        success(`Installed skill "${result.name}" (symlinked)`)
        info(`Location: ${result.path}`)
      }
    } catch (error) {
      spinner.stop()
      this.error(error instanceof Error ? error.message : String(error), {exit: 1})
    }
  }
}
