import {expect} from 'chai'

import {parseSkillMeta} from '../../src/lib/skill-manager.js'

describe('parseSkillMeta', () => {
  it('parses valid YAML frontmatter', () => {
    const content = `---
name: my-skill
description: A test skill
---
# My Skill`
    const result = parseSkillMeta(content)
    expect(result).to.deep.equal({description: 'A test skill', name: 'my-skill'})
  })

  it('returns null if no frontmatter', () => {
    const result = parseSkillMeta('# Just a heading')
    expect(result).to.be.null
  })

  it('returns null if name is missing', () => {
    const content = `---
description: No name field
---`
    const result = parseSkillMeta(content)
    expect(result).to.be.null
  })

  it('defaults description to empty string', () => {
    const content = `---
name: minimal
---`
    const result = parseSkillMeta(content)
    expect(result).to.deep.equal({description: '', name: 'minimal'})
  })
})
