# Plane API Quick Reference

Quick-reference table for all operations available through the Plane skill scripts.

## Authentication

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PLANE_API_KEY` | One of API key or token | — | Plane API key |
| `PLANE_ACCESS_TOKEN` | One of API key or token | — | Personal access token |
| `PLANE_WORKSPACE_SLUG` | Yes | — | Workspace slug identifier |
| `PLANE_BASE_URL` | No | `https://api.plane.so/api/v1` | API base URL |

## Projects (`plane_projects.py`)

| Command | Description | Key Arguments |
|---------|-------------|---------------|
| `list` | List all projects | — |
| `create` | Create project | `--name`, `--identifier`, `--description`, `--network` |
| `get` | Get by ID | `--project-id` |
| `update` | Update project | `--project-id`, `--name`, `--description`, `--identifier` |
| `delete` | Delete project | `--project-id`, `--confirm` ⚠️ |
| `members` | List members | `--project-id` |
| `features` | Get features | `--project-id` |

## Work Items (`plane_work_items.py`)

| Command | Description | Key Arguments |
|---------|-------------|---------------|
| `list` | List items | `--project-id` |
| `create` | Create item | `--project-id`, `--name`, `--priority`, `--state-id`, `--assignees` |
| `get` | Get by UUID | `--project-id`, `--work-item-id` |
| `get-by-id` | Get by identifier | `--project-identifier`, `--sequence` |
| `update` | Update item | `--project-id`, `--work-item-id`, `--name`, `--priority`, `--state-id` |
| `delete` | Delete item | `--project-id`, `--work-item-id`, `--confirm` ⚠️ |
| `search` | Search items | `--query` |

## Cycles (`plane_cycles.py`)

| Command | Description | Key Arguments |
|---------|-------------|---------------|
| `list` | List cycles | `--project-id` |
| `create` | Create cycle | `--project-id`, `--name`, `--start-date`, `--end-date` |
| `get` | Get by ID | `--project-id`, `--cycle-id` |
| `update` | Update cycle | `--project-id`, `--cycle-id`, `--name`, `--start-date`, `--end-date` |
| `delete` | Delete cycle | `--project-id`, `--cycle-id`, `--confirm` ⚠️ |
| `archive` | Archive cycle | `--project-id`, `--cycle-id` |
| `unarchive` | Unarchive cycle | `--project-id`, `--cycle-id` |
| `add-items` | Add work items | `--project-id`, `--cycle-id`, `--issue-ids` |
| `remove-item` | Remove work item | `--project-id`, `--cycle-id`, `--work-item-id` |
| `list-items` | List work items | `--project-id`, `--cycle-id` |
| `transfer-items` | Transfer items | `--project-id`, `--cycle-id`, `--target-cycle-id` |

## Modules (`plane_modules.py`)

| Command | Description | Key Arguments |
|---------|-------------|---------------|
| `list` | List modules | `--project-id` |
| `create` | Create module | `--project-id`, `--name`, `--start-date`, `--target-date` |
| `get` | Get by ID | `--project-id`, `--module-id` |
| `update` | Update module | `--project-id`, `--module-id`, `--name` |
| `delete` | Delete module | `--project-id`, `--module-id`, `--confirm` ⚠️ |
| `archive` | Archive | `--project-id`, `--module-id` |
| `unarchive` | Unarchive | `--project-id`, `--module-id` |
| `add-items` | Add work items | `--project-id`, `--module-id`, `--issue-ids` |
| `remove-item` | Remove item | `--project-id`, `--module-id`, `--work-item-id` |
| `list-items` | List items | `--project-id`, `--module-id` |

## Initiatives (`plane_initiatives.py`)

| Command | Description | Key Arguments |
|---------|-------------|---------------|
| `list` | List initiatives | — |
| `create` | Create | `--name`, `--description` |
| `get` | Get by ID | `--initiative-id` |
| `update` | Update | `--initiative-id`, `--name`, `--description` |
| `delete` | Delete | `--initiative-id`, `--confirm` ⚠️ |

## Intake (`plane_intake.py`)

| Command | Description | Key Arguments |
|---------|-------------|---------------|
| `list` | List intake items | `--project-id` |
| `create` | Create intake item | `--project-id`, `--name` |
| `get` | Get by ID | `--project-id`, `--work-item-id` |
| `update` | Update | `--project-id`, `--work-item-id`, `--name`, `--status` |
| `delete` | Delete | `--project-id`, `--work-item-id`, `--confirm` ⚠️ |

