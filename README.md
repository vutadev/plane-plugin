# Plane Agent Skill

An agent skill for interacting with [Plane](https://plane.so) — an open-source project management platform — via the `plane-sdk` Python library.

## Prerequisites

- Python ≥ 3.10
- A Plane instance (cloud or self-hosted)
- API key or access token

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set environment variables:

```bash
export PLANE_API_KEY="your-api-key"
export PLANE_WORKSPACE_SLUG="your-workspace-slug"
# Optional — defaults to https://api.plane.so
export PLANE_BASE_URL="https://your-plane-instance.com/api/v1"
```

3. Verify the connection:

```bash
python scripts/plane_verify.py
```

## Usage

Each script is a standalone CLI tool with sub-commands:

```bash
# Projects
python scripts/plane_projects.py list
python scripts/plane_projects.py create --name "My Project" --identifier "MP"

# Work Items
python scripts/plane_work_items.py list --project-id <uuid>
python scripts/plane_work_items.py create --project-id <uuid> --name "Fix bug"

# Cycles
python scripts/plane_cycles.py list --project-id <uuid>

# Modules
python scripts/plane_modules.py list --project-id <uuid>
```

All scripts output JSON and accept `--help` for full usage info.

## Directory Structure

```
plane-skill/
├── SKILL.md                  # Agent skill instructions
├── scripts/                  # CLI helper scripts
│   ├── plane_client.py       # Shared auth/client helper
│   ├── plane_verify.py       # Connection verification
│   ├── plane_projects.py     # Project management
│   ├── plane_work_items.py   # Work item management
│   ├── plane_cycles.py       # Cycle management
│   ├── plane_modules.py      # Module management
│   └── ...                   # Extended scripts
├── examples/                 # Workflow examples
├── resources/                # Quick-reference docs
└── tests/                    # Smoke tests
```

## License

MIT
