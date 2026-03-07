# Plane Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `python: command not found` | No `python` binary | Use `python3` or `PYTHON=$(command -v python3)` |
| `ModuleNotFoundError: No module named 'plane'` | SDK not installed | `pip install -r requirements.txt` (or `pip3`, or `$PYTHON -m pip`) |
| `'api_key' or 'access_token' must be set in .planerc` | Missing auth in config | Create `~/.planerc` with `api_key=your-key` — get key from Plane → Settings → API Tokens |
| `'workspace_slug' must be set in .planerc` | Missing workspace in config | Add `workspace_slug=slug` to `.planerc` — find slug in your Plane URL |
| `Failed to get current user` / 401 | Invalid/expired token | Regenerate token in Plane → Settings → API Tokens |
| `Failed to list projects` / 404 | Wrong slug or base URL | Verify `workspace_slug` in `.planerc`; check `baseUrl` for self-hosted |
| `Failed to parse ~/.planerc` | Malformed JSON | Validate JSON syntax (check for trailing commas, missing quotes) |

## Auth Setup

```bash
# Recommended (interactive setup, prompts for global vs local):
bash scripts/plane_setup.sh

# Or create .planerc manually:
# Global config (all projects):
cat > ~/.planerc << 'EOF'
# Plane API Configuration
api_key=plane-api-key-here
workspace_slug=my-workspace
base_url=https://api.plane.so
EOF
chmod 600 ~/.planerc

# Or project-local config (overrides global):
cat > .planerc << 'EOF'
api_key=plane-api-key-here
workspace_slug=my-workspace
EOF
chmod 600 .planerc
```

- API key: Plane → Settings → API Tokens → Create new token
- Workspace slug: in your Plane URL `https://app.plane.so/<workspace-slug>/...`
- Config format: KEY=VALUE (like .envrc/.npmrc) with fields `api_key`, `workspace_slug`, `base_url` (optional `access_token` as alternative to `api_key`). JSON format also supported for TS CLI compatibility.

## Pre-flight Check

```bash
PYTHON=$(command -v python3 || command -v python)
$PYTHON -c "import plane" 2>/dev/null || pip install -r requirements.txt
$PYTHON scripts/plane_verify.py
```

If `plane_verify.py` fails → STOP. Fix config before running other commands.

## Logout / Credential Reset

```bash
bash scripts/plane_logout.sh --confirm
```

This removes both `~/.planerc` (global) and `./.planerc` (project-local). Note: removing global config affects all projects.
