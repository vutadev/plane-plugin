# System Architecture

**Last Updated:** 2026-03-03

## Overview

The Plane Plugin provides dual-path access to Plane project management APIs:

1. **Legacy Python Skill** — Standalone scripts (plane-sdk wrapper) for backward compatibility
2. **TypeScript CLI** — Modern oclif-based unified command interface (no SDK dependency)

Both paths serve the same purpose: programmatic CLI access to Plane resources without UI friction.

## High-Level Data Flow

```
User Input
   │
   ├─→ Python Script (legacy)
   │   │
   │   ├─→ get_client() [plane_client.py]
   │   │   └─→ PlaneSDK (plane-sdk==0.2.2)
   │   │       └─→ HTTP/HTTPS to Plane API
   │   │
   │   └─→ JSON Output (stdout)
   │
   └─→ TypeScript CLI (modern)
       │
       ├─→ BaseCommand (oclif)
       │   └─→ Config (~/.planerc)
       │
       ├─→ API Client [api.ts - raw fetch]
       │   └─→ HTTP/HTTPS to Plane API
       │
       └─→ Output
           ├─→ TTY: Pretty tables (chalk, cli-table3)
           └─→ Piped: JSON
```

## Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    User / Claude Code Plugin                     │
└────────────────┬───────────────────────────────────┬─────────────┘
                 │                                   │
         plane script (legacy)            plane-cli command (modern)
                 │                                   │
         ┌───────▼────────┐             ┌───────────▼──────────┐
         │ Python Script  │             │   oclif Command      │
         │ (e.g., projects)│            │ (e.g., project list) │
         └───────┬────────┘             └───────┬──────────────┘
                 │                              │
         ┌───────▼────────┐             ┌──────▼────────┐
         │ plane_client.py│             │ base-command  │
         │ get_client()   │             │ BaseCommand   │
         └───────┬────────┘             └──────┬────────┘
                 │                             │
         ┌───────▼────────────┐        ┌───────▼──────────────┐
         │  plane-sdk         │        │ api.ts               │
         │ PlaneSDK class     │        │ (raw fetch wrapper)  │
         └───────┬────────────┘        └───────┬──────────────┘
                 │                             │
         ┌───────▼────────────────────────────▼──────────┐
         │  HTTPS to Plane API Endpoint                  │
         │  https://api.plane.so/api/v1/{resource}/{id}  │
         └────────────────────────────────────────────────┘
                 │
         ┌───────▼────────────┐
         │  Plane API         │
         │  (Server-side)     │
         └────────────────────┘
