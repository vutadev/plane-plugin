# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Plane Agent Skill** — a collection of Python CLI scripts for interacting with [Plane](https://plane.so), an open-source project management platform. It wraps the `plane-sdk` Python library (`plane-sdk==0.2.2`) to provide command-line access to Plane's API for managing projects, work items, cycles, modules, and more.

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r skills/plane/requirements.txt

# Configure credentials via .planerc (KEY=VALUE format):
# Global config (all projects):
cat > ~/.planerc << 'EOF'
# Plane API Configuration
api_key=your-api-key
workspace=your-workspace
base_url=https://api.plane.so
EOF
chmod 600 ~/.planerc

# OR project-local config (overrides global):
cat > .planerc << 'EOF'
api_key=your-api-key
workspace=your-workspace
EOF
chmod 600 .planerc

# OR use the interactive setup:
bash skills/plane/scripts/plane_setup.sh
```

### Running Scripts
All scripts are standalone CLI tools with subcommands:
```bash
# Verify connection
python skills/plane/scripts/plane_verify.py

# List projects
python skills/plane/scripts/plane_projects.py list

# Create a work item
python skills/plane/scripts/plane_work_items.py create --project-id <uuid> --name "Fix bug"
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_smoke.py

# Run with verbose output
pytest tests/ -v
```

## Architecture

### Directory Structure
```
plane-skill/
├── .claude-plugin/           # Plugin manifest
│   └── plugin.json           # Plugin metadata (name, version, etc.)
├── skills/
│   └── plane/                # Self-contained skill package
│       ├── SKILL.md          # Agent skill instructions (YAML frontmatter)
│       ├── requirements.txt  # Single dependency: plane-sdk==0.2.2
│       ├── scripts/          # CLI helper scripts (all executable)
│       │   ├── plane_client.py
│       │   ├── plane_verify.py
│       │   ├── plane_projects.py
│       │   ├── plane_work_items.py
│       │   ├── plane_cycles.py
│       │   ├── plane_modules.py
│       │   ├── plane_work_item_extras.py
│       │   └── ...
│       └── references/       # Quick-reference docs (API reference, workflows)
├── tests/
│   └── test_smoke.py         # Import tests, --help validation, arg parsing tests
├── CLAUDE.md
└── README.md
```

**Plugin Structure:** This repository is a Claude Code plugin. The manifest at `.claude-plugin/plugin.json` registers the skill at `skills/plane/SKILL.md`. Test locally with:

```bash
claude --plugin-dir .
```

### Script Architecture Pattern

Each script follows a consistent pattern:

1. **Module docstring**: Describes subcommands and usage examples
2. **Command functions**: One function per subcommand (`cmd_list`, `cmd_create`, etc.)
3. **Argument parser**: `build_parser()` returns configured `argparse.ArgumentParser`
4. **Command dispatcher**: `COMMANDS` dict maps subcommand names to functions
5. **Main entry point**: `main()` parses args and dispatches to command handler

**Example pattern from `plane_projects.py`:**
```python
def cmd_list(args: argparse.Namespace) -> None:
    client, slug = get_client()  # From plane_client.py
    response = client.projects.list(slug)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))  # From plane_client.py

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(...)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List all projects")
    # ... more subparsers
    return parser

COMMANDS = {"list": cmd_list, ...}

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    COMMANDS[args.command](args)
```

### Shared Components (`plane_client.py`)

- **`get_client()`**: Returns `(PlaneClient, workspace_slug)` tuple; reads from `~/.planerc` and `CWD/.planerc` (JSON); exits with error code 1 if config missing
- **`dump_json(data)`**: Pretty-prints Pydantic models or dicts as JSON
- **`json_serial(obj)`**: Handles Pydantic model serialization

### Safety Controls

**Destructive operations require explicit `--confirm` flag.** Without it, scripts exit with error:

```python
def cmd_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)
    # ... proceed with deletion
```

This applies to all `delete` commands across scripts.

### Script Categories

| Category | Scripts | Purpose |
|----------|---------|---------|
| Core | `plane_projects.py`, `plane_work_items.py`, `plane_cycles.py`, `plane_modules.py` | Primary project management |
| Extended | `plane_initiatives.py`, `plane_intake.py`, `plane_labels.py`, `plane_states.py`, `plane_pages.py` | Additional Plane features |
| Workspace | `plane_users.py`, `plane_workspaces.py` | User/workspace info |
| Sub-resources | `plane_work_item_extras.py` | Nested resources (comments, links, relations, work-logs, types) |

### Special Script: `plane_work_item_extras.py`

Uses a two-level command structure: `resource action`:
```bash
python skills/plane/scripts/plane_work_item_extras.py comments create --project-id <id> --work-item-id <id> --body "..."
python skills/plane/scripts/plane_work_item_extras.py work-logs list --project-id <id> --work-item-id <id>
```

Resources: `activities`, `comments`, `links`, `relations`, `work-logs`, `types`

### Testing Approach

Tests in `tests/test_smoke.py` verify:
- All modules can be imported
- All scripts handle `--help` correctly
- Argument parsing works for key commands
- Client helper validates missing .planerc config
- SKILL.md has valid YAML frontmatter

**No live API calls are made during tests.**

## Key Conventions

- All scripts output **JSON** (pipe to `jq` for filtering)
- Use `--help` on any script for full usage information
- All UUIDs are expected as command arguments (project-id, work-item-id, etc.)
- Work items can be retrieved by UUID or by `project-identifier` + `sequence` number
- Bulk operations use comma-separated IDs (e.g., `--issue-ids "id1,id2,id3"`)
