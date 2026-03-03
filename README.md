# Plane Agent Skill

A Claude Code plugin for interacting with [Plane](https://plane.so) — an open-source project management platform. Includes both a **TypeScript CLI** (`plane-cli`) and **Python skill scripts** for Claude Code plugin usage.

## Installation

### TypeScript CLI (Recommended)

```bash
cd packages/cli
npm install
npm run build

# Run directly
./bin/run.js --help

# Or link globally
npm link
plane --help        # shorthand
plane-cli --help    # also works
```

Both `plane` and `plane-cli` commands are available after linking (defined in `package.json` bin).

If you're not installing globally, add a shell alias instead:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias plane="/path/to/plane-plugin/packages/cli/bin/run.js"
```

Requires Node.js ≥ 18.

### As Claude Code Plugin

```bash
claude --plugin-dir /path/to/plane-plugin
# Or from the repo root
claude --plugin-dir .
```

Once loaded, invoke with: `/plane:plane <command>`

### Prerequisites

- **CLI**: Node.js ≥ 18
- **Plugin scripts**: Python ≥ 3.10, `pip install -r skills/plane/requirements.txt`
- A Plane instance (cloud or self-hosted)
- API key or access token

## Configuration

### CLI (`plane-cli`)

Interactive setup:

```bash
plane-cli config init
```

This creates `~/.planerc` with your workspace, API key, and base URL.

Manual config:

```bash
plane-cli config set workspace my-workspace
plane-cli config set apiKey plane_api_xxx
plane-cli config set baseUrl https://api.plane.so/api/v1
```

View current config:

```bash
plane-cli config show
```

### Environment Variables (both CLI and Python scripts)

Environment variables override config file values:

```bash
export PLANE_API_KEY="your-api-key"           # OR PLANE_ACCESS_TOKEN
export PLANE_WORKSPACE_SLUG="your-workspace"
export PLANE_BASE_URL="https://api.plane.so/api/v1"  # Optional (default shown)
```

### Python Scripts Setup

```bash
bash skills/plane/scripts/plane_setup.sh
python skills/plane/scripts/plane_verify.py
```

## CLI Usage

### Global Flags

```
--json         Output raw JSON instead of formatted tables
--no-input     Disable interactive prompts (all args required)
--help         Show command help
```

### Commands

#### Projects

```bash
plane-cli project list
plane-cli project create --name "My Project" --identifier "MP"
plane-cli project get <project-id>
plane-cli project update <project-id> --name "New Name"
plane-cli project delete <project-id>
plane-cli project members <project-id>
```

#### Issues (Work Items)

```bash
plane-cli issue list --project <project-id>
plane-cli issue create --project <project-id> --name "Fix login bug"
plane-cli issue get <PROJECT-123>           # Supports identifier format
plane-cli issue update <issue-id> --project <project-id> --name "Updated"
plane-cli issue delete <issue-id> --project <project-id>
plane-cli issue search --project <project-id> --query "bug"
```

#### Cycles

```bash
plane-cli cycle list --project <project-id>
plane-cli cycle create --project <project-id> --name "Sprint 1"
plane-cli cycle get <cycle-id> --project <project-id>
plane-cli cycle update <cycle-id> --project <project-id> --name "Sprint 1 Updated"
plane-cli cycle delete <cycle-id> --project <project-id>
plane-cli cycle archive <cycle-id> --project <project-id>
plane-cli cycle unarchive <cycle-id> --project <project-id>
plane-cli cycle add-issues <cycle-id> --project <project-id> --issues "id1,id2"
plane-cli cycle remove-issue <cycle-id> --project <project-id> --issue <issue-id>
```

#### Modules

```bash
plane-cli module list --project <project-id>
plane-cli module create --project <project-id> --name "Auth Module"
plane-cli module get <module-id> --project <project-id>
plane-cli module update <module-id> --project <project-id> --name "Updated"
plane-cli module delete <module-id> --project <project-id>
plane-cli module archive <module-id> --project <project-id>
plane-cli module unarchive <module-id> --project <project-id>
plane-cli module add-issues <module-id> --project <project-id> --issues "id1,id2"
```

#### Labels

```bash
plane-cli label list --project <project-id>
plane-cli label create --project <project-id> --name "bug" --color "#FF0000"
plane-cli label get <label-id> --project <project-id>
plane-cli label update <label-id> --project <project-id> --name "critical"
plane-cli label delete <label-id> --project <project-id>
```

#### States

```bash
plane-cli state list --project <project-id>
plane-cli state create --project <project-id> --name "In Review"
plane-cli state delete <state-id> --project <project-id>
```

#### Other Commands

```bash
plane-cli intake list --project <project-id>
plane-cli initiative list
plane-cli page get-workspace
plane-cli page get-project --project <project-id>
plane-cli user me
plane-cli workspace members
```

### Example Workflow

```bash
# 1. Setup
plane-cli config init

# 2. List projects
plane-cli project list

# 3. Create an issue
plane-cli issue create --project <project-id> --name "Implement auth"

# 4. Add to a cycle
plane-cli cycle add-issues <cycle-id> --project <project-id> --issues "<issue-id>"

# 5. Search issues
plane-cli issue search --project <project-id> --query "auth"
```

## Python Scripts Usage

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

# Sub-resources (comments, links, relations, work-logs)
python skills/plane/scripts/plane_work_item_extras.py comments create \
  --project-id <id> --work-item-id <id> --body "Fixed in latest commit"
```

All scripts output JSON and accept `--help` for full usage info.

## Logout / Clear Credentials

```bash
# CLI
rm ~/.planerc

# Python scripts
bash skills/plane/scripts/plane_logout.sh --confirm
unset PLANE_API_KEY PLANE_ACCESS_TOKEN PLANE_WORKSPACE_SLUG PLANE_BASE_URL PLANE_ENV_FILE
```

## Directory Structure

```
plane-plugin/
├── .claude-plugin/           # Plugin manifest
│   └── plugin.json
├── packages/
│   └── cli/                  # TypeScript CLI (oclif)
│       ├── bin/run.js        # Entry point
│       ├── src/
│       │   ├── base-command.ts
│       │   ├── commands/     # All CLI commands
│       │   ├── lib/          # API client, config, output formatting
│       │   ├── types/        # TypeScript type definitions
│       │   └── hooks/        # Init hooks (update checker)
│       ├── package.json
│       └── tsconfig.json
├── skills/
│   └── plane/                # Python skill scripts
│       ├── SKILL.md
│       ├── requirements.txt
│       ├── scripts/          # CLI helper scripts
│       └── references/       # API reference docs
├── tests/                    # Smoke tests (Python)
├── CLAUDE.md
└── README.md
```

## Development

### CLI

```bash
cd packages/cli
npm install
npm run build          # Compile TypeScript
npm run lint           # Run ESLint
npm run test           # Run Mocha tests
```

### Python Scripts

```bash
pip install -r skills/plane/requirements.txt
pytest tests/ -v
```

## License

MIT
