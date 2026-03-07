#!/usr/bin/env python3
"""Manage Plane intake (triage) work items.

Sub-commands:
    list       List intake work items in a project
    create     Create a new intake work item
    get        Get an intake work item
    update     Update an intake work item
    delete     Delete an intake work item (requires --confirm)
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
    response = client.intake.list(slug, project_id)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def cmd_create(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.intake import CreateIntakeWorkItem

    fields: dict = {"name": args.name}
    if args.description:
        fields["description_html"] = args.description

    payload = CreateIntakeWorkItem(**fields)
    item = client.intake.create(slug, project_id, payload)
    print(dump_json(item.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    item = client.intake.retrieve(slug, project_id, args.work_item_id)
    print(dump_json(item.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.intake import UpdateIntakeWorkItem

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.status:
        fields["status"] = int(args.status)

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateIntakeWorkItem(**fields)
    item = client.intake.update(slug, project_id, args.work_item_id, payload)
    print(dump_json(item.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)
    project_id = resolve_project_id(args)
    client, slug = get_client()
    client.intake.delete(slug, project_id, args.work_item_id)
    print(dump_json({"status": "deleted", "work_item_id": args.work_item_id}))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane intake work items",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List intake work items")
    p_list.add_argument("--project-id", default=None, help="Project UUID")

    p_create = sub.add_parser("create", help="Create an intake work item")
    p_create.add_argument("--project-id", default=None, help="Project UUID")
    p_create.add_argument("--name", required=True, help="Work item name")
    p_create.add_argument("--description", help="Description (HTML)")

    p_get = sub.add_parser("get", help="Get intake work item")
    p_get.add_argument("--project-id", default=None, help="Project UUID")
    p_get.add_argument("--work-item-id", required=True, help="Work item UUID")

    p_update = sub.add_parser("update", help="Update an intake work item")
    p_update.add_argument("--project-id", default=None, help="Project UUID")
    p_update.add_argument("--work-item-id", required=True, help="Work item UUID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--status", help="New status (integer)")

    p_delete = sub.add_parser("delete", help="Delete an intake work item (requires --confirm)")
    p_delete.add_argument("--project-id", default=None, help="Project UUID")
    p_delete.add_argument("--work-item-id", required=True, help="Work item UUID")
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
