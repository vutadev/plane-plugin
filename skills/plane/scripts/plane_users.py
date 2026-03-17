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

from scripts.plane_client import get_client, dump_json, print_list_response, require_confirm, run_command


def cmd_me(args: argparse.Namespace) -> None:
    client, _ = get_client()
    user = client.users.get_me()
    print(dump_json(user.model_dump()))


def cmd_upload_asset(args: argparse.Namespace) -> None:
    client, _ = get_client()
    result = client.users.upload_asset(args.file_path)
    print(dump_json(result.model_dump() if hasattr(result, "model_dump") else result))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plane user operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("me", help="Get current user info")

    p_upload = sub.add_parser("upload-asset", help="Upload a user asset")
    p_upload.add_argument("--file-path", required=True, help="Path to file to upload")

    return parser


COMMANDS = {
    "me": cmd_me,
    "upload-asset": cmd_upload_asset,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_command(COMMANDS[args.command], args)


if __name__ == "__main__":
    main()
