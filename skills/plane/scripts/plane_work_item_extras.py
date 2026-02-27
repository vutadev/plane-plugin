#!/usr/bin/env python3
"""Manage Plane work item sub-resources.

Top-level sub-commands (resource groups):
    activities   Work item activities (list, get)
    comments     Work item comments (list, get, create, update, delete)
    links        Work item links (list, get, create, update, delete)
    relations    Work item relations (list, create, delete)
    work-logs    Work item work logs (list, create, update, delete)
    types        Work item types (list, get, create, update, delete)

Usage:
    python scripts/plane_work_item_extras.py comments list --project-id <id> --work-item-id <id>
    python scripts/plane_work_item_extras.py links create --project-id <id> --work-item-id <id> --url https://...
    python scripts/plane_work_item_extras.py types list --project-id <id>
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json


# ── Activities ────────────────────────────────────────────────────────────────

def activities_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.work_items.activities.list(slug, args.project_id, args.work_item_id)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def activities_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    activity = client.work_items.activities.retrieve(
        slug, args.project_id, args.work_item_id, args.activity_id
    )
    print(dump_json(activity.model_dump()))


# ── Comments ──────────────────────────────────────────────────────────────────

def comments_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.work_items.comments.list(slug, args.project_id, args.work_item_id)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def comments_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    comment = client.work_items.comments.retrieve(
        slug, args.project_id, args.work_item_id, args.comment_id
    )
    print(dump_json(comment.model_dump()))


def comments_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.work_items import CreateWorkItemComment

    payload = CreateWorkItemComment(comment_html=args.body)
    comment = client.work_items.comments.create(
        slug, args.project_id, args.work_item_id, payload
    )
    print(dump_json(comment.model_dump()))


def comments_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.work_items import UpdateWorkItemComment

    payload = UpdateWorkItemComment(comment_html=args.body)
    comment = client.work_items.comments.update(
        slug, args.project_id, args.work_item_id, args.comment_id, payload
    )
    print(dump_json(comment.model_dump()))


def comments_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)
    client, slug = get_client()
    client.work_items.comments.delete(
        slug, args.project_id, args.work_item_id, args.comment_id
    )
    print(dump_json({"status": "deleted", "comment_id": args.comment_id}))


# ── Links ─────────────────────────────────────────────────────────────────────

def links_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.work_items.links.list(slug, args.project_id, args.work_item_id)
    results = response.results if hasattr(response, "results") else response
    data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def links_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    link = client.work_items.links.retrieve(
        slug, args.project_id, args.work_item_id, args.link_id
    )
    print(dump_json(link.model_dump()))


def links_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.work_items import CreateWorkItemLink

    fields: dict = {"url": args.url}
    if args.title:
        fields["title"] = args.title

    payload = CreateWorkItemLink(**fields)
    link = client.work_items.links.create(
        slug, args.project_id, args.work_item_id, payload
    )
    print(dump_json(link.model_dump()))


def links_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.work_items import UpdateWorkItemLink

    fields: dict = {}
    if args.url:
        fields["url"] = args.url
    if args.title:
        fields["title"] = args.title

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateWorkItemLink(**fields)
    link = client.work_items.links.update(
        slug, args.project_id, args.work_item_id, args.link_id, payload
    )
    print(dump_json(link.model_dump()))


def links_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)
    client, slug = get_client()
    client.work_items.links.delete(
        slug, args.project_id, args.work_item_id, args.link_id
    )
    print(dump_json({"status": "deleted", "link_id": args.link_id}))


# ── Relations ─────────────────────────────────────────────────────────────────

def relations_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.work_items.relations.list(slug, args.project_id, args.work_item_id)
    print(dump_json(response.model_dump() if hasattr(response, "model_dump") else response))


def relations_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.work_items import CreateWorkItemRelation

    payload = CreateWorkItemRelation(
        related_list=[{"issue": args.related_id, "relation_type": args.relation_type}]
    )
    client.work_items.relations.create(
        slug, args.project_id, args.work_item_id, payload
    )
    print(dump_json({
        "status": "created",
        "work_item_id": args.work_item_id,
        "related_id": args.related_id,
        "relation_type": args.relation_type,
    }))


def relations_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)
    client, slug = get_client()
    from plane.models.work_items import RemoveWorkItemRelation

    payload = RemoveWorkItemRelation(
        issue=args.related_id,
        relation_type=args.relation_type,
    )
    client.work_items.relations.delete(
        slug, args.project_id, args.work_item_id, payload
    )
    print(dump_json({"status": "deleted", "related_id": args.related_id}))


# ── Work Logs ─────────────────────────────────────────────────────────────────

def work_logs_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    logs = client.work_items.work_logs.list(slug, args.project_id, args.work_item_id)
    data = [l.model_dump() if hasattr(l, "model_dump") else l for l in logs]
    print(dump_json(data))


def work_logs_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    payload = {"duration": int(args.duration)}
    if args.description:
        payload["description"] = args.description
    log = client.work_items.work_logs.create(
        slug, args.project_id, args.work_item_id, payload
    )
    print(dump_json(log.model_dump()))


def work_logs_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    fields: dict = {}
    if args.duration:
        fields["duration"] = int(args.duration)
    if args.description:
        fields["description"] = args.description

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    log = client.work_items.work_logs.update(
        slug, args.project_id, args.work_item_id, args.work_log_id, fields
    )
    print(dump_json(log.model_dump()))


def work_logs_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)
    client, slug = get_client()
    client.work_items.work_logs.delete(
        slug, args.project_id, args.work_item_id, args.work_log_id
    )
    print(dump_json({"status": "deleted", "work_log_id": args.work_log_id}))


# ── Work Item Types ───────────────────────────────────────────────────────────

def types_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    types = client.work_item_types.list(slug, args.project_id)
    data = [t.model_dump() if hasattr(t, "model_dump") else t for t in types]
    print(dump_json(data))


def types_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    t = client.work_item_types.retrieve(slug, args.project_id, args.type_id)
    print(dump_json(t.model_dump()))


def types_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.work_item_types import CreateWorkItemType

    fields: dict = {"name": args.name}
    if args.description:
        fields["description"] = args.description

    payload = CreateWorkItemType(**fields)
    t = client.work_item_types.create(slug, args.project_id, payload)
    print(dump_json(t.model_dump()))


def types_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.work_item_types import UpdateWorkItemType

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.description is not None:
        fields["description"] = args.description

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateWorkItemType(**fields)
    t = client.work_item_types.update(slug, args.project_id, args.type_id, payload)
    print(dump_json(t.model_dump()))


def types_delete(args: argparse.Namespace) -> None:
    if not args.confirm:
        print("ERROR: Destructive operation — pass --confirm to proceed.", file=sys.stderr)
        sys.exit(1)
    client, slug = get_client()
    client.work_item_types.delete(slug, args.project_id, args.type_id)
    print(dump_json({"status": "deleted", "type_id": args.type_id}))


# ── Parser construction ──────────────────────────────────────────────────────

def _add_wi_args(p: argparse.ArgumentParser) -> None:
    """Add common --project-id and --work-item-id args."""
    p.add_argument("--project-id", required=True, help="Project UUID")
    p.add_argument("--work-item-id", required=True, help="Work item UUID")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane work item sub-resources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    top = parser.add_subparsers(dest="resource", required=True)

    # ── activities ──
    p_act = top.add_parser("activities", help="Work item activities")
    act_sub = p_act.add_subparsers(dest="action", required=True)

    act_list = act_sub.add_parser("list", help="List activities")
    _add_wi_args(act_list)

    act_get = act_sub.add_parser("get", help="Get activity by ID")
    _add_wi_args(act_get)
    act_get.add_argument("--activity-id", required=True, help="Activity UUID")

    # ── comments ──
    p_com = top.add_parser("comments", help="Work item comments")
    com_sub = p_com.add_subparsers(dest="action", required=True)

    com_list = com_sub.add_parser("list", help="List comments")
    _add_wi_args(com_list)

    com_get = com_sub.add_parser("get", help="Get comment by ID")
    _add_wi_args(com_get)
    com_get.add_argument("--comment-id", required=True, help="Comment UUID")

    com_create = com_sub.add_parser("create", help="Create a comment")
    _add_wi_args(com_create)
    com_create.add_argument("--body", required=True, help="Comment body (HTML)")

    com_update = com_sub.add_parser("update", help="Update a comment")
    _add_wi_args(com_update)
    com_update.add_argument("--comment-id", required=True, help="Comment UUID")
    com_update.add_argument("--body", required=True, help="New body (HTML)")

    com_delete = com_sub.add_parser("delete", help="Delete a comment")
    _add_wi_args(com_delete)
    com_delete.add_argument("--comment-id", required=True, help="Comment UUID")
    com_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # ── links ──
    p_lnk = top.add_parser("links", help="Work item links")
    lnk_sub = p_lnk.add_subparsers(dest="action", required=True)

    lnk_list = lnk_sub.add_parser("list", help="List links")
    _add_wi_args(lnk_list)

    lnk_get = lnk_sub.add_parser("get", help="Get link by ID")
    _add_wi_args(lnk_get)
    lnk_get.add_argument("--link-id", required=True, help="Link UUID")

    lnk_create = lnk_sub.add_parser("create", help="Create a link")
    _add_wi_args(lnk_create)
    lnk_create.add_argument("--url", required=True, help="URL")
    lnk_create.add_argument("--title", help="Link title")

    lnk_update = lnk_sub.add_parser("update", help="Update a link")
    _add_wi_args(lnk_update)
    lnk_update.add_argument("--link-id", required=True, help="Link UUID")
    lnk_update.add_argument("--url", help="New URL")
    lnk_update.add_argument("--title", help="New title")

    lnk_delete = lnk_sub.add_parser("delete", help="Delete a link")
    _add_wi_args(lnk_delete)
    lnk_delete.add_argument("--link-id", required=True, help="Link UUID")
    lnk_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # ── relations ──
    p_rel = top.add_parser("relations", help="Work item relations")
    rel_sub = p_rel.add_subparsers(dest="action", required=True)

    rel_list = rel_sub.add_parser("list", help="List relations")
    _add_wi_args(rel_list)

    rel_create = rel_sub.add_parser("create", help="Create a relation")
    _add_wi_args(rel_create)
    rel_create.add_argument("--related-id", required=True, help="Related work item UUID")
    rel_create.add_argument("--relation-type", required=True,
                            help="Relation type (e.g. relates_to, blocks, blocked_by, duplicate)")

    rel_delete = rel_sub.add_parser("delete", help="Remove a relation")
    _add_wi_args(rel_delete)
    rel_delete.add_argument("--related-id", required=True, help="Related work item UUID")
    rel_delete.add_argument("--relation-type", required=True, help="Relation type")
    rel_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # ── work-logs ──
    p_wl = top.add_parser("work-logs", help="Work item work logs")
    wl_sub = p_wl.add_subparsers(dest="action", required=True)

    wl_list = wl_sub.add_parser("list", help="List work logs")
    _add_wi_args(wl_list)

    wl_create = wl_sub.add_parser("create", help="Create a work log")
    _add_wi_args(wl_create)
    wl_create.add_argument("--duration", required=True, help="Duration in minutes")
    wl_create.add_argument("--description", help="Description")

    wl_update = wl_sub.add_parser("update", help="Update a work log")
    _add_wi_args(wl_update)
    wl_update.add_argument("--work-log-id", required=True, help="Work log UUID")
    wl_update.add_argument("--duration", help="New duration in minutes")
    wl_update.add_argument("--description", help="New description")

    wl_delete = wl_sub.add_parser("delete", help="Delete a work log")
    _add_wi_args(wl_delete)
    wl_delete.add_argument("--work-log-id", required=True, help="Work log UUID")
    wl_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # ── types ──
    p_typ = top.add_parser("types", help="Work item types")
    typ_sub = p_typ.add_subparsers(dest="action", required=True)

    typ_list = typ_sub.add_parser("list", help="List work item types")
    typ_list.add_argument("--project-id", required=True, help="Project UUID")

    typ_get = typ_sub.add_parser("get", help="Get work item type by ID")
    typ_get.add_argument("--project-id", required=True, help="Project UUID")
    typ_get.add_argument("--type-id", required=True, help="Work item type UUID")

    typ_create = typ_sub.add_parser("create", help="Create a work item type")
    typ_create.add_argument("--project-id", required=True, help="Project UUID")
    typ_create.add_argument("--name", required=True, help="Type name")
    typ_create.add_argument("--description", help="Description")

    typ_update = typ_sub.add_parser("update", help="Update a work item type")
    typ_update.add_argument("--project-id", required=True, help="Project UUID")
    typ_update.add_argument("--type-id", required=True, help="Work item type UUID")
    typ_update.add_argument("--name", help="New name")
    typ_update.add_argument("--description", help="New description")

    typ_delete = typ_sub.add_parser("delete", help="Delete a work item type")
    typ_delete.add_argument("--project-id", required=True, help="Project UUID")
    typ_delete.add_argument("--type-id", required=True, help="Work item type UUID")
    typ_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    return parser


# Dispatch table: (resource, action) -> handler
DISPATCH = {
    ("activities", "list"): activities_list,
    ("activities", "get"): activities_get,
    ("comments", "list"): comments_list,
    ("comments", "get"): comments_get,
    ("comments", "create"): comments_create,
    ("comments", "update"): comments_update,
    ("comments", "delete"): comments_delete,
    ("links", "list"): links_list,
    ("links", "get"): links_get,
    ("links", "create"): links_create,
    ("links", "update"): links_update,
    ("links", "delete"): links_delete,
    ("relations", "list"): relations_list,
    ("relations", "create"): relations_create,
    ("relations", "delete"): relations_delete,
    ("work-logs", "list"): work_logs_list,
    ("work-logs", "create"): work_logs_create,
    ("work-logs", "update"): work_logs_update,
    ("work-logs", "delete"): work_logs_delete,
    ("types", "list"): types_list,
    ("types", "get"): types_get,
    ("types", "create"): types_create,
    ("types", "update"): types_update,
    ("types", "delete"): types_delete,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    key = (args.resource, args.action)
    handler = DISPATCH.get(key)
    if not handler:
        parser.error(f"Unknown command: {args.resource} {args.action}")
    handler(args)


if __name__ == "__main__":
    main()
