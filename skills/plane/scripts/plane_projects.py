#!/usr/bin/env python3
"""Manage Plane projects.

Sub-commands:
    list       List all projects
    create     Create a new project
    get        Get a project by ID
    update     Update a project
    delete     Delete a project (requires --confirm)
    members    List project members
    features   Get/update project features

Usage:
    python scripts/plane_projects.py list
    python scripts/plane_projects.py create --name "My Project" --identifier "MP"
    python scripts/plane_projects.py get --project-id <uuid>
    python scripts/plane_projects.py update --project-id <uuid> --name "New Name"
    python scripts/plane_projects.py delete --project-id <uuid> --confirm
    python scripts/plane_projects.py members --project-id <uuid>
    python scripts/plane_projects.py features --project-id <uuid>
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json, resolve_project_id, load_planerc_config, print_list_response, require_confirm, run_command


def cmd_list(args: argparse.Namespace) -> None:
    client, slug = get_client()
    config = load_planerc_config()
    default_pid = config.get("project_id") or config.get("default_project_id")
    if default_pid:
        # Restricted to a single project
        project = client.projects.retrieve(slug, default_pid)
        data = [project.model_dump() if hasattr(project, "model_dump") else project]
    else:
        response = client.projects.list(slug)
        results = response.results if hasattr(response, "results") else response
        data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
    print(dump_json(data))


def cmd_create(args: argparse.Namespace) -> None:
    client, slug = get_client()
    from plane.models.projects import CreateProject

    payload = CreateProject(
        name=args.name,
        identifier=args.identifier,
        description=args.description or "",
        network=int(args.network) if args.network else 2,  # 0=secret, 2=public
    )
    project = client.projects.create(slug, payload)
    print(dump_json(project.model_dump()))


def cmd_get(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    project = client.projects.retrieve(slug, project_id)
    print(dump_json(project.model_dump()))


def cmd_update(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.projects import UpdateProject

    fields: dict = {}
    if args.name:
        fields["name"] = args.name
    if args.description is not None:
        fields["description"] = args.description
    if args.identifier:
        fields["identifier"] = args.identifier

    if not fields:
        print("ERROR: No update fields specified.", file=sys.stderr)
        sys.exit(1)

    payload = UpdateProject(**fields)
    project = client.projects.update(slug, project_id, payload)
    print(dump_json(project.model_dump()))


def cmd_delete(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    require_confirm(args)
    client, slug = get_client()
    client.projects.delete(slug, project_id)
    print(dump_json({"status": "deleted", "project_id": project_id}))


def cmd_members(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    members = client.projects.get_members(slug, project_id)
    print_list_response(members)


def cmd_features(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    features = client.projects.get_features(slug, project_id)
    print(dump_json(features.model_dump()))


def cmd_worklog_summary(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    summary = client.projects.get_worklog_summary(slug, project_id)
    print(dump_json(summary.model_dump() if hasattr(summary, "model_dump") else summary))


def cmd_update_features(args: argparse.Namespace) -> None:
    project_id = resolve_project_id(args)
    client, slug = get_client()
    from plane.models.projects import UpdateProject
    fields: dict = {}
    if args.cycles is not None:
        fields["cycles"] = args.cycles.lower() == "true"
    if args.modules is not None:
        fields["modules"] = args.modules.lower() == "true"
    if args.pages is not None:
        fields["pages"] = args.pages.lower() == "true"
    if args.inbox is not None:
        fields["inbox"] = args.inbox.lower() == "true"
    if not fields:
        print("ERROR: No feature flags specified.", file=sys.stderr)
        sys.exit(1)
    result = client.projects.update_features(slug, project_id, fields)
    print(dump_json(result.model_dump() if hasattr(result, "model_dump") else result))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    sub.add_parser("list", help="List all projects")

    # create
    p_create = sub.add_parser("create", help="Create a new project")
    p_create.add_argument("--name", required=True, help="Project name")
    p_create.add_argument("--identifier", required=True, help="Project identifier (e.g. MP)")
    p_create.add_argument("--description", default="", help="Project description")
    p_create.add_argument("--network", default="2", help="Network type (0=secret, 2=public)")

    # get
    p_get = sub.add_parser("get", help="Get project by ID")
    p_get.add_argument("--project-id", default=None, help="Project UUID")

    # update
    p_update = sub.add_parser("update", help="Update a project")
    p_update.add_argument("--project-id", default=None, help="Project UUID")
    p_update.add_argument("--name", help="New project name")
    p_update.add_argument("--description", help="New description")
    p_update.add_argument("--identifier", help="New identifier")

    # delete
    p_delete = sub.add_parser("delete", help="Delete a project (requires --confirm)")
    p_delete.add_argument("--project-id", default=None, help="Project UUID")
    p_delete.add_argument("--confirm", action="store_true", help="Confirm deletion")

    # members
    p_members = sub.add_parser("members", help="List project members")
    p_members.add_argument("--project-id", default=None, help="Project UUID")

    # features
    p_features = sub.add_parser("features", help="Get project features")
    p_features.add_argument("--project-id", default=None, help="Project UUID")

    # worklog-summary
    p_wl = sub.add_parser("worklog-summary", help="Get project worklog summary")
    p_wl.add_argument("--project-id", default=None, help="Project UUID")

    # update-features
    p_uf = sub.add_parser("update-features", help="Update project features")
    p_uf.add_argument("--project-id", default=None, help="Project UUID")
    p_uf.add_argument("--cycles", help="Enable/disable cycles (true/false)")
    p_uf.add_argument("--modules", help="Enable/disable modules (true/false)")
    p_uf.add_argument("--pages", help="Enable/disable pages (true/false)")
    p_uf.add_argument("--inbox", help="Enable/disable inbox (true/false)")

    return parser


COMMANDS = {
    "list": cmd_list,
    "create": cmd_create,
    "get": cmd_get,
    "update": cmd_update,
    "delete": cmd_delete,
    "members": cmd_members,
    "features": cmd_features,
    "worklog-summary": cmd_worklog_summary,
    "update-features": cmd_update_features,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_command(COMMANDS[args.command], args)


if __name__ == "__main__":
    main()
