#!/usr/bin/env python3
"""Manage Plane initiatives.

Sub-commands:
    list       List initiatives in the workspace
    create     Create a new initiative
    get        Get an initiative by ID
    update     Update an initiative
    delete     Delete an initiative (requires --confirm)
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json


def cmd_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.initiatives.list(slug)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def cmd_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.initiatives import CreateInitiative

    fields: dict = {"name": args.name}
    if args.description:
        fields["description"] = args.description

    payload = CreateInitiative(**fields)
    initiative = client.initiatives.create(slug, payload)
    print(dump_json(initiative.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    initiative = client.initiatives.retrieve(slug, args.initiative_id)
    print(dump_json(initiative.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.initiatives import UpdateInitiative

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.description is not None:
        fields["description"] = args.description

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateInitiative(**fields)
    initiative = client.initiatives.update(slug, args.initiative_id, payload)
    print(dump_json(initiative.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)
    client, slug = get_client()
    client.initiatives.delete(slug, args.initiative_id)
    print(dump_json({"status": "deleted", "initiative_id": args.initiative_id}))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane initiatives",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List initiatives")

    p_create = sub.add_parser("create", help="Create an initiative")
    p_create.add_argument("--name", required=True, help="Initiative name")
    p_create.add_argument("--description", help="Description")

    p_get = sub.add_parser("get", help="Get initiative by ID")
    p_get.add_argument("--initiative-id", required=True, help="Initiative UUID")

    p_update = sub.add_parser("update", help="Update an initiative")
    p_update.add_argument("--initiative-id", required=True, help="Initiative UUID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--description", help="New description")

    p_delete = sub.add_parser("delete", help="Delete an initiative (requires --confirm)")
    p_delete.add_argument("--initiative-id", required=True, help="Initiative UUID")
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
