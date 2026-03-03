# Project Overview & Product Development Requirements (PDR)

**Last Updated:** 2026-03-03
**Project Status:** Production (TypeScript CLI), Active Maintenance (Python skill)
**Maintained by:** Development Team

## Executive Summary

**Plane Agent Skill** is a dual-implementation CLI for programmatic interaction with Plane, an open-source project management platform. It provides command-line and Claude Code plugin access to Plane's projects, issues, cycles, modules, and related resources.

The project supports:
- **Legacy Python skill** (13 CLI scripts, SDK-based) — maintained for backward compatibility
- **Modern TypeScript CLI** (53 oclif commands, npm distributed) — primary development path

Both implementations wrap the Plane API with identical functionality but different technical approaches, targeting different user preferences and deployment models.

## Product Vision

Enable developers and automation systems to interact with Plane project management entirely via CLI/programmatic interfaces, eliminating the need for UI navigation for common operations like:
- Listing/filtering projects and issues
- Creating/updating/deleting work items
- Managing cycles, modules, and labels
- Organizing issues into sprints and releases
- Querying workspace and team information

## Core Features

### 1. Project Management
- **List projects** across workspace
- **Get project details** by UUID
- **Create projects** with name, identifier, description
- **Update project** metadata
- **Delete projects** (requires --confirm)
- **List project members**

### 2. Issue Management
- **List issues** with filters (cycle, module, assignee, state, priority)
- **Get issue by UUID or sequence** (e.g., PROJECT-123)
- **Create issues** with name, priority, state, cycle, module assignment
- **Update issue** properties (name, priority, state, assignee, dates)
- **Delete issues** (requires --confirm)
- **Search issues** by full-text query

### 3. Cycle Management (Sprints)
- **List cycles** in project
- **Get cycle details**
- **Create cycles** with start/end dates
- **Update cycle** properties
- **Delete cycles** (requires --confirm)
- **Archive/unarchive** cycles
- **Add/remove issues** to cycle
- **Transfer issues** between cycles

### 4. Module Management
- **List modules** in project
- **Get module details**
- **Create modules** with name, description, dates
- **Update module** properties
- **Delete modules** (requires --confirm)
- **Archive/unarchive** modules
- **Add/remove issues** to module

### 5. Additional Resources
- **Labels:** List, get, create, update, delete
- **States:** List, create, delete
- **Pages:** Create, retrieve (workspace/project scoped)
- **Initiatives:** List, create, delete
- **Intake:** List, create, delete
- **Users:** Get current user info
- **Workspace:** List members

### 6. Configuration & Authentication
- **Interactive setup** (plane-cli config init)
- **Multi-profile support** (TypeScript CLI future enhancement)
- **API key or access token** authentication
- **Environment variable override** for CI/CD
- **Config file** at ~/.planerc (TypeScript) or env vars (Python)

## Non-Functional Requirements

### Performance
- **Command latency:** <2 seconds for list operations
- **Concurrent requests:** Support 10+ simultaneous operations
- **Batch operations:** Handle 100+ items in single request
- **Issue resolution:** Optimize PROJECT-123 lookups (currently fetches all)

### Reliability
- **Error handling:** Distinguish config (exit 2), auth (exit 3), general (exit 1) errors
- **Destructive operations:** Require explicit --confirm flag
- **Timeouts:** Default 30s, configurable
- **Retry logic:** 3 retries for transient failures (future)

### Usability
- **Interactive mode:** Prompts for missing required arguments
- **Batch mode:** --no-input flag for automation
- **Output flexibility:** TTY-aware (pretty tables) or JSON (piped)
- **Help system:** --help on all commands with examples
- **Clear error messages:** Actionable guidance on failures

### Security
- **Credentials:** Stored securely (env vars or ~/.planerc with 0o600 permissions)
- **HTTPS only:** All API calls via HTTPS
- **No logging:** Credentials never logged to files
- **Auth errors:** Exit code 3 distinguishes from general errors
- **Input validation:** Zod schema validation on config

### Maintainability
- **Code standards:** TypeScript strict mode, ESLint, consistent naming
- **Testing:** Unit tests (mocha), E2E tests (pytest), smoke tests
- **Documentation:** Inline comments, JSDoc/docstrings, README, guides
- **Modularity:** Commands, libs, types separated; DRY principles
- **Version control:** Clean commits, no confidential data

