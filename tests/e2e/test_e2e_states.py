"""E2E tests for Plane state commands.

Covers:
- state:list - List states in a project
- state:create - Create a new state
- state:get - Get state details
- state:update - Update state
- state:delete - Delete a state
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.e2e.conftest import generate_test_name, run_cli, skip_if_no_credentials


# State groups in Plane
STATE_GROUPS = ["backlog", "unstarted", "started", "completed", "cancelled"]

# Common state colors
STATE_COLORS = [
    "#3b82f6",  # blue
    "#22c55e",  # green
    "#ef4444",  # red
    "#f59e0b",  # amber
    "#8b5cf6",  # violet
    "#6b7280",  # gray
]


@pytest.mark.e2e
class TestStateCommands:
    """E2E tests for state management commands."""

    def test_state_list(self, test_project: dict[str, Any]) -> None:
        """TC-STATE-01: List states in a project."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_states.py",
            "list",
            "--project-id", test_project["id"],
        )

        assert isinstance(result.json, list)

        # Verify default states exist (backlog, todo, in progress, done)
        # At minimum, we should have some states
        if len(result.json) > 0:
            state = result.json[0]
            assert "id" in state
            assert "name" in state
            assert "group" in state

    def test_state_create_and_delete(self, test_project: dict[str, Any]) -> None:
        """TC-STATE-02: Create state then delete it."""
        skip_if_no_credentials()

        state_name = generate_test_name("test-state")

        create_result = run_cli(
            "plane_states.py",
            "create",
            "--project-id", test_project["id"],
            "--name", state_name,
            "--group", "backlog",
            "--color", "#3b82f6",
        )

        state = create_result.json
        assert state["name"] == state_name
        assert state["group"] == "backlog"
        assert "id" in state

        state_id = state["id"]

        # Get state
        get_result = run_cli(
            "plane_states.py",
            "get",
            "--project-id", test_project["id"],
            "--state-id", state_id,
        )
        assert get_result.json["id"] == state_id

        # Delete
        delete_result = run_cli(
            "plane_states.py",
            "delete",
            "--project-id", test_project["id"],
            "--state-id", state_id,
            "--confirm",
        )
        assert delete_result.json["status"] == "deleted"

    def test_state_update(self, test_project: dict[str, Any]) -> None:
        """TC-STATE-03: Update state fields."""
        skip_if_no_credentials()

        state_name = generate_test_name("update-state")

        create_result = run_cli(
            "plane_states.py",
            "create",
            "--project-id", test_project["id"],
            "--name", state_name,
            "--group", "backlog",
            "--color", "#3b82f6",
        )

        state_id = create_result.json["id"]

        try:
            new_name = generate_test_name("updated-state")

            update_result = run_cli(
                "plane_states.py",
                "update",
                "--project-id", test_project["id"],
                "--state-id", state_id,
                "--name", new_name,
                "--color", "#22c55e",
            )

            assert update_result.json["name"] == new_name
            assert update_result.json["color"] == "#22c55e"
        finally:
            run_cli(
                "plane_states.py",
                "delete",
                "--project-id", test_project["id"],
                "--state-id", state_id,
                "--confirm",
                check=False,
            )

    def test_state_create_all_groups(self, test_project: dict[str, Any]) -> None:
        """TC-STATE-04: Create states in all groups."""
        skip_if_no_credentials()

        created_states = []

        try:
            for group in STATE_GROUPS:
                state_name = generate_test_name(f"state-{group}")

                result = run_cli(
                    "plane_states.py",
                    "create",
                    "--project-id", test_project["id"],
                    "--name", state_name,
                    "--group", group,
                    "--color", STATE_COLORS[len(created_states) % len(STATE_COLORS)],
                )

                assert result.json["group"] == group
                created_states.append(result.json["id"])
        finally:
            # Cleanup all created states
            for state_id in created_states:
                run_cli(
                    "plane_states.py",
                    "delete",
                    "--project-id", test_project["id"],
                    "--state-id", state_id,
                    "--confirm",
                    check=False,
                )

    def test_state_delete_without_confirm(self, test_project: dict[str, Any]) -> None:
        """TC-STATE-05: Delete without --confirm fails."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_states.py",
            "delete",
            "--project-id", test_project["id"],
            "--state-id", "some-uuid",
            check=False,
        )

        assert result.returncode != 0
        assert "--confirm" in result.stderr

    def test_state_get_invalid_id(self, test_project: dict[str, Any]) -> None:
        """TC-STATE-06: Get state with invalid ID fails."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_states.py",
            "get",
            "--project-id", test_project["id"],
            "--state-id", "invalid-uuid",
            check=False,
        )

        assert result.returncode != 0


@pytest.mark.e2e
class TestStateEdgeCases:
    """Edge case tests for state commands."""

    def test_state_create_invalid_group(self, test_project: dict[str, Any]) -> None:
        """TC-STATE-EDGE-01: Create state with invalid group."""
        skip_if_no_credentials()

        state_name = generate_test_name("invalid-group")

        result = run_cli(
            "plane_states.py",
            "create",
            "--project-id", test_project["id"],
            "--name", state_name,
            "--group", "invalid-group",
            "--color", "#3b82f6",
            check=False,
        )

        # API may accept or reject - just verify no crash
        if result.returncode == 0:
            state_id = result.json["id"]
            run_cli(
                "plane_states.py",
                "delete",
                "--project-id", test_project["id"],
                "--state-id", state_id,
                "--confirm",
                check=False,
            )

    def test_state_create_unicode_name(self, test_project: dict[str, Any]) -> None:
        """TC-STATE-EDGE-02: Create state with unicode name."""
        skip_if_no_credentials()

        unicode_name = f"状态-{generate_test_name('').split('-')[-1]}"

        result = run_cli(
            "plane_states.py",
            "create",
            "--project-id", test_project["id"],
            "--name", unicode_name,
            "--group", "backlog",
            "--color", "#3b82f6",
            check=False,
        )

        if result.returncode == 0:
            state_id = result.json["id"]
            run_cli(
                "plane_states.py",
                "delete",
                "--project-id", test_project["id"],
                "--state-id", state_id,
                "--confirm",
                check=False,
            )

    def test_state_create_duplicate_name(self, test_project: dict[str, Any]) -> None:
        """TC-STATE-EDGE-03: Create state with duplicate name fails."""
        skip_if_no_credentials()

        state_name = generate_test_name("dup-state")

        # Create first state
        result1 = run_cli(
            "plane_states.py",
            "create",
            "--project-id", test_project["id"],
            "--name", state_name,
            "--group", "backlog",
            "--color", "#3b82f6",
        )
        state_id = result1.json["id"]

        try:
            # Try to create duplicate
            result2 = run_cli(
                "plane_states.py",
                "create",
                "--project-id", test_project["id"],
                "--name", state_name,
                "--group", "started",
                "--color", "#22c55e",
                check=False,
            )

            assert result2.returncode != 0
        finally:
            run_cli(
                "plane_states.py",
                "delete",
                "--project-id", test_project["id"],
                "--state-id", state_id,
                "--confirm",
                check=False,
            )
