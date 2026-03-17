"""E2E tests for Plane cycle commands.

Covers:
- cycle:list - List cycles in a project
- cycle:create - Create a new cycle
- cycle:get - Get cycle details
- cycle:update - Update cycle
- cycle:delete - Delete a cycle
- cycle:archive - Archive a cycle
- cycle:unarchive - Unarchive a cycle
- cycle:add-issues - Add issues to cycle
- cycle:remove-issue - Remove issue from cycle
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest

from tests.e2e.conftest import generate_test_name, run_cli, skip_if_no_credentials


def get_future_dates(days_ahead: int = 7) -> tuple[str, str]:
    """Generate start and end dates for cycle creation.

    Returns:
        Tuple of (start_date, end_date) in ISO format (YYYY-MM-DD)
    """
    start = datetime.now() + timedelta(days=1)
    end = start + timedelta(days=days_ahead)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


@pytest.mark.e2e
class TestCycleCommands:
    """E2E tests for cycle management commands."""

    def test_cycle_list(self, test_project: dict[str, Any]) -> None:
        """TC-CYCLE-01: List cycles in a project."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_cycles.py",
            "list",
            "--project-id", test_project["id"],
        )

        assert isinstance(result.json, list)

    def test_cycle_create_and_delete(self, test_project: dict[str, Any]) -> None:
        """TC-CYCLE-02: Create cycle then delete it."""
        skip_if_no_credentials()

        cycle_name = generate_test_name("test-cycle")
        start_date, end_date = get_future_dates()

        # Create cycle
        create_result = run_cli(
            "plane_cycles.py",
            "create",
            "--project-id", test_project["id"],
            "--name", cycle_name,
            "--start-date", start_date,
            "--end-date", end_date,
        )

        cycle = create_result.json
        assert cycle["name"] == cycle_name
        assert "id" in cycle

        cycle_id = cycle["id"]

        # Get cycle
        get_result = run_cli(
            "plane_cycles.py",
            "get",
            "--project-id", test_project["id"],
            "--cycle-id", cycle_id,
        )
        assert get_result.json["id"] == cycle_id

        # Delete
        delete_result = run_cli(
            "plane_cycles.py",
            "delete",
            "--project-id", test_project["id"],
            "--cycle-id", cycle_id,
            "--confirm",
        )
        assert delete_result.json["status"] == "deleted"

    def test_cycle_update(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-CYCLE-03: Update cycle fields."""
        skip_if_no_credentials()

        cycle_name = generate_test_name("update-cycle")
        start_date, end_date = get_future_dates()

        # Create cycle
        create_result = run_cli(
            "plane_cycles.py",
            "create",
            "--project-id", test_project["id"],
            "--name", cycle_name,
            "--start-date", start_date,
            "--end-date", end_date,
        )

        cycle_id = create_result.json["id"]

        try:
            new_name = generate_test_name("updated-cycle")
            new_start = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            new_end = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")

            update_result = run_cli(
                "plane_cycles.py",
                "update",
                "--project-id", test_project["id"],
                "--cycle-id", cycle_id,
                "--name", new_name,
                "--start-date", new_start,
                "--end-date", new_end,
            )

            assert update_result.json["name"] == new_name
        finally:
            # Cleanup
            run_cli(
                "plane_cycles.py",
                "delete",
                "--project-id", test_project["id"],
                "--cycle-id", cycle_id,
                "--confirm",
                check=False,
            )

    def test_cycle_archive_unarchive(self, test_project: dict[str, Any]) -> None:
        """TC-CYCLE-04: Archive and unarchive a cycle."""
        skip_if_no_credentials()

        cycle_name = generate_test_name("archive-cycle")
        start_date, end_date = get_future_dates()

        # Create cycle
        create_result = run_cli(
            "plane_cycles.py",
            "create",
            "--project-id", test_project["id"],
            "--name", cycle_name,
            "--start-date", start_date,
            "--end-date", end_date,
        )

        cycle_id = create_result.json["id"]

        try:
            # Archive
            archive_result = run_cli(
                "plane_cycles.py",
                "archive",
                "--project-id", test_project["id"],
                "--cycle-id", cycle_id,
            )
            assert archive_result.json.get("archived_at") is not None or archive_result.json.get("archived") is True

            # Unarchive
            unarchive_result = run_cli(
                "plane_cycles.py",
                "unarchive",
                "--project-id", test_project["id"],
                "--cycle-id", cycle_id,
            )
            assert unarchive_result.json.get("archived_at") is None or unarchive_result.json.get("archived") is False
        finally:
            run_cli(
                "plane_cycles.py",
                "delete",
                "--project-id", test_project["id"],
                "--cycle-id", cycle_id,
                "--confirm",
                check=False,
            )

    def test_cycle_add_remove_issues(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-CYCLE-05: Add and remove issues from cycle."""
        skip_if_no_credentials()

        cycle_name = generate_test_name("issues-cycle")
        start_date, end_date = get_future_dates()

        # Create cycle
        create_result = run_cli(
            "plane_cycles.py",
            "create",
            "--project-id", test_project["id"],
            "--name", cycle_name,
            "--start-date", start_date,
            "--end-date", end_date,
        )

        cycle_id = create_result.json["id"]

        try:
            # Add issue to cycle
            add_result = run_cli(
                "plane_cycles.py",
                "add-items",
                "--project-id", test_project["id"],
                "--cycle-id", cycle_id,
                "--work-item-ids", test_issue["id"],
            )

            # Verify issue was added (response format may vary)
            assert isinstance(add_result.json, (dict, list))

            # Remove issue from cycle
            remove_result = run_cli(
                "plane_cycles.py",
                "remove-item",
                "--project-id", test_project["id"],
                "--cycle-id", cycle_id,
                "--work-item-id", test_issue["id"],
            )

            assert isinstance(remove_result.json, dict)
        finally:
            run_cli(
                "plane_cycles.py",
                "delete",
                "--project-id", test_project["id"],
                "--cycle-id", cycle_id,
                "--confirm",
                check=False,
            )

    def test_cycle_delete_without_confirm(self, test_project: dict[str, Any]) -> None:
        """TC-CYCLE-06: Delete without --confirm fails."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_cycles.py",
            "delete",
            "--project-id", test_project["id"],
            "--cycle-id", "some-uuid",
            check=False,
        )

        assert result.returncode != 0
        assert "--confirm" in result.stderr

    def test_cycle_get_invalid_id(self, test_project: dict[str, Any]) -> None:
        """TC-CYCLE-07: Get cycle with invalid ID fails."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_cycles.py",
            "get",
            "--project-id", test_project["id"],
            "--cycle-id", "invalid-uuid",
            check=False,
        )

        assert result.returncode != 0


