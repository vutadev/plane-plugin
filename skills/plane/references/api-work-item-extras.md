# Plane API Reference — Work Item Sub-resources

Use as: `python scripts/plane_work_item_extras.py <resource> <action> [args]`

⚠️ = Destructive — requires `--confirm` flag

## Activities

| Action | Key Arguments |
|--------|---------------|
| `list` | `--project-id`, `--work-item-id` |
| `get` | `--project-id`, `--work-item-id`, `--activity-id` |

## Comments

| Action | Key Arguments |
|--------|---------------|
| `list` | `--project-id`, `--work-item-id` |
| `get` | `--project-id`, `--work-item-id`, `--comment-id` |
| `create` | `--project-id`, `--work-item-id`, `--body` |
| `update` | `--project-id`, `--work-item-id`, `--comment-id`, `--body` |
| `delete` | `--project-id`, `--work-item-id`, `--comment-id`, `--confirm` ⚠️ |

## Links

| Action | Key Arguments |
|--------|---------------|
| `list` | `--project-id`, `--work-item-id` |
| `get` | `--project-id`, `--work-item-id`, `--link-id` |
| `create` | `--project-id`, `--work-item-id`, `--url`, `--title` |
| `update` | `--project-id`, `--work-item-id`, `--link-id`, `--url`, `--title` |
| `delete` | `--project-id`, `--work-item-id`, `--link-id`, `--confirm` ⚠️ |

## Relations

| Action | Key Arguments |
|--------|---------------|
| `list` | `--project-id`, `--work-item-id` |
| `create` | `--project-id`, `--work-item-id`, `--related-id`, `--relation-type` |
| `delete` | `--project-id`, `--work-item-id`, `--related-id`, `--relation-type`, `--confirm` ⚠️ |

## Work Logs

| Action | Key Arguments |
|--------|---------------|
| `list` | `--project-id`, `--work-item-id` |
| `create` | `--project-id`, `--work-item-id`, `--duration`, `--description` |
| `update` | `--project-id`, `--work-item-id`, `--work-log-id`, `--duration`, `--description` |
| `delete` | `--project-id`, `--work-item-id`, `--work-log-id`, `--confirm` ⚠️ |

## Types

| Action | Key Arguments |
|--------|---------------|
| `list` | `--project-id` |
| `get` | `--project-id`, `--type-id` |
| `create` | `--project-id`, `--name`, `--description` |
| `update` | `--project-id`, `--type-id`, `--name`, `--description` |
| `delete` | `--project-id`, `--type-id`, `--confirm` ⚠️ |
