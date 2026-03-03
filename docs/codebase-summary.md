# Codebase Summary

**Last Updated:** 2026-03-03
**Repomix Stats:** 127 files, 90,675 tokens, 376,749 characters

## Project Overview

This is a dual-implementation Plane Agent Skill supporting both Python legacy scripts and a modern TypeScript CLI (`plane-cli`). The project provides programmatic access to Plane, an open-source project management platform, for managing projects, issues, cycles, modules, and more.

## High-Level Architecture

```
plane-plugin/
├── skills/plane/                    # Legacy Python skill package
│   ├── scripts/                     # 13 standalone Python CLI tools
│   ├── references/                  # API docs, workflows, troubleshooting
│   └── requirements.txt             # plane-sdk==0.2.2
├── packages/cli/                    # New TypeScript CLI (oclif 4)
│   ├── src/
│   │   ├── commands/               # 53 command implementations (11 resource groups)
│   │   ├── lib/                    # Core modules (api, config, prompts, output, etc.)
│   │   ├── types/                  # TypeScript interfaces
│   │   └── hooks/                  # Lifecycle hooks
│   ├── test/                        # 49 unit tests (mocha + chai)
│   └── bin/                         # Entry points
├── tests/
│   ├── e2e/                        # End-to-end Python tests (8 files)
│   └── test_smoke.py               # Import validation tests
└── .claude-plugin/
    └── plugin.json                 # Claude Code plugin manifest
```

## Components

### 1. Legacy Python Skill (`skills/plane/`)

**Status:** Active, maintained for backward compatibility

- **13 Python scripts** covering projects, issues, cycles, modules, labels, states, pages, users, workspaces, initiatives, intake, and work-item extras
- **Single dependency:** `plane-sdk==0.2.2`
- **Pattern:** Each script is standalone with subcommands (e.g., `plane_projects.py list`)
- **Output:** JSON only
- **Configuration:** Environment variables (`PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`, `PLANE_BASE_URL`)
- **Safety:** Destructive operations require `--confirm` flag

**Key files:**
- `plane_client.py`: Shared client initialization and JSON serialization
- `plane_work_items.py`: Issue CRUD operations
- `plane_work_item_extras.py`: Comments, links, relations, work-logs (18,999 chars, largest Python file)

### 2. New TypeScript CLI (`packages/cli/`)

**Status:** Production-ready (49 tests passing)
**Framework:** oclif 4 with TypeScript 5
**Node:** >=18.0.0
**Distribution:** npm as `plane-cli`

#### Commands (53 total across 11 resource groups)

| Group | Count | Commands |
|-------|-------|----------|
| config | 3 | init, set, show |
| project | 6 | list, get, create, update, delete, members |
| issue | 6 | list, get, create, update, delete, search |
| cycle | 10 | list, get, create, update, delete, archive, unarchive, add-issues, remove-issue, transfer |
| module | 9 | list, get, create, update, delete, archive, unarchive, add-issues, remove-issue |
| label | 5 | list, get, create, update, delete |
| state | 3 | list, create, delete |
| page | 3 | get-workspace, get-project, create |
| initiative | 3 | list, create, delete |
| intake | 3 | list, create, delete |
| user | 1 | me |
| workspace | 1 | members |

#### Core Modules

**`src/lib/api.ts`** (3,241 tokens)
- Plane API client wrapper around fetch
- Methods for all CRUD operations on resources
- Error handling with typed responses
- Implements full SDK without external dependency

**`src/lib/config.ts`**
- Reads/writes `~/.planerc` (JSON config file)
- Zod schema validation
- Environment variable override support
- Returns config or null if missing

**`src/lib/output.ts`**
- TTY detection (terminal vs piped)
- JSON and pretty-table formatting
- Spinner, success, warning, error helpers
- Uses chalk for colors, cli-table3 for tables, ora for spinners

**`src/lib/prompts.ts`**
- Interactive input via @inquirer/prompts
- Helpers: promptApiKey, promptWorkspace, promptConfirm, promptMultiSelect, etc.

**`src/lib/issue-resolver.ts`**
- Resolves issue references by `PROJECT-123` format
- Currently fetches all issues (performance concern noted in code-reviewer memory)

**`src/lib/errors.ts`**
- Custom error classes (ConfigError, AuthError, NotFoundError, etc.)
- Exit codes: 0 (success), 1 (general), 2 (config), 3 (auth), 130 (user cancel)

**`src/base-command.ts`**
- Base class for all commands
- Manages config, API, flags
- Requires config and API to be initialized

#### Configuration

**Location:** `~/.planerc` (JSON format)
```json
{
  "workspace": "my-workspace",
  "apiKey": "plane_api_xxx",
  "baseUrl": "https://api.plane.so/api/v1",
  "accessToken": "optional_token",
  "defaults": { "project": "optional_default_project" }
}
```

**Priority:** Flags > Env vars > Config file > Defaults

