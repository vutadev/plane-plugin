# Plane Agent Skill

A Claude Code plugin for interacting with [Plane](https://plane.so) — an open-source project management platform — via the `plane-sdk` Python library.

## Installation

### As Claude Code Plugin

```bash
# Run from this directory
claude --plugin-dir /path/to/plane-plugin

# Or install from local directory
claude --plugin-dir .
```

Once loaded, invoke with: `/plane:plane <command>`

### Prerequisites

- Python ≥ 3.10
- A Plane instance (cloud or self-hosted)
- API key or access token

## Setup

1. Install dependencies:

```bash
pip install -r skills/plane/requirements.txt
```

2. Set environment variables (or run setup to create `.plane.env` in your project directory):

```bash
bash skills/plane/scripts/plane_setup.sh
# OR manually export:
export PLANE_API_KEY="your-api-key"
export PLANE_WORKSPACE_SLUG="your-workspace-slug"
# Optional — defaults to https://api.plane.so/api/v1
export PLANE_BASE_URL="https://your-plane-instance.com/api/v1"
```

3. Verify the connection:

```bash
python skills/plane/scripts/plane_verify.py
```

## Usage

### Claude Code plugin

```bash
claude --plugin-dir .
```

Then invoke:

```text
/plane:plane init
```

### CLI scripts

Each script is a standalone CLI tool with sub-commands:

```bash
# Projects
python skills/plane/scripts/plane_projects.py list
python skills/plane/scripts/plane_projects.py create --name "My Project" --identifier "MP"

# Work Items
python skills/plane/scripts/plane_work_items.py list --project-id <uuid>
python skills/plane/scripts/plane_work_items.py create --project-id <uuid> --name "Fix bug"

# Cycles
python skills/plane/scripts/plane_cycles.py list --project-id <uuid>

# Modules
python skills/plane/scripts/plane_modules.py list --project-id <uuid>
```

All scripts output JSON and accept `--help` for full usage info.

## Logout / Clear Credentials

```bash
bash skills/plane/scripts/plane_logout.sh --confirm
unset PLANE_API_KEY PLANE_ACCESS_TOKEN PLANE_WORKSPACE_SLUG PLANE_BASE_URL PLANE_ENV_FILE
```

## Directory Structure

```
plane-plugin/                 # This IS the plugin directory
├── .claude-plugin/           # Plugin manifest
│   └── plugin.json           # Plugin metadata
├── skills/
│   └── plane/                # Self-contained skill package
│       ├── SKILL.md
│       ├── requirements.txt
│       ├── scripts/          # CLI helper scripts
│       └── references/       # API reference docs
├── tests/                    # Smoke tests
├── CLAUDE.md
└── README.md
```

## License

MIT
