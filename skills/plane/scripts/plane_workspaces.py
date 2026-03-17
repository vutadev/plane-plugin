#!/usr/bin/env python3
"""Manage Plane workspace.

Sub-commands:
    members    List workspace members
    features   Get workspace features
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json, print_list_response, require_confirm, run_command


def cmd_members(args: argparse.Namespace) -> None:
    client, slug = get_client()
    members = client.workspaces.get_members(slug)
    print_list_response(members)


def cmd_features(args: argparse.Namespace) -> None:
    client, slug = get_client()
    features = client.workspaces.get_features(slug)
    print(dump_json(features.model_dump()))


def cmd_update_features(args: argparse.Namespace) -> None:
    client, slug = get_client()
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
    result = client.workspaces.update_features(slug, fields)
    print(dump_json(result.model_dump() if hasattr(result, "model_dump") else result))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("members", help="List workspace members")
    sub.add_parser("features", help="Get workspace features")

    p_uf = sub.add_parser("update-features", help="Update workspace features")
    p_uf.add_argument("--cycles", help="Enable/disable cycles (true/false)")
    p_uf.add_argument("--modules", help="Enable/disable modules (true/false)")
    p_uf.add_argument("--pages", help="Enable/disable pages (true/false)")
    p_uf.add_argument("--inbox", help="Enable/disable inbox (true/false)")

    return parser


COMMANDS = {
    "members": cmd_members,
    "features": cmd_features,
    "update-features": cmd_update_features,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_command(COMMANDS[args.command], args)


if __name__ == "__main__":
    main()
