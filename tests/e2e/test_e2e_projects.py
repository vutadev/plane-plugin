"""E2E tests for Plane project commands.

Covers:
- project:list - List all projects
- project:create - Create a new project
- project:get - Get project details
- project:update - Update project fields
- project:delete - Delete a project
- project:members - List project members
- project:features - Get project features
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from tests.e2e.conftest import (
    E2EError,
    generate_test_name,
    run_cli,
    skip_if_no_credentials,
)


@pytest.mark.e2e
class TestProjectCommands:
    """E2E tests for project management commands."""

    def test_project_list(self) -> None:
        """TC-PROJ-01: List projects returns valid response."""
        skip_if_no_credentials()

        result = run_cli("plane_projects.py", "list")

        # Verify response is a list
        assert isinstance(result.json, list)
        # Verify each project has required fields
        for project in result.json:
            assert "id" in project
            assert "name" in project
            assert "identifier" in project

    def test_project_create_and_delete(self) -> None:
        """TC-PROJ-02: Create project then delete it.

        Creates a project, verifies it exists, then deletes it.
        """
        skip_if_no_credentials()

        project_name = generate_test_name("test-create")
        identifier = f"TST{uuid.uuid4().hex[:4].upper()}"

        # Create project
        create_result = run_cli(
            "plane_projects.py",
            "create",
            "--name", project_name,
            "--identifier", identifier,
            "--description", "Test project for E2E",
            "--network", "2",
        )

        project = create_result.json
        assert project["name"] == project_name
        assert project["identifier"] == identifier
        assert "id" in project

        project_id = project["id"]

        # Verify project can be retrieved
        get_result = run_cli(
            "plane_projects.py",
            "get",
            "--project-id", project_id,
        )
        assert get_result.json["id"] == project_id

        # Delete project
        delete_result = run_cli(
            "plane_projects.py",
            "delete",
            "--project-id", project_id,
            "--confirm",
        )
        assert delete_result.json["status"] == "deleted"
        assert delete_result.json["project_id"] == project_id

    def test_project_get_with_invalid_id(self) -> None:
        """TC-PROJ-03: Get project with invalid ID returns error."""
        skip_if_no_credentials()

        invalid_id = "invalid-uuid-12345"

        result = run_cli(
            "plane_projects.py",
            "get",
            "--project-id", invalid_id,
            check=False,
        )

        # Should fail with non-zero exit code
        assert result.returncode != 0

    def test_project_update(self, test_project: dict[str, Any]) -> None:
        """TC-PROJ-04: Update project fields.

        Uses the test_project fixture which auto-cleans up.
        """
        skip_if_no_credentials()

        project_id = test_project["id"]
        new_name = generate_test_name("updated-name")
        new_description = "Updated description for E2E test"

        # Update project
        update_result = run_cli(
            "plane_projects.py",
            "update",
            "--project-id", project_id,
            "--name", new_name,
            "--description", new_description,
        )

        updated = update_result.json
        assert updated["name"] == new_name
        assert updated["description"] == new_description

        # Verify by getting the project again
        get_result = run_cli(
            "plane_projects.py",
            "get",
            "--project-id", project_id,
        )
        assert get_result.json["name"] == new_name

    def test_project_update_no_fields(self) -> None:
        """TC-PROJ-05: Update with no fields specified fails gracefully."""
        skip_if_no_credentials()

        # This test doesn't need a real project since it validates args first
        # But the script will try to get client first, so we need credentials

        result = run_cli(
            "plane_projects.py",
            "update",
            "--project-id", "some-uuid",
            check=False,
        )

        # Should fail because no update fields provided
        assert result.returncode != 0
        assert "No update fields specified" in result.stderr

    def test_project_members(self, test_project: dict[str, Any]) -> None:
        """TC-PROJ-06: List project members.

        Verifies members endpoint returns data for a valid project.
        """
        skip_if_no_credentials()

        result = run_cli(
            "plane_projects.py",
            "members",
            "--project-id", test_project["id"],
        )

        # Members should be a list (could be empty)
        assert isinstance(result.json, list)

    def test_project_features(self, test_project: dict[str, Any]) -> None:
        """TC-PROJ-07: Get project features.

        Verifies features endpoint returns data for a valid project.
        """
        skip_if_no_credentials()

        result = run_cli(
            "plane_projects.py",
            "features",
            "--project-id", test_project["id"],
        )

        # Features should be an object with feature flags
        assert isinstance(result.json, dict)

    def test_project_delete_without_confirm(self) -> None:
        """TC-PROJ-08: Delete without --confirm flag fails."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_projects.py",
            "delete",
            "--project-id", "some-uuid",
            check=False,
        )

        assert result.returncode != 0
        assert "--confirm" in result.stderr
        assert "Destructive operation" in result.stderr

    def test_project_create_duplicate_identifier(self) -> None:
        """TC-PROJ-09: Create project with duplicate identifier fails.

        Uses the test_project fixture to get an existing identifier.
        """
        skip_if_no_credentials()

        # First create a project
        project_name = generate_test_name("test-dup")
        identifier = f"DUP{uuid.uuid4().hex[:4].upper()}"

        result1 = run_cli(
            "plane_projects.py",
            "create",
            "--name", project_name,
            "--identifier", identifier,
        )
        project_id = result1.json["id"]

        try:
            # Try to create another with same identifier
            result2 = run_cli(
                "plane_projects.py",
                "create",
                "--name", generate_test_name("test-dup2"),
                "--identifier", identifier,
                check=False,
            )

            # Should fail - identifier already exists
            assert result2.returncode != 0
        finally:
            # Cleanup first project
            run_cli(
                "plane_projects.py",
                "delete",
                "--project-id", project_id,
                "--confirm",
                check=False,
            )