## Labels (`plane_labels.py`)

| Command | Description | Key Arguments |
|---------|-------------|---------------|
| `list` | List labels | `--project-id` |
| `create` | Create label | `--project-id`, `--name`, `--color` |
| `get` | Get by ID | `--project-id`, `--label-id` |
| `update` | Update | `--project-id`, `--label-id`, `--name`, `--color` |
| `delete` | Delete | `--project-id`, `--label-id`, `--confirm` ⚠️ |

## States (`plane_states.py`)

| Command | Description | Key Arguments |
|---------|-------------|---------------|
| `list` | List states | `--project-id` |
| `create` | Create state | `--project-id`, `--name`, `--color`, `--group` |
| `get` | Get by ID | `--project-id`, `--state-id` |
| `update` | Update | `--project-id`, `--state-id`, `--name`, `--color` |
| `delete` | Delete | `--project-id`, `--state-id`, `--confirm` ⚠️ |

## Pages (`plane_pages.py`)

| Command | Description | Key Arguments |
|---------|-------------|---------------|
| `get-workspace` | Get workspace page | `--page-id` |
| `get-project` | Get project page | `--project-id`, `--page-id` |
| `create-workspace` | Create workspace page | `--name`, `--description` |
| `create-project` | Create project page | `--project-id`, `--name`, `--description` |

## Users (`plane_users.py`)

| Command | Description |
|---------|-------------|
| `me` | Get current user info |

## Workspaces (`plane_workspaces.py`)

| Command | Description |
|---------|-------------|
| `members` | List workspace members |
| `features` | Get workspace features |

## Work Item Sub-resources (`plane_work_item_extras.py`)

Use as: `python scripts/plane_work_item_extras.py <resource> <action> [args]`

### Activities
| Action | Key Arguments |
|--------|---------------|
| `list` | `--project-id`, `--work-item-id` |
| `get` | `--project-id`, `--work-item-id`, `--activity-id` |

### Comments
| Action | Key Arguments |
|--------|---------------|
| `list` | `--project-id`, `--work-item-id` |
| `get` | `--project-id`, `--work-item-id`, `--comment-id` |
| `create` | `--project-id`, `--work-item-id`, `--body` |
| `update` | `--project-id`, `--work-item-id`, `--comment-id`, `--body` |
| `delete` | `--project-id`, `--work-item-id`, `--comment-id`, `--confirm` ⚠️ |

### Links
| Action | Key Arguments |
|--------|---------------|
| `list` | `--project-id`, `--work-item-id` |
| `get` | `--project-id`, `--work-item-id`, `--link-id` |
| `create` | `--project-id`, `--work-item-id`, `--url`, `--title` |
| `update` | `--project-id`, `--work-item-id`, `--link-id`, `--url`, `--title` |
| `delete` | `--project-id`, `--work-item-id`, `--link-id`, `--confirm` ⚠️ |

### Relations
| Action | Key Arguments |
|--------|---------------|
| `list` | `--project-id`, `--work-item-id` |
| `create` | `--project-id`, `--work-item-id`, `--related-id`, `--relation-type` |
| `delete` | `--project-id`, `--work-item-id`, `--related-id`, `--relation-type`, `--confirm` ⚠️ |

### Work Logs
| Action | Key Arguments |
|--------|---------------|
| `list` | `--project-id`, `--work-item-id` |
| `create` | `--project-id`, `--work-item-id`, `--duration`, `--description` |
| `update` | `--project-id`, `--work-item-id`, `--work-log-id`, `--duration`, `--description` |
| `delete` | `--project-id`, `--work-item-id`, `--work-log-id`, `--confirm` ⚠️ |

### Types
| Action | Key Arguments |
|--------|---------------|
| `list` | `--project-id` |
| `get` | `--project-id`, `--type-id` |
| `create` | `--project-id`, `--name`, `--description` |
| `update` | `--project-id`, `--type-id`, `--name`, `--description` |
| `delete` | `--project-id`, `--type-id`, `--confirm` ⚠️ |

---

⚠️ = Destructive operation — requires `--confirm` flag