### Accessibility
- **CLI framework:** oclif (TypeScript) with auto-generated help
- **Output formats:** JSON for piping, pretty tables for humans
- **CLI structure:** Nested commands (resource action) vs multiple scripts
- **Configuration:** Single config file vs env vars, both supported

## Functional Requirements

### FR-001: Project Operations
- **Description:** CRUD operations on Plane projects
- **Inputs:** Project UUID, name, identifier, description
- **Outputs:** Project object, success/error message
- **Constraints:** Create requires name + identifier; update accepts partial fields
- **Acceptance Criteria:**
  - List returns all projects as JSON or table
  - Get by UUID returns single project
  - Create with valid name/identifier succeeds
  - Update modifies specified fields only
  - Delete with --confirm removes project

### FR-002: Issue Operations
- **Description:** CRUD operations on work items (issues)
- **Inputs:** Issue UUID, sequence (PROJECT-123), name, description, priority, state, cycle, module
- **Outputs:** Issue object, success/error message
- **Constraints:** Create requires project + name; sequence lookup requires fetching all issues
- **Acceptance Criteria:**
  - List with filters returns matching issues
  - Get by UUID or sequence returns single issue
  - Create with required fields succeeds
  - Update modifies specified fields
  - Delete with --confirm removes issue
  - Search returns matching results

### FR-003: Cycle Management
- **Description:** Sprint/cycle management operations
- **Inputs:** Cycle UUID, name, start_date, end_date, status
- **Outputs:** Cycle object, success/error message
- **Constraints:** Dates are ISO8601; transfer moves issues between cycles
- **Acceptance Criteria:**
  - List returns cycles for project
  - Create with dates succeeds
  - Archive prevents issue assignment; unarchive enables
  - Add/remove issues updates cycle membership
  - Transfer moves all issues to target cycle

### FR-004: Configuration Management
- **Description:** Store and manage API credentials
- **Inputs:** API key, access token, workspace slug, base URL
- **Outputs:** Config file, validation status
- **Constraints:** Config stored at ~/.planerc; env vars override file; requires valid workspace
- **Acceptance Criteria:**
  - Init creates valid config file
  - Show displays current config (masked secrets)
  - Set updates specific keys
  - Env vars override config file
  - Invalid config blocks command execution with clear error

### FR-005: Interactive Prompts
- **Description:** Guide users through common operations
- **Inputs:** User selections, text input
- **Outputs:** Configuration, resource selection
- **Constraints:** Disabled via --no-input flag for CI/CD
- **Acceptance Criteria:**
  - Config init prompts for API key, workspace
  - Create commands prompt for required fields
  - Multi-select for bulk operations (cycles, modules)
  - Cancelled operations exit gracefully

### FR-006: Output Formatting
- **Description:** Adapt output format based on context
- **Inputs:** Command flags (--json), terminal detection (isTTY)
- **Outputs:** JSON or formatted table
- **Constraints:** Piped output defaults to JSON; TTY defaults to table
- **Acceptance Criteria:**
  - Terminal shows colored tables with columns
  - Piped output is valid JSON
  - --json flag forces JSON output
  - --output pretty forces table output
  - Errors formatted consistently

### FR-007: Error Handling & Exit Codes
- **Description:** Communicate success/failure with appropriate exit codes
- **Inputs:** Operation outcome, error type
- **Outputs:** Error message, exit code
- **Constraints:** Exit codes: 0 (success), 1 (general), 2 (config), 3 (auth), 130 (cancel)
- **Acceptance Criteria:**
  - Success exits with 0
  - Config errors exit with 2
  - Auth errors exit with 3
  - General errors exit with 1
  - Ctrl+C exits with 130
  - Error messages are actionable

### FR-008: Destructive Operation Safety
- **Description:** Prevent accidental deletion/archiving
- **Inputs:** --confirm flag
- **Outputs:** Operation result or error
- **Constraints:** Delete and archive require --confirm flag
- **Acceptance Criteria:**
  - Delete without --confirm shows error
  - Delete with --confirm succeeds
  - Archive requires --confirm
  - Error message explains requirement

## Non-Functional Requirements Detail

