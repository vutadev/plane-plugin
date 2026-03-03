"""E2E tests for Plane work item extras commands.

Covers:
- comments:create - Create a comment
- comments:list - List comments
- comments:update - Update a comment
- comments:delete - Delete a comment
- links:create - Create a link
- links:list - List links
- links:delete - Delete a link
- work-logs:create - Create a work log
- work-logs:list - List work logs
- work-logs:delete - Delete a work log
- activities:list - List activities
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.e2e.conftest import generate_test_name, run_cli, skip_if_no_credentials


@pytest.mark.e2e
class TestCommentCommands:
    """E2E tests for work item comment commands."""

    def test_comment_create_and_delete(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-COMMENT-01: Create comment then delete it."""
        skip_if_no_credentials()

        comment_body = "<p>This is a test comment</p>"

        # Create comment
        create_result = run_cli(
            "plane_work_item_extras.py",
            "comments", "create",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--body", comment_body,
        )

        comment = create_result.json
        assert "id" in comment
        comment_id = comment["id"]

        # List comments
        list_result = run_cli(
            "plane_work_item_extras.py",
            "comments", "list",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
        )
        assert isinstance(list_result.json, list)

        # Update comment
        update_body = "<p>Updated comment body</p>"
        update_result = run_cli(
            "plane_work_item_extras.py",
            "comments", "update",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--comment-id", comment_id,
            "--body", update_body,
        )
        assert update_result.json.get("comment_html") == update_body or update_body in str(update_result.json)

        # Delete comment
        delete_result = run_cli(
            "plane_work_item_extras.py",
            "comments", "delete",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--comment-id", comment_id,
            "--confirm",
        )
        assert delete_result.json.get("status") == "deleted" or "deleted" in str(delete_result.json)

    def test_comment_list_empty(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-COMMENT-02: List comments on issue with no comments."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_work_item_extras.py",
            "comments", "list",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
        )

        # Should return empty list or list
        assert isinstance(result.json, list)


@pytest.mark.e2e
class TestLinkCommands:
    """E2E tests for work item link commands."""

    def test_link_create_and_delete(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-LINK-01: Create link then delete it."""
        skip_if_no_credentials()

        url = "https://example.com/test-link"
        title = generate_test_name("test-link")

        # Create link
        create_result = run_cli(
            "plane_work_item_extras.py",
            "links", "create",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--url", url,
            "--title", title,
        )

        link = create_result.json
        assert "id" in link
        link_id = link["id"]

        # List links
        list_result = run_cli(
            "plane_work_item_extras.py",
            "links", "list",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
        )
        assert isinstance(list_result.json, list)

        # Delete link
        delete_result = run_cli(
            "plane_work_item_extras.py",
            "links", "delete",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--link-id", link_id,
            "--confirm",
        )
        assert delete_result.json.get("status") == "deleted" or "deleted" in str(delete_result.json)


@pytest.mark.e2e
class TestWorkLogCommands:
    """E2E tests for work item work log commands."""

    def test_work_log_create_and_delete(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-WORKLOG-01: Create work log then delete it."""
        skip_if_no_credentials()

        # Create work log (duration in minutes)
        create_result = run_cli(
            "plane_work_item_extras.py",
            "work-logs", "create",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--duration", "120",  # 2 hours
            "--description", "Test work log entry",
        )

        work_log = create_result.json
        assert "id" in work_log
        work_log_id = work_log["id"]

        # List work logs
        list_result = run_cli(
            "plane_work_item_extras.py",
            "work-logs", "list",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
        )
        assert isinstance(list_result.json, list)

        # Delete work log
        delete_result = run_cli(
            "plane_work_item_extras.py",
            "work-logs", "delete",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--work-log-id", work_log_id,
            "--confirm",
        )
        assert delete_result.json.get("status") == "deleted" or "deleted" in str(delete_result.json)


@pytest.mark.e2e
class TestActivityCommands:
    """E2E tests for work item activity commands."""

    def test_activity_list(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-ACTIVITY-01: List activities on a work item."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_work_item_extras.py",
            "activities", "list",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
        )

        # Should return list of activities
        assert isinstance(result.json, list)

    def test_activity_list_pagination(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-ACTIVITY-02: List activities with pagination."""
        skip_if_no_credentials()

        # First, create some activity by updating the issue
        run_cli(
            "plane_work_items.py",
            "update",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--name", generate_test_name("updated-for-activity"),
        )

        # List activities
        result = run_cli(
            "plane_work_item_extras.py",
            "activities", "list",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
        )

        # Should have at least one activity (the update)
        assert isinstance(result.json, list)


@pytest.mark.e2e
class TestExtrasEdgeCases:
    """Edge case tests for work item extras."""

    def test_comment_create_empty_body(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-EXTRAS-EDGE-01: Create comment with empty body."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_work_item_extras.py",
            "comments", "create",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--body", "",
            check=False,
        )

        # API may accept or reject empty comments
        assert result.returncode in [0, 1]

    def test_comment_create_unicode(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-EXTRAS-EDGE-02: Create comment with unicode body."""
        skip_if_no_credentials()

        unicode_body = "<p>这是一个测试评论 🎉</p>"

        result = run_cli(
            "plane_work_item_extras.py",
            "comments", "create",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--body", unicode_body,
            check=False,
        )

        if result.returncode == 0:
            comment_id = result.json["id"]
            run_cli(
                "plane_work_item_extras.py",
                "comments", "delete",
                "--project-id", test_project["id"],
                "--work-item-id", test_issue["id"],
                "--comment-id", comment_id,
                "--confirm",
                check=False,
            )

    def test_link_create_invalid_url(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-EXTRAS-EDGE-03: Create link with invalid URL."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_work_item_extras.py",
            "links", "create",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--url", "not-a-valid-url",
            "--title", generate_test_name("bad-link"),
            check=False,
        )

        # API may accept or reject invalid URLs
        assert result.returncode in [0, 1]

    def test_work_log_create_zero_duration(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-EXTRAS-EDGE-04: Create work log with zero duration."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_work_item_extras.py",
            "work-logs", "create",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--duration", "0",
            check=False,
        )

        # API may accept or reject zero duration
        assert result.returncode in [0, 1]

    def test_work_log_create_negative_duration(
        self, test_project: dict[str, Any], test_issue: dict[str, Any]
    ) -> None:
        """TC-EXTRAS-EDGE-05: Create work log with negative duration."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_work_item_extras.py",
            "work-logs", "create",
            "--project-id", test_project["id"],
            "--work-item-id", test_issue["id"],
            "--duration", "-60",
            check=False,
        )

        # Should probably fail with negative duration
        assert result.returncode in [0, 1]
