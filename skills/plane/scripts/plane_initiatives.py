#!/usr/bin/env python3
"""Manage Plane initiatives.

Sub-commands:
    list           List initiatives in the workspace
    create         Create a new initiative
    get            Get an initiative by ID
    update         Update an initiative
    delete         Delete an initiative (requires --confirm)
    epics          Manage initiative epics (list, add, remove)
    labels         Manage initiative labels (list, create, get, update, delete, add-labels, remove-labels)
    projects       Manage initiative projects (list, add, remove)
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json, print_list_response, require_confirm, run_command


def cmd_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.initiatives.list(slug)
    print_list_response(response)


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
    require_confirm(args)
    client, slug = get_client()
    client.initiatives.delete(slug, args.initiative_id)
    print(dump_json({"status": "deleted", "initiative_id": args.initiative_id}))


# ── Epics sub-resource ─────────────────────────────────────────────────────

def cmd_epics_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.initiatives.epics.list(slug, args.initiative_id)
    print_list_response(response)


def cmd_epics_add(args: argparse.Namespace) -> None:
    client, slug = get_client()
    epic_ids = [i.strip() for i in args.epic_ids.split(",")]
    client.initiatives.epics.add(slug, args.initiative_id, epic_ids)
    print(dump_json({"status": "added", "initiative_id": args.initiative_id, "epic_ids": epic_ids}))


def cmd_epics_remove(args: argparse.Namespace) -> None:
    client, slug = get_client()
    client.initiatives.epics.remove(slug, args.initiative_id, args.epic_id)
    print(dump_json({"status": "removed", "initiative_id": args.initiative_id, "epic_id": args.epic_id}))


# ── Labels sub-resource ────────────────────────────────────────────────────

def cmd_labels_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.initiatives.labels.list(slug, args.initiative_id)
    print_list_response(response)


def cmd_labels_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.initiatives import CreateInitiativeLabel

    fields: dict = {"name": args.name}
    if args.color:
        fields["color"] = args.color
    payload = CreateInitiativeLabel(**fields)
    label = client.initiatives.labels.create(slug, args.initiative_id, payload)
    print(dump_json(label.model_dump()))


def cmd_labels_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    label = client.initiatives.labels.retrieve(slug, args.initiative_id, args.label_id)
    print(dump_json(label.model_dump()))


def cmd_labels_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.initiatives import UpdateInitiativeLabel

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.color:
        fields["color"] = args.color
    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)
    payload = UpdateInitiativeLabel(**fields)
    label = client.initiatives.labels.update(slug, args.initiative_id, args.label_id, payload)
    print(dump_json(label.model_dump()))


def cmd_labels_delete(args: argparse.Namespace) -> None:
    require_confirm(args)
    client, slug = get_client()
    client.initiatives.labels.delete(slug, args.initiative_id, args.label_id)
    print(dump_json({"status": "deleted", "label_id": args.label_id}))


# ── Projects sub-resource ──────────────────────────────────────────────────

def cmd_projects_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.initiatives.projects.list(slug, args.initiative_id)
    print_list_response(response)


def cmd_projects_add(args: argparse.Namespace) -> None:
    client, slug = get_client()
    project_ids = [i.strip() for i in args.project_ids.split(",")]
    client.initiatives.projects.add(slug, args.initiative_id, project_ids)
    print(dump_json({"status": "added", "initiative_id": args.initiative_id, "project_ids": project_ids}))


def cmd_projects_remove(args: argparse.Namespace) -> None:
    client, slug = get_client()
    client.initiatives.projects.remove(slug, args.initiative_id, args.project_id)
    print(dump_json({"status": "removed", "initiative_id": args.initiative_id, "project_id": args.project_id}))


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

    # ── epics sub-resource ──
    p_epics = sub.add_parser("epics", help="Manage initiative epics")
    ep_sub = p_epics.add_subparsers(dest="action", required=True)

    ep_list = ep_sub.add_parser("list", help="List epics")
    ep_list.add_argument("--initiative-id", required=True, help="Initiative UUID")

    ep_add = ep_sub.add_parser("add", help="Add epics to initiative")
    ep_add.add_argument("--initiative-id", required=True, help="Initiative UUID")
    ep_add.add_argument("--epic-ids", required=True, help="Comma-separated epic UUIDs")

    ep_remove = ep_sub.add_parser("remove", help="Remove epic from initiative")
    ep_remove.add_argument("--initiative-id", required=True, help="Initiative UUID")
    ep_remove.add_argument("--epic-id", required=True, help="Epic UUID")

    # ── labels sub-resource ──
    p_labels = sub.add_parser("labels", help="Manage initiative labels")
    lb_sub = p_labels.add_subparsers(dest="action", required=True)

    lb_list = lb_sub.add_parser("list", help="List labels")
    lb_list.add_argument("--initiative-id", required=True, help="Initiative UUID")

    lb_create = lb_sub.add_parser("create", help="Create a label")
    lb_create.add_argument("--initiative-id", required=True, help="Initiative UUID")
    lb_create.add_argument("--name", required=True, help="Label name")
    lb_create.add_argument("--color", help="Label color (hex)")

    lb_get = lb_sub.add_parser("get", help="Get label by ID")
    lb_get.add_argument("--initiative-id", required=True, help="Initiative UUID")
    lb_get.add_argument("--label-id", required=True, help="Label UUID")

    lb_update = lb_sub.add_parser("update", help="Update a label")
    lb_update.add_argument("--initiative-id", required=True, help="Initiative UUID")
    lb_update.add_argument("--label-id", required=True, help="Label UUID")
    lb_update.add_argument("--name", help="New name")
    lb_update.add_argument("--color", help="New color")

    lb_delete = lb_sub.add_parser("delete", help="Delete a label")
    lb_delete.add_argument("--initiative-id", required=True, help="Initiative UUID")
    lb_delete.add_argument("--label-id", required=True, help="Label UUID")
    lb_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # ── projects sub-resource ──
    p_projs = sub.add_parser("projects", help="Manage initiative projects")
    pj_sub = p_projs.add_subparsers(dest="action", required=True)

    pj_list = pj_sub.add_parser("list", help="List projects")
    pj_list.add_argument("--initiative-id", required=True, help="Initiative UUID")

    pj_add = pj_sub.add_parser("add", help="Add projects to initiative")
    pj_add.add_argument("--initiative-id", required=True, help="Initiative UUID")
    pj_add.add_argument("--project-ids", required=True, help="Comma-separated project UUIDs")

    pj_remove = pj_sub.add_parser("remove", help="Remove project from initiative")
    pj_remove.add_argument("--initiative-id", required=True, help="Initiative UUID")
    pj_remove.add_argument("--project-id", required=True, help="Project UUID")

    return parser


# Dispatch: top-level commands use "command", sub-resources use ("command", "action")
COMMANDS = {
    "list": cmd_list,
    "create": cmd_create,
    "get": cmd_get,
    "update": cmd_update,
    "delete": cmd_delete,
}


SUB_DISPATCH = {
    ("epics", "list"): cmd_epics_list,
    ("epics", "add"): cmd_epics_add,
    ("epics", "remove"): cmd_epics_remove,
    ("labels", "list"): cmd_labels_list,
    ("labels", "create"): cmd_labels_create,
    ("labels", "get"): cmd_labels_get,
    ("labels", "update"): cmd_labels_update,
    ("labels", "delete"): cmd_labels_delete,
    ("projects", "list"): cmd_projects_list,
    ("projects", "add"): cmd_projects_add,
    ("projects", "remove"): cmd_projects_remove,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    action = getattr(args, "action", None)
    if action:
        handler = SUB_DISPATCH.get((args.command, action))
        if not handler:
            parser.error(f"Unknown: {args.command} {action}")
        run_command(handler, args)
    else:
        run_command(COMMANDS[args.command], args)


if __name__ == "__main__":
    main()
