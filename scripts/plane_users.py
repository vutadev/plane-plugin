#!/usr/bin/env python3
"""Plane user operations.

Sub-commands:
    me         Get current user info
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.plane_client import get_client, dump_json


def cmd_me(args: argparse.Namespace) -> None:
    client, _ = get_client()
    user = client.users.get_me()
    print(dump_json(user.model_dump()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plane user operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("me", help="Get current user info")

    return parser


COMMANDS = {
    "me": cmd_me,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    COMMANDS[args.command](args)


if __name__ == "__main__":
    main()
