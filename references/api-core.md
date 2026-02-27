# Plane API Reference — Core Scripts

⚠️ = Destructive — requires `--confirm` flag

## Projects (`plane_projects.py`)

| Command | Key Arguments |
|---------|---------------|
| `list` | — |
| `create` | `--name`, `--identifier`, `--description`, `--network` |
| `get` | `--project-id` |
| `update` | `--project-id`, `--name`, `--description`, `--identifier` |
| `delete` | `--project-id`, `--confirm` ⚠️ |
| `members` | `--project-id` |
| `features` | `--project-id` |

## Work Items (`plane_work_items.py`)

| Command | Key Arguments |
|---------|---------------|
| `list` | `--project-id` |
| `create` | `--project-id`, `--name`, `--priority`, `--state-id`, `--assignees` |
| `get` | `--project-id`, `--work-item-id` |
| `get-by-id` | `--project-identifier`, `--sequence` |
| `update` | `--project-id`, `--work-item-id`, `--name`, `--priority`, `--state-id` |
| `delete` | `--project-id`, `--work-item-id`, `--confirm` ⚠️ |
| `search` | `--query` |

## Cycles (`plane_cycles.py`)

| Command | Key Arguments |
|---------|---------------|
| `list` | `--project-id` |
| `create` | `--project-id`, `--name`, `--start-date`, `--end-date` |
| `get` | `--project-id`, `--cycle-id` |
| `update` | `--project-id`, `--cycle-id`, `--name`, `--start-date`, `--end-date` |
| `delete` | `--project-id`, `--cycle-id`, `--confirm` ⚠️ |
| `archive` / `unarchive` | `--project-id`, `--cycle-id` |
| `add-items` | `--project-id`, `--cycle-id`, `--issue-ids` |
| `remove-item` | `--project-id`, `--cycle-id`, `--work-item-id` |
| `list-items` | `--project-id`, `--cycle-id` |
| `transfer-items` | `--project-id`, `--cycle-id`, `--target-cycle-id` |

## Modules (`plane_modules.py`)

| Command | Key Arguments |
|---------|---------------|
| `list` | `--project-id` |
| `create` | `--project-id`, `--name`, `--start-date`, `--target-date` |
| `get` | `--project-id`, `--module-id` |
| `update` | `--project-id`, `--module-id`, `--name` |
| `delete` | `--project-id`, `--module-id`, `--confirm` ⚠️ |
| `archive` / `unarchive` | `--project-id`, `--module-id` |
| `add-items` | `--project-id`, `--module-id`, `--issue-ids` |
| `remove-item` | `--project-id`, `--module-id`, `--work-item-id` |
| `list-items` | `--project-id`, `--module-id` |
