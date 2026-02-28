# Plane CLI Refactor: Python to TypeScript

**Date:** 2026-02-28  
**Status:** Approved

## Overview

Refactor the Plane Agent Skill from Python scripts to a unified TypeScript CLI, compiled to a single bundled JS file.

## Goals

- Eliminate Python dependency
- Better DX with TypeScript types and IDE support
- Single entry point CLI with nested subcommands
- Multi-profile support for multiple workspaces
- Improved output with TTY auto-detection

## Technology Stack

| Component | Choice |
|-----------|--------|
| Language | TypeScript |
| Runtime | Node.js (compiled) |
| SDK | `@makeplane/plane-node-sdk` v0.2.8 |
| CLI Framework | Commander.js |
| Bundler | esbuild |
| Output | Single bundled JS file |

## Architecture

```
skills/plane/
├── src/
│   ├── index.ts              # CLI entry point
│   ├── cli/
│   │   ├── index.ts          # Commander app setup
│   │   ├── commands/         # Subcommand handlers
│   │   │   ├── login.ts      # plane login
│   │   │   ├── projects.ts   # plane projects <action>
│   │   │   ├── issues.ts     # plane issues <action>
│   │   │   ├── cycles.ts     # plane cycles <action>
│   │   │   ├── modules.ts    # plane modules <action>
│   │   │   └── ...
│   │   └── output.ts         # TTY detection, formatting
│   ├── client/
│   │   ├── index.ts          # PlaneClient wrapper
│   │   └── config.ts         # Config file (~/.plane/config.json)
│   └── types/
│       └── index.ts          # Shared types
├── dist/
│   └── plane.js              # Bundled CLI (single file)
├── package.json
├── tsconfig.json
├── esbuild.config.js
└── SKILL.md
```

## Config & Profiles

**Location:** `~/.plane/config.json`

**Structure:**
```json
{
  "profiles": {
    "default": {
      "apiKey": "plane_api_xxx",
      "workspaceSlug": "my-workspace",
      "baseUrl": "https://api.plane.so/api/v1"
    },
    "work": {
      "apiKey": "plane_api_yyy",
      "workspaceSlug": "company-workspace",
      "baseUrl": "https://api.plane.so/api/v1"
    }
  },
  "activeProfile": "default"
}
```

**Profile selection priority:**
1. `--profile <name>` flag
2. `PLANE_PROFILE` env var
3. `activeProfile` in config
4. Fallback to `"default"`

**Profile commands:**
```bash
plane login                         # Interactive prompt (default profile)
plane login --name work             # Create/update named profile
plane login --name work --api-key $KEY --workspace my-slug  # Non-interactive
plane logout                        # Remove active profile
plane logout --profile work         # Remove specific profile
plane profile list                  # List all profiles
plane profile use work              # Set active profile
```

## CLI Commands

**Structure:**
```
plane [global-options] <resource> <action> [action-options]
```

**Global options:**
- `--profile <name>` — Use specific profile
- `--output <json|pretty>` — Override auto-detect
- `--help` — Show help

**Resources:**

| Resource | Actions |
|----------|---------|
| `login` | (none) — interactive setup |
| `logout` | (none) — clear credentials |
| `profile` | `list`, `use`, `delete` |
| `projects` | `list`, `get`, `create`, `update`, `delete` |
| `issues` | `list`, `get`, `get-by-id`, `create`, `update`, `delete`, `search` |
| `cycles` | `list`, `get`, `create`, `update`, `delete`, `archive`, `unarchive`, `add-items`, `remove-item`, `list-items`, `transfer-items` |
| `modules` | `list`, `get`, `create`, `update`, `delete`, `archive`, `unarchive`, `add-items`, `remove-item`, `list-items` |
| `labels` | `list`, `get`, `create`, `update`, `delete` |
| `states` | `list`, `get`, `create`, `update`, `delete` |
| `initiatives` | `list`, `get`, `create`, `update`, `delete` |
| `intake` | `list`, `get`, `create`, `update`, `delete` |
| `pages` | `get-workspace`, `get-project`, `create-workspace`, `create-project` |
| `users` | `me` |

**Safety:** All `delete` commands require `--confirm` flag.

## Output Handling

**Auto-detection:**
```typescript
function isTTY(): boolean {
  return process.stdout.isTTY === true;
}
```

| Context | Output |
|---------|--------|
| TTY (terminal) | Pretty-printed tables |
| Piped/redirected | JSON |
| `--output json` | JSON |
| `--output pretty` | Pretty tables |

**Pretty output example:**
```
┌──────────────────────────────────────┬──────────┬─────────┬────────────┐
│ ID                                   │ Name     │ Ident…  │ Created    │
├──────────────────────────────────────┼──────────┼─────────┼────────────┤
│ 550e8400-e29b-41d4-a716-446655440000 │ My App   │ MA      │ 2024-01-15 │
└──────────────────────────────────────┴──────────┴─────────┴────────────┘
```

**JSON output (same as Python):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "My App",
    "identifier": "MA",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

## Error Handling

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Authentication error |
| 130 | User cancelled (Ctrl+C) |

**TTY error format:**
```
✗ Error: Project not found
  Run `plane projects list` to see available projects
```

**JSON error format:**
```json
{
  "error": true,
  "message": "Project not found",
  "code": "NOT_FOUND"
}
```

## Implementation Phases

### Phase 1: Foundation
- Project setup (package.json, tsconfig.json, esbuild.config.js)
- Config module (`~/.plane/config.json` read/write)
- Client wrapper (PlaneClient from SDK)
- Profile management (login, logout, profile list/use)

### Phase 2: Core Resources
- projects (list, get, create, update, delete)
- issues (list, get, get-by-id, create, update, delete, search)
- Output handling (TTY detection, pretty/JSON)

### Phase 3: Extended Resources
- cycles, modules, labels, states
- initiatives, intake, pages, users

### Phase 4: Polish & Migration
- Error handling refinement
- Help text and documentation
- SKILL.md update
- Remove Python scripts
- Update plugin.json

## Migration Notes

- Config moves from `.plane.env` (project-local) to `~/.plane/config.json` (global)
- Multi-profile support added (was single workspace in Python)
- CLI unified from multiple Python scripts to single `plane` command
- Output auto-detects TTY (Python was JSON-only)

## Dependencies

```json
{
  "dependencies": {
    "@makeplane/plane-node-sdk": "^0.2.8",
    "commander": "^12.0.0"
  },
  "devDependencies": {
    "esbuild": "^0.20.0",
    "typescript": "^5.4.0",
    "@types/node": "^20.0.0"
  }
}
```