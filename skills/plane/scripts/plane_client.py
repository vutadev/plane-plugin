#!/usr/bin/env python3
"""Shared helper for Plane SDK client initialization.

Reads configuration from .planerc JSON files and returns
a ready-to-use (PlaneClient, workspace_slug) tuple.

Config resolution:
    1) ~/.planerc (global config)
    2) CWD/.planerc (project-local override, field-level merge)

JSON schema (shared with TS CLI):
    {"apiKey": "...", "workspace": "...", "baseUrl": "..."}
    Optional: {"accessToken": "..."} (alternative to apiKey)
"""

from __future__ import annotations

import sys
import json
from pathlib import Path

from plane import PlaneClient


DEFAULT_BASE_URL = "https://api.plane.so"


def _load_planerc_config() -> dict:
    """Load config from ~/.planerc (global) merged with CWD/.planerc (local).

    Returns merged config dict. Project-local values override global.
    """
    config: dict = {}
    global_path = Path.home() / ".planerc"
    local_path = Path.cwd() / ".planerc"

    for path in [global_path, local_path]:
        if path.is_file():
            try:
                with open(path) as f:
                    data = json.load(f)
                config.update(data)
            except json.JSONDecodeError as exc:
                print(f"ERROR: Failed to parse {path}: {exc}", file=sys.stderr)
                sys.exit(1)
            except OSError as exc:
                print(f"ERROR: Cannot read {path}: {exc}", file=sys.stderr)
                sys.exit(1)

    return config


def get_client() -> tuple["PlaneClient", str]:
    """Create a PlaneClient from .planerc config files.

    Returns:
        (PlaneClient, workspace_slug) tuple

    Raises:
        SystemExit: if required config fields are missing.
    """
    config = _load_planerc_config()

    api_key = config.get("apiKey")
    access_token = config.get("accessToken")
    workspace = config.get("workspace")
    base_url = config.get("baseUrl", DEFAULT_BASE_URL)

    errors: list[str] = []

    if not api_key and not access_token:
        errors.append(
            "Either 'apiKey' or 'accessToken' must be set in .planerc."
        )

    if not workspace:
        errors.append("'workspace' must be set in .planerc.")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print(
            '\nCreate ~/.planerc or ./.planerc with: {"apiKey": "...", "workspace": "..."}',
            file=sys.stderr,
        )
        sys.exit(1)

    client = PlaneClient(
        base_url=base_url,
        api_key=api_key,
        access_token=access_token if not api_key else None,
    )

    return client, workspace  # type: ignore[return-value]


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
