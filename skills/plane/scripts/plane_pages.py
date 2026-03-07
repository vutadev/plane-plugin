#!/usr/bin/env python3
"""Manage Plane pages.

Sub-commands:
    get-workspace     Get a workspace page by ID
    get-project       Get a project page by ID
    create-workspace  Create a workspace page
    create-project    Create a project page
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json, resolve_project_id


def cmd_get_workspace(args: argparse.Namespace) -> None:
    client, slug = get_client()
    page = client.pages.retrieve_workspace_page(slug, args.page_id)
    print(dump_json(page.model_dump()))


def cmd_get_project(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    page = client.pages.retrieve_project_page(slug, project_id, args.page_id)
    print(dump_json(page.model_dump()))


def cmd_create_workspace(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.pages import CreatePage

    fields: dict = {"name": args.name}
    if args.description:
        fields["description_html"] = args.description

    payload = CreatePage(**fields)
    page = client.pages.create_workspace_page(slug, payload)
    print(dump_json(page.model_dump()))


def cmd_create_project(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.pages import CreatePage

    fields: dict = {"name": args.name}
    if args.description:
        fields["description_html"] = args.description

    payload = CreatePage(**fields)
    page = client.pages.create_project_page(slug, project_id, payload)
    print(dump_json(page.model_dump()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_gw = sub.add_parser("get-workspace", help="Get a workspace page")
    p_gw.add_argument("--page-id", required=True, help="Page UUID")

    p_gp = sub.add_parser("get-project", help="Get a project page")
    p_gp.add_argument("--project-id", default=None, help="Project UUID")
    p_gp.add_argument("--page-id", required=True, help="Page UUID")

    p_cw = sub.add_parser("create-workspace", help="Create a workspace page")
    p_cw.add_argument("--name", required=True, help="Page name")
    p_cw.add_argument("--description", help="Page description (HTML)")

    p_cp = sub.add_parser("create-project", help="Create a project page")
    p_cp.add_argument("--project-id", default=None, help="Project UUID")
    p_cp.add_argument("--name", required=True, help="Page name")
    p_cp.add_argument("--description", help="Page description (HTML)")

    return parser


COMMANDS = {
    "get-workspace": cmd_get_workspace,
    "get-project": cmd_get_project,
    "create-workspace": cmd_create_workspace,
    "create-project": cmd_create_project,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    COMMANDS[args.command](args)


if __name__ == "__main__":
    main()
