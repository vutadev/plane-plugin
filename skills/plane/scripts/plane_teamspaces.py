#!/usr/bin/env python3
"""Manage Plane teamspaces.

Top-level sub-commands:
    list       List teamspaces
    create     Create a new teamspace
    get        Get a teamspace by ID
    update     Update a teamspace
    delete     Delete a teamspace (requires --confirm)
    members    Manage teamspace members (list, add, remove)
    projects   Manage teamspace projects (list, add, remove)
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json, print_list_response, require_confirm, run_command


# ── Teamspaces CRUD ────────────────────────────────────────────────────────

def cmd_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.teamspaces.list(slug)
    print_list_response(response)


def cmd_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.teamspaces import CreateTeamspace

    fields: dict = {"name": args.name}
    if args.description:
        fields["description"] = args.description

    payload = CreateTeamspace(**fields)
    ts = client.teamspaces.create(slug, payload)
    print(dump_json(ts.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    ts = client.teamspaces.retrieve(slug, args.teamspace_id)
    print(dump_json(ts.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.teamspaces import UpdateTeamspace

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.description is not None:
        fields["description"] = args.description

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateTeamspace(**fields)
    ts = client.teamspaces.update(slug, args.teamspace_id, payload)
    print(dump_json(ts.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    require_confirm(args)
    client, slug = get_client()
    client.teamspaces.delete(slug, args.teamspace_id)
    print(dump_json({"status": "deleted", "teamspace_id": args.teamspace_id}))


# ── Members sub-resource ───────────────────────────────────────────────────

def members_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.teamspaces.members.list(slug, args.teamspace_id)
    print_list_response(response)


def members_add(args: argparse.Namespace) -> None:
    client, slug = get_client()
    member_ids = [i.strip() for i in args.member_ids.split(",")]
    client.teamspaces.members.add(slug, args.teamspace_id, member_ids)
    print(dump_json({"status": "added", "teamspace_id": args.teamspace_id, "member_ids": member_ids}))


def members_remove(args: argparse.Namespace) -> None:
    client, slug = get_client()
    client.teamspaces.members.remove(slug, args.teamspace_id, args.member_id)
    print(dump_json({"status": "removed", "teamspace_id": args.teamspace_id, "member_id": args.member_id}))


# ── Projects sub-resource ──────────────────────────────────────────────────

def projects_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.teamspaces.projects.list(slug, args.teamspace_id)
    print_list_response(response)


def projects_add(args: argparse.Namespace) -> None:
    client, slug = get_client()
    project_ids = [i.strip() for i in args.project_ids.split(",")]
    client.teamspaces.projects.add(slug, args.teamspace_id, project_ids)
    print(dump_json({"status": "added", "teamspace_id": args.teamspace_id, "project_ids": project_ids}))


def projects_remove(args: argparse.Namespace) -> None:
    client, slug = get_client()
    client.teamspaces.projects.remove(slug, args.teamspace_id, args.project_id)
    print(dump_json({"status": "removed", "teamspace_id": args.teamspace_id, "project_id": args.project_id}))


# ── Parser ─────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane teamspaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    top = parser.add_subparsers(dest="resource", required=True)

    top.add_parser("list", help="List teamspaces")

    p_create = top.add_parser("create", help="Create a teamspace")
    p_create.add_argument("--name", required=True, help="Teamspace name")
    p_create.add_argument("--description", help="Description")

    p_get = top.add_parser("get", help="Get teamspace by ID")
    p_get.add_argument("--teamspace-id", required=True, help="Teamspace UUID")

    p_update = top.add_parser("update", help="Update a teamspace")
    p_update.add_argument("--teamspace-id", required=True, help="Teamspace UUID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--description", help="New description")

    p_delete = top.add_parser("delete", help="Delete a teamspace (requires --confirm)")
    p_delete.add_argument("--teamspace-id", required=True, help="Teamspace UUID")
    p_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # ── members ──
    p_mem = top.add_parser("members", help="Teamspace members")
    mem_sub = p_mem.add_subparsers(dest="action", required=True)

    ml = mem_sub.add_parser("list", help="List members")
    ml.add_argument("--teamspace-id", required=True, help="Teamspace UUID")

    ma = mem_sub.add_parser("add", help="Add members")
    ma.add_argument("--teamspace-id", required=True, help="Teamspace UUID")
    ma.add_argument("--member-ids", required=True, help="Comma-separated member UUIDs")

    mr = mem_sub.add_parser("remove", help="Remove a member")
    mr.add_argument("--teamspace-id", required=True, help="Teamspace UUID")
    mr.add_argument("--member-id", required=True, help="Member UUID")

    # ── projects ──
    p_proj = top.add_parser("projects", help="Teamspace projects")
    proj_sub = p_proj.add_subparsers(dest="action", required=True)

    pl = proj_sub.add_parser("list", help="List projects")
    pl.add_argument("--teamspace-id", required=True, help="Teamspace UUID")

    pa = proj_sub.add_parser("add", help="Add projects")
    pa.add_argument("--teamspace-id", required=True, help="Teamspace UUID")
    pa.add_argument("--project-ids", required=True, help="Comma-separated project UUIDs")

    pr = proj_sub.add_parser("remove", help="Remove a project")
    pr.add_argument("--teamspace-id", required=True, help="Teamspace UUID")
    pr.add_argument("--project-id", required=True, help="Project UUID")

    return parser


TOP_COMMANDS = {
    "list": cmd_list,
    "create": cmd_create,
    "get": cmd_get,
    "update": cmd_update,
    "delete": cmd_delete,
}

SUB_DISPATCH = {
    ("members", "list"): members_list,
    ("members", "add"): members_add,
    ("members", "remove"): members_remove,
    ("projects", "list"): projects_list,
    ("projects", "add"): projects_add,
    ("projects", "remove"): projects_remove,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    action = getattr(args, "action", None)
    if action:
        handler = SUB_DISPATCH.get((args.resource, action))
        if not handler:
            parser.error(f"Unknown: {args.resource} {action}")
        run_command(handler, args)
    else:
        handler = TOP_COMMANDS.get(args.resource)
        if not handler:
            parser.error(f"Unknown command: {args.resource}")
        run_command(handler, args)


if __name__ == "__main__":
    main()
