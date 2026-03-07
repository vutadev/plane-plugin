#!/usr/bin/env python3
"""Manage Plane states.

Sub-commands:
    list       List states in a project
    create     Create a new state
    get        Get a state by ID
    update     Update a state
    delete     Delete a state (requires --confirm)
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json, resolve_project_id


def cmd_list(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    response = client.states.list(slug, project_id)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def cmd_create(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.states import CreateState

    fields: dict = {"name": args.name}
    if args.color:
        fields["color"] = args.color
    if args.group:
        fields["group"] = args.group

    payload = CreateState(**fields)
    state = client.states.create(slug, project_id, payload)
    print(dump_json(state.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    state = client.states.retrieve(slug, project_id, args.state_id)
    print(dump_json(state.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.states import UpdateState

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.color:
        fields["color"] = args.color

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateState(**fields)
    state = client.states.update(slug, project_id, args.state_id, payload)
    print(dump_json(state.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)
    project_id = resolve_project_id(args)
    client, slug = get_client()
    client.states.delete(slug, project_id, args.state_id)
    print(dump_json({"status": "deleted", "state_id": args.state_id}))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane states",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List states")
    p_list.add_argument("--project-id", default=None, help="Project UUID")

    p_create = sub.add_parser("create", help="Create a state")
    p_create.add_argument("--project-id", default=None, help="Project UUID")
    p_create.add_argument("--name", required=True, help="State name")
    p_create.add_argument("--color", help="State color (hex)")
    p_create.add_argument("--group", help="State group (backlog, unstarted, started, completed, cancelled)")

    p_get = sub.add_parser("get", help="Get state by ID")
    p_get.add_argument("--project-id", default=None, help="Project UUID")
    p_get.add_argument("--state-id", required=True, help="State UUID")

    p_update = sub.add_parser("update", help="Update a state")
    p_update.add_argument("--project-id", default=None, help="Project UUID")
    p_update.add_argument("--state-id", required=True, help="State UUID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--color", help="New color")

    p_delete = sub.add_parser("delete", help="Delete a state (requires --confirm)")
    p_delete.add_argument("--project-id", default=None, help="Project UUID")
    p_delete.add_argument("--state-id", required=True, help="State UUID")
    p_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    return parser


COMMANDS = {
    "list": cmd_list,
    "create": cmd_create,
    "get": cmd_get,
    "update": cmd_update,
    "delete": cmd_delete,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    COMMANDS[args.command](args)


if __name__ == "__main__":
    main()
