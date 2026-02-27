# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Plane Agent Skill** — a collection of Python CLI scripts for interacting with [Plane](https://plane.so), an open-source project management platform. It wraps the `plane-sdk` Python library (`plane-sdk==0.2.2`) to provide command-line access to Plane's API for managing projects, work items, cycles, modules, and more.

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set required environment variables
export PLANE_API_KEY="your-api-key"           # OR use PLANE_ACCESS_TOKEN
export PLANE_WORKSPACE_SLUG="your-workspace"
export PLANE_BASE_URL="https://api.plane.so/api/v1"  # Optional (default shown)
```

### Running Scripts
All scripts are standalone CLI tools with subcommands:
```bash
# Verify connection
python scripts/plane_verify.py

# List projects
python scripts/plane_projects.py list

# Create a work item
python scripts/plane_work_items.py create --project-id <uuid> --name "Fix bug"
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
├── scripts/                  # CLI helper scripts (all executable)
│   ├── plane_client.py       # Shared auth/client helper (imported by others)
│   ├── plane_verify.py       # Connection verification
│   ├── plane_projects.py     # Project management (list, create, update, delete)
│   ├── plane_work_items.py   # Work item (issue) management
│   ├── plane_cycles.py       # Cycle (sprint) management
│   ├── plane_modules.py      # Module management
│   ├── plane_work_item_extras.py  # Comments, links, relations, work-logs, types
│   └── ...                   # Additional scripts for initiatives, intake, labels, etc.
├── tests/
│   └── test_smoke.py         # Import tests, --help validation, arg parsing tests
├── resources/                # Quick-reference docs (API reference, workflows)
├── examples/                 # Workflow examples
├── SKILL.md                  # Agent skill instructions (YAML frontmatter)
└── requirements.txt          # Single dependency: plane-sdk==0.2.2
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

- **`get_client()`**: Returns `(PlaneClient, workspace_slug)` tuple; validates env vars; exits with error code 1 if config missing
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
python scripts/plane_work_item_extras.py comments create --project-id <id> --work-item-id <id> --body "..."
python scripts/plane_work_item_extras.py work-logs list --project-id <id> --work-item-id <id>
```

Resources: `activities`, `comments`, `links`, `relations`, `work-logs`, `types`

### Testing Approach

Tests in `tests/test_smoke.py` verify:
- All modules can be imported
- All scripts handle `--help` correctly
- Argument parsing works for key commands
- Client helper validates missing env vars
- SKILL.md has valid YAML frontmatter

**No live API calls are made during tests.**

## Key Conventions

- All scripts output **JSON** (pipe to `jq` for filtering)
- Use `--help` on any script for full usage information
- All UUIDs are expected as command arguments (project-id, work-item-id, etc.)
- Work items can be retrieved by UUID or by `project-identifier` + `sequence` number
- Bulk operations use comma-separated IDs (e.g., `--issue-ids "id1,id2,id3"`)
