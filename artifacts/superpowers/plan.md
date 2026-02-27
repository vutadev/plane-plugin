# Plane Agent Skill — Implementation Plan

Build a hybrid agent skill (`SKILL.md` + Python helper scripts) that wraps the Plane project management platform using `plane-sdk`.

## Assumptions

- Python >=3.10 available on the system
- `plane-sdk` will be installed as the sole runtime dependency
- All scripts are **standalone CLI tools** (argparse, JSON I/O, env-var auth)
- No MCP server required — scripts call `plane-sdk` directly
- User will provide `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`, and optionally `PLANE_BASE_URL` as env vars

---

## Plan

### Step 1: Project Scaffolding

- Files: `SKILL.md`, `scripts/__init__.py`, `requirements.txt`, `README.md`
- Change:
  - Create directory structure: `scripts/`, `examples/`, `resources/`
  - Create minimal `SKILL.md` with YAML frontmatter (placeholder body)
  - Create `requirements.txt` with `plane-sdk==0.2.2`
  - Create `README.md` with setup instructions
- Verify: `ls -R plane-skill/` shows expected tree; `cat SKILL.md` has frontmatter

---

### Step 2: Auth & Client Helper

- Files: `scripts/plane_client.py`
- Change:
  - Shared helper that reads `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`, `PLANE_BASE_URL` from env
  - Returns `(PlaneClient, workspace_slug)` tuple
  - Raises clear errors on missing config
- Verify: `python scripts/plane_client.py` (self-test mode) prints connection status or clear error

---

### Step 3: Connection Verification Script

- Files: `scripts/plane_verify.py`
- Change:
  - CLI script that calls `get_me()` and `list_projects()` to validate auth + workspace
  - Prints JSON summary: user info, project count, workspace slug
- Verify: `python scripts/plane_verify.py` returns user info or descriptive error

---

### Step 4: Core — Projects Script

- Files: `scripts/plane_projects.py`
- Change:
  - Sub-commands: `list`, `create`, `get`, `update`, `delete`, `members`, `features`
  - JSON output for all operations
  - Confirmation prompt for `delete`
- Verify: `python scripts/plane_projects.py list` returns project list JSON

---

### Step 5: Core — Work Items Script

- Files: `scripts/plane_work_items.py`
- Change:
  - Sub-commands: `list`, `create`, `get`, `get-by-id`, `update`, `delete`, `search`
  - Supports `--project-id` flag
  - Confirmation prompt for `delete`
- Verify: `python scripts/plane_work_items.py list --project-id <id>` returns items

---

### Step 6: Core — Cycles & Modules Scripts

- Files: `scripts/plane_cycles.py`, `scripts/plane_modules.py`
- Change:
  - Cycles: `list`, `create`, `get`, `update`, `delete`, `archive`, `unarchive`, `add-items`, `remove-item`, `list-items`, `transfer-items`
  - Modules: `list`, `create`, `get`, `update`, `delete`, `archive`, `unarchive`, `add-items`, `remove-item`, `list-items`
  - Both require `--project-id`
- Verify: `python scripts/plane_cycles.py list --project-id <id>` works

---

### Step 7: Extended Scripts (Initiatives, Intake, Labels, Pages, States, Users, Workspaces, Work Logs)

- Files: `scripts/plane_initiatives.py`, `scripts/plane_intake.py`, `scripts/plane_labels.py`, `scripts/plane_pages.py`, `scripts/plane_states.py`, `scripts/plane_users.py`, `scripts/plane_workspaces.py`, `scripts/plane_work_logs.py`
- Change:
  - Each script: standard CRUD sub-commands with JSON output
  - `plane_users.py`: `me` command
  - `plane_states.py`, `plane_labels.py`: `list`, `create`, `get`, `update`, `delete`
- Verify: `python scripts/plane_users.py me` returns current user JSON

---

### Step 8: Extended Scripts — Work Item Sub-resources

- Files: `scripts/plane_work_item_extras.py`
- Change:
  - Single script with sub-commands for: `activities`, `comments`, `links`, `relations`, `properties`, `types`
  - Each sub-command has standard CRUD operations
  - Keeps the script count manageable (1 instead of 6)
- Verify: `python scripts/plane_work_item_extras.py comments list --project-id <id> --work-item-id <id>` works

---

### Step 9: Write Full SKILL.md & Examples

- Files: `SKILL.md`, `examples/create_project_workflow.md`, `examples/sprint_planning.md`, `resources/plane_api_reference.md`
- Change:
  - `SKILL.md`: Complete skill with sections for "When to use", "Prerequisites", "Auth setup", workflow checklists for each category, safety controls for destructive ops, script reference
  - Examples: step-by-step walkthroughs using the scripts
  - API reference: quick-reference table of all operations
- Verify: `SKILL.md` has valid YAML frontmatter; examples reference real scripts

---

### Step 10: Verification & Review

- Files: `tests/test_smoke.py`
- Change:
  - Smoke tests: import each script, verify CLI `--help` works, verify arg parsing
  - No live API calls (mock `PlaneClient`)
- Verify: `python -m pytest tests/ -v` passes

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| `plane-sdk` API surface mismatch | Pin `plane-sdk==0.2.2`; test with mocks |
| Destructive ops (delete) | All delete commands require `--confirm` flag |
| Missing env vars | Clear error messages in `plane_client.py` |
| Large scope (18 modules) | Steps 4-8 are sequential; each independently verifiable |

## Rollback Plan

All files are new — rollback = `rm -rf` the created files. No existing code modified.

---

## Verification Plan

### Automated Tests
- `python -m pytest tests/test_smoke.py -v` — verifies all scripts import and parse args correctly
- Each script's `--help` flag must work without env vars set

### Manual Verification
- Set `PLANE_API_KEY` and `PLANE_WORKSPACE_SLUG` env vars
- Run `python scripts/plane_verify.py` — should show user info
- Run `python scripts/plane_projects.py list` — should list projects
- Follow `examples/create_project_workflow.md` end-to-end
