#!/usr/bin/env python3
"""Manage Plane modules.

Sub-commands:
    list           List modules in a project
    create         Create a new module
    get            Get a module by ID
    update         Update a module
    delete         Delete a module (requires --confirm)
    archive        Archive a module
    unarchive      Unarchive a module
    add-items      Add work items to a module
    remove-item    Remove a work item from a module
    list-items     List work items in a module

Usage:
    python scripts/plane_modules.py list --project-id <uuid>
    python scripts/plane_modules.py create --project-id <uuid> --name "Auth Module"
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
    response = client.modules.list(slug, project_id)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def cmd_create(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.modules import CreateModule

    fields: dict = {"name": args.name}
    if args.description:
        fields["description"] = args.description
    if args.start_date:
        fields["start_date"] = args.start_date
    if args.target_date:
        fields["target_date"] = args.target_date

    payload = CreateModule(**fields)
    module = client.modules.create(slug, project_id, payload)
    print(dump_json(module.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    module = client.modules.retrieve(slug, project_id, args.module_id)
    print(dump_json(module.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.modules import UpdateModule

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.description is not None:
        fields["description"] = args.description
    if args.start_date:
        fields["start_date"] = args.start_date
    if args.target_date:
        fields["target_date"] = args.target_date

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateModule(**fields)
    module = client.modules.update(slug, project_id, args.module_id, payload)
    print(dump_json(module.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)
    project_id = resolve_project_id(args)
    client, slug = get_client()
    client.modules.delete(slug, project_id, args.module_id)
    print(dump_json({"status": "deleted", "module_id": args.module_id}))


def cmd_archive(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    client.modules.archive(slug, project_id, args.module_id)
    print(dump_json({"status": "archived", "module_id": args.module_id}))


def cmd_unarchive(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    client.modules.unarchive(slug, project_id, args.module_id)
    print(dump_json({"status": "unarchived", "module_id": args.module_id}))


def cmd_add_items(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    issue_ids = [i.strip() for i in args.issue_ids.split(",")]
    client.modules.add_work_items(slug, project_id, args.module_id, issue_ids)
    print(dump_json({"status": "added", "module_id": args.module_id, "issue_ids": issue_ids}))


def cmd_remove_item(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    client.modules.remove_work_item(slug, project_id, args.module_id, args.work_item_id)
    print(dump_json({"status": "removed", "module_id": args.module_id, "work_item_id": args.work_item_id}))


def cmd_list_items(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    response = client.modules.list_work_items(slug, project_id, args.module_id)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane modules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="List modules")
    p_list.add_argument("--project-id", default=None, help="Project UUID")

    # create
    p_create = sub.add_parser("create", help="Create a module")
    p_create.add_argument("--project-id", default=None, help="Project UUID")
    p_create.add_argument("--name", required=True, help="Module name")
    p_create.add_argument("--description", help="Description")
    p_create.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    p_create.add_argument("--target-date", help="Target date (YYYY-MM-DD)")

    # get
    p_get = sub.add_parser("get", help="Get module by ID")
    p_get.add_argument("--project-id", default=None, help="Project UUID")
    p_get.add_argument("--module-id", required=True, help="Module UUID")

    # update
    p_update = sub.add_parser("update", help="Update a module")
    p_update.add_argument("--project-id", default=None, help="Project UUID")
    p_update.add_argument("--module-id", required=True, help="Module UUID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--description", help="New description")
    p_update.add_argument("--start-date", help="New start date")
    p_update.add_argument("--target-date", help="New target date")

    # delete
    p_delete = sub.add_parser("delete", help="Delete a module (requires --confirm)")
    p_delete.add_argument("--project-id", default=None, help="Project UUID")
    p_delete.add_argument("--module-id", required=True, help="Module UUID")
    p_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # archive
    p_archive = sub.add_parser("archive", help="Archive a module")
    p_archive.add_argument("--project-id", default=None, help="Project UUID")
    p_archive.add_argument("--module-id", required=True, help="Module UUID")

    # unarchive
    p_unarchive = sub.add_parser("unarchive", help="Unarchive a module")
    p_unarchive.add_argument("--project-id", default=None, help="Project UUID")
    p_unarchive.add_argument("--module-id", required=True, help="Module UUID")

    # add-items
    p_add = sub.add_parser("add-items", help="Add work items to a module")
    p_add.add_argument("--project-id", default=None, help="Project UUID")
    p_add.add_argument("--module-id", required=True, help="Module UUID")
    p_add.add_argument("--issue-ids", required=True, help="Comma-separated work item UUIDs")

    # remove-item
    p_remove = sub.add_parser("remove-item", help="Remove a work item from a module")
    p_remove.add_argument("--project-id", default=None, help="Project UUID")
    p_remove.add_argument("--module-id", required=True, help="Module UUID")
    p_remove.add_argument("--work-item-id", required=True, help="Work item UUID")

    # list-items
    p_list_items = sub.add_parser("list-items", help="List work items in a module")
    p_list_items.add_argument("--project-id", default=None, help="Project UUID")
    p_list_items.add_argument("--module-id", required=True, help="Module UUID")

    return parser


COMMANDS = {
    "list": cmd_list,
    "create": cmd_create,
    "get": cmd_get,
    "update": cmd_update,
    "delete": cmd_delete,
    "archive": cmd_archive,
    "unarchive": cmd_unarchive,
    "add-items": cmd_add_items,
    "remove-item": cmd_remove_item,
    "list-items": cmd_list_items,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    COMMANDS[args.command](args)


if __name__ == "__main__":
    main()
