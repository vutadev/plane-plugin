#!/usr/bin/env python3
"""Manage Plane epics.

Sub-commands:
    list       List epics in a project
    get        Get an epic by ID
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json, resolve_project_id, print_list_response, require_confirm, run_command


def cmd_list(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    response = client.epics.list(slug, project_id)
    print_list_response(response)


def cmd_get(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    epic = client.epics.retrieve(slug, project_id, args.epic_id)
    print(dump_json(epic.model_dump()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane epics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List epics")
    p_list.add_argument("--project-id", default=None, help="Project UUID")

    p_get = sub.add_parser("get", help="Get epic by ID")
    p_get.add_argument("--project-id", default=None, help="Project UUID")
    p_get.add_argument("--epic-id", required=True, help="Epic UUID")

    return parser


COMMANDS = {
    "list": cmd_list,
    "get": cmd_get,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_command(COMMANDS[args.command], args)


if __name__ == "__main__":
    main()