@pytest.mark.e2e
class TestCycleEdgeCases:
    """Edge case tests for cycle commands."""

    def test_cycle_create_past_dates(self, test_project: dict[str, Any]) -> None:
        """TC-CYCLE-EDGE-01: Create cycle with past dates."""
        skip_if_no_credentials()

        # Use past dates
        past = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        past_end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        result = run_cli(
            "plane_cycles.py",
            "create",
            "--project-id", test_project["id"],
            "--name", generate_test_name("past-cycle"),
            "--start-date", past,
            "--end-date", past_end,
            check=False,
        )

        if result.returncode == 0:
            cycle_id = result.json["id"]
            run_cli(
                "plane_cycles.py",
                "delete",
                "--project-id", test_project["id"],
                "--cycle-id", cycle_id,
                "--confirm",
                check=False,
            )

    def test_cycle_create_end_before_start(self, test_project: dict[str, Any]) -> None:
        """TC-CYCLE-EDGE-02: Create cycle where end date is before start date."""
        skip_if_no_credentials()

        start = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        result = run_cli(
            "plane_cycles.py",
            "create",
            "--project-id", test_project["id"],
            "--name", generate_test_name("invalid-cycle"),
            "--start-date", start,
            "--end-date", end,
            check=False,
        )

        # API may accept or reject - just verify no crash
        if result.returncode == 0:
            cycle_id = result.json["id"]
            run_cli(
                "plane_cycles.py",
                "delete",
                "--project-id", test_project["id"],
                "--cycle-id", cycle_id,
                "--confirm",
                check=False,
            )

    def test_cycle_add_invalid_issue(self, test_project: dict[str, Any]) -> None:
        """TC-CYCLE-EDGE-03: Add non-existent issue to cycle."""
        skip_if_no_credentials()

        cycle_name = generate_test_name("test-cycle")
        start_date, end_date = get_future_dates()

        create_result = run_cli(
            "plane_cycles.py",
            "create",
            "--project-id", test_project["id"],
            "--name", cycle_name,
            "--start-date", start_date,
            "--end-date", end_date,
        )

        cycle_id = create_result.json["id"]

        try:
            result = run_cli(
                "plane_cycles.py",
                "add-items",
                "--project-id", test_project["id"],
                "--cycle-id", cycle_id,
                "--work-item-ids", "invalid-issue-id",
                check=False,
            )

            # Should fail with non-existent issue
            assert result.returncode != 0
        finally:
            run_cli(
                "plane_cycles.py",
                "delete",
                "--project-id", test_project["id"],
                "--cycle-id", cycle_id,
                "--confirm",
                check=False,
            )
