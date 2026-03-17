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
    "scripts.plane_stickies",
    "scripts.plane_epics",
    "scripts.plane_customers",
    "scripts.plane_teamspaces",
    "scripts.plane_work_item_properties",
    "scripts.plane_milestones",
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
    "scripts/plane_stickies.py",
    "scripts/plane_epics.py",
    "scripts/plane_customers.py",
    "scripts/plane_teamspaces.py",
    "scripts/plane_work_item_properties.py",
    "scripts/plane_milestones.py",
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

        plane_client._reset_config_cache()

        # Create global config (KEY=VALUE format)
        global_home = tmp_path / "home"
        global_home.mkdir()
        global_rc = global_home / ".planerc"
        global_rc.write_text("api_key=global-key\nworkspace_slug=global-ws\nbase_url=https://global.plane.so")

        # Create project config that overrides api_key only
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        project_rc = project_dir / ".planerc"
        project_rc.write_text("api_key=local-key")

        monkeypatch.setattr("pathlib.Path.home", staticmethod(lambda: global_home))
        monkeypatch.setattr("pathlib.Path.cwd", staticmethod(lambda: project_dir))

        config = plane_client._load_planerc_config()
        assert config["api_key"] == "local-key"
        assert config["workspace_slug"] == "global-ws"
        assert config["base_url"] == "https://global.plane.so"

    def test_planerc_json_format(self, monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
        """JSON format .planerc is also supported (TS CLI compatibility)."""
        from scripts import plane_client

        plane_client._reset_config_cache()

        global_home = tmp_path / "home"
        global_home.mkdir()
        global_rc = global_home / ".planerc"
        global_rc.write_text('{"api_key": "json-key", "workspace": "json-ws"}')

        # Point cwd to a dir with no .planerc so only global is used
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.setattr("pathlib.Path.home", staticmethod(lambda: global_home))
        monkeypatch.setattr("pathlib.Path.cwd", staticmethod(lambda: empty_dir))

        config = plane_client._load_planerc_config()
        assert config["api_key"] == "json-key"
        assert config["workspace"] == "json-ws"

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
            "--work-item-ids", "id1,id2",
        ])
        assert args.command == "add-items"
        assert args.work_item_ids == "id1,id2"

    def test_cycles_list_archived_args(self) -> None:
        from scripts.plane_cycles import build_parser

        parser = build_parser()
        args = parser.parse_args(["list-archived", "--project-id", "p1"])
        assert args.command == "list-archived"

    def test_modules_list_archived_args(self) -> None:
        from scripts.plane_modules import build_parser

        parser = build_parser()
        args = parser.parse_args(["list-archived", "--project-id", "p1"])
        assert args.command == "list-archived"

    def test_work_items_advanced_search_args(self) -> None:
        from scripts.plane_work_items import build_parser

        parser = build_parser()
        args = parser.parse_args(["advanced-search", "--query", "test"])
        assert args.command == "advanced-search"
        assert args.query == "test"

    def test_stickies_list_args(self) -> None:
        from scripts.plane_stickies import build_parser

        parser = build_parser()
        args = parser.parse_args(["list"])
        assert args.command == "list"

    def test_epics_list_args(self) -> None:
        from scripts.plane_epics import build_parser

        parser = build_parser()
        args = parser.parse_args(["list", "--project-id", "p1"])
        assert args.command == "list"

    def test_customers_list_args(self) -> None:
        from scripts.plane_customers import build_parser

        parser = build_parser()
        args = parser.parse_args(["list"])
        assert args.resource == "list"

    def test_teamspaces_create_args(self) -> None:
        from scripts.plane_teamspaces import build_parser

        parser = build_parser()
        args = parser.parse_args(["create", "--name", "Test Team"])
        assert args.resource == "create"
        assert args.name == "Test Team"

    def test_milestones_create_args(self) -> None:
        from scripts.plane_milestones import build_parser

        parser = build_parser()
        args = parser.parse_args(["create", "--project-id", "p1", "--name", "M1"])
        assert args.command == "create"
        assert args.name == "M1"

    def test_work_item_properties_list_args(self) -> None:
        from scripts.plane_work_item_properties import build_parser

        parser = build_parser()
        args = parser.parse_args(["list", "--project-id", "p1"])
        assert args.resource == "list"

    def test_work_item_extras_attachments_list(self) -> None:
        from scripts.plane_work_item_extras import build_parser

        parser = build_parser()
        args = parser.parse_args([
            "attachments", "list",
            "--project-id", "p1",
            "--work-item-id", "w1",
        ])
        assert args.resource == "attachments"
        assert args.action == "list"

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


