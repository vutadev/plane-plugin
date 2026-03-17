#!/usr/bin/env python3
"""Shared helper for Plane SDK client initialization.

Reads configuration from .planerc files and returns
a ready-to-use (PlaneClient, workspace_slug) tuple.

Config resolution:
    1) ~/.planerc (global config)
    2) $PWD/.planerc (project-local override, field-level merge)

Supported formats (auto-detected):
    KEY=VALUE (like .envrc/.npmrc):
        api_key=plane_api_xxx
        workspace_slug=my-workspace
        base_url=https://api.plane.so

    JSON (compatible with TS CLI):
        {"api_key": "...", "workspace_slug": "...", "base_url": "..."}
"""

from __future__ import annotations

import argparse
import os
import sys
import json
from pathlib import Path

from plane import PlaneClient


DEFAULT_BASE_URL = "https://api.plane.so"

_CONFIG_CACHE: dict | None = None


def _reset_config_cache() -> None:
    """Clear the config cache, forcing re-parse on next call."""
    global _CONFIG_CACHE
    _CONFIG_CACHE = None


def _parse_planerc(text: str, path: Path) -> dict:
    """Parse a .planerc file, auto-detecting JSON vs KEY=VALUE format."""
    stripped = text.strip()
    if not stripped:
        return {}

    # Auto-detect: if it starts with '{', parse as JSON
    if stripped.startswith("{"):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError as exc:
            print(f"ERROR: Failed to parse {path} as JSON: {exc}", file=sys.stderr)
            sys.exit(1)

    # Otherwise parse as KEY=VALUE
    config: dict = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            print(f"ERROR: Invalid line in {path}:{lineno}: {line!r}", file=sys.stderr)
            sys.exit(1)
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key:
            config[key] = value
    return config


def _resolve_project_dir() -> Path:
    """Resolve the project root directory.

    Fallback chain:
        1. $PLANE_PROJECT_DIR  (explicit, agent-agnostic)
        2. $CLAUDE_PROJECT_DIR (Claude Code specific)
        3. git rev-parse --show-toplevel (any git project)
        4. $PWD (last resort)
    """
    for env_var in ("PLANE_PROJECT_DIR", "CLAUDE_PROJECT_DIR"):
        val = os.environ.get(env_var)
        if val:
            return Path(val)

    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return Path.cwd()


def load_planerc_config() -> dict:
    """Load config from project .planerc (local) or ~/.planerc (global).

    If a local .planerc exists, it is used exclusively (global is ignored).
    If no local .planerc exists, the global ~/.planerc is used.
    This prevents mixing credentials from different scopes.

    Project dir resolution: $PLANE_PROJECT_DIR > $CLAUDE_PROJECT_DIR > git root > $PWD.
    Results are cached for the lifetime of the process.
    """
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    global_path = Path.home() / ".planerc"
    project_path = _resolve_project_dir() / ".planerc"

    chosen = project_path if project_path.is_file() else global_path
    config: dict = {}
    if chosen.is_file():
        try:
            text = chosen.read_text()
        except OSError as exc:
            print(f"ERROR: Cannot read {chosen}: {exc}", file=sys.stderr)
            sys.exit(1)
        config = _parse_planerc(text, chosen)

    _CONFIG_CACHE = config
    return config


def get_client() -> tuple["PlaneClient", str]:
    """Create a PlaneClient from .planerc config files.

    Returns:
        (PlaneClient, workspace_slug) tuple

    Raises:
        SystemExit: if required config fields are missing.
    """
    config = load_planerc_config()

    api_key = config.get("api_key")
    access_token = config.get("access_token")
    workspace = config.get("workspace_slug") or config.get("workspace")
    base_url = config.get("base_url", DEFAULT_BASE_URL)

    errors: list[str] = []

    if not api_key and not access_token:
        errors.append(
            "Either 'api_key' or 'access_token' must be set in .planerc."
        )

    if not workspace:
        errors.append("'workspace_slug' (or 'workspace') must be set in .planerc.")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print(
            "\nCreate ~/.planerc or ./.planerc with:",
            file=sys.stderr,
        )
        print(
            "  api_key=your-api-key\n  workspace_slug=your-workspace",
            file=sys.stderr,
        )
        sys.exit(1)

    client = PlaneClient(
        base_url=base_url,
        api_key=api_key,
        access_token=access_token if not api_key else None,
    )

    return client, workspace  # type: ignore[return-value]


def resolve_project_id(args: argparse.Namespace) -> str:
    """Resolve project ID from CLI arg or config default.

    Priority: explicit --project-id > project_id in .planerc > default_project_id (legacy) > error.
    """
    pid = getattr(args, "project_id", None)
    if pid:
        return pid
    config = load_planerc_config()
    pid = config.get("project_id") or config.get("default_project_id")
    if pid:
        return pid
    print(
        "ERROR: --project-id is required (no project_id in .planerc).",
        file=sys.stderr,
    )
    sys.exit(1)


def parse_identifier(identifier: str) -> tuple[str, int]:
    """Parse 'PROJECT-123' into ('PROJECT', 123). Splits on last '-'."""
    sep_index = identifier.rfind("-")
    if sep_index <= 0:
        print(
            f"ERROR: Invalid identifier format '{identifier}'. Expected 'PROJECT-123'.",
            file=sys.stderr,
        )
        sys.exit(1)
    project_part = identifier[:sep_index]
    try:
        sequence = int(identifier[sep_index + 1 :])
    except ValueError:
        print(
            f"ERROR: Invalid sequence number in '{identifier}'. Expected 'PROJECT-123'.",
            file=sys.stderr,
        )
        sys.exit(1)
    return project_part, sequence


def json_serial(obj: object) -> object:
    """JSON serializer for objects not serializable by default."""
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


def dump_json(data: object) -> str:
    """Serialize data to a pretty-printed JSON string."""
    return json.dumps(data, indent=2, default=json_serial)


def print_list_response(response: object) -> None:
    """Extract results from a paginated response and print as JSON."""
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def require_confirm(args: argparse.Namespace) -> None:
    """Exit with error if --confirm was not passed."""
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)


def run_command(handler: callable, args: argparse.Namespace) -> None:
    """Run a command handler with top-level exception handling."""
    try:
        handler(args)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Self-test mode: run `python scripts/plane_client.py` to verify config
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        client, slug = get_client()
        global_rc = Path.home() / ".planerc"
        project_rc = Path.cwd() / ".planerc"
        print(dump_json({
            "status": "ok",
            "workspace_slug": slug,
            "base_url": client.config.base_path,
            "auth_method": "api_key" if client.config.api_key else "access_token",
            "config_sources": {
                "global": str(global_rc) if global_rc.is_file() else None,
                "project": str(project_rc) if project_rc.is_file() else None,
            },
        }))
    except SystemExit:
        pass  # error already printed