**Env vars supported:**
- `PLANE_API_KEY` or `PLANE_ACCESS_TOKEN`
- `PLANE_WORKSPACE_SLUG`
- `PLANE_BASE_URL` (optional, defaults to https://api.plane.so/api/v1)

#### Output Handling

- **TTY (terminal):** Pretty tables with colors
- **Piped:** JSON
- **Flags:** `--json` override, `--no-input` disable prompts
- **Error format:** Varies by output mode (JSON vs TTY with emojis)

#### Testing

**Framework:** mocha + chai + @oclif/test
**Count:** 49 unit tests passing
**Coverage:**
- Command argument parsing
- Config read/write operations
- API request/response handling
- Error scenarios

**Mock strategy:** `test/helpers/mock-api.ts` provides full PlaneAPI mock, tests use `globalThis.fetch` mocking

### 3. End-to-End Tests (`tests/e2e/`)

**Status:** 8 Python test files (requires live Plane instance)
**Scope:** Projects, issues, cycles, modules, labels, states, work-item extras, workspace

**Key files:**
- `test_e2e_work_items.py` and `test_e2e_work_item_extras.py` (largest, ~2,450 tokens each)
- `conftest.py`: Pytest fixtures

**Note:** E2E tests require `pytest` and live Plane API access

### 4. Plugin Integration (`Claude Code`)

**Manifest:** `.claude-plugin/plugin.json`
**Skill location:** `skills/plane/SKILL.md`

Registration as Claude Code plugin allows CLI access from within Claude Code editor.

## Dependencies

### Python
- **plane-sdk==0.2.2** (sole runtime dependency)
- pytest, pytest-dotenv (dev/test)

### TypeScript/Node
- **@oclif/core**: CLI framework
- **@makeplane/plane-node-sdk**: Not used; instead custom `api.ts` (raw fetch)
- **chalk, cli-table3, ora**: Output formatting
- **@inquirer/prompts**: Interactive prompts
- **zod**: Config validation
- **mocha, chai, @oclif/test**: Testing

## Key Conventions

### File Structure
- Python scripts: one-per-resource model (`plane_X.py`)
- TypeScript commands: `src/commands/{resource}/{action}.ts`
- Config: global `~/.planerc` (TypeScript), local `.plane.env` or env vars (Python)

### Code Patterns

**TypeScript:**
```typescript
// All commands extend BaseCommand
export default class ProjectList extends BaseCommand {
  static description = 'List all projects'
  static flags = { json: Flags.boolean(...) }

  async run(): Promise<void> {
    const {flags} = await this.parse(ProjectList)
    const api = this.requireApi()
    const config = this.requireConfig()
    // ... implementation
  }
}
```

**Python:**
```python
# Pattern: command functions + dispatcher
def cmd_list(args):
    client, slug = get_client()
    response = client.projects.list(slug)
    print(dump_json(response))

COMMANDS = {"list": cmd_list, ...}
def main():
    args = build_parser().parse_args()
    COMMANDS[args.command](args)
```

### Safety & Validation
- Destructive operations (`delete`, `archive`) require `--confirm` flag
- Config stored at `~/.planerc` with `0o600` permissions (TypeScript)
- Zod schemas validate configuration shape
- Environment variable override for API credentials

### Error Handling
- TypeScript: Custom error classes with typed messages
- Python: SDK exceptions propagated, exit code 1 on error
- Both: Clear error messages differentiate config vs auth vs runtime errors

## Code Metrics

| Metric | Value |
|--------|-------|
| Total files | 127 |
| TypeScript commands | 53 |
| Python scripts | 13 |
| Total tests | 49 (TypeScript) + 8 (E2E Python) |
| Main CLI lib code | ~3,400 lines |
| Largest file | `plane_work_item_extras.py` (5,000 tokens) |
| Total tokens | 90,675 |

## Recent Changes

**CLI refactor (2026-02-28):** Migrated from individual Python scripts to unified TypeScript CLI built with oclif 4, providing better DX, nested subcommands, TTY-aware output, and no-dependency raw API wrapper.

## Known Issues (from code-reviewer memory, 2026-03-03)

1. **API response handling:** `api.ts` `request()` always calls `res.json()` — crashes on 204 No Content (DELETE ops)
2. **Config prompt bug:** `config:init` accesses token prompt calls `promptConfirm` instead of `promptAccessToken`
3. **Flag conflicts:** `enableJsonFlag = true` on BaseCommand conflicts with manual `--json` flags
4. **Cycle commands:** Missing `...BaseCommand.baseFlags` spread (no-input not parsed)
5. **Performance:** `issue-resolver.ts` fetches ALL issues to find by sequence_id
6. **Code duplication:** `stripHtml` function duplicated 3 times (output.ts, issue/get.ts, issue/update.ts)
7. **Error handling:** Mixed approach (some use `process.exit(1)`, some use `this.error()`)

## Next Steps

1. Fix API response handling for DELETE operations (204 responses)
2. Consolidate error handling and exit codes
3. Extract shared utilities (stripHtml, etc.)
4. Optimize issue resolver to avoid full list fetch
5. Remove legacy Python scripts once TypeScript CLI is fully adopted
