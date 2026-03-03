# Code Standards & Development Guide

**Last Updated:** 2026-03-03

## Repository Structure

```
plane-plugin/                          # Monorepo root
├── packages/
│   └── cli/                           # TypeScript CLI (oclif 4)
│       ├── src/
│       │   ├── commands/              # 53 command implementations
│       │   │   └── {resource}/{action}.ts
│       │   ├── lib/                   # Core modules
│       │   │   ├── api.ts             # Plane API client wrapper
│       │   │   ├── config.ts          # ~/.planerc management
│       │   │   ├── output.ts          # TTY detection, formatting
│       │   │   ├── prompts.ts         # Interactive input
│       │   │   ├── issue-resolver.ts  # Issue ref resolution
│       │   │   ├── errors.ts          # Custom error classes
│       │   │   └── npm.ts             # npm package checks
│       │   ├── types/
│       │   │   ├── config.ts          # Config interfaces
│       │   │   └── plane.ts           # Plane API types
│       │   ├── hooks/
│       │   │   └── init/check-update.ts
│       │   ├── base-command.ts        # BaseCommand parent class
│       │   └── index.ts               # Main entry point
│       ├── test/
│       │   ├── commands/              # Command tests
│       │   ├── lib/                   # Library tests
│       │   └── helpers/
│       │       └── mock-api.ts        # PlaneAPI mock
│       ├── bin/                       # Executable entry points
│       ├── package.json
│       ├── tsconfig.json
│       └── README.md
├── skills/
│   └── plane/                         # Legacy Python skill
│       ├── scripts/                   # 13 Python CLI scripts
│       │   ├── plane_*.py             # Resource-specific (projects, issues, etc.)
│       │   ├── plane_client.py        # Shared SDK wrapper
│       │   ├── plane_setup.sh         # Config initialization
│       │   └── plane_logout.sh        # Credential cleanup
│       ├── references/                # API docs, workflows
│       └── requirements.txt           # plane-sdk==0.2.2
├── tests/
│   ├── e2e/                           # End-to-end Python tests
│   └── test_smoke.py                  # Import validation
├── docs/                              # Project documentation
│   ├── codebase-summary.md
│   ├── system-architecture.md
│   ├── code-standards.md (this file)
│   └── project-overview-pdr.md        # Requirements & PDR
├── .claude-plugin/
│   └── plugin.json                    # Claude Code plugin manifest
├── CLAUDE.md                          # Project development guide
└── README.md                          # Quick start
```

## TypeScript/Node Standards (`packages/cli/`)

### File Naming Convention

- **Commands:** `kebab-case.ts` matching oclif command structure
  - `src/commands/project/list.ts` → `plane-cli project list`
  - `src/commands/issue/search.ts` → `plane-cli issue search`
- **Libraries:** `kebab-case.ts` for utilities and modules
  - `api.ts`, `config.ts`, `output.ts`, `prompts.ts`, `issue-resolver.ts`
- **Types:** Match their purpose
  - `config.ts`, `plane.ts` (interfaces/types)
- **Tests:** Mirror source structure with `.test.ts` suffix
  - `test/commands/project.test.ts`
  - `test/lib/api.test.ts`

### Language & Version Requirements

- **TypeScript:** 5.x (strict mode enabled)
- **Node:** >=18.0.0
- **Module system:** ES Modules (`"type": "module"` in package.json)
- **Target:** `ES2022` (tsconfig.json)

### Code Organization

#### Command Structure

All commands extend `BaseCommand` and follow this pattern:

```typescript
// src/commands/{resource}/{action}.ts
import {Args, Flags} from '@oclif/core'
import {BaseCommand} from '../../base-command.js'
import {createSpinner, error, success} from '../../lib/output.js'

export default class ProjectList extends BaseCommand {
  // 1. Static metadata
  static args = {
    id: Args.string({description: '...', required: true}),
  }

  static description = 'One-sentence description of what this does'

  static flags = {
    json: Flags.boolean({description: 'Output as JSON'}),
    'no-input': Flags.boolean({default: false}),
    // Destructive ops MUST have --confirm
    confirm: Flags.boolean({description: 'Confirm destructive action'}),
  }

  // 2. Main entry point
  async run(): Promise<void> {
    const {args, flags} = await this.parse(ProjectList)

    // 3. Validate required config
    const api = this.requireApi()
    const config = this.requireConfig()

    // 4. Main logic
    try {
      const result = await api.listProjects(config.workspace)

      if (flags.json) {
        this.logJson(result)
      } else {
        // Format output
        this.logTable(result)
      }
    } catch (err) {
      this.error(`Failed to list projects: ${err.message}`, {exit: 1})
    }
  }
}
```

