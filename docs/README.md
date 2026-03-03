# Plane Plugin Documentation

**Last Updated:** 2026-03-03
**Coverage:** TypeScript CLI + Python Skill

This directory contains comprehensive documentation for the Plane Agent Skill, a dual-implementation CLI for Plane project management.

## Quick Navigation

### 📋 For New Developers
Start here to understand the project:
1. **[Project Overview & PDR](./project-overview-pdr.md)** — What the project does, core features, requirements, roadmap
2. **[Codebase Summary](./codebase-summary.md)** — High-level overview of structure, metrics, known issues

### 🏗️ For Architecture & Design
Understand how the system works:
1. **[System Architecture](./system-architecture.md)** — Data flows, component interactions, request sequences, security considerations

### 📝 For Development
Build new features and fixes:
1. **[Code Standards](./code-standards.md)** — File naming, code patterns, testing, error handling for both TypeScript and Python

### 🔧 For Maintenance
Manage the codebase:
1. Review [known issues](./codebase-summary.md#known-issues) from codebase-summary.md
2. Check [roadmap](./project-overview-pdr.md#roadmap) from project-overview-pdr.md
3. Follow [development workflow](./code-standards.md#development-workflow) from code-standards.md

## Document Guide

| Document | Purpose | Audience | Size |
|----------|---------|----------|------|
| **[project-overview-pdr.md](./project-overview-pdr.md)** | Vision, requirements, roadmap | Product managers, developers | 448 lines |
| **[codebase-summary.md](./codebase-summary.md)** | Structure, metrics, components | Developers, architects | 265 lines |
| **[system-architecture.md](./system-architecture.md)** | Design, data flows, interactions | Architects, senior developers | 588 lines |
| **[code-standards.md](./code-standards.md)** | Coding guidelines, patterns, conventions | All developers | 867 lines |

**Total:** 2,168 lines of documentation

## Key Information

### Project Structure
```
plane-plugin/
├── packages/cli/               # TypeScript CLI (oclif 4)
│   ├── src/commands/           # 53 commands (11 resource groups)
│   ├── src/lib/                # Core modules (api, config, output, etc.)
│   ├── test/                   # Unit tests (49 passing)
│   └── package.json            # npm package as `plane-cli`
├── skills/plane/               # Legacy Python skill
│   └── scripts/                # 13 CLI scripts (plane-sdk wrapper)
└── tests/
    └── e2e/                    # E2E tests (8 Python files)
```

### Quick Facts
- **TypeScript CLI:** oclif 4, Node >=18.0.0, TypeScript 5, 53 commands
- **Python Skill:** Python >=3.10, plane-sdk only, 13 scripts
- **Config:** ~/.planerc (TypeScript), env vars (both)
- **Tests:** 49 unit tests (mocha) + 8 E2E tests (pytest)
- **Distribution:** npm package (`plane-cli`), Claude Code plugin

### Command Summary
| Resource | Count | Examples |
|----------|-------|----------|
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
| **TOTAL** | **53** | **Full CRUD for Plane resources** |

## Common Tasks

### I want to...

#### Understand what this project does
→ Read [Project Overview & PDR](./project-overview-pdr.md#executive-summary)

#### Learn the system architecture
→ Read [System Architecture](./system-architecture.md#overview)

#### Set up development environment
→ See [Code Standards → Development Workflow](./code-standards.md#development-workflow)

#### Add a new TypeScript command
→ Follow [Code Standards → Adding a New TypeScript Command](./code-standards.md#adding-a-new-typescript-command)

#### Add a new Python script
→ Follow [Code Standards → Adding a New Python Script](./code-standards.md#adding-a-new-python-script)

#### Fix a bug
1. Check [Known Issues](./codebase-summary.md#known-issues) (7 documented)
2. Review [Error Handling](./code-standards.md#error-handling)
3. Add tests (see [Testing Standards](./code-standards.md#testing-standards))

#### Understand the codebase
→ Read [Codebase Summary](./codebase-summary.md)

#### Review security practices
→ See [System Architecture → Security](./system-architecture.md#security-considerations)

#### Plan new features
→ Check [Roadmap](./project-overview-pdr.md#roadmap)

## Known Issues

**7 documented issues** (priorities P0-P2):

| # | Issue | Severity | Impact | Fix |
|---|-------|----------|--------|-----|
| 1 | API response crashes on 204 No Content | P0 | DELETE fails | Check status before json() |
| 2 | Config init prompt bug | P0 | Access token setup fails | Call correct prompt function |
| 3 | Cycle commands missing baseFlags | P1 | --no-input not parsed | Add spread to all cycle commands |
| 4 | Issue resolver fetches all issues | P1 | Slow on large projects | Implement pagination/filter |
| 5 | stripHtml duplicated 3x | P1 | Maintenance burden | Extract to shared utility |
| 6 | Mixed error handling | P2 | Inconsistent behavior | Standardize error classes |
| 7 | Flag conflicts on BaseCommand | P2 | Potential flag issues | Review flag setup |

See [Known Issues](./codebase-summary.md#known-issues-from-code-reviewer-memory-2026-03-03) for details.

## Roadmap

**5 phases, 4-14 weeks:**

1. **Stabilization (2-4w):** Fix P0/P1 bugs, expand test coverage
2. **Performance (4-6w):** Optimize issue resolver, add caching
3. **Extended Features (6-10w):** Multi-profile, bulk import/export, templates
4. **Migration (10-14w):** Full parity with Python, deprecate scripts
5. **Advanced (TBD):** AI suggestions, integrations, offline mode

See [Roadmap](./project-overview-pdr.md#roadmap) for details.

## Development Standards

### Code Naming
- **Files:** kebab-case (e.g., `api.ts`, `plane_projects.py`)
- **Variables:** camelCase (e.g., `projectId`, `workspace`)
- **Classes/Types:** PascalCase (e.g., `BaseCommand`, `PlaneAPI`)
- **Commands:** kebab-case (e.g., `project list`, `issue create`)

### Error Handling
- **Exit codes:** 0 (success), 1 (general), 2 (config), 3 (auth), 130 (cancel)
- **Destructive ops:** Require `--confirm` flag
- **Messages:** Actionable, never leak credentials

### Testing
- **TypeScript:** mocha + chai + @oclif/test
- **Python:** pytest
- **Coverage:** Aim for >70%
- **Mocks:** Use PlaneAPI mock for unit tests

See [Code Standards](./code-standards.md) for comprehensive guidelines.

## Contributing

1. **Read** the relevant section from this README
2. **Check** [Code Standards](./code-standards.md) for your language
3. **Follow** naming conventions and patterns
4. **Test** your changes (npm test or pytest)
5. **Document** new features in appropriate docs file

## References

- **Plane Documentation:** https://docs.plane.so/
- **oclif Documentation:** https://oclif.io/
- **npm Package:** https://www.npmjs.com/package/plane-cli
- **GitHub:** https://github.com/plane-so/plane-cli
- **Issues:** Use GitHub Issues for bugs and features

## Documentation Maintenance

**Last updated:** 2026-03-03 by docs-manager
**Next review:** 2026-04-03
**Owner:** Development Team

To update documentation:
1. Edit relevant `.md` file
2. Verify markdown syntax
3. Keep sections in consistent order
4. Update "Last Updated" date
5. Commit with message: `docs: update {filename} for {reason}`

---

**Total Documentation:** 2,168 lines across 4 files
**Coverage:** Architecture, code standards, requirements, roadmap
**Status:** Current as of 2026-03-03
