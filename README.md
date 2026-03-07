# Plane Plugin for Claude Code

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin for managing projects, work items, cycles, modules, and more on [Plane](https://plane.so) — an open-source project management platform.

## Quick Start

### Install the Plugin

From within Claude Code, add the marketplace and install the plugin:

```
/plugin marketplace add vutadev/plane-plugin
/plugin install plane@vutadev-plane-plugin
```

Or for local development:

```bash
claude --plugin-dir /path/to/plane-plugin
```

Once loaded, the plugin's skill is available as `/plane:plane`.

### First-Time Setup

Run the interactive setup to configure your Plane credentials:

```
/plane init
```

This installs Python dependencies, prompts for your API key and workspace slug, saves configuration to `.planerc`, and verifies the connection.

### Prerequisites

- Python >= 3.10
- A Plane instance (cloud or self-hosted)
- API key or access token

## Configuration (.planerc)

The plugin reads credentials from `~/.planerc` (global) and `./.planerc` (project-local override):

```bash
# ~/.planerc
api_key=your-api-key
workspace_slug=your-workspace
base_url=https://api.plane.so        # optional, defaults to https://api.plane.so
project_id=your-default-project-uuid  # optional, makes --project-id args optional
```

To clear credentials:

```bash
bash skills/plane/scripts/plane_logout.sh --confirm
```

## What You Can Do

Once configured, Claude can use the plugin to:

- **Projects** — list, create, update, delete projects; view members and features
- **Work Items** — create, update, search, and close issues; retrieve by UUID or human-readable ID (e.g., `MP-42`)
- **Cycles** — plan sprints, add/remove/transfer items between cycles, archive old cycles
- **Modules** — organize work into modules, manage module membership
- **Labels & States** — create and manage workflow states and labels
- **Initiatives & Intake** — manage strategic initiatives and triage incoming requests
- **Pages** — create and retrieve workspace or project pages
- **Sub-resources** — add comments, links, relations, and work logs to items

All destructive operations (deletes) require explicit confirmation for safety.

## CLI — Skill Manager (plane-cli)

The `plane-cli` is a TypeScript CLI for managing Claude Code skills. It is **not required** for using the Plane plugin — it's a separate tool for installing, updating, and removing skills.

```bash
cd packages/cli
npm install && npm run build
./bin/run.js skill list
```

| Command | Description |
| --- | --- |
| `plane-cli skill install [SOURCE]` | Install a skill from a local path or GitHub |
| `plane-cli skill list` | List installed skills |
| `plane-cli skill update [NAME]` | Update installed skills |
| `plane-cli skill remove <NAME>` | Remove an installed skill |

See [`packages/cli/README.md`](packages/cli/README.md) for full CLI documentation.

## Directory Structure

```
plane-plugin/
├── .claude-plugin/           # Plugin manifest
│   └── plugin.json
├── packages/
│   └── cli/                  # TypeScript CLI (skill manager)
├── skills/
│   └── plane/                # Plane skill (Python scripts + references)
│       ├── SKILL.md          # Skill definition
│       ├── requirements.txt
│       ├── scripts/          # CLI helper scripts
│       └── references/       # API reference docs
├── tests/                    # Smoke tests
├── CLAUDE.md
└── README.md
```

## Development

```bash
# Python — install deps and run tests
pip install -r skills/plane/requirements.txt
pytest tests/test_smoke.py -v

# CLI — build and test
cd packages/cli
npm install
npm run build
npm run test
```

## License

MIT