```

## Python Skill Architecture (`skills/plane/`)

### Entry Points

- **Individual scripts** — Each resource gets a standalone CLI tool
  - `plane_projects.py list|get|create|update|delete`
  - `plane_work_items.py list|get|create|update|delete|search`
  - `plane_cycles.py`, `plane_modules.py`, `plane_labels.py`, etc.
- **Setup/Logout** — Configuration management
  - `plane_setup.sh` — Interactive config creation (.plane.env)
  - `plane_logout.sh` — Credential removal

### Client Layer

**`plane_client.py`** — Shared utilities
```python
get_client() -> (PlaneClient, workspace_slug)
  ├─ Validates PLANE_API_KEY, PLANE_WORKSPACE_SLUG
  ├─ Reads PLANE_BASE_URL (default: https://api.plane.so/api/v1)
  └─ Returns initialized SDK client

dump_json(obj) -> str
  └─ Pretty-prints Pydantic models or dicts

json_serial(obj)
  └─ Handles model serialization for JSON
```

### Script Pattern

```
Module Docstring (usage)
    │
    ├─ Command Functions
    │  ├─ cmd_list(args)
    │  ├─ cmd_create(args)
    │  └─ cmd_delete(args) [requires --confirm]
    │
    ├─ Argument Parser [argparse]
    │  └─ build_parser() -> ArgumentParser
    │
    ├─ Command Dispatcher
    │  └─ COMMANDS = {"list": cmd_list, "create": cmd_create, ...}
    │
    └─ Main Entry Point
       └─ main() [parses args, dispatches to COMMANDS[args.command]]
```

### Configuration

**Method 1:** Environment Variables
```bash
export PLANE_API_KEY="plane_api_xxx"
export PLANE_WORKSPACE_SLUG="my-workspace"
export PLANE_BASE_URL="https://custom.plane.com/api/v1"  # Optional
```

**Method 2:** Setup Script
```bash
bash skills/plane/scripts/plane_setup.sh
# Creates .plane.env with prompt-based values
```

**Priority:** Env vars > .plane.env file > Defaults

### Output Format

- **All outputs:** JSON (for piping to `jq`)
- **Error handling:** Exit code 1 on failure, stderr messages
- **Destructive ops:** Require `--confirm` flag

## TypeScript CLI Architecture (`packages/cli/`)

### Entry Points

**Binary executables:**
```bash
plane-cli <command> [args]  # npm-installed
plane <command> [args]       # symlink to same binary
```

**Internally:**
- `bin/run.js` — Main entry point (oclif execute)
- `src/index.ts` — Re-exports oclif core run function

### Command Structure

```
packages/cli/src/commands/
├─ config/
│  ├─ init.ts      [--api-key|--access-token, --workspace, --no-input]
│  ├─ set.ts       [key value] — nested keys like defaults.project
│  └─ show.ts      [--json]
├─ project/
│  ├─ list.ts      [--json]
│  ├─ get.ts       <id> [--json]
│  ├─ create.ts    [--name, --identifier, --description, ...]
│  ├─ update.ts    <id> [--name, --identifier, ...]
│  ├─ delete.ts    <id> [--confirm]
│  └─ members.ts   <id> [--json]
├─ issue/
│  ├─ list.ts      [--project, --cycle, --module, ...]
│  ├─ get.ts       <id|PROJECT-123> [--project] [--json]
│  ├─ create.ts    [--project, --name, --priority, ...]
│  ├─ update.ts    <id|PROJECT-123> [...]
│  ├─ delete.ts    <id|PROJECT-123> [--confirm]
│  └─ search.ts    <query> [--json]
├─ cycle/, module/, label/, state/, ...
│  └─ [list|get|create|update|delete|archive|unarchive|...]
└─ page/, user/, workspace/
   └─ [resource-specific commands]
```

### Base Command Class

**`src/base-command.ts`** — All oclif commands extend this
```typescript
export class BaseCommand extends Command {
  requireApi(): PlaneAPI
    └─ Lazy-loads API client, validates config

  requireConfig(): Config
    └─ Loads ~/.planerc, validates with Zod schema

  flags = {
    json: Flags.boolean({ enableJsonFlag: true }),
    'no-input': Flags.boolean(),
  }
}
```

### Config Management

**`src/lib/config.ts`**

**Location:** `~/.planerc` (JSON format)
```json
{
  "workspace": "my-workspace",
  "apiKey": "plane_api_xxx",
  "baseUrl": "https://api.plane.so/api/v1",
  "accessToken": "optional_token",
  "currentProfile": "default",
  "defaults": {
    "project": "optional_uuid"
  }
}
```

**Zod Schema:**
```typescript
ConfigSchema = z.object({
  workspace: z.string(),
  apiKey: z.string().optional(),
  accessToken: z.string().optional(),
  baseUrl: z.string().default('https://api.plane.so/api/v1'),
  currentProfile: z.string().optional(),
  defaults: z.object({ project: z.string() }).optional(),
})
```

**API:**
```typescript
getConfig(): Config | null     // Loads from ~/.planerc
saveConfig(config: Config): void  // Writes to ~/.planerc (0o600 perms)
hasConfig(): boolean           // Check existence
```

### API Client (`src/lib/api.ts`)

**Raw fetch wrapper** (no external SDK dependency)

```typescript
class PlaneAPI {
  constructor(
    baseUrl: string,
    workspaceSlug: string,
    apiKey: string | undefined,
    accessToken: string | undefined
  )

  // Generic method dispatch
  async request<T>(
    method: 'GET' | 'POST' | 'PATCH' | 'DELETE',
    endpoint: string,
    body?: object,
    options?: RequestOptions
  ): Promise<T>

  // Resource methods
  async listProjects(slug): Promise<{ results: Project[] }>
  async getProject(slug, id): Promise<Project>
  async createProject(slug, data): Promise<Project>
  async updateProject(slug, id, data): Promise<Project>
  async deleteProject(slug, id): Promise<void>

  async listIssues(slug, projectId, filters?): Promise<{ results: Issue[] }>
  async getIssue(slug, projectId, id): Promise<Issue>
  async createIssue(slug, projectId, data): Promise<Issue>
  async updateIssue(slug, projectId, id, data): Promise<Issue>
  async deleteIssue(slug, projectId, id): Promise<void>

  // ... cycles, modules, labels, states, etc.
}
```

**Authentication:**
- Bearer token: `apiKey` or `accessToken` in Authorization header
- Fallback to env vars if not configured

### Output Formatting (`src/lib/output.ts`)

**TTY Detection:**
```typescript
function isTTY(): boolean {
  return process.stdout.isTTY === true
}
```

**Output Modes:**
| Context | Default | Override |
|---------|---------|----------|
| TTY (terminal) | Pretty table | `--json` |
| Piped (file/pipe) | JSON | `--output pretty` |

**Helpers:**
```typescript
printJson(data)           // console.log(JSON.stringify(data, null, 2))
printTable(data, columns) // cli-table3 with column definitions
createSpinner(text)       // ora spinner for long operations
success(msg)              // chalk green checkmark
error(msg)                // chalk red X
warning(msg)              // chalk yellow !
info(msg)                 // chalk blue i
```

### Interactive Prompts (`src/lib/prompts.ts`)

**@inquirer/prompts integration:**
```typescript
promptApiKey(): Promise<string>
promptAccessToken(): Promise<string>
promptWorkspace(): Promise<string>
promptConfirm(message, defaultValue): Promise<boolean>
promptText(message, defaultValue?): Promise<string>
promptSelect(message, choices): Promise<string>
promptMultiSelect(message, choices): Promise<string[]>
```

**Disabled via:** `--no-input` flag

### Issue Resolver (`src/lib/issue-resolver.ts`)

**Resolves issue references to UUIDs:**
```typescript
// Accepts both:
// - UUID: "550e8400-e29b-41d4-a716-446655440000"
// - Sequence: "PROJECT-123"

resolveIssue(slug, projectId, ref): Promise<Issue>
  ├─ If UUID: fetch directly by ID
  └─ If sequence: fetch ALL issues, find by sequence_id
```

**Performance concern:** Fetches entire issue list for sequence lookups (scalability issue for large projects).

### Error Handling (`src/lib/errors.ts`)

**Custom error classes:**
```typescript
class ConfigError extends Error { code = 'CONFIG_ERROR' }     // Exit 2
class AuthError extends Error { code = 'AUTH_ERROR' }         // Exit 3
class NotFoundError extends Error { code = 'NOT_FOUND' }      // Exit 1
class ValidationError extends Error { code = 'VALIDATION' }   // Exit 1
```

**Exit codes:**
| Code | Trigger |
|------|---------|
| 0 | Success |
| 1 | General error (API error, validation, etc.) |
| 2 | Config error (missing ~/.planerc, invalid config) |
| 3 | Auth error (invalid API key, unauthorized) |
| 130 | User cancel (Ctrl+C) |

### Testing Architecture

**Framework:** mocha + chai + @oclif/test
**Location:** `test/`

**Mocking strategy:**
```
test/helpers/mock-api.ts
  └─ Full PlaneAPI mock implementation
     └─ Returns static test data
     └─ Used by tests via globalThis.fetch mock

test/commands/*.test.ts
  ├─ Config tests (read/write ~/.planerc)
  ├─ Command tests (@oclif/test runCommand)
  └─ API tests (mock fetch globally)

test/lib/*.test.ts
  ├─ Config schema validation
  ├─ Issue resolver reference parsing
  └─ API request formatting
```

## Request-Response Flow Example

### TypeScript CLI: `plane-cli project list`

```
1. User Input
   $ plane-cli project list

2. Entry Point (bin/run.js)
   └─ oclif execute() → src/index.ts

3. Command Resolution (oclif)
   └─ Routes to src/commands/project/list.ts

4. ProjectList Command
   ├─ parse(ProjectList) → {flags: {json: false}, args: {}}
   ├─ requireConfig() → loads ~/.planerc
   ├─ requireApi() → initializes PlaneAPI
   └─ api.listProjects(config.workspace)

5. API Client (src/lib/api.ts)
   ├─ request('GET', '/projects/', ...)
   ├─ Adds headers:
   │  ├─ Authorization: Bearer {apiKey|accessToken}
   │  └─ Content-Type: application/json
   └─ fetch(baseUrl + endpoint)

6. Network
   └─ HTTPS POST → https://api.plane.so/api/v1/workspaces/my-workspace/projects/

7. Plane API Response
   ├─ 200 OK
   └─ { results: [Project1, Project2, ...] }

8. Response Processing
   ├─ Check isTTY()
   ├─ If TTY: printTable(results, columns)
   └─ If !TTY: printJson(results)

9. Output
   ┌─────────────────────────────────────┐
   │ TTY:  Project table (colors)        │
   │ JSON: [{"id":"...", "name":"..."}]  │
   └─────────────────────────────────────┘
```

### Python Script: `python plane_projects.py list`

```
1. User Input
   $ python skills/plane/scripts/plane_projects.py list

2. Script Entry (main())
   ├─ build_parser() → argparse.ArgumentParser
   ├─ parse_args() → Namespace(command='list')
   └─ COMMANDS['list'](args)

3. cmd_list(args)
   ├─ get_client() → (PlaneSDK, workspace_slug)
   ├─ client.projects.list(workspace_slug)
   └─ dump_json(results)

4. SDK Layer (plane-sdk)
   ├─ Validates PLANE_API_KEY env var
   ├─ Uses plane-sdk==0.2.2
   └─ HTTPS to Plane API

5. Response
   └─ JSON output (stdout)
```

## Data Models

### Core Resources

**Project:**
```typescript
{
  id: string (UUID)
  name: string
  identifier: string (2-3 chars, e.g., "MP")
  description?: string
  created_at: ISO8601
  workspace_id: string
}
```

**Issue (a.k.a. Work Item):**
```typescript
{
  id: string (UUID)
  name: string
  sequence_id: number (e.g., 42 in "PROJECT-42")
  state_id: string (UUID)
  priority?: 'urgent' | 'high' | 'medium' | 'low'
  cycle_id?: string
  module_id?: string
  assigned_to?: string
  project_id: string
  created_at: ISO8601
}
```

**Cycle:**
```typescript
{
  id: string (UUID)
  name: string
  start_date?: ISO8601
  end_date?: ISO8601
  project_id: string
  status?: 'draft' | 'started' | 'completed'
  is_archived: boolean
}
```

**Module:**
```typescript
{
  id: string (UUID)
  name: string
  description?: string
  start_date?: ISO8601
  end_date?: ISO8601
  project_id: string
  is_archived: boolean
}
```

## Security Considerations

### Authentication
- **Credentials storage:** `~/.planerc` (JSON, 0o600 permissions)
- **In-memory:** API key/token only used during request headers
- **Env var override:** `PLANE_API_KEY`, `PLANE_ACCESS_TOKEN`, `PLANE_WORKSPACE_SLUG`

### Data Protection
- **HTTPS only:** All API calls use HTTPS
- **No request/response logging** to file (stdout only)
- **--confirm flag** on destructive operations (delete, archive)

### Error Messages
- Don't leak API URLs or workspace slugs in public errors
- Distinguish auth errors (exit 3) from general errors (exit 1)

## Deployment & Distribution

### TypeScript CLI

**npm Package:**
```bash
npm install -g plane-cli
# or
npm install --save-dev plane-cli
```

**Local Development:**
```bash
cd packages/cli
npm install
npm run build  # TypeScript → JavaScript
npm test       # mocha tests
plane-cli --help
```

### Python Skill

**Plugin registration:**
```json
{
  "name": "plane",
  "type": "skill",
  "entrypoint": "skills/plane/SKILL.md"
}
```

**Setup:**
```bash
pip install -r skills/plane/requirements.txt
bash skills/plane/scripts/plane_setup.sh
```

## Comparison Matrix

| Aspect | Python | TypeScript |
|--------|--------|-----------|
| **Framework** | argparse | oclif 4 |
| **Entry point** | Multiple scripts | Single CLI |
| **Language** | Python 3.10+ | TypeScript 5 |
| **Runtime** | CPython | Node 18+ |
| **Dependencies** | plane-sdk only | @oclif, chalk, cli-table3, etc. |
| **API client** | plane-sdk SDK | Custom raw fetch |
| **Output** | JSON only | TTY-aware (JSON/pretty) |
| **Config** | Env vars + .plane.env | ~/.planerc (JSON) |
| **Interactive** | No | Yes (@inquirer/prompts) |
| **Tests** | E2E Python + smoke | Unit tests (mocha) |
| **Distribution** | None (reference) | npm package |
| **Status** | Maintained | Production |

## Future Architecture Improvements

1. **Consolidate error handling** — Use consistent exit codes, remove mixed `process.exit()` and `this.error()`
2. **Optimize issue resolution** — Cache or lazy-load issues instead of fetching entire list
3. **Extract shared utilities** — DRY out `stripHtml` duplication
4. **Add middleware support** — Hook system for custom pre/post-processing
5. **Deprecate Python scripts** — Migrate fully to TypeScript CLI once mature
