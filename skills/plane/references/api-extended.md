# Plane API Reference — Extended Scripts

⚠️ = Destructive — requires `--confirm` flag

## Initiatives (`plane_initiatives.py`)

| Command | Key Arguments |
|---------|---------------|
| `list` | — |
| `create` | `--name`, `--description` |
| `get` | `--initiative-id` |
| `update` | `--initiative-id`, `--name`, `--description` |
| `delete` | `--initiative-id`, `--confirm` ⚠️ |

## Intake (`plane_intake.py`)

| Command | Key Arguments |
|---------|---------------|
| `list` | `--project-id` |
| `create` | `--project-id`, `--name` |
| `get` | `--project-id`, `--work-item-id` |
| `update` | `--project-id`, `--work-item-id`, `--name`, `--status` |
| `delete` | `--project-id`, `--work-item-id`, `--confirm` ⚠️ |

## Labels (`plane_labels.py`)

| Command | Key Arguments |
|---------|---------------|
| `list` | `--project-id` |
| `create` | `--project-id`, `--name`, `--color` |
| `get` | `--project-id`, `--label-id` |
| `update` | `--project-id`, `--label-id`, `--name`, `--color` |
| `delete` | `--project-id`, `--label-id`, `--confirm` ⚠️ |

## States (`plane_states.py`)

| Command | Key Arguments |
|---------|---------------|
| `list` | `--project-id` |
| `create` | `--project-id`, `--name`, `--color`, `--group` |
| `get` | `--project-id`, `--state-id` |
| `update` | `--project-id`, `--state-id`, `--name`, `--color` |
| `delete` | `--project-id`, `--state-id`, `--confirm` ⚠️ |

## Pages (`plane_pages.py`)

| Command | Key Arguments |
|---------|---------------|
| `get-workspace` | `--page-id` |
| `get-project` | `--project-id`, `--page-id` |
| `create-workspace` | `--name`, `--description` |
| `create-project` | `--project-id`, `--name`, `--description` |

## Users & Workspaces

| Script | Command | Description |
|--------|---------|-------------|
| `plane_users.py` | `me` | Current user info |
| `plane_workspaces.py` | `members` | List workspace members |
| `plane_workspaces.py` | `features` | Get workspace features |