@pytest.mark.e2e
class TestProjectEdgeCases:
    """Edge case tests for project commands."""

    def test_project_create_with_unicode_name(self) -> None:
        """TC-PROJ-EDGE-01: Create project with unicode name."""
        skip_if_no_credentials()

        unicode_name = f"测试项目-{uuid.uuid4().hex[:4]}"
        identifier = f"UNI{uuid.uuid4().hex[:4].upper()}"

        result = run_cli(
            "plane_projects.py",
            "create",
            "--name", unicode_name,
            "--identifier", identifier,
            check=False,
        )

        if result.returncode == 0:
            # Cleanup if successful
            project_id = result.json["id"]
            run_cli(
                "plane_projects.py",
                "delete",
                "--project-id", project_id,
                "--confirm",
                check=False,
            )

    def test_project_create_with_very_long_name(self) -> None:
        """TC-PROJ-EDGE-02: Create project with very long name."""
        skip_if_no_credentials()

        long_name = "A" * 200  # Very long name
        identifier = f"LNG{uuid.uuid4().hex[:4].upper()}"

        result = run_cli(
            "plane_projects.py",
            "create",
            "--name", long_name,
            "--identifier", identifier,
            check=False,
        )

        # May succeed or fail depending on API limits
        # We just verify it doesn't crash

        if result.returncode == 0:
            project_id = result.json["id"]
            run_cli(
                "plane_projects.py",
                "delete",
                "--project-id", project_id,
                "--confirm",
                check=False,
            )

    def test_project_create_with_special_chars_in_description(self) -> None:
        """TC-PROJ-EDGE-03: Create project with HTML/special chars in description."""
        skip_if_no_credentials()

        description = "<script>alert('xss')</script> &amp; test &#x27;quote&#x27;"
        identifier = f"XSS{uuid.uuid4().hex[:4].upper()}"

        result = run_cli(
            "plane_projects.py",
            "create",
            "--name", generate_test_name("test-xss"),
            "--identifier", identifier,
            "--description", description,
        )

        project_id = result.json["id"]

        # Verify the project was created
        get_result = run_cli(
            "plane_projects.py",
            "get",
            "--project-id", project_id,
        )

        # Description should be stored (possibly sanitized)
        assert "description" in get_result.json

        # Cleanup
        run_cli(
            "plane_projects.py",
            "delete",
            "--project-id", project_id,
            "--confirm",
            check=False,
        )
