#!/usr/bin/env python3
"""Shared helper for Plane SDK client initialization.

Reads configuration from environment variables and returns
a ready-to-use (PlaneClient, workspace_slug) tuple.

Environment variables:
    PLANE_API_KEY          – Plane API key (required unless PLANE_ACCESS_TOKEN is set)
    PLANE_ACCESS_TOKEN     – Plane personal access token (alternative to API key)
    PLANE_WORKSPACE_SLUG   – Workspace slug (required)
    PLANE_BASE_URL         – Base URL of the Plane API (default: https://api.plane.so/api/v1)

Optional env-file resolution controls:
    PLANE_ENV_FILE         – Explicit env file path (absolute, or relative to PROJECT_DIR/cwd)
    PROJECT_DIR            – Project root used for .plane.env lookup

Env-file lookup order:
    1) PLANE_ENV_FILE (if set)
    2) PROJECT_DIR/.plane.env (if PROJECT_DIR set)
    3) CWD/.plane.env
    4) Legacy skill-local file (skills/plane/.plane.env)
"""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path

from plane import PlaneClient


DEFAULT_BASE_URL = "https://api.plane.so/api/v1"


def _plane_env_candidates() -> list[Path]:
    """Return candidate .plane.env paths in resolution order."""
    candidates: list[Path] = []

    env_override = os.environ.get("PLANE_ENV_FILE")
    if env_override:
        override_path = Path(env_override).expanduser()
        if not override_path.is_absolute():
            base = Path(os.environ.get("PROJECT_DIR") or os.getcwd())
            override_path = base / override_path
        candidates.append(override_path)

    project_dir = os.environ.get("PROJECT_DIR")
    if project_dir:
        candidates.append(Path(project_dir).expanduser() / ".plane.env")

    candidates.append(Path.cwd() / ".plane.env")

    # Backward compatibility with old location
    candidates.append(Path(__file__).resolve().parent.parent / ".plane.env")

    # De-duplicate while preserving order
    deduped: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(path)
    return deduped


def _resolve_plane_env_file() -> Path | None:
    """Resolve the first existing .plane.env file."""
    for env_file in _plane_env_candidates():
        if env_file.exists():
            return env_file
    return None


def _load_plane_env() -> None:
    """Load .plane.env from resolved location if vars not already set."""
    env_file = _resolve_plane_env_file()
    if env_file is None:
        return

    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        # Don't override existing env vars
        if key and key not in os.environ:
            os.environ[key] = value


def get_client() -> tuple["PlaneClient", str]:
    """Create a PlaneClient from environment variables.

    Returns:
        (PlaneClient, workspace_slug) tuple

    Raises:
        SystemExit: if required env vars are missing.
    """
    _load_plane_env()
    api_key = os.environ.get("PLANE_API_KEY")
    access_token = os.environ.get("PLANE_ACCESS_TOKEN")
    workspace_slug = os.environ.get("PLANE_WORKSPACE_SLUG")
    base_url = os.environ.get("PLANE_BASE_URL", DEFAULT_BASE_URL)

    errors: list[str] = []

    if not api_key and not access_token:
        errors.append(
            "Either PLANE_API_KEY or PLANE_ACCESS_TOKEN must be set."
        )

    if not workspace_slug:
        errors.append("PLANE_WORKSPACE_SLUG must be set.")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print(
            "\nPlease set the required environment variables and try again.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = PlaneClient(
        base_url=base_url,
        api_key=api_key,
        access_token=access_token if not api_key else None,
    )

    return client, workspace_slug  # type: ignore[return-value]


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
        env_file = _resolve_plane_env_file()
        print(dump_json({
            "status": "ok",
            "workspace_slug": slug,
            "base_url": client.config.base_path,
            "auth_method": "api_key" if client.config.api_key else "access_token",
            "env_file": str(env_file) if env_file else None,
        }))
    except SystemExit:
        pass  # error already printed
