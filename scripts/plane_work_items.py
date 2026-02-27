#!/usr/bin/env python3
"""Manage Plane work items (issues).

Sub-commands:
    list       List work items in a project
    create     Create a new work item
    get        Get a work item by UUID
    get-by-id  Get a work item by project identifier + sequence number
    update     Update a work item
    delete     Delete a work item (requires --confirm)
    search     Search work items across the workspace

Usage:
    python scripts/plane_work_items.py list --project-id <uuid>
    python scripts/plane_work_items.py create --project-id <uuid> --name "Fix bug"
    python scripts/plane_work_items.py get --project-id <uuid> --work-item-id <uuid>
    python scripts/plane_work_items.py get-by-id --project-identifier "MP" --sequence 42
    python scripts/plane_work_items.py search --query "login bug"
    python scripts/plane_work_items.py delete --project-id <uuid> --work-item-id <uuid> --confirm
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json


def cmd_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.work_items.list(slug, args.project_id)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def cmd_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.work_items import CreateWorkItem

    fields: dict = {"name": args.name}
    if args.description:
        fields["description_html"] = args.description
    if args.priority:
        fields["priority"] = args.priority
    if args.state_id:
        fields["state"] = args.state_id
    if args.assignees:
        fields["assignees"] = args.assignees.split(",")

    payload = CreateWorkItem(**fields)
    work_item = client.work_items.create(slug, args.project_id, payload)
    print(dump_json(work_item.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    work_item = client.work_items.retrieve(slug, args.project_id, args.work_item_id)
    print(dump_json(work_item.model_dump()))


def cmd_get_by_id(args: argparse.Namespace) -> None:
    client, slug = get_client()
    work_item = client.work_items.retrieve_by_identifier(
        slug, args.project_identifier, int(args.sequence)
    )
    print(dump_json(work_item.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.work_items import UpdateWorkItem

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.description:
        fields["description_html"] = args.description
    if args.priority:
        fields["priority"] = args.priority
    if args.state_id:
        fields["state"] = args.state_id

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateWorkItem(**fields)
    work_item = client.work_items.update(
        slug, args.project_id, args.work_item_id, payload
    )
    print(dump_json(work_item.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        print(
            "ERROR: Destructive operation — pass --confirm to proceed.",
            file=sys.stderr,
        )
        sys.exit(1)
    client, slug = get_client()
    client.work_items.delete(slug, args.project_id, args.work_item_id)
    print(dump_json({"status": "deleted", "work_item_id": args.work_item_id}))


def cmd_search(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.work_items.search(slug, args.query)
    print(dump_json(response.model_dump() if hasattr(response, "model_dump") else response))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane work items",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="List work items in a project")
    p_list.add_argument("--project-id", required=True, help="Project UUID")

    # create
    p_create = sub.add_parser("create", help="Create a new work item")
    p_create.add_argument("--project-id", required=True, help="Project UUID")
    p_create.add_argument("--name", required=True, help="Work item name")
    p_create.add_argument("--description", help="Description (HTML)")
    p_create.add_argument("--priority", help="Priority: urgent|high|medium|low|none")
    p_create.add_argument("--state-id", help="State UUID")
    p_create.add_argument("--assignees", help="Comma-separated assignee UUIDs")

    # get
    p_get = sub.add_parser("get", help="Get work item by UUID")
    p_get.add_argument("--project-id", required=True, help="Project UUID")
    p_get.add_argument("--work-item-id", required=True, help="Work item UUID")

    # get-by-id
    p_get_by_id = sub.add_parser("get-by-id", help="Get work item by identifier")
    p_get_by_id.add_argument("--project-identifier", required=True, help="Project identifier (e.g. MP)")
    p_get_by_id.add_argument("--sequence", required=True, help="Issue sequence number")

    # update
    p_update = sub.add_parser("update", help="Update a work item")
    p_update.add_argument("--project-id", required=True, help="Project UUID")
    p_update.add_argument("--work-item-id", required=True, help="Work item UUID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--description", help="New description (HTML)")
    p_update.add_argument("--priority", help="New priority")
    p_update.add_argument("--state-id", help="New state UUID")

    # delete
    p_delete = sub.add_parser("delete", help="Delete a work item (requires --confirm)")
    p_delete.add_argument("--project-id", required=True, help="Project UUID")
    p_delete.add_argument("--work-item-id", required=True, help="Work item UUID")
    p_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # search
    p_search = sub.add_parser("search", help="Search work items")
    p_search.add_argument("--query", required=True, help="Search query")

    return parser


COMMANDS = {
    "list": cmd_list,
    "create": cmd_create,
    "get": cmd_get,
    "get-by-id": cmd_get_by_id,
    "update": cmd_update,
    "delete": cmd_delete,
    "search": cmd_search,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    COMMANDS[args.command](args)


if __name__ == "__main__":
    main()