### NFR-001: Performance
- **Requirement:** List operations complete within 2 seconds for workspaces <500 items
- **Measurement:** Command execution time (excluding network)
- **Success Metric:** p95 latency <2s
- **Future:** Cache results, implement pagination

### NFR-002: Compatibility
- **TypeScript CLI:** Node >=18.0.0, ES modules
- **Python Skill:** Python >=3.10, single dependency (plane-sdk)
- **OS:** Linux, macOS, Windows (via WSL or native Node)

### NFR-003: Maintainability
- **Code size:** Individual modules <300 LOC (commands <100 LOC)
- **Test coverage:** >70% for critical paths
- **Documentation:** All public APIs documented; README maintained
- **Conventions:** Consistent naming, error handling, file structure

### NFR-004: Security
- **Credential storage:** No hardcoding; env vars or secure file only
- **API communication:** HTTPS enforced
- **Data handling:** No unnecessary logging; clean error messages
- **Dependencies:** Minimal; audit regularly

### NFR-005: Usability
- **Discoverability:** --help works on all commands
- **Consistency:** Identical flags and behaviors across commands
- **Feedback:** Clear success/error messages; progress spinners for long ops
- **Accessibility:** JSON output for tooling; pretty output for humans

## Architecture Decisions

### Decision 1: Dual Implementation
- **Rationale:** Python legacy maintains backward compatibility while TypeScript CLI modernizes architecture
- **Trade-off:** Code duplication vs. smooth migration path
- **Timeline:** Deprecate Python scripts after TypeScript CLI matures

### Decision 2: oclif Framework (TypeScript)
- **Rationale:** Excellent CLI framework with built-in help, plugins, auto-documentation
- **Alternative:** Commander.js (simpler but less feature-rich)
- **Benefit:** Consistent plugin interface, auto-generated README

### Decision 3: Raw Fetch API Client (No SDK)
- **Rationale:** Eliminate SDK dependency; direct control over requests/responses; simpler troubleshooting
- **Alternative:** Use @makeplane/plane-node-sdk (TypeScript)
- **Trade-off:** More client code but better error handling, fewer surprises

### Decision 4: ~/.planerc Configuration (TypeScript)
- **Rationale:** User-level global config; standard JSON format; env var override for CI/CD
- **Alternative:** .plane.env (project-local) or YAML
- **Benefit:** Better multi-workspace support; secure permissions

### Decision 5: TTY-Aware Output
- **Rationale:** Pretty tables for humans, JSON for automation
- **Implementation:** `process.stdout.isTTY` detection
- **Benefit:** Better UX without breaking pipes/redirects

## Success Metrics

### Adoption
- [ ] npm package downloaded 100+ times/month
- [ ] Used in 10+ open-source projects
- [ ] GitHub issues resolved within 48 hours

### Quality
- [ ] 49 unit tests passing
- [ ] 8 E2E test files covering major workflows
- [ ] 0 unresolved security issues

### Performance
- [ ] List operations <2s (p95)
- [ ] Create operations <3s (p95)
- [ ] Memory usage <50MB per command

### User Satisfaction
- [ ] >4.0/5.0 rating on npm
- [ ] Clear documentation with examples
- [ ] Active maintenance (commits/month)

## Known Issues & Technical Debt

### Critical (P0)
1. **API Response Handling:** `api.ts` `request()` crashes on 204 No Content (DELETE ops)
   - **Impact:** Delete operations may fail
   - **Fix:** Check response status before calling `res.json()`

2. **Config Prompt Bug:** `config:init` accesses wrong prompt function
   - **Impact:** Access token setup fails
   - **Fix:** Call `promptAccessToken()` instead of `promptConfirm()`

### High Priority (P1)
3. **Cycle Command Flags:** Missing `...BaseCommand.baseFlags` spread
   - **Impact:** --no-input not parsed in cycle commands
   - **Fix:** Add spread to all cycle commands

4. **Issue Resolution Performance:** Fetches ALL issues to find by sequence_id
   - **Impact:** Slow on large projects (500+ issues)
   - **Fix:** Implement indexed lookup or API filter

5. **Code Duplication:** `stripHtml` function copied 3 times
   - **Impact:** Maintenance burden
   - **Fix:** Extract to shared utility

### Medium Priority (P2)
6. **Error Handling Inconsistency:** Mixed use of `process.exit()` and `this.error()`
   - **Impact:** Inconsistent behavior
   - **Fix:** Standardize on custom error classes