**Key patterns:**
- Always use `this.requireApi()` and `this.requireConfig()` to ensure config is loaded
- Destructive operations require `--confirm` flag validation
- Use try-catch with meaningful error messages
- Output formatting respects `--json` flag
- Exit codes: 0 (success), 1 (error), 2 (config error), 3 (auth error)

#### Library Module Pattern

```typescript
// src/lib/{name}.ts
/**
 * Brief description of module purpose
 */

// 1. Imports
import {someType} from '../types/index.js'

// 2. Types/Interfaces (if module-specific)
interface LocalConfig {
  key: string
}

// 3. Main exports
export async function doSomething(input: string): Promise<string> {
  // Implementation
  return result
}

export class Helper {
  // Class implementation
}

// 4. Helper/private functions (no export)
function _internalHelper(): void {
  // Private utility
}
```

**Conventions:**
- Prefix private functions with `_`
- Use meaningful names over abbreviations
- Document public APIs with JSDoc
- Separate concerns (one file = one responsibility)

### Error Handling

**Custom error classes** (`src/lib/errors.ts`):

```typescript
export class ConfigError extends Error {
  code = 'CONFIG_ERROR'
  constructor(message: string) {
    super(message)
  }
}

export class AuthError extends Error {
  code = 'AUTH_ERROR'
}

export class NotFoundError extends Error {
  code = 'NOT_FOUND'
}
```

**Usage in commands:**

```typescript
try {
  const config = this.requireConfig()
} catch (err) {
  if (err instanceof ConfigError) {
    this.error('Configuration missing. Run: plane-cli config init', {exit: 2})
  } else if (err instanceof AuthError) {
    this.error('Invalid API key. Check config.', {exit: 3})
  } else {
    this.error(`Unexpected error: ${err.message}`, {exit: 1})
  }
}
```

**Exit codes must match intent:**
- `0` — Success
- `1` — General runtime error (API failure, validation)
- `2` — Configuration error (missing ~/.planerc, invalid config)
- `3` — Authentication error (invalid API key, unauthorized)
- `130` — User cancelled (Ctrl+C handled by oclif)

### Configuration Management

**Config file location:** `~/.planerc` (JSON format)

**Schema validation** (Zod):

```typescript
import {z} from 'zod'

export const ConfigSchema = z.object({
  workspace: z.string(),
  apiKey: z.string().optional(),
  accessToken: z.string().optional(),
  baseUrl: z.string().default('https://api.plane.so/api/v1'),
  currentProfile: z.string().optional(),
  defaults: z.object({
    project: z.string().optional(),
  }).optional(),
})

export type Config = z.infer<typeof ConfigSchema>
```

**Load/save operations:**

```typescript
import {getConfig, saveConfig, hasConfig} from '../../lib/config.js'

// Load
const config = await getConfig()
if (!config) {
  this.error('No config found. Run: plane-cli config init', {exit: 2})
}

// Save (with 0o600 permissions on Unix)
await saveConfig({
  workspace: 'my-workspace',
  apiKey: 'plane_api_xxx',
  baseUrl: 'https://api.plane.so/api/v1',
})
```

### API Client Patterns

**Making requests:**

```typescript
import {PlaneAPI} from '../../lib/api.js'

const api = new PlaneAPI(
  config.baseUrl,
  config.workspace,
  config.apiKey,
  config.accessToken,
)

// Fetch single resource
const project = await api.getProject(config.workspace, projectId)

// Fetch list
const {results} = await api.listIssues(config.workspace, projectId)

// Create resource
const newProject = await api.createProject(config.workspace, {
  name: 'My Project',
  identifier: 'MP',
})

// Update resource
const updated = await api.updateProject(config.workspace, projectId, {
  name: 'Updated Name',
})

// Delete resource
await api.deleteProject(config.workspace, projectId)
```

**Error handling from API:**

```typescript
try {
  const project = await api.getProject(workspace, id)
} catch (err) {
  if (err.code === 404) {
    this.error(`Project not found: ${id}`, {exit: 1})
  } else if (err.code === 401) {
    this.error('Unauthorized. Check API credentials.', {exit: 3})
  } else {
    this.error(`API error: ${err.message}`, {exit: 1})
  }
}
```

