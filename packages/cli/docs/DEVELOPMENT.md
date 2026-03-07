# Development Guide

## Prerequisites

- Node.js >= 18.0.0
- npm

## Setup

```bash
# Install dependencies
npm install

# Build
npm run build

# Run in development mode
node --import=tsx/esm bin/dev.js skill list
```

## Project Structure

```
packages/cli/
├── bin/                    # Entry points (run.js, dev.js)
├── src/
│   ├── index.ts            # Re-exports @oclif/core run
│   ├── commands/
│   │   └── skill/          # Skill management commands
│   │       ├── install.ts  # Install from local path or GitHub
│   │       ├── list.ts     # List installed skills
│   │       ├── remove.ts   # Remove a skill
│   │       └── update.ts   # Update skills from original source
│   └── lib/
│       ├── skill-manager.ts # Core skill install/update/remove/list logic
│       ├── output.ts        # Table formatting, spinners, colored messages
│       ├── prompts.ts       # Confirmation prompt wrapper
│       └── errors.ts        # Error classes and handler
├── test/
│   ├── commands/
│   │   └── skill.test.ts   # Command integration tests
│   └── lib/
│       └── skill-manager.test.ts  # Unit tests for skill manager
├── docs/
│   └── DEVELOPMENT.md      # This file
├── package.json
└── tsconfig.json
```

## Scripts

```bash
# Build (compile TypeScript to dist/)
npm run build

# Run tests + lint
npm test

# Lint only
npm run lint

# Generate oclif manifest
npx oclif manifest
```

## Architecture

### Skill Manager (`src/lib/skill-manager.ts`)

Core module handling all skill operations:

- **`installFromLocal()`** — Creates a symlink at `~/.claude/skills/<name>` pointing to the source directory. Writes a `<name>.source.json` metadata file to track the original path.
- **`installFromGit()`** — Clones a git repo to a temp directory, discovers the skill (looks for `SKILL.md`), copies it to `~/.claude/skills/<name>`. Writes source metadata with the original git URL.
- **`updateSkill()`** — Re-installs a skill from its original source. For git skills, deletes and re-clones. For local symlinks, removes and re-creates. Falls back to `fs.readlink()` if no source metadata exists.
- **`removeSkill()`** — Deletes the skill directory/symlink and its source metadata file.
- **`listSkills()`** — Reads `~/.claude/skills/`, filters entries with `SKILL.md`, detects symlinks vs copies, and reads source metadata.

### Source Metadata

When a skill is installed, a `<name>.source.json` file is written alongside the skill directory in `~/.claude/skills/`:

```json
{
  "type": "git",
  "url": "github:user/repo",
  "installedAt": "2026-03-07T..."
}
```

```json
{
  "type": "local",
  "originalPath": "/absolute/path/to/skill",
  "installedAt": "2026-03-07T..."
}
```

This metadata enables `skill update` to re-install from the original source without the user re-specifying it.

### Skill Discovery

`discoverSkillDir()` looks for `SKILL.md` in two locations:
1. The base directory itself
2. `<baseDir>/skills/*/SKILL.md` (one level deep)

If multiple skills are found, it throws an error asking the user to specify the path explicitly.

### SKILL.md Format

Skills are identified by their `SKILL.md` file with YAML frontmatter:

```markdown
---
name: my-skill
description: A description of the skill
---

# Skill content here...
```

The `name` field is required. The `description` field is optional (defaults to empty string).

## Testing

```bash
# Run all tests
npm test

# Run tests only (no lint)
npx mocha --forbid-only "test/**/*.test.ts" --import=tsx/esm

# Run a specific test file
npx mocha "test/lib/skill-manager.test.ts" --import=tsx/esm
```

Tests use [mocha](https://mochajs.org/) + [chai](https://www.chaijs.com/) with [tsx](https://tsx.is/) for TypeScript execution, and [@oclif/test](https://github.com/oclif/test) for command integration tests.

## Development Workflow

```bash
# Symlink your skill during development
node bin/dev.js skill install ./my-skill

# Changes to SKILL.md are reflected immediately via symlink

# Test from GitHub when ready
node bin/dev.js skill remove my-skill
node bin/dev.js skill install github:myuser/my-skill

# Update to pull latest
node bin/dev.js skill update my-skill
```

## Dependencies

| Package | Purpose |
| --- | --- |
| `@oclif/core` | CLI framework |
| `@oclif/plugin-help` | Help command |
| `@oclif/plugin-plugins` | Plugin management |
| `@inquirer/prompts` | Confirmation prompt (skill remove) |
| `chalk` | Terminal colors |
| `cli-table3` | Table formatting |
| `ora` | Loading spinners |
