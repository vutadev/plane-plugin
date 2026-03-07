---
name: plane
description: Manage projects, work items, cycles, modules, and more on the Plane project management platform via the plane-sdk Python library.
argument-hint: "[init]"
---

# Plane Agent Skill

Interact with [Plane](https://plane.so) — an open-source project management platform — via CLI scripts wrapping `plane-sdk==0.2.2`.

## Path Resolution (Plugin Layout)

This skill is self-contained under `skills/plane/`.
Resolve all relative paths from this directory:

- Scripts: `scripts/...`
- References: `references/...`
- Config: `~/.planerc` (global) + `./.planerc` (project override, KEY=VALUE or JSON format)
- Requirements: `requirements.txt`

## Configuration (.planerc)

Config is read from `~/.planerc` (global) and `./.planerc` (project-local). Local values override global on a per-field basis.

Supported formats (auto-detected):

**KEY=VALUE:**
```
# Plane API Configuration
api_key=plane_api_xxx
workspace_slug=my-workspace
base_url=https://api.plane.so
project_id=your-project-uuid
```

**JSON:**
```json
{
  "api_key": "plane_api_xxx",
  "workspace_slug": "my-workspace",
  "base_url": "https://api.plane.so",
  "project_id": "your-project-uuid"
}
```

### Config Keys

```
# (required*) API key for authentication
api_key=plane_api_xxx

# (required*) Alternative: access token (use one of api_key or access_token)
access_token=your-access-token

# (required) Workspace slug (alias: workspace)
workspace_slug=my-workspace

# (optional) API base URL (default: https://api.plane.so)
base_url=https://api.plane.so

# (optional) Default project UUID — when set, all commands use this project
# and --project-id becomes optional
project_id=your-project-uuid

# (optional) Set to "true" to block work item deletion
disable_delete_issue=true
```

## When to Use

- Manage projects, states, labels, members
- Create/update/close work items (issues), log time, add comments
- Plan sprints with cycles; transfer items between sprints
- Organize work into modules; manage initiatives and intake triage
- Search work items across the workspace

## Argument Handling

If `$ARGUMENTS` equals `init`, run the setup procedure below and stop.
Otherwise, proceed with the full skill instructions.

## Setup (`/plane init`)

Run the interactive setup to install Python deps and configure `.planerc`:

```bash
bash scripts/plane_setup.sh
```

This will: detect Python ≥ 3.10, install `plane-sdk`, prompt for API key + workspace slug if `.planerc` is missing, ask whether to save globally (`~/.planerc`) or locally (`./.planerc`), and verify the connection.

## Pre-flight (Run Once Per Session)

Verify connection before running any other script:

```bash
PYTHON=$(command -v python3 || command -v python)
$PYTHON scripts/plane_verify.py
```

If verify fails, check that `~/.planerc` or `./.planerc` exists with valid JSON, or run `bash scripts/plane_setup.sh`. See `references/troubleshooting.md` for details.

## Logout / Clear Credentials

```bash
bash scripts/plane_logout.sh --confirm
```

`plane_logout.sh` removes `.planerc` from both global (`~/.planerc`) and project-local locations. Note: removing the global config affects all projects.

## Safety Controls

All `delete` commands require `--confirm` flag — omitting it prints an error and exits safely.

```bash
# Fails safely (no --confirm):
$PYTHON scripts/plane_projects.py delete --project-id <uuid>

# Succeeds:
$PYTHON scripts/plane_projects.py delete --project-id <uuid> --confirm
```

## Script Reference

All scripts output JSON. Use `--help` for full argument details.

### Core

| Script | Sub-commands |
|--------|-------------|
| `plane_verify.py` | — (connection check) |
| `plane_projects.py` | `list` `create` `get` `update` `delete` `members` `features` |
| `plane_work_items.py` | `list` `create` `get` `get-by-id` `update` `delete` `search` |
| `plane_cycles.py` | `list` `create` `get` `update` `delete` `archive` `unarchive` `add-items` `remove-item` `list-items` `transfer-items` |
| `plane_modules.py` | `list` `create` `get` `update` `delete` `archive` `unarchive` `add-items` `remove-item` `list-items` |

→ Full args: `references/api-core.md`

### Extended

| Script | Sub-commands |
|--------|-------------|
| `plane_initiatives.py` | `list` `create` `get` `update` `delete` |
| `plane_intake.py` | `list` `create` `get` `update` `delete` |
| `plane_labels.py` | `list` `create` `get` `update` `delete` |
| `plane_states.py` | `list` `create` `get` `update` `delete` |
| `plane_pages.py` | `get-workspace` `get-project` `create-workspace` `create-project` |
| `plane_users.py` | `me` |
| `plane_workspaces.py` | `members` `features` |

→ Full args: `references/api-extended.md`

### Work Item Sub-resources

```bash
$PYTHON scripts/plane_work_item_extras.py <resource> <action> [args]
```

Resources: `activities` `comments` `links` `relations` `work-logs` `types`

→ Full args: `references/api-work-item-extras.md`

## Quick Tips

- Pipe output to `jq`: `$PYTHON scripts/plane_projects.py list | jq '.[0].id'`
- Get item by human ID: `$PYTHON scripts/plane_work_items.py get-by-id --project-identifier MP --sequence 42`
- Bulk operations: comma-separated IDs — `--issue-ids "id1,id2,id3"`

## References

- Auth setup & troubleshooting: `references/troubleshooting.md`
- Common workflows (sprint planning, triage, search): `references/workflows.md`
- Core API args (projects, work items, cycles, modules): `references/api-core.md`
- Extended API args (labels, states, intake, pages, etc.): `references/api-extended.md`
- Work item sub-resources (comments, links, logs, etc.): `references/api-work-item-extras.md`
