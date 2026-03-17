#!/usr/bin/env python3
"""Manage Plane work item properties (custom fields).

Top-level sub-commands:
    list       List work item properties in a project
    create     Create a new property
    get        Get a property by ID
    update     Update a property
    delete     Delete a property (requires --confirm)
    options    Manage property options (list, get, create, update, delete)
    values     Manage property values on work items (list, create)
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json, resolve_project_id, print_list_response, require_confirm, run_command


# ── Properties CRUD ────────────────────────────────────────────────────────

def cmd_list(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    response = client.work_item_properties.list(slug, project_id)
    print_list_response(response)


def cmd_create(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.work_item_properties import CreateWorkItemProperty

    fields: dict = {"display_name": args.display_name, "property_type": args.property_type}
    if args.description:
        fields["description"] = args.description
    if args.is_required is not None:
        fields["is_required"] = args.is_required.lower() == "true"

    payload = CreateWorkItemProperty(**fields)
    prop = client.work_item_properties.create(slug, project_id, payload)
    print(dump_json(prop.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    prop = client.work_item_properties.retrieve(slug, project_id, args.property_id)
    print(dump_json(prop.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.work_item_properties import UpdateWorkItemProperty

    fields: dict = {}
    if args.display_name:
        fields["display_name"] = args.display_name
    if args.description is not None:
        fields["description"] = args.description
    if args.is_required is not None:
        fields["is_required"] = args.is_required.lower() == "true"

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateWorkItemProperty(**fields)
    prop = client.work_item_properties.update(slug, project_id, args.property_id, payload)
    print(dump_json(prop.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    require_confirm(args)
    project_id = resolve_project_id(args)
    client, slug = get_client()
    client.work_item_properties.delete(slug, project_id, args.property_id)
    print(dump_json({"status": "deleted", "property_id": args.property_id}))


# ── Options sub-resource ───────────────────────────────────────────────────

def opts_list(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    response = client.work_item_properties.options.list(slug, project_id, args.property_id)
    print_list_response(response)


def opts_get(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    opt = client.work_item_properties.options.retrieve(slug, project_id, args.property_id, args.option_id)
    print(dump_json(opt.model_dump()))


def opts_create(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.work_item_properties import CreateWorkItemPropertyOption

    fields: dict = {"name": args.name}
    payload = CreateWorkItemPropertyOption(**fields)
    opt = client.work_item_properties.options.create(slug, project_id, args.property_id, payload)
    print(dump_json(opt.model_dump()))


def opts_update(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.work_item_properties import UpdateWorkItemPropertyOption

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)
    payload = UpdateWorkItemPropertyOption(**fields)
    opt = client.work_item_properties.options.update(slug, project_id, args.property_id, args.option_id, payload)
    print(dump_json(opt.model_dump()))


def opts_delete(args: argparse.Namespace) -> None:
    require_confirm(args)
    project_id = resolve_project_id(args)
    client, slug = get_client()
    client.work_item_properties.options.delete(slug, project_id, args.property_id, args.option_id)
    print(dump_json({"status": "deleted", "option_id": args.option_id}))


# ── Values sub-resource ────────────────────────────────────────────────────

def vals_list(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    response = client.work_item_properties.values.list(slug, project_id, args.work_item_id)
    print_list_response(response)


def vals_create(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.work_item_properties import CreateWorkItemPropertyValue

    payload = CreateWorkItemPropertyValue(
        property_id=args.property_id,
        value=args.value,
    )
    val = client.work_item_properties.values.create(slug, project_id, args.work_item_id, payload)
    print(dump_json(val.model_dump() if hasattr(val, "model_dump") else val))


# ── Parser ─────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane work item properties",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    top = parser.add_subparsers(dest="resource", required=True)

    # top-level CRUD
    p_list = top.add_parser("list", help="List properties")
    p_list.add_argument("--project-id", default=None, help="Project UUID")

    p_create = top.add_parser("create", help="Create a property")
    p_create.add_argument("--project-id", default=None, help="Project UUID")
    p_create.add_argument("--display-name", required=True, help="Display name")
    p_create.add_argument("--property-type", required=True, help="Property type")
    p_create.add_argument("--description", help="Description")
    p_create.add_argument("--is-required", help="Is required (true/false)")

    p_get = top.add_parser("get", help="Get property by ID")
    p_get.add_argument("--project-id", default=None, help="Project UUID")
    p_get.add_argument("--property-id", required=True, help="Property UUID")

    p_update = top.add_parser("update", help="Update a property")
    p_update.add_argument("--project-id", default=None, help="Project UUID")
    p_update.add_argument("--property-id", required=True, help="Property UUID")
    p_update.add_argument("--display-name", help="New display name")
    p_update.add_argument("--description", help="New description")
    p_update.add_argument("--is-required", help="Is required (true/false)")

    p_delete = top.add_parser("delete", help="Delete a property (requires --confirm)")
    p_delete.add_argument("--project-id", default=None, help="Project UUID")
    p_delete.add_argument("--property-id", required=True, help="Property UUID")
    p_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # ── options ──
    p_opts = top.add_parser("options", help="Property options")
    opts_sub = p_opts.add_subparsers(dest="action", required=True)

    ol = opts_sub.add_parser("list", help="List options")
    ol.add_argument("--project-id", default=None, help="Project UUID")
    ol.add_argument("--property-id", required=True, help="Property UUID")

    og = opts_sub.add_parser("get", help="Get option by ID")
    og.add_argument("--project-id", default=None, help="Project UUID")
    og.add_argument("--property-id", required=True, help="Property UUID")
    og.add_argument("--option-id", required=True, help="Option UUID")

    oc = opts_sub.add_parser("create", help="Create an option")
    oc.add_argument("--project-id", default=None, help="Project UUID")
    oc.add_argument("--property-id", required=True, help="Property UUID")
    oc.add_argument("--name", required=True, help="Option name")

    ou = opts_sub.add_parser("update", help="Update an option")
    ou.add_argument("--project-id", default=None, help="Project UUID")
    ou.add_argument("--property-id", required=True, help="Property UUID")
    ou.add_argument("--option-id", required=True, help="Option UUID")
    ou.add_argument("--name", help="New name")

    od = opts_sub.add_parser("delete", help="Delete an option")
    od.add_argument("--project-id", default=None, help="Project UUID")
    od.add_argument("--property-id", required=True, help="Property UUID")
    od.add_argument("--option-id", required=True, help="Option UUID")
    od.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # ── values ──
    p_vals = top.add_parser("values", help="Property values on work items")
    vals_sub = p_vals.add_subparsers(dest="action", required=True)

    vl = vals_sub.add_parser("list", help="List property values for a work item")
    vl.add_argument("--project-id", default=None, help="Project UUID")
    vl.add_argument("--work-item-id", required=True, help="Work item UUID")

    vc = vals_sub.add_parser("create", help="Set a property value on a work item")
    vc.add_argument("--project-id", default=None, help="Project UUID")
    vc.add_argument("--work-item-id", required=True, help="Work item UUID")
    vc.add_argument("--property-id", required=True, help="Property UUID")
    vc.add_argument("--value", required=True, help="Value to set")

    return parser


TOP_COMMANDS = {
    "list": cmd_list,
    "create": cmd_create,
    "get": cmd_get,
    "update": cmd_update,
    "delete": cmd_delete,
}

SUB_DISPATCH = {
    ("options", "list"): opts_list,
    ("options", "get"): opts_get,
    ("options", "create"): opts_create,
    ("options", "update"): opts_update,
    ("options", "delete"): opts_delete,
    ("values", "list"): vals_list,
    ("values", "create"): vals_create,
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