7. **Config Flag Conflicts:** `enableJsonFlag = true` conflicts with manual flags
   - **Impact:** Potential flag parsing issues
   - **Fix:** Review BaseCommand flag setup

## Roadmap

### Phase 1: Stabilization (Current)
- Fix critical bugs (API response, config prompts)
- Improve error handling consistency
- Expand test coverage to 80%
- **Timeline:** 2-4 weeks

### Phase 2: Performance
- Optimize issue resolver (add pagination/filtering)
- Implement caching for config
- Add progress indicators for batch ops
- **Timeline:** 4-6 weeks

### Phase 3: Extended Features
- Multi-profile support (for multiple workspaces)
- Bulk import/export (CSV to issues)
- Custom templates for issue creation
- Webhook integration for CI/CD
- **Timeline:** 6-10 weeks

### Phase 4: Migration & Deprecation
- Full feature parity with Python scripts
- Migrate all users to TypeScript CLI
- Remove Python scripts
- Archive legacy skill
- **Timeline:** 10-14 weeks

### Phase 5: Advanced (Future)
- AI-powered issue suggestions
- Integration with other tools (GitHub, Jira, etc.)
- Offline mode with sync
- Cloud-hosted command execution
- **Timeline:** TBD

## Dependencies

### TypeScript/Node
- `@oclif/core@4`: CLI framework
- `@inquirer/prompts@7`: Interactive prompts
- `chalk@5`: Colored output
- `cli-table3@0.6`: Table formatting
- `ora@8`: Spinners
- `zod@3`: Schema validation
- `mocha@11`, `chai@4`: Testing

### Python
- `plane-sdk@0.2.2`: Plane API SDK (sole dependency)
- `pytest@7`: Testing framework
- `python-dotenv@1`: .env file support

## Risk Assessment

### Technical Risks
1. **API breaking changes** — Plane API may change
   - **Mitigation:** Maintain version pins; monitor API docs; versioned releases

2. **Performance degradation** — Large workspaces may slow down
   - **Mitigation:** Implement pagination, caching, async operations

3. **Security vulnerabilities** — Dependencies may have CVEs
   - **Mitigation:** Audit regularly; minimal dependencies; security releases

### Operational Risks
1. **Maintenance burden** — Dual implementation doubles effort
   - **Mitigation:** Clear deprecation path; timeline for Python removal

2. **User confusion** — Two different CLIs may confuse users
   - **Mitigation:** Clear docs; deprecation notices; migration guide

### Market Risks
1. **Adoption** — Users may prefer Plane web UI
   - **Mitigation:** Focus on automation/scripting use cases; CI/CD integration

2. **Plane platform changes** — Licensing or feature changes
   - **Mitigation:** Open-source friendly; community-driven alternatives

## Compliance & Standards

- **License:** MIT (permissive, commercial-friendly)
- **Code style:** ESLint (TypeScript), black/flake8 (Python)
- **Documentation:** Markdown, inline comments, JSDoc/docstrings
- **Testing:** Unit + E2E coverage, no external API mocks required
- **Security:** No hardcoded credentials; env var + file-based config

## References

- **Plane Documentation:** https://docs.plane.so/
- **oclif Documentation:** https://oclif.io/
- **npm Package:** https://www.npmjs.com/package/plane-cli
- **GitHub Repository:** https://github.com/plane-so/plane-cli
- **Project Issues:** GitHub Issues for bugs/features

## Appendix: Command Matrix

| Resource | Commands |
|----------|----------|
| config | init, set, show |
| project | list, get, create, update, delete, members |
| issue | list, get, create, update, delete, search |
| cycle | list, get, create, update, delete, archive, unarchive, add-issues, remove-issue, transfer |
| module | list, get, create, update, delete, archive, unarchive, add-issues, remove-issue |
| label | list, get, create, update, delete |
| state | list, create, delete |
| page | get-workspace, get-project, create |
| initiative | list, create, delete |
| intake | list, create, delete |
| user | me |
| workspace | members |

**Total:** 53 commands across 11 resource groups

---

**Document Version:** 1.0
**Last Review:** 2026-03-03
**Next Review:** 2026-04-03
**Owner:** Development Team
