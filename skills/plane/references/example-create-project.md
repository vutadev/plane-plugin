# Create a Project — End-to-End Workflow

This example walks through creating a complete project from scratch,
including states, labels, and initial work items.

## Prerequisites

- Config file set up (`~/.planerc` or `./.planerc` with `apiKey` and `workspace`)
- Connection verified: `python scripts/plane_verify.py`

## Steps

### 1. Create the Project

```bash
python scripts/plane_projects.py create \
  --name "Acme Web App" \
  --identifier "AWA" \
  --description "Main web application for Acme Corp"
```

Note the `id` field from the JSON output — this is your `<PROJECT_ID>`.

### 2. Check Default States

Every new project comes with default states. List them:

```bash
python scripts/plane_states.py list --project-id <PROJECT_ID>
```

### 3. Create Custom Labels

```bash
python scripts/plane_labels.py create \
  --project-id <PROJECT_ID> \
  --name "bug" \
  --color "#e11d48"

python scripts/plane_labels.py create \
  --project-id <PROJECT_ID> \
  --name "feature" \
  --color "#2563eb"

python scripts/plane_labels.py create \
  --project-id <PROJECT_ID> \
  --name "docs" \
  --color "#16a34a"
```

### 4. Create Initial Work Items

```bash
# A feature request
python scripts/plane_work_items.py create \
  --project-id <PROJECT_ID> \
  --name "Implement user authentication" \
  --description "<p>Add login, signup, and password reset flows</p>" \
  --priority high

# A bug report
python scripts/plane_work_items.py create \
  --project-id <PROJECT_ID> \
  --name "Fix homepage loading speed" \
  --description "<p>Homepage takes >5s to load on slow connections</p>" \
  --priority urgent

# A documentation task
python scripts/plane_work_items.py create \
  --project-id <PROJECT_ID> \
  --name "Write API documentation" \
  --priority low
```

### 5. List All Work Items

```bash
python scripts/plane_work_items.py list --project-id <PROJECT_ID>
```

### 6. View Project Members

```bash
python scripts/plane_projects.py members --project-id <PROJECT_ID>
```

## Result

You now have a fully set up project with:
- 3 custom labels (bug, feature, docs)
- 3 work items at different priorities
- Default workflow states ready to use
