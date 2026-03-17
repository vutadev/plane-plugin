#!/usr/bin/env python3
"""Manage Plane milestones (requires plane-sdk >= 0.2.6).

Sub-commands:
    list           List milestones in a project
    create         Create a new milestone
    get            Get a milestone by ID
    update         Update a milestone
    delete         Delete a milestone (requires --confirm)
    add-items      Add work items to a milestone
    remove-items   Remove work items from a milestone
    list-items     List work items in a milestone
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
    response = client.milestones.list(slug, project_id)
    print_list_response(response)


def cmd_create(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.milestones import CreateMilestone

    fields: dict = {"name": args.name}
    if args.description:
        fields["description"] = args.description
    if args.start_date:
        fields["start_date"] = args.start_date
    if args.end_date:
        fields["end_date"] = args.end_date

    payload = CreateMilestone(**fields)
    milestone = client.milestones.create(slug, project_id, payload)
    print(dump_json(milestone.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    milestone = client.milestones.retrieve(slug, project_id, args.milestone_id)
    print(dump_json(milestone.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.milestones import UpdateMilestone

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.description is not None:
        fields["description"] = args.description
    if args.start_date:
        fields["start_date"] = args.start_date
    if args.end_date:
        fields["end_date"] = args.end_date

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateMilestone(**fields)
    milestone = client.milestones.update(slug, project_id, args.milestone_id, payload)
    print(dump_json(milestone.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    require_confirm(args)
    project_id = resolve_project_id(args)
    client, slug = get_client()
    client.milestones.delete(slug, project_id, args.milestone_id)
    print(dump_json({"status": "deleted", "milestone_id": args.milestone_id}))


def cmd_add_items(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    work_item_ids = [i.strip() for i in args.work_item_ids.split(",")]
    client.milestones.add_work_items(slug, project_id, args.milestone_id, work_item_ids)
    print(dump_json({"status": "added", "milestone_id": args.milestone_id, "work_item_ids": work_item_ids}))


def cmd_remove_items(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    work_item_ids = [i.strip() for i in args.work_item_ids.split(",")]
    client.milestones.remove_work_items(slug, project_id, args.milestone_id, work_item_ids)
    print(dump_json({"status": "removed", "milestone_id": args.milestone_id, "work_item_ids": work_item_ids}))


def cmd_list_items(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    response = client.milestones.list_work_items(slug, project_id, args.milestone_id)
    print_list_response(response)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane milestones",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List milestones")
    p_list.add_argument("--project-id", default=None, help="Project UUID")

    p_create = sub.add_parser("create", help="Create a milestone")
    p_create.add_argument("--project-id", default=None, help="Project UUID")
    p_create.add_argument("--name", required=True, help="Milestone name")
    p_create.add_argument("--description", help="Description")
    p_create.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    p_create.add_argument("--end-date", help="End date (YYYY-MM-DD)")

    p_get = sub.add_parser("get", help="Get milestone by ID")
    p_get.add_argument("--project-id", default=None, help="Project UUID")
    p_get.add_argument("--milestone-id", required=True, help="Milestone UUID")

    p_update = sub.add_parser("update", help="Update a milestone")
    p_update.add_argument("--project-id", default=None, help="Project UUID")
    p_update.add_argument("--milestone-id", required=True, help="Milestone UUID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--description", help="New description")
    p_update.add_argument("--start-date", help="New start date")
    p_update.add_argument("--end-date", help="New end date")

    p_delete = sub.add_parser("delete", help="Delete a milestone (requires --confirm)")
    p_delete.add_argument("--project-id", default=None, help="Project UUID")
    p_delete.add_argument("--milestone-id", required=True, help="Milestone UUID")
    p_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    p_add = sub.add_parser("add-items", help="Add work items to a milestone")
    p_add.add_argument("--project-id", default=None, help="Project UUID")
    p_add.add_argument("--milestone-id", required=True, help="Milestone UUID")
    p_add.add_argument("--work-item-ids", required=True, help="Comma-separated work item UUIDs")

    p_remove = sub.add_parser("remove-items", help="Remove work items from a milestone")
    p_remove.add_argument("--project-id", default=None, help="Project UUID")
    p_remove.add_argument("--milestone-id", required=True, help="Milestone UUID")
    p_remove.add_argument("--work-item-ids", required=True, help="Comma-separated work item UUIDs")

    p_list_items = sub.add_parser("list-items", help="List work items in a milestone")
    p_list_items.add_argument("--project-id", default=None, help="Project UUID")
    p_list_items.add_argument("--milestone-id", required=True, help="Milestone UUID")

    return parser


COMMANDS = {
    "list": cmd_list,
    "create": cmd_create,
    "get": cmd_get,
    "update": cmd_update,
    "delete": cmd_delete,
    "add-items": cmd_add_items,
    "remove-items": cmd_remove_items,
    "list-items": cmd_list_items,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_command(COMMANDS[args.command], args)


if __name__ == "__main__":
    main()
