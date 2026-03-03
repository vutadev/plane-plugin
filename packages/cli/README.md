# plane-cli

CLI for [Plane](https://plane.so) project management.

[![oclif](https://img.shields.io/badge/cli-oclif-brightgreen.svg)](https://oclif.io)
[![Version](https://img.shields.io/npm/v/plane-cli.svg)](https://npmjs.org/package/plane-cli)
[![Downloads/week](https://img.shields.io/npm/dw/plane-cli.svg)](https://npmjs.org/package/plane-cli)

<!-- toc -->

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Commands](#commands)
- [Examples](#examples)
<!-- tocstop -->

## Installation

```bash
npm install -g plane-cli
```

## Quick Start

```bash
# Configure authentication
plane-cli config init

# List your projects
plane-cli project list

# Create an issue
plane-cli issue create --project MY-PROJECT --name "Fix login bug"

# View issue details (supports PROJECT-123 format)
plane-cli issue get MY-42
```

## Configuration

Configuration is stored in `~/.planerc`:

```json
{
  "workspace": "my-workspace",
  "apiKey": "plane_api_xxx",
  "baseUrl": "https://api.plane.so/api/v1"
}
```

Or use environment variables:

- `PLANE_API_KEY` or `PLANE_ACCESS_TOKEN` - Your Plane API credentials
- `PLANE_WORKSPACE_SLUG` - Your workspace slug
- `PLANE_BASE_URL` - API base URL (optional, defaults to https://api.plane.so/api/v1)

Environment variables override config file values.

### Config Commands

```bash
# Initialize configuration interactively
plane-cli config init

# View current configuration
plane-cli config show

# Set a specific config value
plane-cli config set workspace my-workspace
plane-cli config set apiKey plane_api_xxx
```

## Commands

### Project Commands

| Command                      | Description                        |
| ---------------------------- | ---------------------------------- |
| `plane-cli project list`     | List all projects in workspace     |
| `plane-cli project get <id>` | Get project details                |
| `plane-cli project create`   | Create a new project (interactive) |
| `plane-cli project update`   | Update a project                   |
| `plane-cli project delete`   | Delete a project                   |
| `plane-cli project members`  | List project members               |

### Issue Commands

| Command                           | Description                          |
| --------------------------------- | ------------------------------------ |
| `plane-cli issue list`            | List issues in a project             |
| `plane-cli issue get <id>`        | Get issue details (supports PROJECT-123 format) |
| `plane-cli issue create`          | Create an issue (interactive wizard) |
| `plane-cli issue update <id>`     | Update an issue                      |
| `plane-cli issue delete <id>`     | Delete an issue                      |
| `plane-cli issue search <query>`  | Search issues                        |

### Cycle Commands

| Command                               | Description                    |
| ------------------------------------- | ------------------------------ |
| `plane-cli cycle list`                | List cycles                    |
| `plane-cli cycle get <id>`            | Get cycle details              |
| `plane-cli cycle create`              | Create a cycle                 |
| `plane-cli cycle update <id>`         | Update a cycle                 |
| `plane-cli cycle delete <id>`         | Delete a cycle                 |
| `plane-cli cycle archive <id>`        | Archive a cycle                |
| `plane-cli cycle unarchive <id>`      | Unarchive a cycle              |
| `plane-cli cycle add-issues <id>`     | Add issues to a cycle          |
| `plane-cli cycle remove-issue <id>`   | Remove an issue from a cycle   |
| `plane-cli cycle transfer <from> <to>`| Transfer issues between cycles |

### Module Commands

| Command                                | Description                    |
| -------------------------------------- | ------------------------------ |
| `plane-cli module list`                | List modules                   |
| `plane-cli module get <id>`            | Get module details             |
| `plane-cli module create`              | Create a module                |
| `plane-cli module update <id>`         | Update a module                |
| `plane-cli module delete <id>`         | Delete a module                |
| `plane-cli module archive <id>`        | Archive a module               |
| `plane-cli module unarchive <id>`      | Unarchive a module             |
| `plane-cli module add-issues <id>`     | Add issues to a module         |
| `plane-cli module remove-issue <id>`   | Remove an issue from a module  |

### Label Commands

| Command                      | Description           |
| ---------------------------- | --------------------- |
| `plane-cli label list`       | List labels           |
| `plane-cli label get <id>`   | Get label details     |
| `plane-cli label create`     | Create a label        |
| `plane-cli label update <id>`| Update a label        |
| `plane-cli label delete <id>`| Delete a label        |

### State Commands

| Command                      | Description           |
| ---------------------------- | --------------------- |
| `plane-cli state list`       | List states           |
| `plane-cli state create`     | Create a state        |
| `plane-cli state delete <id>`| Delete a state        |

### Intake Commands

| Command                      | Description           |
| ---------------------------- | --------------------- |
| `plane-cli intake list`      | List intakes          |
| `plane-cli intake create`    | Create an intake      |
| `plane-cli intake delete <id>`| Delete an intake     |

### Initiative Commands

| Command                           | Description              |
| --------------------------------- | ------------------------ |
| `plane-cli initiative list`       | List initiatives         |
| `plane-cli initiative create`     | Create an initiative     |
| `plane-cli initiative delete <id>`| Delete an initiative     |

### Page Commands

| Command                                      | Description                  |
| -------------------------------------------- | ---------------------------- |
| `plane-cli page get-workspace <id>`          | Get workspace page           |
| `plane-cli page get-project <project> <id>`  | Get project page             |
| `plane-cli page create`                      | Create a page                |

### User Commands

| Command           | Description         |
| ----------------- | ------------------- |
| `plane-cli user me` | Get current user  |

### Workspace Commands

| Command                      | Description              |
| ---------------------------- | ------------------------ |
| `plane-cli workspace members`| List workspace members   |

## Examples

### Working with Projects

```bash
# List all projects
plane-cli project list

# List projects as JSON
plane-cli project list --json

# Get project details
plane-cli project get proj-uuid-1234

# Create a new project
plane-cli project create --name "My Project" --identifier "MP"

# Delete a project (requires confirmation)
plane-cli project delete proj-uuid-1234 --confirm
```

### Working with Issues

```bash
# List issues in a project
plane-cli issue list --project proj-uuid-1234

# List issues filtered by cycle
plane-cli issue list --project proj-uuid-1234 --cycle cycle-uuid

# Get issue by PROJECT-123 format
plane-cli issue get MP-42

# Get issue by UUID
plane-cli issue get issue-uuid-1234 --project proj-uuid-1234

# Create a high priority issue
plane-cli issue create --project proj-uuid-1234 --name "Critical bug" --priority urgent

# Search issues
plane-cli issue search "login bug"
```

### Working with Cycles

```bash
# List all cycles
plane-cli cycle list --project proj-uuid-1234

# Create a cycle with dates
plane-cli cycle create --project proj-uuid-1234 --name "Sprint 1" --start-date 2024-01-01 --end-date 2024-01-14

# Add issues to a cycle
plane-cli cycle add-issues cycle-uuid --issues issue-1,issue-2,issue-3

# Archive a cycle
plane-cli cycle archive cycle-uuid
```

### Working with Modules

```bash
# List modules
plane-cli module list --project proj-uuid-1234

# Create a module
plane-cli module create --project proj-uuid-1234 --name "Feature Module"

# Add issues to a module
plane-cli module add-issues module-uuid --issues issue-1,issue-2
```

### Global Flags

All commands support these global flags:

| Flag          | Description                        |
| ------------- | ---------------------------------- |
| `--json`      | Output as JSON                     |
| `--no-input`  | Disable interactive prompts        |
| `--help`      | Show help for a command            |

## API Documentation

For more information about the Plane API, visit the [Plane API Documentation](https://docs.plane.so/api-reference/introduction).

## License

MIT