### Output Formatting

**TTY Detection:**

```typescript
import {isTTY, printJson, printTable, createSpinner, success, error, warning} from '../../lib/output.js'

// Automatic detection
if (isTTY()) {
  // Running in terminal → pretty output
  printTable(data, {columns: ['id', 'name', 'status']})
} else {
  // Piped/redirected → JSON
  printJson(data)
}

// Manual override
if (flags.json) {
  printJson(data)
} else {
  printTable(data, {...})
}
```

**Spinners for long operations:**

```typescript
const spinner = createSpinner('Creating project...')
try {
  const project = await api.createProject(workspace, data)
  spinner.stop()
  success(`Project created: ${project.name}`)
} catch (err) {
  spinner.stop()
  error(`Failed to create project: ${err.message}`)
  process.exit(1)
}
```

### Testing Standards

**Framework:** mocha + chai + @oclif/test

**Test file structure:**

```typescript
// test/commands/project.test.ts
import {expect} from 'chai'
import {runCommand} from '@oclif/test'
import {getConfig, saveConfig} from '../../src/lib/config.js'

describe('ProjectList', () => {
  // Mock config for isolation
  beforeEach(async () => {
    process.env.PLANE_CONFIG_PATH = '/tmp/test-config'
    await saveConfig({
      workspace: 'test-workspace',
      apiKey: 'test-key',
      baseUrl: 'https://api.plane.so/api/v1',
    })
  })

  afterEach(() => {
    delete process.env.PLANE_CONFIG_PATH
  })

  it('should list projects as JSON', async () => {
    const {stdout} = await runCommand(['project', 'list', '--json'])
    const data = JSON.parse(stdout)
    expect(data).to.be.an('array')
  })

  it('should require config', async () => {
    process.env.PLANE_CONFIG_PATH = '/nonexistent'
    const result = await runCommand(['project', 'list'])
    expect(result.error).to.exist
  })
})
```

**Mock API pattern:**

```typescript
// test/helpers/mock-api.ts
export const mockPlaneAPI = {
  listProjects: async () => ({
    results: [
      {
        id: 'proj-1',
        name: 'Test Project',
        identifier: 'TP',
      },
    ],
  }),
  // ... other methods
}

// In tests
globalThis.fetch = async (url, options) => {
  if (url.includes('/projects/')) {
    return new Response(JSON.stringify(mockPlaneAPI.listProjects()))
  }
  // ...
}
```

**Coverage targets:**
- All command argument parsing
- Config read/write/validation
- API request formatting
- Error scenarios
- Edge cases (empty lists, missing fields, etc.)

### Linting & Formatting

**ESLint config:** `eslint.config.mjs` (flat config)

**Run linting:**
```bash
npm run lint
```

**Auto-fix:**
```bash
npm run lint -- --fix
```

**Prettier configuration:** `.prettierrc` (via oclif)

### Build & Distribution

**Build TypeScript:**
```bash
npm run build
# Outputs dist/ (JavaScript files)
```

**Package for npm:**
```bash
npm pack
# Creates plane-cli-0.1.0.tgz
npm publish
# Publishes to npm registry
```

**Entry points:** `bin/run.js` and `bin/dev.js` (for development)

## Python Skill Standards (`skills/plane/`)

### File Naming Convention

- **Scripts:** `plane_{resource}.py`
  - `plane_projects.py`, `plane_work_items.py`, `plane_cycles.py`, etc.
- **Shared:** `plane_client.py` (SDK wrapper)
- **Utilities:** `plane_{utility}.py`
- **Setup/Admin:** `plane_{action}.sh` (bash scripts)

### Language Requirements

- **Python:** >=3.10
- **Package:** plane-sdk==0.2.2 (sole dependency)

### Script Structure

