# Sprint Planning Workflow

This example walks through planning and running a sprint (cycle) in Plane.

## Prerequisites

- A project exists with work items in the backlog
- Environment variables configured

## Steps

### 1. Find Your Project

```bash
python scripts/plane_projects.py list
```

Note the `id` of your target project.

### 2. Review Backlog

```bash
python scripts/plane_work_items.py list --project-id <PROJECT_ID>
```

### 3. Create a Sprint Cycle

```bash
python scripts/plane_cycles.py create \
  --project-id <PROJECT_ID> \
  --name "Sprint 1 — MVP Features" \
  --start-date "2025-01-06" \
  --end-date "2025-01-20"
```

Note the `id` of the created cycle.

### 4. Add Work Items to the Sprint

Collect work item IDs from the backlog listing, then:

```bash
python scripts/plane_cycles.py add-items \
  --project-id <PROJECT_ID> \
  --cycle-id <CYCLE_ID> \
  --issue-ids "id1,id2,id3"
```

### 5. Monitor Sprint Progress

```bash
python scripts/plane_cycles.py list-items \
  --project-id <PROJECT_ID> \
  --cycle-id <CYCLE_ID>
```

### 6. Update Work Item Status During Sprint

```bash
# Move item to "in progress"
python scripts/plane_work_items.py update \
  --project-id <PROJECT_ID> \
  --work-item-id <ITEM_ID> \
  --state-id <IN_PROGRESS_STATE_ID>

# Add a comment for daily standup notes
python scripts/plane_work_item_extras.py comments create \
  --project-id <PROJECT_ID> \
  --work-item-id <ITEM_ID> \
  --body "<p>Started working on this. ETA: 2 days.</p>"

# Log work time
python scripts/plane_work_item_extras.py work-logs create \
  --project-id <PROJECT_ID> \
  --work-item-id <ITEM_ID> \
  --duration 240 \
  --description "Implemented core logic"
```

### 7. End of Sprint — Transfer Remaining Items

If some items aren't completed, create the next sprint and transfer:

```bash
# Create next sprint
python scripts/plane_cycles.py create \
  --project-id <PROJECT_ID> \
  --name "Sprint 2 — Carryover + Polish" \
  --start-date "2025-01-20" \
  --end-date "2025-02-03"

# Transfer incomplete items
python scripts/plane_cycles.py transfer-items \
  --project-id <PROJECT_ID> \
  --cycle-id <OLD_CYCLE_ID> \
  --target-cycle-id <NEW_CYCLE_ID>
```

### 8. Archive Completed Sprint

```bash
python scripts/plane_cycles.py archive \
  --project-id <PROJECT_ID> \
  --cycle-id <OLD_CYCLE_ID>
```

## Tips

- Use `plane_work_items.py search --query "keyword"` to quickly find items
- Group related items into modules for better organization
- Review activities with `plane_work_item_extras.py activities list` for audit trails