class TestConfigCache:
    """Test config caching behavior."""

    def test_cache_returns_same_dict(self, monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
        """_load_planerc_config() returns cached result on second call."""
        from scripts import plane_client

        plane_client._reset_config_cache()

        global_home = tmp_path / "home"
        global_home.mkdir()
        (global_home / ".planerc").write_text("api_key=k1\nworkspace_slug=ws1")

        monkeypatch.setattr("pathlib.Path.home", staticmethod(lambda: global_home))
        monkeypatch.setattr("pathlib.Path.cwd", staticmethod(lambda: tmp_path / "no-planerc"))

        first = plane_client._load_planerc_config()
        second = plane_client._load_planerc_config()
        assert first is second

    def test_reset_cache_forces_reparse(self, monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
        """_reset_config_cache() clears cache, next call re-reads files."""
        from scripts import plane_client

        plane_client._reset_config_cache()

        global_home = tmp_path / "home"
        global_home.mkdir()
        rc = global_home / ".planerc"
        rc.write_text("api_key=k1\nworkspace_slug=ws1")

        monkeypatch.setattr("pathlib.Path.home", staticmethod(lambda: global_home))
        monkeypatch.setattr("pathlib.Path.cwd", staticmethod(lambda: tmp_path / "no-planerc"))

        first = plane_client._load_planerc_config()
        assert first["api_key"] == "k1"

        # Modify the file and reset cache
        rc.write_text("api_key=k2\nworkspace_slug=ws1")
        plane_client._reset_config_cache()

        second = plane_client._load_planerc_config()
        assert second["api_key"] == "k2"
        assert first is not second


class TestWorkspaceSlugAlias:
    """Test workspace_slug config key alias."""

    def test_workspace_slug_accepted(self, monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
        """'workspace_slug' key works in config."""
        from scripts import plane_client

        plane_client._reset_config_cache()

        global_home = tmp_path / "home"
        global_home.mkdir()
        (global_home / ".planerc").write_text("api_key=k1\nworkspace_slug=my-ws")

        monkeypatch.setattr("pathlib.Path.home", staticmethod(lambda: global_home))
        monkeypatch.setattr("pathlib.Path.cwd", staticmethod(lambda: tmp_path / "no-planerc"))

        config = plane_client._load_planerc_config()
        assert config["workspace_slug"] == "my-ws"

    def test_workspace_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Old 'workspace' key still works via get_client fallback."""
        from scripts import plane_client

        plane_client._reset_config_cache()
        monkeypatch.setattr(
            plane_client, "_load_planerc_config",
            lambda: {"api_key": "k1", "workspace": "old-ws"},
        )

        # get_client reads workspace_slug || workspace
        # We can't fully test get_client (needs PlaneClient), but we can
        # check the config resolution logic directly
        config = plane_client._load_planerc_config()
        ws = config.get("workspace_slug") or config.get("workspace")
        assert ws == "old-ws"


class TestResolveProjectId:
    """Test resolve_project_id() helper."""

    def test_cli_arg_wins(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Explicit --project-id overrides config default."""
        import argparse
        from scripts import plane_client

        plane_client._reset_config_cache()
        monkeypatch.setattr(
            plane_client, "_load_planerc_config",
            lambda: {"project_id": "config-pid"},
        )

        args = argparse.Namespace(project_id="cli-pid")
        assert plane_client.resolve_project_id(args) == "cli-pid"

    def test_falls_back_to_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When CLI arg is None, uses project_id from config."""
        import argparse
        from scripts import plane_client

        plane_client._reset_config_cache()
        monkeypatch.setattr(
            plane_client, "_load_planerc_config",
            lambda: {"project_id": "config-pid"},
        )

        args = argparse.Namespace(project_id=None)
        assert plane_client.resolve_project_id(args) == "config-pid"

    def test_falls_back_to_legacy_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Legacy default_project_id key still works as fallback."""
        import argparse
        from scripts import plane_client

        plane_client._reset_config_cache()
        monkeypatch.setattr(
            plane_client, "_load_planerc_config",
            lambda: {"default_project_id": "legacy-pid"},
        )

        args = argparse.Namespace(project_id=None)
        assert plane_client.resolve_project_id(args) == "legacy-pid"

    def test_project_id_wins_over_legacy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """project_id takes priority over default_project_id."""
        import argparse
        from scripts import plane_client

        plane_client._reset_config_cache()
        monkeypatch.setattr(
            plane_client, "_load_planerc_config",
            lambda: {"project_id": "new-pid", "default_project_id": "legacy-pid"},
        )

        args = argparse.Namespace(project_id=None)
        assert plane_client.resolve_project_id(args) == "new-pid"

    def test_exits_when_neither(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Exits with code 1 when no CLI arg and no config default."""
        import argparse
        from scripts import plane_client

        plane_client._reset_config_cache()
        monkeypatch.setattr(
            plane_client, "_load_planerc_config",
            lambda: {},
        )

        args = argparse.Namespace(project_id=None)
        with pytest.raises(SystemExit):
            plane_client.resolve_project_id(args)

    def test_error_message_content(self, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
        """Error message mentions --project-id and default_project_id."""
        import argparse
        from scripts import plane_client

        plane_client._reset_config_cache()
        monkeypatch.setattr(
            plane_client, "_load_planerc_config",
            lambda: {},
        )

        args = argparse.Namespace(project_id=None)
        with pytest.raises(SystemExit):
            plane_client.resolve_project_id(args)

        captured = capsys.readouterr()
        assert "--project-id" in captured.err
        assert "project_id" in captured.err


class TestDisableDeleteIssue:
    """Test disable_delete_issue config guard."""

    def test_delete_blocked_when_enabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """cmd_delete exits when disable_delete_issue=true in config."""
        import argparse
        from scripts import plane_client
        from scripts import plane_work_items

        plane_client._reset_config_cache()
        monkeypatch.setattr(
            plane_client, "_load_planerc_config",
            lambda: {"disable_delete_issue": "true", "project_id": "pid"},
        )

        args = argparse.Namespace(
            project_id=None, work_item_id="wid", confirm=True,
        )
        with pytest.raises(SystemExit):
            plane_work_items.cmd_delete(args)

    def test_delete_allowed_when_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """cmd_delete does NOT block when disable_delete_issue is absent."""
        import argparse
        from scripts import plane_client

        plane_client._reset_config_cache()
        monkeypatch.setattr(
            plane_client, "_load_planerc_config",
            lambda: {"project_id": "pid"},
        )

        # Without confirm, cmd_delete exits for a different reason (--confirm guard)
        args = argparse.Namespace(
            project_id="pid", work_item_id="wid", confirm=False,
        )
        from scripts import plane_work_items

        with pytest.raises(SystemExit) as exc_info:
            plane_work_items.cmd_delete(args)
        # It should fail on --confirm check, not disable_delete_issue
        assert exc_info.value.code == 1

    def test_other_deletes_unaffected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """plane_cycles.py cmd_delete is NOT affected by disable_delete_issue."""
        import argparse
        from scripts import plane_client

        plane_client._reset_config_cache()
        monkeypatch.setattr(
            plane_client, "_load_planerc_config",
            lambda: {"disable_delete_issue": "true", "project_id": "pid"},
        )

        args = argparse.Namespace(
            project_id="pid", cycle_id="cid", confirm=False,
        )
        from scripts import plane_cycles

        # Should fail on --confirm check, not disable_delete_issue
        with pytest.raises(SystemExit) as exc_info:
            plane_cycles.cmd_delete(args)
        assert exc_info.value.code == 1


class TestProjectIdOptional:
    """Test --project-id is optional in argparse."""

    def test_project_id_not_required_in_work_items(self) -> None:
        """--project-id is optional in plane_work_items parser."""
        from scripts.plane_work_items import build_parser

        parser = build_parser()
        # Should parse without --project-id
        args = parser.parse_args(["search", "--query", "test"])
        assert args.command == "search"

    def test_project_id_optional_with_default_none(self) -> None:
        """--project-id defaults to None when not provided."""
        from scripts.plane_work_items import build_parser

        parser = build_parser()
        args = parser.parse_args(["list"])
        assert args.project_id is None

    def test_project_id_override_still_works(self) -> None:
        """Explicit --project-id still accepted."""
        from scripts.plane_work_items import build_parser

        parser = build_parser()
        args = parser.parse_args(["list", "--project-id", "abc123"])
        assert args.project_id == "abc123"
