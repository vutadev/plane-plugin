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

from scripts.plane_client import get_client, dump_json


def cmd_members(args: argparse.Namespace) -> None:
    client, slug = get_client()
    members = client.workspaces.get_members(slug)
    data = [m.model_dump() if hasattr(m, "model_dump") else m for m in members]
    print(dump_json(data))


def cmd_features(args: argparse.Namespace) -> None:
    client, slug = get_client()
    features = client.workspaces.get_features(slug)
    print(dump_json(features.model_dump()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Plane workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("members", help="List workspace members")
    sub.add_parser("features", help="Get workspace features")

    return parser


COMMANDS = {
    "members": cmd_members,
    "features": cmd_features,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    COMMANDS[args.command](args)


if __name__ == "__main__":
    main()
