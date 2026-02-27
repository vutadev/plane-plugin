# Brainstorm: Agent Skill for Plane Project Management

**Task**: Based on the [Plane MCP Server](https://github.com/makeplane/plane-mcp-server) repo, create an agent skill to adapt this feature and platform.

---

## Goal

Create an **agent skill** that enables AI agents to interact with [Plane](https://plane.so) — an open-source project management platform — using the capabilities exposed by the Plane MCP Server. The skill should provide structured guidance, tool definitions, and workflow patterns for managing projects, work items, cycles, modules, initiatives, and more via the Plane API.

---

## Constraints

1. **Auth requirements**: Plane requires either an API key + workspace slug (stdio), OAuth2 (remote HTTP), or PAT token (header HTTP). The skill must handle secret management safely.
2. **Workspace-scoped**: All operations are scoped to a single workspace slug. Multi-workspace scenarios add complexity.
3. **55+ tools across 18 modules**: The API surface is large (projects, work items, cycles, modules, initiatives, intake, labels, pages, states, users, workspaces, work logs, work item activities / comments / links / relations / properties / types). The skill must organize these coherently — not dump all 55+ tools without guidance.
4. **Python + plane-sdk dependency**: The MCP server uses `fastmcp` + `plane-sdk`. The skill should either depend on the MCP server directly or wrap the Plane REST API.
5. **Skill format**: Must follow the existing SKILL.md pattern (YAML frontmatter + markdown instructions) used by the superpowers skill ecosystem.
6. **No hardcoded secrets**: Must use env vars or a secret manager.

---

## Known Context

| Aspect | Detail |
|--------|--------|
| **Repo** | `makeplane/plane-mcp-server` (MIT license) |
| **Tech** | Python >=3.10, `fastmcp==2.14.1`, `plane-sdk==0.2.2` |
| **Transports** | stdio, SSE (deprecated), streamable HTTP |
| **Auth** | API key (`PLANE_API_KEY`), OAuth2, PAT (`PLANE_ACCESS_TOKEN`) |
| **Tool categories** | Projects (9), Work Items (7), Cycles (12), Modules (11), Initiatives (5), Intake (5), Labels, Pages, States, Users, Workspaces, Work Logs, Work Item Activities/Comments/Links/Relations/Properties/Types |
| **Key models** | `plane.models.*` — Pydantic models for type safety |
| **Existing skills** | `superpowers-rest-automation` (REST API design), `superpowers-plan` (planning) |

---

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Scope creep**: 55+ tools -> bloated skill | High | Group tools into logical workflows; start with core subset (Projects, Work Items, Cycles) |
| **Auth complexity**: 3 auth mechanisms | Medium | Default to API key (simplest); document all 3 as options |
| **Breaking changes**: `plane-sdk` and MCP protocol evolve fast | Medium | Pin versions; document upgrade path |
| **Data loss via destructive ops**: `delete_project`, `delete_work_item`, etc. | High | Mandate dry-run confirmation for destructive operations in the skill instructions |
| **Rate limiting**: Plane API may throttle | Low | Skill should include retry/backoff guidance (extend superpowers-rest-automation) |
| **Workspace config errors**: Wrong slug -> silent 404s | Medium | Skill should include a "verify connection" step |

---

## Options (3)

### Option A: MCP Client Skill (Connect to Plane MCP Server)

Create a skill that instructs the agent to **connect to the Plane MCP Server as an MCP client** (via stdio or remote HTTP), and then use the 55+ tools it exposes.

**Pros:**
- Directly leverages the official MCP server — no reinvention
- Gets all 55+ tools for free, with Pydantic validation
- Automatic updates when the server updates

**Cons:**
- Requires Python + `uvx`/`pip` installed and the MCP server running
- Tight coupling to MCP protocol — less portable
- Agent needs MCP client capabilities

### Option B: REST API Wrapper Skill (Direct HTTP calls)

Create a skill that instructs the agent to **call the Plane REST API directly** using HTTP requests (curl / fetch / requests), without depending on the MCP server.

**Pros:**
- No Python/MCP dependency — works with any agent that can make HTTP calls
- Simpler setup (just API key + base URL)
- Full control over retry/pagination logic

**Cons:**
- Must manually define all API endpoints and models
- No Pydantic validation
- Must maintain parity with Plane API changes manually

### Option C: Hybrid Skill (Markdown instructions + helper scripts)

Create a **SKILL.md** with structured guidance (checklists, workflow patterns, best practices) plus **helper scripts** (Python or shell) that wrap the most common Plane operations. The skill guides the agent *how* to use Plane, while scripts handle the heavy lifting.

**Pros:**
- Best of both worlds: structured guidance + executable helpers
- Scripts can be thin wrappers around `plane-sdk` or raw REST
- Follows the existing superpowers skill pattern
- Easy to extend incrementally

**Cons:**
- Some upfront work to create scripts
- Two maintenance surfaces (docs + scripts)

---

## Recommendation

**Option C — Hybrid Skill** is the strongest choice.

Rationale:
1. **Follows existing conventions**: Matches the superpowers skill ecosystem (`SKILL.md` + `scripts/`).
2. **Incremental delivery**: Start with SKILL.md covering core workflows (Projects, Work Items, Cycles), then add helper scripts as needed.
3. **Flexible auth**: Scripts can read from env vars and support all 3 auth mechanisms.
4. **Safety by design**: SKILL.md can enforce dry-run gates for destructive ops, verification steps, and checklist-driven workflows.
5. **Portable**: The markdown guidance works with any agent; scripts are optional accelerators.

### Recommended structure:

```
plane-skill/
├── SKILL.md                          # Main skill instructions
├── scripts/
│   ├── plane_auth.py                 # Auth helper (env var -> client)
│   ├── plane_projects.py             # Project CRUD operations
│   ├── plane_work_items.py           # Work item CRUD + search
│   ├── plane_cycles.py               # Cycle management
│   ├── plane_modules.py              # Module management
│   └── plane_verify_connection.py    # Connection health check
├── examples/
│   ├── create_project_workflow.md    # Example: create a project end-to-end
│   ├── sprint_planning.md           # Example: sprint/cycle planning workflow
│   └── intake_triage.md             # Example: triage intake items
└── resources/
    └── plane_api_reference.md        # Quick-reference for Plane API
```

---

## Acceptance Criteria

1. **SKILL.md exists** at `plane-skill/SKILL.md` with valid YAML frontmatter (`name`, `description`)
2. **Core workflows documented**: Projects, Work Items, Cycles — each with step-by-step instructions
3. **Auth setup**: Clear instructions for configuring `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`, `PLANE_BASE_URL`
4. **Connection verification**: A script or checklist step to verify the Plane connection works
5. **Safety controls**: Destructive operations (delete, archive) require explicit confirmation
6. **Helper scripts**: At least `plane_verify_connection.py` and one CRUD script work end-to-end
7. **Examples**: At least one complete workflow example (e.g., "Create a project and first work item")
8. **No hardcoded secrets**: All secrets via env vars
9. **Tests**: At least smoke tests for helper scripts
10. **Follows superpowers conventions**: Same SKILL.md structure as existing skills
