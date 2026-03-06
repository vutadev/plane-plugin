#!/usr/bin/env python3
"""Smoke tests for Plane skill scripts.

Verifies:
1. All scripts can be imported
2. All scripts parse --help without error
3. Key arg-parsing works correctly
4. No live API calls are made
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import os
import pytest

# Ensure skill root is on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_ROOT = os.path.join(ROOT, "skills", "plane")
sys.path.insert(0, SKILL_ROOT)
sys.path.insert(0, ROOT)

SCRIPTS = [
    "scripts.plane_client",
    "scripts.plane_verify",
    "scripts.plane_projects",
    "scripts.plane_work_items",
    "scripts.plane_cycles",
    "scripts.plane_modules",
    "scripts.plane_initiatives",
    "scripts.plane_intake",
    "scripts.plane_labels",
    "scripts.plane_pages",
    "scripts.plane_states",
    "scripts.plane_users",
    "scripts.plane_workspaces",
    "scripts.plane_work_item_extras",
]

SCRIPT_FILES_WITH_HELP = [
    # plane_client.py is a helper module (no argparse)
    # plane_verify.py uses get_client() before argparse
    "scripts/plane_projects.py",
    "scripts/plane_work_items.py",
    "scripts/plane_cycles.py",
    "scripts/plane_modules.py",
    "scripts/plane_initiatives.py",
    "scripts/plane_intake.py",
    "scripts/plane_labels.py",
    "scripts/plane_pages.py",
    "scripts/plane_states.py",
    "scripts/plane_users.py",
    "scripts/plane_workspaces.py",
    "scripts/plane_work_item_extras.py",
]


class TestImports:
    """Verify all scripts can be imported without error."""

    @pytest.mark.parametrize("module_name", SCRIPTS)
    def test_import(self, module_name: str) -> None:
        mod = importlib.import_module(module_name)
        assert mod is not None


class TestHelp:
    """Verify all scripts handle --help correctly."""

    @pytest.mark.parametrize("script", SCRIPT_FILES_WITH_HELP)
    def test_help(self, script: str) -> None:
        result = subprocess.run(
            [sys.executable, os.path.join(SKILL_ROOT, script), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"{script} --help failed: {result.stderr}"
        assert "usage:" in result.stdout.lower() or "help" in result.stdout.lower()


class TestClientHelper:
    """Test the plane_client helper module."""

    def test_get_client_missing_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_client() should exit with error when no .planerc exists."""
        from scripts import plane_client

        monkeypatch.setattr(plane_client, "_load_planerc_config", lambda: {})

        with pytest.raises(SystemExit):
            plane_client.get_client()

    def test_planerc_merge_override(self, monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
        """Project-local .planerc fields override global, non-overridden fields survive."""
        from scripts import plane_client

        # Create global config
        global_home = tmp_path / "home"
        global_home.mkdir()
        global_rc = global_home / ".planerc"
        global_rc.write_text('{"apiKey": "global-key", "workspace": "global-ws", "baseUrl": "https://global.plane.so/api/v1"}')

        # Create local config that overrides apiKey only
        local_dir = tmp_path / "project"
        local_dir.mkdir()
        local_rc = local_dir / ".planerc"
        local_rc.write_text('{"apiKey": "local-key"}')

        monkeypatch.setattr("pathlib.Path.home", staticmethod(lambda: global_home))
        monkeypatch.setattr("pathlib.Path.cwd", staticmethod(lambda: local_dir))

        config = plane_client._load_planerc_config()
        assert config["apiKey"] == "local-key"
        assert config["workspace"] == "global-ws"
        assert config["baseUrl"] == "https://global.plane.so/api/v1"

    def test_dump_json(self) -> None:
        from scripts.plane_client import dump_json

        result = dump_json({"key": "value"})
        assert '"key"' in result
        assert '"value"' in result

    def test_json_serial_dict(self) -> None:
        from scripts.plane_client import json_serial

        class FakeObj:
            def __init__(self):
                self.x = 1

        result = json_serial(FakeObj())
        assert isinstance(result, dict)
        assert result["x"] == 1


class TestArgParsing:
    """Test argparse works correctly for key scripts."""

    def test_projects_list_args(self) -> None:
        from scripts.plane_projects import build_parser

        parser = build_parser()
        args = parser.parse_args(["list"])
        assert args.command == "list"

    def test_projects_create_args(self) -> None:
        from scripts.plane_projects import build_parser

        parser = build_parser()
        args = parser.parse_args(["create", "--name", "Test", "--identifier", "TST"])
        assert args.command == "create"
        assert args.name == "Test"
        assert args.identifier == "TST"

    def test_projects_delete_no_confirm(self) -> None:
        from scripts.plane_projects import build_parser

        parser = build_parser()
        args = parser.parse_args(["delete", "--project-id", "abc123"])
        assert args.command == "delete"
        assert args.confirm is False

    def test_work_items_search_args(self) -> None:
        from scripts.plane_work_items import build_parser

        parser = build_parser()
        args = parser.parse_args(["search", "--query", "login bug"])
        assert args.command == "search"
        assert args.query == "login bug"

    def test_cycles_add_items_args(self) -> None:
        from scripts.plane_cycles import build_parser

        parser = build_parser()
        args = parser.parse_args([
            "add-items",
            "--project-id", "p1",
            "--cycle-id", "c1",
            "--issue-ids", "id1,id2",
        ])
        assert args.command == "add-items"
        assert args.issue_ids == "id1,id2"

    def test_work_item_extras_comments_create(self) -> None:
        from scripts.plane_work_item_extras import build_parser

        parser = build_parser()
        args = parser.parse_args([
            "comments", "create",
            "--project-id", "p1",
            "--work-item-id", "w1",
            "--body", "<p>test</p>",
        ])
        assert args.resource == "comments"
        assert args.action == "create"
        assert args.body == "<p>test</p>"

    def test_skill_md_frontmatter(self) -> None:
        """Verify SKILL.md has valid YAML frontmatter."""
        skill_path = os.path.join(ROOT, "skills/plane/SKILL.md")
        with open(skill_path) as f:
            content = f.read()

        # Check for YAML frontmatter delimiters
        assert content.startswith("---"), "SKILL.md must start with ---"
        # Find closing ---
        second_dash = content.index("---", 3)
        frontmatter = content[3:second_dash].strip()
        assert "name:" in frontmatter
        assert "description:" in frontmatter
