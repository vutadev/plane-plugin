import {execFileSync} from 'node:child_process'
import {promises as fs} from 'node:fs'
import {homedir, tmpdir} from 'node:os'
import {basename, join, resolve} from 'node:path'

export interface SkillMeta {
  description: string
  name: string
}

export interface SkillSource {
  installedAt: string
  originalPath?: string
  type: 'git' | 'local'
  url?: string
}

export interface InstalledSkill extends SkillMeta {
  path: string
  source?: null | SkillSource
  type: 'copy' | 'symlink'
}

export function getSkillsDir(): string {
  if (process.env.PLANE_SKILLS_DIR) {
    return process.env.PLANE_SKILLS_DIR
  }

  return join(homedir(), '.claude', 'skills')
}

export function parseSkillMeta(content: string): null | SkillMeta {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/)
  if (!match) return null

  const frontmatter = match[1]
  const nameMatch = frontmatter.match(/^name:\s*(.+)$/m)
  const descMatch = frontmatter.match(/^description:\s*(.+)$/m)

  if (!nameMatch) return null

  return {
    description: descMatch ? descMatch[1].trim() : '',
    name: nameMatch[1].trim(),
  }
}

export async function discoverSkillDir(baseDir: string): Promise<string> {
  const absBase = resolve(baseDir)

  // Check baseDir itself
  try {
    await fs.access(join(absBase, 'SKILL.md'))
    return absBase
  } catch { /* not here */ }

  // Check skills/*/SKILL.md
  const skillsPath = join(absBase, 'skills')
  try {
    const entries = await fs.readdir(skillsPath, {withFileTypes: true})
    const checks = entries
      .filter((e) => e.isDirectory())
      .map(async (entry) => {
        const candidate = join(skillsPath, entry.name, 'SKILL.md')
        try {
          await fs.access(candidate)
          return join(skillsPath, entry.name)
        } catch {
          return null
        }
      })
    const found = (await Promise.all(checks)).filter((p): p is string => p !== null)

    if (found.length === 1) return found[0]
    if (found.length > 1) {
      throw new Error(`Multiple skills found: ${found.map((f) => basename(f)).join(', ')}. Specify the path explicitly.`)
    }
  } catch (error) {
    if (error instanceof Error && error.message.includes('Multiple skills')) throw error
    // skills/ dir doesn't exist, fall through
  }

  throw new Error('No SKILL.md found in current directory or skills/*/')
}

export async function readSkillMeta(skillDir: string): Promise<SkillMeta> {
  const content = await fs.readFile(join(skillDir, 'SKILL.md'), 'utf8')
  const meta = parseSkillMeta(content)
  if (!meta) {
    throw new Error('SKILL.md is missing required "name" in YAML frontmatter')
  }

  return meta
}

async function writeSkillSource(skillName: string, source: SkillSource): Promise<void> {
  await fs.writeFile(
    join(getSkillsDir(), `${skillName}.source.json`),
    JSON.stringify(source, null, 2),
    'utf8',
  )
}

export async function readSkillSource(skillName: string): Promise<null | SkillSource> {
  try {
    const content = await fs.readFile(
      join(getSkillsDir(), `${skillName}.source.json`),
      'utf8',
    )
    return JSON.parse(content) as SkillSource
  } catch {
    return null
  }
}

export async function installFromLocal(skillDir: string, options?: {force?: boolean}): Promise<InstalledSkill> {
  const absSkillDir = resolve(skillDir)
  const meta = await readSkillMeta(absSkillDir)
  const targetDir = join(getSkillsDir(), meta.name)

  // Ensure parent dir exists
  await fs.mkdir(getSkillsDir(), {recursive: true})

  // Check if already installed
  try {
    await fs.access(targetDir)
    if (!options?.force) {
      throw new Error(`Skill "${meta.name}" already installed. Use --force to overwrite.`)
    }

    // Remove existing
    await fs.rm(targetDir, {force: true, recursive: true})
  } catch (error) {
    if (error instanceof Error && error.message.includes('already installed')) throw error
  }

  // Create symlink
  await fs.symlink(absSkillDir, targetDir, 'dir')

  // Persist source metadata
  await writeSkillSource(meta.name, {
    installedAt: new Date().toISOString(),
    originalPath: absSkillDir,
    type: 'local',
  })

  // Run install.sh if it exists (non-fatal)
  await runPostInstall(absSkillDir)

  return {...meta, path: targetDir, type: 'symlink'}
}

