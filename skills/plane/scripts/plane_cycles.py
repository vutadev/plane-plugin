#!/usr/bin/env python3
"""Manage Plane cycles.

Sub-commands:
    list           List cycles in a project
    create         Create a new cycle
    get            Get a cycle by ID
    update         Update a cycle
    delete         Delete a cycle (requires --confirm)
    archive        Archive a cycle
    unarchive      Unarchive a cycle
    add-items      Add work items to a cycle
    remove-item    Remove a work item from a cycle
    list-items     List work items in a cycle
    transfer-items Transfer work items to another cycle

Usage:
    python scripts/plane_cycles.py list --project-id <uuid>
    python scripts/plane_cycles.py create --project-id <uuid> --name "Sprint 1"
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
    response = client.cycles.list(slug, project_id)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def cmd_create(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.cycles import CreateCycle

    fields: dict = {"name": args.name}
    if args.description:
        fields["description"] = args.description
    if args.start_date:
        fields["start_date"] = args.start_date
    if args.end_date:
        fields["end_date"] = args.end_date

    payload = CreateCycle(**fields)
    cycle = client.cycles.create(slug, project_id, payload)
    print(dump_json(cycle.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    cycle = client.cycles.retrieve(slug, project_id, args.cycle_id)
    print(dump_json(cycle.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.cycles import UpdateCycle

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

    payload = UpdateCycle(**fields)
    cycle = client.cycles.update(slug, project_id, args.cycle_id, payload)
    print(dump_json(cycle.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)
    client, slug = get_client()
    client.cycles.delete(slug, project_id, args.cycle_id)
    print(dump_json({"status": "deleted", "cycle_id": args.cycle_id}))


def cmd_archive(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    client.cycles.archive(slug, project_id, args.cycle_id)
    print(dump_json({"status": "archived", "cycle_id": args.cycle_id}))


def cmd_unarchive(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    client.cycles.unarchive(slug, project_id, args.cycle_id)
    print(dump_json({"status": "unarchived", "cycle_id": args.cycle_id}))


def cmd_add_items(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    work_item_ids = [i.strip() for i in args.work_item_ids.split(",")]
    client.cycles.add_work_items(slug, project_id, args.cycle_id, work_item_ids)
    print(dump_json({"status": "added", "cycle_id": args.cycle_id, "work_item_ids": work_item_ids}))


def cmd_remove_item(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    client.cycles.remove_work_item(slug, project_id, args.cycle_id, args.work_item_id)
    print(dump_json({"status": "removed", "cycle_id": args.cycle_id, "work_item_id": args.work_item_id}))


def cmd_list_items(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    response = client.cycles.list_work_items(slug, project_id, args.cycle_id)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def cmd_transfer_items(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.cycles import TransferCycleWorkItemsRequest

    payload = TransferCycleWorkItemsRequest(new_cycle_id=args.target_cycle_id)
    client.cycles.transfer_work_items(slug, project_id, args.cycle_id, payload)
    print(dump_json({
        "status": "transferred",
        "source_cycle_id": args.cycle_id,
        "target_cycle_id": args.target_cycle_id,
    }))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane cycles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="List cycles")
    p_list.add_argument("--project-id", default=None, help="Project UUID")

    # create
    p_create = sub.add_parser("create", help="Create a cycle")
    p_create.add_argument("--project-id", default=None, help="Project UUID")
    p_create.add_argument("--name", required=True, help="Cycle name")
    p_create.add_argument("--description", help="Description")
    p_create.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    p_create.add_argument("--end-date", help="End date (YYYY-MM-DD)")

    # get
    p_get = sub.add_parser("get", help="Get cycle by ID")
    p_get.add_argument("--project-id", default=None, help="Project UUID")
    p_get.add_argument("--cycle-id", required=True, help="Cycle UUID")

    # update
    p_update = sub.add_parser("update", help="Update a cycle")
    p_update.add_argument("--project-id", default=None, help="Project UUID")
    p_update.add_argument("--cycle-id", required=True, help="Cycle UUID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--description", help="New description")
    p_update.add_argument("--start-date", help="New start date")
    p_update.add_argument("--end-date", help="New end date")

    # delete
    p_delete = sub.add_parser("delete", help="Delete a cycle (requires --confirm)")
    p_delete.add_argument("--project-id", default=None, help="Project UUID")
    p_delete.add_argument("--cycle-id", required=True, help="Cycle UUID")
    p_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # archive
    p_archive = sub.add_parser("archive", help="Archive a cycle")
    p_archive.add_argument("--project-id", default=None, help="Project UUID")
    p_archive.add_argument("--cycle-id", required=True, help="Cycle UUID")

    # unarchive
    p_unarchive = sub.add_parser("unarchive", help="Unarchive a cycle")
    p_unarchive.add_argument("--project-id", default=None, help="Project UUID")
    p_unarchive.add_argument("--cycle-id", required=True, help="Cycle UUID")

    # add-items
    p_add = sub.add_parser("add-items", help="Add work items to a cycle")
    p_add.add_argument("--project-id", default=None, help="Project UUID")
    p_add.add_argument("--cycle-id", required=True, help="Cycle UUID")
    p_add.add_argument("--work-item-ids", required=True, help="Comma-separated work item UUIDs")

    # remove-item
    p_remove = sub.add_parser("remove-item", help="Remove a work item from a cycle")
    p_remove.add_argument("--project-id", default=None, help="Project UUID")
    p_remove.add_argument("--cycle-id", required=True, help="Cycle UUID")
    p_remove.add_argument("--work-item-id", required=True, help="Work item UUID")

    # list-items
    p_list_items = sub.add_parser("list-items", help="List work items in a cycle")
    p_list_items.add_argument("--project-id", default=None, help="Project UUID")
    p_list_items.add_argument("--cycle-id", required=True, help="Cycle UUID")

    # transfer-items
    p_transfer = sub.add_parser("transfer-items", help="Transfer work items to another cycle")
    p_transfer.add_argument("--project-id", default=None, help="Project UUID")
    p_transfer.add_argument("--cycle-id", required=True, help="Source cycle UUID")
    p_transfer.add_argument("--target-cycle-id", required=True, help="Target cycle UUID")

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
    "transfer-items": cmd_transfer_items,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    COMMANDS[args.command](args)


if __name__ == "__main__":
    main()
