"""E2E tests for Plane workspace and user commands.

Covers:
- user:me - Get current user
- user:list - List users in workspace
- workspace:members - List workspace members
- workspace:get - Get workspace details
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.e2e.conftest import run_cli, skip_if_no_credentials


@pytest.mark.e2e
class TestUserCommands:
    """E2E tests for user commands."""

    def test_user_me(self) -> None:
        """TC-USER-01: Get current user details."""
        skip_if_no_credentials()

        result = run_cli("plane_users.py", "me")

        # Should return user object
        user = result.json
        assert isinstance(user, dict)
        assert "id" in user

        # Common fields that should exist
        assert any(field in user for field in ["email", "username", "display_name", "first_name"])

    def test_user_list(self) -> None:
        """TC-USER-02: List users in workspace."""
        skip_if_no_credentials()

        result = run_cli("plane_users.py", "list")

        # Should return a list of users
        assert isinstance(result.json, list)

        if len(result.json) > 0:
            user = result.json[0]
            assert "id" in user


@pytest.mark.e2e
class TestWorkspaceCommands:
    """E2E tests for workspace commands."""

    def test_workspace_get(self, test_workspace: str) -> None:
        """TC-WORKSPACE-01: Get workspace details."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_workspaces.py",
            "get",
            "--workspace-slug", test_workspace,
        )

        workspace = result.json
        assert isinstance(workspace, dict)
        assert "id" in workspace
        assert "slug" in workspace or "name" in workspace

    def test_workspace_members(self, test_workspace: str) -> None:
        """TC-WORKSPACE-02: List workspace members."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_workspaces.py",
            "members",
            "--workspace-slug", test_workspace,
        )

        # Should return a list of members
        assert isinstance(result.json, list)

        if len(result.json) > 0:
            member = result.json[0]
            assert "id" in member
            # Member should have user info or role info

    def test_workspace_get_invalid_slug(self) -> None:
        """TC-WORKSPACE-03: Get workspace with invalid slug fails."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_workspaces.py",
            "get",
            "--workspace-slug", "non-existent-workspace-12345",
            check=False,
        )

        assert result.returncode != 0

    def test_workspace_invitations(self, test_workspace: str) -> None:
        """TC-WORKSPACE-04: List workspace invitations."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_workspaces.py",
            "invitations",
            "--workspace-slug", test_workspace,
        )

        # Should return a list (may be empty)
        assert isinstance(result.json, list)


@pytest.mark.e2e
class TestVerifyCommand:
    """E2E tests for verify command."""

    def test_verify_connection(self, test_workspace: str) -> None:
        """TC-VERIFY-01: Verify API connection works."""
        skip_if_no_credentials()

        result = run_cli("plane_verify.py")

        # Should return status info
        assert isinstance(result.json, dict)
        assert "status" in result.json
        assert result.json["status"] == "ok"

        # Should include workspace info
        if "workspace" in result.json:
            assert result.json["workspace"] == test_workspace


@pytest.mark.e2e
class TestAuthEdgeCases:
    """Edge case tests for authentication."""

    def test_command_with_invalid_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-AUTH-EDGE-01: Command with invalid API key fails."""
        skip_if_no_credentials()

        # Save original values
        import os
        original_key = os.environ.get("PLANE_API_KEY")
        original_token = os.environ.get("PLANE_ACCESS_TOKEN")

        # Set invalid key
        monkeypatch.setenv("PLANE_API_KEY", "invalid-key-12345")
        monkeypatch.delenv("PLANE_ACCESS_TOKEN", raising=False)

        try:
            result = run_cli(
                "plane_projects.py",
                "list",
                check=False,
            )

            # Should fail with auth error
            assert result.returncode != 0
        finally:
            # Restore original values
            if original_key:
                monkeypatch.setenv("PLANE_API_KEY", original_key)
            else:
                monkeypatch.delenv("PLANE_API_KEY", raising=False)
            if original_token:
                monkeypatch.setenv("PLANE_ACCESS_TOKEN", original_token)

    def test_command_without_workspace(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-AUTH-EDGE-02: Command without workspace fails."""
        skip_if_no_credentials()

        # Save original
        import os
        original_workspace = os.environ.get("PLANE_WORKSPACE_SLUG")

        # Remove workspace
        monkeypatch.delenv("PLANE_WORKSPACE_SLUG", raising=False)

        try:
            result = run_cli(
                "plane_projects.py",
                "list",
                check=False,
            )

            assert result.returncode != 0
            assert "PLANE_WORKSPACE_SLUG" in result.stderr
        finally:
            if original_workspace:
                monkeypatch.setenv("PLANE_WORKSPACE_SLUG", original_workspace)
