#!/usr/bin/env python3
"""Manage Plane stickies.

Sub-commands:
    list       List stickies in the workspace
    create     Create a new sticky
    get        Get a sticky by ID
    update     Update a sticky
    delete     Delete a sticky (requires --confirm)
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json, print_list_response, require_confirm, run_command


def cmd_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.stickies.list(slug)
    print_list_response(response)


def cmd_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.stickies import CreateSticky

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.description:
        fields["description"] = args.description
    if args.color:
        fields["color"] = args.color

    payload = CreateSticky(**fields)
    sticky = client.stickies.create(slug, payload)
    print(dump_json(sticky.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    sticky = client.stickies.retrieve(slug, args.sticky_id)
    print(dump_json(sticky.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.stickies import UpdateSticky

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.description:
        fields["description"] = args.description
    if args.color:
        fields["color"] = args.color

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateSticky(**fields)
    sticky = client.stickies.update(slug, args.sticky_id, payload)
    print(dump_json(sticky.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    require_confirm(args)
    client, slug = get_client()
    client.stickies.delete(slug, args.sticky_id)
    print(dump_json({"status": "deleted", "sticky_id": args.sticky_id}))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane stickies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List stickies")

    p_create = sub.add_parser("create", help="Create a sticky")
    p_create.add_argument("--name", help="Sticky name")
    p_create.add_argument("--description", help="Sticky description")
    p_create.add_argument("--color", help="Sticky color")

    p_get = sub.add_parser("get", help="Get sticky by ID")
    p_get.add_argument("--sticky-id", required=True, help="Sticky UUID")

    p_update = sub.add_parser("update", help="Update a sticky")
    p_update.add_argument("--sticky-id", required=True, help="Sticky UUID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--description", help="New description")
    p_update.add_argument("--color", help="New color")

    p_delete = sub.add_parser("delete", help="Delete a sticky (requires --confirm)")
    p_delete.add_argument("--sticky-id", required=True, help="Sticky UUID")
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
    run_command(COMMANDS[args.command], args)


if __name__ == "__main__":
    main()
