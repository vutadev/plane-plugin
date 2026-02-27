#!/usr/bin/env python3
"""Manage Plane labels.

Sub-commands:
    list       List labels in a project
    create     Create a new label
    get        Get a label by ID
    update     Update a label
    delete     Delete a label (requires --confirm)
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json


def cmd_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.labels.list(slug, args.project_id)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def cmd_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.labels import CreateLabel

    fields: dict = {"name": args.name}
    if args.color:
        fields["color"] = args.color

    payload = CreateLabel(**fields)
    label = client.labels.create(slug, args.project_id, payload)
    print(dump_json(label.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    label = client.labels.retrieve(slug, args.project_id, args.label_id)
    print(dump_json(label.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.labels import UpdateLabel

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.color:
        fields["color"] = args.color

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateLabel(**fields)
    label = client.labels.update(slug, args.project_id, args.label_id, payload)
    print(dump_json(label.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)
    client, slug = get_client()
    client.labels.delete(slug, args.project_id, args.label_id)
    print(dump_json({"status": "deleted", "label_id": args.label_id}))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane labels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List labels")
    p_list.add_argument("--project-id", required=True, help="Project UUID")

    p_create = sub.add_parser("create", help="Create a label")
    p_create.add_argument("--project-id", required=True, help="Project UUID")
    p_create.add_argument("--name", required=True, help="Label name")
    p_create.add_argument("--color", help="Label color (hex, e.g. #ff0000)")

    p_get = sub.add_parser("get", help="Get label by ID")
    p_get.add_argument("--project-id", required=True, help="Project UUID")
    p_get.add_argument("--label-id", required=True, help="Label UUID")

    p_update = sub.add_parser("update", help="Update a label")
    p_update.add_argument("--project-id", required=True, help="Project UUID")
    p_update.add_argument("--label-id", required=True, help="Label UUID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--color", help="New color")

    p_delete = sub.add_parser("delete", help="Delete a label (requires --confirm)")
    p_delete.add_argument("--project-id", required=True, help="Project UUID")
    p_delete.add_argument("--label-id", required=True, help="Label UUID")
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