export async function installFromGit(source: string, options?: {force?: boolean}): Promise<InstalledSkill> {
  // Normalize source: "github:user/repo" → "https://github.com/user/repo.git"
  let url = source
  if (url.startsWith('github:')) {
    url = `https://github.com/${url.slice(7)}.git`
  }

  // Clone to temp directory
  const tempDir = join(tmpdir(), `plane-skill-${Date.now()}`)
  try {
    execFileSync('git', ['clone', '--depth', '1', url, tempDir], {stdio: 'pipe'})
  } catch {
    throw new Error(`Failed to clone ${url}`)
  }

  try {
    // Discover skill in cloned repo
    const skillDir = await discoverSkillDir(tempDir)
    const meta = await readSkillMeta(skillDir)
    const targetDir = join(getSkillsDir(), meta.name)

    // Ensure parent dir exists
    await fs.mkdir(getSkillsDir(), {recursive: true})

    // Check if already installed
    try {
      await fs.access(targetDir)
      if (!options?.force) {
        throw new Error(`Skill "${meta.name}" already installed. Use --force to overwrite.`)
      }

      await fs.rm(targetDir, {force: true, recursive: true})
    } catch (error) {
      if (error instanceof Error && error.message.includes('already installed')) throw error
    }

    // Copy skill dir to target
    execFileSync('cp', ['-r', skillDir, targetDir], {stdio: 'pipe'})

    // Persist source metadata
    await writeSkillSource(meta.name, {
      installedAt: new Date().toISOString(),
      type: 'git',
      url: source,
    })

    // Run install.sh if it exists (non-fatal)
    await runPostInstall(targetDir)

    return {...meta, path: targetDir, type: 'copy'}
  } finally {
    // Cleanup temp dir
    await fs.rm(tempDir, {force: true, recursive: true}).catch(() => {})
  }
}

export async function removeSkill(name: string): Promise<void> {
  const targetDir = join(getSkillsDir(), name)
  try {
    await fs.access(targetDir)
  } catch {
    throw new Error(`Skill "${name}" is not installed`)
  }

  await fs.rm(targetDir, {force: true, recursive: true})
  // Clean up source metadata
  await fs.rm(join(getSkillsDir(), `${name}.source.json`), {force: true}).catch(() => {})
}

export async function updateSkill(name: string): Promise<InstalledSkill> {
  const targetDir = join(getSkillsDir(), name)

  try {
    await fs.access(targetDir)
  } catch {
    throw new Error(`Skill "${name}" is not installed`)
  }

  const source = await readSkillSource(name)
  const stat = await fs.lstat(targetDir)
  const isSymlink = stat.isSymbolicLink()

  if (isSymlink) {
    // For local symlinks: remove and re-create symlink
    const originalPath = source?.originalPath ?? await fs.readlink(targetDir)
    await fs.rm(targetDir, {force: true, recursive: true})
    await fs.rm(join(getSkillsDir(), `${name}.source.json`), {force: true}).catch(() => {})
    return installFromLocal(originalPath, {force: true})
  }

  // For git-installed (copy): need the URL
  if (!source?.url) {
    throw new Error(
      `No source URL recorded for skill "${name}". ` +
      `Re-install with "skill install github:user/repo" to enable updates.`,
    )
  }

  await fs.rm(targetDir, {force: true, recursive: true})
  await fs.rm(join(getSkillsDir(), `${name}.source.json`), {force: true}).catch(() => {})

  return installFromGit(source.url, {force: true})
}

export async function listSkills(): Promise<InstalledSkill[]> {
  const skillsDir = getSkillsDir()
  try {
    await fs.access(skillsDir)
  } catch {
    return []
  }

  const entries = await fs.readdir(skillsDir, {withFileTypes: true})
  const candidates = entries.filter((e) => e.isDirectory() || e.isSymbolicLink())

  const results = await Promise.all(
    candidates.map(async (entry): Promise<InstalledSkill | null> => {
      const entryPath = join(skillsDir, entry.name)
      const skillMdPath = join(entryPath, 'SKILL.md')

      try {
        await fs.access(skillMdPath)
      } catch {
        return null
      }

      const stat = await fs.lstat(entryPath)
      const type = stat.isSymbolicLink() ? 'symlink' : 'copy'
      const realPath = stat.isSymbolicLink() ? await fs.readlink(entryPath) : entryPath
      const source = await readSkillSource(entry.name)

      try {
        const meta = await readSkillMeta(entryPath)
        return {...meta, path: realPath, source, type}
      } catch {
        return null
      }
    }),
  )

  return results.filter((s): s is InstalledSkill => s !== null)
}

async function runPostInstall(dir: string): Promise<void> {
  const scriptPath = join(dir, 'scripts', 'install.sh')
  try {
    await fs.access(scriptPath)
    execFileSync('bash', [scriptPath], {cwd: dir, stdio: 'pipe'})
  } catch {
    // Non-fatal: install.sh missing or failed
  }
}
