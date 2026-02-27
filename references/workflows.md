# Plane Workflows

Set `PYTHON=$(command -v python3 || command -v python)` before running commands.

## Create a New Project

```bash
$PYTHON scripts/plane_projects.py create --name "Project Name" --identifier "PN"
# Note returned project ID
$PYTHON scripts/plane_states.py create --project-id <id> --name "In Progress" --group started
$PYTHON scripts/plane_labels.py create --project-id <id> --name "bug" --color "#ff0000"
$PYTHON scripts/plane_work_items.py create --project-id <id> --name "First task"
```

## Sprint Planning

```bash
$PYTHON scripts/plane_projects.py list
$PYTHON scripts/plane_cycles.py create --project-id <id> --name "Sprint 1" --start-date 2025-01-01 --end-date 2025-01-14
$PYTHON scripts/plane_work_items.py list --project-id <id>
$PYTHON scripts/plane_cycles.py add-items --project-id <id> --cycle-id <cid> --issue-ids "id1,id2,id3"
$PYTHON scripts/plane_cycles.py list-items --project-id <id> --cycle-id <cid>
# End of sprint — transfer remaining items
$PYTHON scripts/plane_cycles.py transfer-items --project-id <id> --cycle-id <old> --target-cycle-id <new>
$PYTHON scripts/plane_cycles.py archive --project-id <id> --cycle-id <old>
```

## Search and Update Work Items

```bash
$PYTHON scripts/plane_work_items.py search --query "login bug"
$PYTHON scripts/plane_work_items.py get --project-id <id> --work-item-id <wid>
$PYTHON scripts/plane_work_items.py update --project-id <id> --work-item-id <wid> --priority high
$PYTHON scripts/plane_work_item_extras.py comments create --project-id <id> --work-item-id <wid> --body "Investigating..."
$PYTHON scripts/plane_work_item_extras.py work-logs create --project-id <id> --work-item-id <wid> --duration 120
```

## Triage Intake Items

```bash
$PYTHON scripts/plane_intake.py list --project-id <id>
$PYTHON scripts/plane_intake.py get --project-id <id> --work-item-id <wid>
$PYTHON scripts/plane_intake.py update --project-id <id> --work-item-id <wid> --status 1
# Or delete if spam:
$PYTHON scripts/plane_intake.py delete --project-id <id> --work-item-id <wid> --confirm
```

## Organize with Modules

```bash
$PYTHON scripts/plane_modules.py create --project-id <id> --name "Auth Feature" --start-date 2025-01-01 --target-date 2025-01-31
$PYTHON scripts/plane_modules.py add-items --project-id <id> --module-id <mid> --issue-ids "id1,id2"
$PYTHON scripts/plane_modules.py list-items --project-id <id> --module-id <mid>
```
