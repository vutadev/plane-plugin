import {runCommand} from '@oclif/test'
import {expect} from 'chai'

describe('skill commands', () => {
  it('skill list runs without error', async () => {
    const {error} = await runCommand(['skill', 'list'])
    expect(error).to.be.undefined
  })

  it('skill install --help shows help', async () => {
    const {stdout} = await runCommand(['skill', 'install', '--help'])
    expect(stdout).to.contain('Install a Claude Code skill')
  })

  it('skill remove --help shows help', async () => {
    const {stdout} = await runCommand(['skill', 'remove', '--help'])
    expect(stdout).to.contain('Remove an installed Claude Code skill')
  })

  it('skill update --help shows help', async () => {
    const {stdout} = await runCommand(['skill', 'update', '--help'])
    expect(stdout).to.contain('Update installed Claude Code skills')
  })
})