```python
"""
plane_projects.py — Manage Plane projects

USAGE:
    python plane_projects.py list [--json]
    python plane_projects.py get <project_id> [--json]
    python plane_projects.py create --name <name> --identifier <id> [--description <desc>]
    python plane_projects.py update <project_id> [--name <name>]
    python plane_projects.py delete <project_id> --confirm
"""

import argparse
import json
import sys
from typing import Any

from plane_client import dump_json, get_client


# 1. Command functions
def cmd_list(args: argparse.Namespace) -> None:
    """List all projects."""
    client, slug = get_client()
    response = client.projects.list(slug)
    results = response.results if hasattr(response, 'results') else response
    data = [
        r.model_dump() if hasattr(r, 'model_dump') else r
        for r in results
    ]
    print(dump_json(data))


def cmd_create(args: argparse.Namespace) -> None:
    """Create a new project."""
    client, slug = get_client()

    payload = {
        'name': args.name,
        'identifier': args.identifier,
    }
    if args.description:
        payload['description'] = args.description

    response = client.projects.create(slug, **payload)
    result = response.model_dump() if hasattr(response, 'model_dump') else response
    print(dump_json(result))


def cmd_delete(args: argparse.Namespace) -> None:
    """Delete a project."""
    if not args.confirm:
        print('ERROR: Destructive operation — pass --confirm to proceed.', file=sys.stderr)
        sys.exit(1)

    client, slug = get_client()
    client.projects.delete(slug, args.project_id)
    print(dump_json({'message': 'Project deleted successfully'}))


# 2. Argument parser builder
def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description='Manage Plane projects',
        usage='python plane_projects.py <command> [options]',
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # list subcommand
    subparsers.add_parser('list', help='List all projects')

    # get subcommand
    get_parser = subparsers.add_parser('get', help='Get project details')
    get_parser.add_argument('project_id', help='Project UUID')

    # create subcommand
    create_parser = subparsers.add_parser('create', help='Create a new project')
    create_parser.add_argument('--name', required=True, help='Project name')
    create_parser.add_argument('--identifier', required=True, help='Project identifier (2-3 chars)')
    create_parser.add_argument('--description', help='Project description')

    # delete subcommand
    delete_parser = subparsers.add_parser('delete', help='Delete a project')
    delete_parser.add_argument('project_id', help='Project UUID')
    delete_parser.add_argument('--confirm', action='store_true', help='Confirm deletion')

    return parser


# 3. Command dispatcher
COMMANDS = {
    'list': cmd_list,
    'create': cmd_create,
    'get': cmd_get,
    'delete': cmd_delete,
}


# 4. Main entry point
def main() -> None:
    """Parse args and dispatch to command handler."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        COMMANDS[args.command](args)
    except KeyError as e:
        print(f'ERROR: Unknown command: {args.command}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### Client Wrapper Pattern (`plane_client.py`)

```python
"""
plane_client.py — Shared Plane SDK client utilities
"""

import json
import os
import sys
from typing import Any, Tuple

from plane import PlaneSDK
from pydantic import BaseModel


def get_client() -> Tuple[PlaneSDK, str]:
    """Initialize and return PlaneSDK client with workspace slug.

    Returns:
        Tuple of (PlaneSDK client, workspace_slug)

    Raises:
        SystemExit: If required env vars are missing
    """
    api_key = os.getenv('PLANE_API_KEY') or os.getenv('PLANE_ACCESS_TOKEN')
    workspace_slug = os.getenv('PLANE_WORKSPACE_SLUG')
    base_url = os.getenv('PLANE_BASE_URL', 'https://api.plane.so/api/v1')

    if not api_key:
        print('ERROR: PLANE_API_KEY or PLANE_ACCESS_TOKEN env var required', file=sys.stderr)
        sys.exit(1)

    if not workspace_slug:
        print('ERROR: PLANE_WORKSPACE_SLUG env var required', file=sys.stderr)
        sys.exit(1)

    client = PlaneSDK(
        api_token=api_key,
        base_url=base_url,
    )

    return client, workspace_slug


def dump_json(obj: Any) -> str:
    """Pretty-print object as JSON."""
    return json.dumps(obj, default=json_serial, indent=2)


