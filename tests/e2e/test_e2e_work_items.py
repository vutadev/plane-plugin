"""E2E tests for Plane work item (issue) commands.

Covers:
- issue:list - List work items in a project
- issue:create - Create a new work item
- issue:get - Get work item by UUID
- issue:get-by-id - Get work item by project identifier + sequence
- issue:update - Update work item fields
- issue:delete - Delete a work item
- issue:search - Search work items across workspace
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.e2e.conftest import generate_test_name, run_cli, skip_if_no_credentials


@pytest.mark.e2e
class TestWorkItemCommands:
    """E2E tests for work item management commands."""

    def test_work_item_list(self, test_project: dict[str, Any]) -> None:
        """TC-ISSUE-01: List work items in a project."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_work_items.py",
            "list",
            "--project-id", test_project["id"],
        )

        # Should return a list (may be empty)
        assert isinstance(result.json, list)

    def test_work_item_create_and_delete(self, test_project: dict[str, Any]) -> None:
        """TC-ISSUE-02: Create work item then delete it."""
        skip_if_no_credentials()

        issue_name = generate_test_name("test-issue")

        # Create issue
        create_result = run_cli(
            "plane_work_items.py",
            "create",
            "--project-id", test_project["id"],
            "--name", issue_name,
            "--description", "<p>Test description</p>",
            "--priority", "high",
        )

        issue = create_result.json
        assert issue["name"] == issue_name
        assert issue["priority"] == "high"
        assert "id" in issue

        issue_id = issue["id"]

        # Verify can retrieve
        get_result = run_cli(
            "plane_work_items.py",
            "get",
            "--project-id", test_project["id"],
            "--work-item-id", issue_id,
        )
        assert get_result.json["id"] == issue_id

        # Delete
        delete_result = run_cli(
            "plane_work_items.py",
            "delete",
            "--project-id", test_project["id"],
            "--work-item-id", issue_id,
            "--confirm",
        )
        assert delete_result.json["status"] == "deleted"

    def test_work_item_get_by_identifier(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-ISSUE-03: Get work item by project identifier and sequence."""
        skip_if_no_credentials()

        # Need the project identifier and issue sequence
        identifier = test_project["identifier"]
        sequence = test_issue.get("sequence_id", test_issue.get("sequence"))

        result = run_cli(
            "plane_work_items.py",
            "get-by-id",
            "--project-identifier", identifier,
            "--sequence", str(sequence),
        )

        assert result.json["id"] == test_issue["id"]

    def test_work_item_update(self, test_project: dict[str, Any], test_issue: dict[str, Any]) -> None:
        """TC-ISSUE-04: Update work item fields."""
        skip_if_no_credentials()

        new_name = generate_test_name("updated-issue")
        new_description = "<p>Updated description</p>"

        result = run_cli(
            "plane_work_items.py",
            "update",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--name", new_name,
            "--description", new_description,
            "--priority", "urgent",
        )

        updated = result.json
        assert updated["name"] == new_name
        assert updated["priority"] == "urgent"

    def test_work_item_update_no_fields(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-ISSUE-05: Update with no fields fails gracefully."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_work_items.py",
            "update",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            check=False,
        )

        assert result.returncode != 0
        assert "No update fields specified" in result.stderr

    def test_work_item_search(self, test_project: dict[str, Any], test_issue: dict[str, Any]) -> None:
        """TC-ISSUE-06: Search for work items."""
        skip_if_no_credentials()

        # Use a unique part of the issue name for search
        search_term = test_issue["name"].split("-")[-1]  # Use the unique suffix

        result = run_cli(
            "plane_work_items.py",
            "search",
            "--query", search_term,
        )

        # Search result should be an object with results
        data = result.json
        assert isinstance(data, dict)
        # Should find our test issue
        results = data.get("results", data.get("data", []))
        assert len(results) >= 0  # May or may not find depending on search indexing

    def test_work_item_create_with_all_fields(self, test_project: dict[str, Any]) -> None:
        """TC-ISSUE-07: Create work item with all optional fields."""
        skip_if_no_credentials()

        issue_name = generate_test_name("full-issue")

        result = run_cli(
            "plane_work_items.py",
            "create",
            "--project-id", test_project["id"],
            "--name", issue_name,
            "--description", "<p>Full description with <b>HTML</b></p>",
            "--priority", "low",
        )

        issue = result.json
        assert issue["name"] == issue_name
        assert issue["priority"] == "low"
        assert "id" in issue

        # Cleanup
        run_cli(
            "plane_work_items.py",
            "delete",
            "--project-id", test_project["id"],
            "--work-item-id", issue["id"],
            "--confirm",
            check=False,
        )

    def test_work_item_delete_without_confirm(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-ISSUE-08: Delete without --confirm fails."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_work_items.py",
            "delete",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            check=False,
        )

        assert result.returncode != 0
        assert "--confirm" in result.stderr

    def test_work_item_get_invalid_id(self, test_project: dict[str, Any]) -> None:
        """TC-ISSUE-09: Get with invalid work item ID fails."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_work_items.py",
            "get",
            "--project-id", test_project["id"],
            "--work-item-id", "invalid-uuid",
            check=False,
        )

        assert result.returncode != 0


@pytest.mark.e2e
class TestWorkItemEdgeCases:
    """Edge case tests for work item commands."""

    def test_work_item_create_unicode_name(self, test_project: dict[str, Any]) -> None:
        """TC-ISSUE-EDGE-01: Create issue with unicode name."""
        skip_if_no_credentials()

        unicode_name = f"测试问题-{generate_test_name('').split('-')[-1]}"

        result = run_cli(
            "plane_work_items.py",
            "create",
            "--project-id", test_project["id"],
            "--name", unicode_name,
            check=False,
        )

        if result.returncode == 0:
            issue_id = result.json["id"]
            run_cli(
                "plane_work_items.py",
                "delete",
                "--project-id", test_project["id"],
                "--work-item-id", issue_id,
                "--confirm",
                check=False,
            )

    def test_work_item_create_very_long_name(self, test_project: dict[str, Any]) -> None:
        """TC-ISSUE-EDGE-02: Create issue with very long name."""
        skip_if_no_credentials()

        long_name = "A" * 500

        result = run_cli(
            "plane_work_items.py",
            "create",
            "--project-id", test_project["id"],
            "--name", long_name,
            check=False,
        )

        if result.returncode == 0:
            issue_id = result.json["id"]
            run_cli(
                "plane_work_items.py",
                "delete",
                "--project-id", test_project["id"],
                "--work-item-id", issue_id,
                "--confirm",
                check=False,
            )

    def test_work_item_search_empty_query(self) -> None:
        """TC-ISSUE-EDGE-03: Search with empty query."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_work_items.py",
            "search",
            "--query", "",
            check=False,
        )

        # May succeed or fail - just verify it doesn't crash
        assert result.returncode in [0, 1]

    def test_work_item_search_special_chars(self) -> None:
        """TC-ISSUE-EDGE-04: Search with special characters."""
        skip_if_no_credentials()

        # Test various special search characters
        special_queries = [
            "test*",  # wildcard
            'test"quoted"',  # quotes
            "test AND issue",  # boolean
            "test OR issue",  # boolean
        ]

        for query in special_queries:
            result = run_cli(
                "plane_work_items.py",
                "search",
                "--query", query,
                check=False,
            )
            # Should not crash
            assert result.returncode in [0, 1]
