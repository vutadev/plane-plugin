# Plane Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `python: command not found` | No `python` binary | Use `python3` or `PYTHON=$(command -v python3)` |
| `ModuleNotFoundError: No module named 'plane'` | SDK not installed | `pip install -r requirements.txt` (or `pip3`, or `$PYTHON -m pip`) |
| `PLANE_API_KEY or PLANE_ACCESS_TOKEN must be set` | Missing auth var | `export PLANE_API_KEY="your-key"` — get from Plane → Settings → API Tokens |
| `PLANE_WORKSPACE_SLUG must be set` | Missing workspace var | `export PLANE_WORKSPACE_SLUG="slug"` — find in your Plane URL |
| `Failed to get current user` / 401 | Invalid/expired token | Regenerate token in Plane → Settings → API Tokens |
| `Failed to list projects` / 404 | Wrong slug or base URL | Verify `PLANE_WORKSPACE_SLUG`; check `PLANE_BASE_URL` for self-hosted |

## Auth Setup

```bash
export PLANE_API_KEY="plane-api-key-here"        # OR
export PLANE_ACCESS_TOKEN="plane-pat-here"
export PLANE_WORKSPACE_SLUG="my-workspace"
export PLANE_BASE_URL="https://your-instance.com/api/v1"  # only for self-hosted
```

- API key: Plane → Settings → API Tokens → Create new token
- Workspace slug: in your Plane URL `https://app.plane.so/<workspace-slug>/...`

## Pre-flight Check

```bash
PYTHON=$(command -v python3 || command -v python)
$PYTHON -c "import plane" 2>/dev/null || pip install -r requirements.txt
$PYTHON scripts/plane_verify.py
```

If `plane_verify.py` fails → STOP. Fix auth before running other commands.