def json_serial(obj: Any) -> Any:
    """Handle Pydantic model serialization."""
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    raise TypeError(f'Object of type {type(obj)} is not JSON serializable')
```

### Error Handling

**Exit codes:**
- `0` — Success
- `1` — General error (API, validation, unknown command)
- `2` — Missing required arguments
- `3` — Missing or invalid config (env vars)

**Error message format:**
```python
print(f'ERROR: {message}', file=sys.stderr)
sys.exit(1)
```

### Configuration

**Methods:**
1. Environment variables (recommended)
   ```bash
   export PLANE_API_KEY="plane_api_xxx"
   export PLANE_WORKSPACE_SLUG="my-workspace"
   export PLANE_BASE_URL="https://api.plane.so/api/v1"  # optional
   ```

2. Setup script
   ```bash
   bash skills/plane/scripts/plane_setup.sh
   # Creates .plane.env with sourcing in ~/.bashrc
   ```

3. Local `.plane.env` (project-specific)
   ```bash
   # .plane.env
   export PLANE_API_KEY="..."
   source .plane.env
   python scripts/plane_projects.py list
   ```

### Output Standards

- **Success:** JSON output to stdout
- **Errors:** Human-readable messages to stderr, exit code 1
- **Destructive ops:** Require `--confirm` flag, error if missing
- **Help:** Use `--help` for full usage

## Common Practices (Both Stacks)

### Naming Conventions

| Entity | Convention | Example |
|--------|-----------|---------|
| Variables | camelCase | `projectId`, `workspace` |
| Functions | camelCase | `getProject()`, `listIssues()` |
| Classes/Types | PascalCase | `ProjectList`, `BaseCommand`, `PlaneAPI` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_BASE_URL`, `MAX_RETRIES` |
| Files | kebab-case | `base-command.ts`, `plane_client.py` |
| Commands | kebab-case | `project list`, `config init` |

### Documentation

**Inline comments:**
```typescript
// Why, not what — explain intent
// Fetch all issues to find by sequence_id
// (TODO: optimize with indexed lookup)
const issues = await api.listIssues(slug, projectId)
```

**JSDoc/docstrings for public APIs:**
```typescript
/**
 * Resolve issue reference to UUID
 * @param slug - Workspace slug
 * @param projectId - Project UUID
 * @param ref - Issue UUID or "PROJECT-123" format
 * @returns Resolved Issue object
 * @throws NotFoundError if issue not found
 */
async function resolveIssue(
  slug: string,
  projectId: string,
  ref: string,
): Promise<Issue>
```

```python
def get_client() -> Tuple[PlaneSDK, str]:
    """Initialize and return PlaneSDK client with workspace slug.

    Returns:
        Tuple of (PlaneSDK client, workspace_slug)

    Raises:
        SystemExit: If required env vars are missing
    """
```

### Git Practices

**Commit message format:**
```
feat(cli): add issue search command
fix(config): handle missing ~/.planerc gracefully
docs: update API reference
refactor(api): consolidate error handling
test: add config validation tests
```

**No confidential data:**
- Never commit `.env` files
- Never commit API keys or tokens
- Use `.gitignore` for local config

**Pre-commit checks:**
```bash
# TypeScript
npm run lint
npm run build
npm test

# Python
python -m pytest tests/
```

### Security Checklist

- [ ] API credentials stored securely (env vars or ~/.planerc with 0o600)
- [ ] No credentials in logs or error messages
- [ ] HTTPS for all API calls
- [ ] Destructive ops require `--confirm` or explicit user action
- [ ] Error messages don't leak internal paths or workspace details
- [ ] Input validation on all user-provided arguments
- [ ] Exit codes distinguish config/auth/general errors

## Development Workflow

### Adding a New TypeScript Command

1. **Create command file:**
   ```bash
   mkdir -p packages/cli/src/commands/{resource}
   touch packages/cli/src/commands/{resource}/{action}.ts
   ```

2. **Implement command:**
   ```typescript
   import {Args, Flags} from '@oclif/core'
   import {BaseCommand} from '../../base-command.js'

   export default class ResourceAction extends BaseCommand {
     static description = '...'
     static args = {...}
     static flags = {...}

     async run(): Promise<void> {
       // Implementation
     }
   }
   ```

3. **Add tests:**
   ```bash
   touch test/commands/{resource}.test.ts
   ```

4. **Build and test:**
   ```bash
   npm run build
   npm test
   npm run lint
   ```

5. **Update README.md** (oclif auto-generates from code)
   ```bash
   npm run prepack
   ```

### Adding a New Python Script

1. **Create script:**
   ```bash
   touch skills/plane/scripts/plane_{resource}.py
   ```

2. **Use template from `plane_projects.py`**

3. **Test manually:**
   ```bash
   export PLANE_API_KEY="..."
   export PLANE_WORKSPACE_SLUG="..."
   python skills/plane/scripts/plane_{resource}.py --help
   ```

4. **Add E2E test:**
   ```bash
   touch tests/e2e/test_e2e_{resource}.py
   ```

5. **Run tests:**
   ```bash
   pytest tests/
   ```

## Reference Links

- **TypeScript:** https://www.typescriptlang.org/
- **oclif:** https://oclif.io/
- **Plane API:** https://docs.plane.so/api-reference/introduction
- **Node.js:** https://nodejs.org/
- **Python:** https://www.python.org/
