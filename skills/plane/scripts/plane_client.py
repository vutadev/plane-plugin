#!/usr/bin/env python3
"""Shared helper for Plane SDK client initialization.

Reads configuration from .planerc files and returns
a ready-to-use (PlaneClient, workspace_slug) tuple.

Config resolution:
    1) ~/.planerc (global config)
    2) CWD/.planerc (project-local override, field-level merge)

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


def _load_planerc_config() -> dict:
    """Load config from ~/.planerc (global) merged with CWD/.planerc (local).

    Returns merged config dict. Project-local values override global.
    Results are cached for the lifetime of the process.
    """
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    config: dict = {}
    global_path = Path.home() / ".planerc"
    local_path = Path.cwd() / ".planerc"

    # CLAUDE_PROJECT_DIR points to the actual project root when run as a skill
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    project_path = Path(project_dir) / ".planerc" if project_dir else None

    candidates = [global_path, local_path]
    if project_path and project_path != local_path:
        candidates.append(project_path)

    for path in candidates:
        if path.is_file():
            try:
                text = path.read_text()
            except OSError as exc:
                print(f"ERROR: Cannot read {path}: {exc}", file=sys.stderr)
                sys.exit(1)
            data = _parse_planerc(text, path)
            config.update(data)

    _CONFIG_CACHE = config
    return config


def get_client() -> tuple["PlaneClient", str]:
    """Create a PlaneClient from .planerc config files.

    Returns:
        (PlaneClient, workspace_slug) tuple

    Raises:
        SystemExit: if required config fields are missing.
    """
    config = _load_planerc_config()

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
    config = _load_planerc_config()
    pid = config.get("project_id") or config.get("default_project_id")
    if pid:
        return pid
    print(
        "ERROR: --project-id is required (no project_id in .planerc).",
        file=sys.stderr,
    )
    sys.exit(1)


def json_serial(obj: object) -> str:
    """JSON serializer for objects not serializable by default."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()  # type: ignore[return-value]
    if hasattr(obj, "__dict__"):
        return obj.__dict__  # type: ignore[return-value]
    return str(obj)


def dump_json(data: object) -> str:
    """Serialize data to a pretty-printed JSON string."""
    return json.dumps(data, indent=2, default=json_serial)


# ---------------------------------------------------------------------------
# Self-test mode: run `python scripts/plane_client.py` to verify config
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        client, slug = get_client()
        global_rc = Path.home() / ".planerc"
        local_rc = Path.cwd() / ".planerc"
        print(dump_json({
            "status": "ok",
            "workspace_slug": slug,
            "base_url": client.config.base_path,
            "auth_method": "api_key" if client.config.api_key else "access_token",
            "config_sources": {
                "global": str(global_rc) if global_rc.is_file() else None,
                "local": str(local_rc) if local_rc.is_file() else None,
            },
        }))
    except SystemExit:
        pass  # error already printed
