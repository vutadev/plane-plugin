# plane-cli

CLI for managing Claude Code skills for the [Plane](https://plane.so) plugin.

[![oclif](https://img.shields.io/badge/cli-oclif-brightgreen.svg)](https://oclif.io)

## Installation

```bash
npm install -g plane-cli
```

### Claude Code Plugin

This CLI is part of the **plane-plugin** for Claude Code. To use the Plane skill with Claude Code:

```bash
# Install from a local checkout
claude plugin add /path/to/plane-plugin

# Or run Claude Code with the plugin directory
claude --plugin-dir /path/to/plane-plugin
```

The plugin registers the Plane skill defined in `skills/plane/SKILL.md`, giving Claude Code the ability to manage Plane projects, work items, cycles, and modules.

## Commands

| Command | Description |
| --- | --- |
| `plane-cli skill install [SOURCE]` | Install a skill from a local path or GitHub |
| `plane-cli skill list` | List installed skills |
| `plane-cli skill update [NAME]` | Update installed skills |
| `plane-cli skill remove <NAME>` | Remove an installed skill |

### skill install

```bash
# Install from current directory (auto-discovers SKILL.md)
plane-cli skill install

# Install from a specific path
plane-cli skill install ./my-skill

# Install from GitHub
plane-cli skill install github:user/repo

# Force overwrite an existing skill
plane-cli skill install --force github:user/repo
```

- **Local installs** create a symlink at `~/.claude/skills/<name>` (changes reflected immediately).
- **Git installs** clone the repo and copy the skill to `~/.claude/skills/<name>`.

### skill list

```bash
# Table output
plane-cli skill list

# JSON output
plane-cli skill list --json
```

### skill update

Re-install skills from their original source.

```bash
# Update all installed skills
plane-cli skill update

# Update a specific skill
plane-cli skill update my-skill
```

- **Git skills** are deleted and re-cloned from the original URL.
- **Local skills** are re-symlinked from the original path.

### skill remove

```bash
# Remove with confirmation prompt
plane-cli skill remove my-skill

# Skip confirmation
plane-cli skill remove my-skill --force
```

## Examples

```bash
# Install a skill from GitHub
plane-cli skill install github:user/my-skill

# Check what's installed
plane-cli skill list

# Pull latest changes
plane-cli skill update

# Output as JSON for scripting
plane-cli skill list --json | jq '.[].name'

# Remove a skill
plane-cli skill remove my-skill --force
```

## License

MIT
