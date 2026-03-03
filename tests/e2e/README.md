# E2E Tests for Plane CLI

This directory contains end-to-end tests that verify the CLI works against a real Plane API instance.

## Prerequisites

Set the following environment variables:

```bash
export PLANE_API_KEY="your-api-key"           # OR use PLANE_ACCESS_TOKEN
export PLANE_WORKSPACE_SLUG="your-workspace"
export PLANE_BASE_URL="https://api.plane.so/api/v1"  # Optional, defaults to cloud
```

## Running Tests

### Run all E2E tests

```bash
pytest tests/e2e/ -v
```

### Run specific test file

```bash
pytest tests/e2e/test_e2e_projects.py -v
```

### Run with markers

```bash
# Run only E2E tests
pytest tests/ -v -m e2e

# Exclude E2E tests (run only smoke/unit tests)
pytest tests/ -v -m "not e2e"
```

### Skip when credentials unavailable (CI-friendly)

Tests automatically skip if credentials are not available:

```bash
# In CI without credentials, E2E tests will be skipped
pytest tests/e2e/ -v
```

## Test Coverage

| File | Coverage |
|------|----------|
| `test_e2e_projects.py` | project:create, list, get, update, delete, members, features |
| `test_e2e_work_items.py` | issue:create, list, get, get-by-id, update, delete, search |
| `test_e2e_cycles.py` | cycle:create, list, get, update, delete, archive, add/remove issues |
| `test_e2e_modules.py` | module:create, list, get, update, delete, archive, add/remove issues |
| `test_e2e_labels.py` | label:create, list, get, update, delete |
| `test_e2e_states.py` | state:list, create, get, update, delete |
| `test_e2e_workspace.py` | user:me, user:list, workspace:members, verify |
| `test_e2e_work_item_extras.py` | comments, links, work-logs, activities |

## Test Data Management

- Test resources are created with unique names (timestamp + UUID suffix)
- Resources are automatically cleaned up after tests via fixtures
- Cleanup failures are logged but don't fail the test

## Writing New E2E Tests

Use the test fixtures from `conftest.py`:

```python
def test_something(test_project: dict, test_issue: dict) -> None:
    """Test using auto-created project and issue."""
    # test_project is automatically created and cleaned up
    # test_issue is automatically created and cleaned up
    result = run_cli(
        "plane_work_items.py",
        "get",
        "--project-id", test_project["id"],
        "--work-item-id", test_issue["id"],
    )
    assert result.json["id"] == test_issue["id"]
```

Available fixtures:
- `test_workspace` - Returns workspace slug
- `test_project` - Creates and cleans up a test project
- `test_issue` - Creates and cleans up a test work item

## Test Conventions

1. Use `@pytest.mark.e2e` decorator for all E2E tests
2. Call `skip_if_no_credentials()` at the start of each test
3. Use the `test_project` and `test_issue` fixtures for auto-cleanup
4. Use `run_cli()` helper to execute commands
5. Parse JSON output via `result.json` property
6. Handle cleanup in `finally` blocks for resources not using fixtures
