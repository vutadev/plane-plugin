#!/usr/bin/env python3
"""Verify Plane connection by calling get_me() and listing projects.

Usage:
    python scripts/plane_verify.py
"""

from __future__ import annotations

import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json


def main() -> None:
    client, workspace_slug = get_client()

    print("Verifying Plane connection...\n")

    # 1. Verify auth — get current user
    try:
        user = client.users.get_me()
        user_info = user.model_dump() if hasattr(user, "model_dump") else str(user)
    except Exception as exc:
        print(f"ERROR: Failed to get current user: {exc}", file=sys.stderr)
        sys.exit(1)

    # 2. Verify workspace — list projects
    try:
        projects_response = client.projects.list(workspace_slug)
        project_count = projects_response.total_count if hasattr(projects_response, "total_count") else len(projects_response.results) if hasattr(projects_response, "results") else "unknown"
    except Exception as exc:
        print(f"ERROR: Failed to list projects: {exc}", file=sys.stderr)
        sys.exit(1)

    # 3. Print summary
    result = {
        "status": "connected",
        "workspace_slug": workspace_slug,
        "user": user_info,
        "project_count": project_count,
    }
    print(dump_json(result))


if __name__ == "__main__":
    main()
