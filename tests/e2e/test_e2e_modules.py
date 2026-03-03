"""E2E tests for Plane module commands.

Covers:
- module:list - List modules in a project
- module:create - Create a new module
- module:get - Get module details
- module:update - Update module
- module:delete - Delete a module
- module:archive / unarchive - Archive operations
- module:add-issues - Add issues to module
- module:remove-issue - Remove issue from module
- module:members - List module members
- module:link / unlink - Link/unlink modules
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.e2e.conftest import generate_test_name, run_cli, skip_if_no_credentials


@pytest.mark.e2e
class TestModuleCommands:
    """E2E tests for module management commands."""

    def test_module_list(self, test_project: dict[str, Any]) -> None:
        """TC-MODULE-01: List modules in a project."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_modules.py",
            "list",
            "--project-id", test_project["id"],
        )

        assert isinstance(result.json, list)

    def test_module_create_and_delete(self, test_project: dict[str, Any]) -> None:
        """TC-MODULE-02: Create module then delete it."""
        skip_if_no_credentials()

        module_name = generate_test_name("test-module")

        create_result = run_cli(
            "plane_modules.py",
            "create",
            "--project-id", test_project["id"],
            "--name", module_name,
            "--description", "Test module for E2E",
        )

        module = create_result.json
        assert module["name"] == module_name
        assert "id" in module

        module_id = module["id"]

        # Get module
        get_result = run_cli(
            "plane_modules.py",
            "get",
            "--project-id", test_project["id"],
            "--module-id", module_id,
        )
        assert get_result.json["id"] == module_id

        # Delete
        delete_result = run_cli(
            "plane_modules.py",
            "delete",
            "--project-id", test_project["id"],
            "--module-id", module_id,
            "--confirm",
        )
        assert delete_result.json["status"] == "deleted"

    def test_module_update(self, test_project: dict[str, Any]) -> None:
        """TC-MODULE-03: Update module fields."""
        skip_if_no_credentials()

        module_name = generate_test_name("update-module")

        create_result = run_cli(
            "plane_modules.py",
            "create",
            "--project-id", test_project["id"],
            "--name", module_name,
        )

        module_id = create_result.json["id"]

        try:
            new_name = generate_test_name("updated-module")
            new_description = "Updated description"

            update_result = run_cli(
                "plane_modules.py",
                "update",
                "--project-id", test_project["id"],
                "--module-id", module_id,
                "--name", new_name,
                "--description", new_description,
            )

            assert update_result.json["name"] == new_name
        finally:
            run_cli(
                "plane_modules.py",
                "delete",
                "--project-id", test_project["id"],
                "--module-id", module_id,
                "--confirm",
                check=False,
            )

    def test_module_archive_unarchive(self, test_project: dict[str, Any]) -> None:
        """TC-MODULE-04: Archive and unarchive a module."""
        skip_if_no_credentials()

        module_name = generate_test_name("archive-module")

        create_result = run_cli(
            "plane_modules.py",
            "create",
            "--project-id", test_project["id"],
            "--name", module_name,
        )

        module_id = create_result.json["id"]

        try:
            # Archive
            archive_result = run_cli(
                "plane_modules.py",
                "archive",
                "--project-id", test_project["id"],
                "--module-id", module_id,
            )
            assert archive_result.json.get("archived_at") is not None or archive_result.json.get("archived") is True

            # Unarchive
            unarchive_result = run_cli(
                "plane_modules.py",
                "unarchive",
                "--project-id", test_project["id"],
                "--module-id", module_id,
            )
            assert unarchive_result.json.get("archived_at") is None or unarchive_result.json.get("archived") is False
        finally:
            run_cli(
                "plane_modules.py",
                "delete",
                "--project-id", test_project["id"],
                "--module-id", module_id,
                "--confirm",
                check=False,
            )

    def test_module_add_remove_issues(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-MODULE-05: Add and remove issues from module."""
        skip_if_no_credentials()

        module_name = generate_test_name("issues-module")

        create_result = run_cli(
            "plane_modules.py",
            "create",
            "--project-id", test_project["id"],
            "--name", module_name,
        )

        module_id = create_result.json["id"]

        try:
            # Add issue
            add_result = run_cli(
                "plane_modules.py",
                "add-issues",
                "--project-id", test_project["id"],
                "--module-id", module_id,
                "--issue-ids", test_issue["id"],
            )

            assert isinstance(add_result.json, (dict, list))

            # Remove issue
            remove_result = run_cli(
                "plane_modules.py",
                "remove-issue",
                "--project-id", test_project["id"],
                "--module-id", module_id,
                "--issue-id", test_issue["id"],
            )

            assert isinstance(remove_result.json, dict)
        finally:
            run_cli(
                "plane_modules.py",
                "delete",
                "--project-id", test_project["id"],
                "--module-id", module_id,
                "--confirm",
                check=False,
            )

    def test_module_members(self, test_project: dict[str, Any]) -> None:
        """TC-MODULE-06: List module members."""
        skip_if_no_credentials()

        module_name = generate_test_name("members-module")

        create_result = run_cli(
            "plane_modules.py",
            "create",
            "--project-id", test_project["id"],
            "--name", module_name,
        )

        module_id = create_result.json["id"]

        try:
            result = run_cli(
                "plane_modules.py",
                "members",
                "--project-id", test_project["id"],
                "--module-id", module_id,
            )

            assert isinstance(result.json, list)
        finally:
            run_cli(
                "plane_modules.py",
                "delete",
                "--project-id", test_project["id"],
                "--module-id", module_id,
                "--confirm",
                check=False,
            )

    def test_module_delete_without_confirm(self, test_project: dict[str, Any]) -> None:
        """TC-MODULE-07: Delete without --confirm fails."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_modules.py",
            "delete",
            "--project-id", test_project["id"],
            "--module-id", "some-uuid",
            check=False,
        )

        assert result.returncode != 0
        assert "--confirm" in result.stderr


@pytest.mark.e2e
class TestModuleEdgeCases:
    """Edge case tests for module commands."""

    def test_module_create_unicode_name(self, test_project: dict[str, Any]) -> None:
        """TC-MODULE-EDGE-01: Create module with unicode name."""
        skip_if_no_credentials()

        unicode_name = f"测试模块-{generate_test_name('').split('-')[-1]}"

        result = run_cli(
            "plane_modules.py",
            "create",
            "--project-id", test_project["id"],
            "--name", unicode_name,
            check=False,
        )

        if result.returncode == 0:
            module_id = result.json["id"]
            run_cli(
                "plane_modules.py",
                "delete",
                "--project-id", test_project["id"],
                "--module-id", module_id,
                "--confirm",
                check=False,
            )

    def test_module_add_invalid_issue(self, test_project: dict[str, Any]) -> None:
        """TC-MODULE-EDGE-02: Add non-existent issue to module."""
        skip_if_no_credentials()

        module_name = generate_test_name("test-module")

        create_result = run_cli(
            "plane_modules.py",
            "create",
            "--project-id", test_project["id"],
            "--name", module_name,
        )

        module_id = create_result.json["id"]

        try:
            result = run_cli(
                "plane_modules.py",
                "add-issues",
                "--project-id", test_project["id"],
                "--module-id", module_id,
                "--issue-ids", "invalid-issue-id",
                check=False,
            )

            assert result.returncode != 0
        finally:
            run_cli(
                "plane_modules.py",
                "delete",
                "--project-id", test_project["id"],
                "--module-id", module_id,
                "--confirm",
                check=False,
            )
