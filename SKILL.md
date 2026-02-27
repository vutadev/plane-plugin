---
name: plane
description: Manage projects, work items, cycles, modules, and more on the Plane project management platform via the plane-sdk Python library.
---

# Plane Agent Skill

This skill enables you to interact with [Plane](https://plane.so) — an open-source project management platform. It provides CLI helper scripts wrapping the `plane-sdk` Python library for managing projects, work items, cycles, modules, initiatives, and more.

## When to Use This Skill

Use this skill when the user needs to:

- **Manage projects**: Create, list, update, or delete projects on Plane
- **Track work items**: Create issues, update status/priority, assign team members
- **Plan sprints**: Create/manage cycles (sprints), add work items, transfer between cycles
- **Organize modules**: Group work items into feature modules
- **Triage intake**: Review and manage incoming work item requests
- **Track time**: Log work hours against work items
- **Search**: Find work items across the workspace

## Prerequisites

- Python ≥ 3.10
- `plane-sdk==0.2.2` (install via `pip install -r requirements.txt`)
- A Plane instance (cloud at `plane.so` or self-hosted)
- API key or personal access token

## Auth Setup

Set the following environment variables before using any scripts:

```bash
# Required: one of these
export PLANE_API_KEY="plane-api-key-here"        # API key auth
# OR
export PLANE_ACCESS_TOKEN="plane-pat-here"       # Personal access token auth

# Required: workspace identifier
export PLANE_WORKSPACE_SLUG="my-workspace"

# Optional: defaults to https://api.plane.so/api/v1
export PLANE_BASE_URL="https://your-instance.com/api/v1"
```

**Verify the connection:**
```bash
python scripts/plane_verify.py
```

## Safety Controls

> **⚠️ Destructive operations require explicit confirmation.**
>
> All `delete` commands require the `--confirm` flag. Without it, the script will
> refuse to execute and print an error. This prevents accidental data loss.
>
> ```bash
> # This will FAIL (no --confirm):
> python scripts/plane_projects.py delete --project-id <uuid>
>
> # This will succeed:
> python scripts/plane_projects.py delete --project-id <uuid> --confirm
> ```

## Script Reference

All scripts output JSON and accept `--help` for full usage information.

### Core Scripts

| Script | Sub-commands | Description |
|--------|-------------|-------------|
| `plane_verify.py` | — | Verify connection (auth + workspace) |
| `plane_projects.py` | `list`, `create`, `get`, `update`, `delete`, `members`, `features` | Project management |
| `plane_work_items.py` | `list`, `create`, `get`, `get-by-id`, `update`, `delete`, `search` | Work item (issue) management |
| `plane_cycles.py` | `list`, `create`, `get`, `update`, `delete`, `archive`, `unarchive`, `add-items`, `remove-item`, `list-items`, `transfer-items` | Cycle (sprint) management |
| `plane_modules.py` | `list`, `create`, `get`, `update`, `delete`, `archive`, `unarchive`, `add-items`, `remove-item`, `list-items` | Module management |

### Extended Scripts

| Script | Sub-commands | Description |
|--------|-------------|-------------|
| `plane_initiatives.py` | `list`, `create`, `get`, `update`, `delete` | Initiative management |
| `plane_intake.py` | `list`, `create`, `get`, `update`, `delete` | Intake (triage) management |
| `plane_labels.py` | `list`, `create`, `get`, `update`, `delete` | Label management |
| `plane_states.py` | `list`, `create`, `get`, `update`, `delete` | State management |
| `plane_pages.py` | `get-workspace`, `get-project`, `create-workspace`, `create-project` | Page management |
| `plane_users.py` | `me` | User info |
| `plane_workspaces.py` | `members`, `features` | Workspace info |

### Work Item Sub-resources

Use `plane_work_item_extras.py <resource> <action>`:

| Resource | Actions | Description |
|----------|---------|-------------|
| `activities` | `list`, `get` | Work item activity history |
| `comments` | `list`, `get`, `create`, `update`, `delete` | Work item comments |
| `links` | `list`, `get`, `create`, `update`, `delete` | Work item external links |
| `relations` | `list`, `create`, `delete` | Work item relationships (blocks, duplicates, etc.) |
| `work-logs` | `list`, `create`, `update`, `delete` | Time tracking |
| `types` | `list`, `get`, `create`, `update`, `delete` | Work item type definitions |

## Workflow Checklists

### Create a New Project

1. Verify connection: `python scripts/plane_verify.py`
2. Create the project: `python scripts/plane_projects.py create --name "Project Name" --identifier "PN"`
3. Note the returned project ID
4. Set up states: `python scripts/plane_states.py create --project-id <id> --name "In Progress" --group started`
5. Create labels: `python scripts/plane_labels.py create --project-id <id> --name "bug" --color "#ff0000"`
6. Add first work item: `python scripts/plane_work_items.py create --project-id <id> --name "First task"`

### Sprint Planning

1. List projects: `python scripts/plane_projects.py list`
2. Create a cycle: `python scripts/plane_cycles.py create --project-id <id> --name "Sprint 1" --start-date 2025-01-01 --end-date 2025-01-14`
3. List backlog items: `python scripts/plane_work_items.py list --project-id <id>`
4. Add items to cycle: `python scripts/plane_cycles.py add-items --project-id <id> --cycle-id <cid> --issue-ids "id1,id2,id3"`
5. Monitor progress: `python scripts/plane_cycles.py list-items --project-id <id> --cycle-id <cid>`
6. After sprint, transfer remaining: `python scripts/plane_cycles.py transfer-items --project-id <id> --cycle-id <old> --target-cycle-id <new>`

### Triage Intake Items

1. List pending intake: `python scripts/plane_intake.py list --project-id <id>`
2. Review item details: `python scripts/plane_intake.py get --project-id <id> --work-item-id <wid>`
3. Accept or reject: `python scripts/plane_intake.py update --project-id <id> --work-item-id <wid> --status 1`
4. Or delete if spam: `python scripts/plane_intake.py delete --project-id <id> --work-item-id <wid> --confirm`

### Search and Update Work Items

1. Search: `python scripts/plane_work_items.py search --query "login bug"`
2. Get details: `python scripts/plane_work_items.py get --project-id <id> --work-item-id <wid>`
3. Update priority: `python scripts/plane_work_items.py update --project-id <id> --work-item-id <wid> --priority high`
4. Add a comment: `python scripts/plane_work_item_extras.py comments create --project-id <id> --work-item-id <wid> --body "Investigating..."`
5. Log time: `python scripts/plane_work_item_extras.py work-logs create --project-id <id> --work-item-id <wid> --duration 120`

## Tips

- **All outputs are JSON** — you can pipe to `jq` for filtering
- **Get project ID from list**: `python scripts/plane_projects.py list | jq '.[0].id'`
- **Get by human-readable ID**: `python scripts/plane_work_items.py get-by-id --project-identifier MP --sequence 42`
- **Bulk operations**: Use comma-separated IDs for `add-items` commands
- **Dry run destructive ops**: Omit `--confirm` to see the safety error without executing
