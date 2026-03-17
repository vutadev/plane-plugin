#!/usr/bin/env python3
"""Manage Plane customers.

Top-level sub-commands:
    list           List customers
    create         Create a new customer
    get            Get a customer by ID
    update         Update a customer
    delete         Delete a customer (requires --confirm)
    properties     Manage customer properties (list, get, create, update, delete)
    requests       Manage customer requests (list, get, create, update, delete)
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json, print_list_response, require_confirm, run_command


# ── Customers CRUD ─────────────────────────────────────────────────────────

def cmd_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.customers.list(slug)
    print_list_response(response)


def cmd_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.customers import CreateCustomer

    fields: dict = {"name": args.name}
    if args.email:
        fields["email"] = args.email
    if args.description:
        fields["description"] = args.description

    payload = CreateCustomer(**fields)
    customer = client.customers.create(slug, payload)
    print(dump_json(customer.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    customer = client.customers.retrieve(slug, args.customer_id)
    print(dump_json(customer.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.customers import UpdateCustomer

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.email:
        fields["email"] = args.email
    if args.description is not None:
        fields["description"] = args.description

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateCustomer(**fields)
    customer = client.customers.update(slug, args.customer_id, payload)
    print(dump_json(customer.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    require_confirm(args)
    client, slug = get_client()
    client.customers.delete(slug, args.customer_id)
    print(dump_json({"status": "deleted", "customer_id": args.customer_id}))


# ── Properties sub-resource ────────────────────────────────────────────────

def props_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.customers.properties.list(slug)
    print_list_response(response)


def props_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    prop = client.customers.properties.retrieve(slug, args.property_id)
    print(dump_json(prop.model_dump()))


def props_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.customers import CreateCustomerProperty

    fields: dict = {"display_name": args.display_name, "property_type": args.property_type}
    payload = CreateCustomerProperty(**fields)
    prop = client.customers.properties.create(slug, payload)
    print(dump_json(prop.model_dump()))


def props_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.customers import UpdateCustomerProperty

    fields: dict = {}
    if args.display_name:
        fields["display_name"] = args.display_name
    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)
    payload = UpdateCustomerProperty(**fields)
    prop = client.customers.properties.update(slug, args.property_id, payload)
    print(dump_json(prop.model_dump()))


def props_delete(args: argparse.Namespace) -> None:
    require_confirm(args)
    client, slug = get_client()
    client.customers.properties.delete(slug, args.property_id)
    print(dump_json({"status": "deleted", "property_id": args.property_id}))


# ── Requests sub-resource ──────────────────────────────────────────────────

def reqs_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    response = client.customers.requests.list(slug, args.customer_id)
    print_list_response(response)


def reqs_get(args: argparse.Namespace) -> None:
    client, slug = get_client()
    req = client.customers.requests.retrieve(slug, args.customer_id, args.request_id)
    print(dump_json(req.model_dump()))


def reqs_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    fields: dict = {"title": args.title}
    if args.description:
        fields["description"] = args.description
    req = client.customers.requests.create(slug, args.customer_id, fields)
    print(dump_json(req.model_dump() if hasattr(req, "model_dump") else req))


def reqs_update(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.customers import UpdateCustomerRequest

    fields: dict = {}
    if args.title:
        fields["title"] = args.title
    if args.description is not None:
        fields["description"] = args.description
    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)
    payload = UpdateCustomerRequest(**fields)
    req = client.customers.requests.update(slug, args.customer_id, args.request_id, payload)
    print(dump_json(req.model_dump()))


def reqs_delete(args: argparse.Namespace) -> None:
    require_confirm(args)
    client, slug = get_client()
    client.customers.requests.delete(slug, args.customer_id, args.request_id)
    print(dump_json({"status": "deleted", "request_id": args.request_id}))


# ── Parser ─────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane customers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    top = parser.add_subparsers(dest="resource", required=True)

    # ── top-level CRUD (treated as resource="customer", action=<cmd>) ──
    p_list = top.add_parser("list", help="List customers")
    p_create = top.add_parser("create", help="Create a customer")
    p_create.add_argument("--name", required=True, help="Customer name")
    p_create.add_argument("--email", help="Customer email")
    p_create.add_argument("--description", help="Description")

    p_get = top.add_parser("get", help="Get customer by ID")
    p_get.add_argument("--customer-id", required=True, help="Customer UUID")

    p_update = top.add_parser("update", help="Update a customer")
    p_update.add_argument("--customer-id", required=True, help="Customer UUID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--email", help="New email")
    p_update.add_argument("--description", help="New description")

    p_delete = top.add_parser("delete", help="Delete a customer (requires --confirm)")
    p_delete.add_argument("--customer-id", required=True, help="Customer UUID")
    p_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # ── properties ──
    p_props = top.add_parser("properties", help="Customer properties")
    props_sub = p_props.add_subparsers(dest="action", required=True)

    props_sub.add_parser("list", help="List properties")

    pg = props_sub.add_parser("get", help="Get property by ID")
    pg.add_argument("--property-id", required=True, help="Property UUID")

    pc = props_sub.add_parser("create", help="Create a property")
    pc.add_argument("--display-name", required=True, help="Display name")
    pc.add_argument("--property-type", required=True, help="Property type (text, number, date, select, etc.)")

    pu = props_sub.add_parser("update", help="Update a property")
    pu.add_argument("--property-id", required=True, help="Property UUID")
    pu.add_argument("--display-name", help="New display name")

    pd = props_sub.add_parser("delete", help="Delete a property")
    pd.add_argument("--property-id", required=True, help="Property UUID")
    pd.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # ── requests ──
    p_reqs = top.add_parser("requests", help="Customer requests")
    reqs_sub = p_reqs.add_subparsers(dest="action", required=True)

    rl = reqs_sub.add_parser("list", help="List requests")
    rl.add_argument("--customer-id", required=True, help="Customer UUID")

    rg = reqs_sub.add_parser("get", help="Get request by ID")
    rg.add_argument("--customer-id", required=True, help="Customer UUID")
    rg.add_argument("--request-id", required=True, help="Request UUID")

    rc = reqs_sub.add_parser("create", help="Create a request")
    rc.add_argument("--customer-id", required=True, help="Customer UUID")
    rc.add_argument("--title", required=True, help="Request title")
    rc.add_argument("--description", help="Description")

    ru = reqs_sub.add_parser("update", help="Update a request")
    ru.add_argument("--customer-id", required=True, help="Customer UUID")
    ru.add_argument("--request-id", required=True, help="Request UUID")
    ru.add_argument("--title", help="New title")
    ru.add_argument("--description", help="New description")

    rd = reqs_sub.add_parser("delete", help="Delete a request")
    rd.add_argument("--customer-id", required=True, help="Customer UUID")
    rd.add_argument("--request-id", required=True, help="Request UUID")
    rd.add_argument("--confirm", action="store_true", help="Confirm deletion")

    return parser


TOP_COMMANDS = {
    "list": cmd_list,
    "create": cmd_create,
    "get": cmd_get,
    "update": cmd_update,
    "delete": cmd_delete,
}

SUB_DISPATCH = {
    ("properties", "list"): props_list,
    ("properties", "get"): props_get,
    ("properties", "create"): props_create,
    ("properties", "update"): props_update,
    ("properties", "delete"): props_delete,
    ("requests", "list"): reqs_list,
    ("requests", "get"): reqs_get,
    ("requests", "create"): reqs_create,
    ("requests", "update"): reqs_update,
    ("requests", "delete"): reqs_delete,
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
