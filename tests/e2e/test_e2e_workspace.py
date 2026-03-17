"""E2E tests for Plane workspace and user commands.

Covers:
- user:me - Get current user
- workspace:members - List workspace members
- workspace:features - Get workspace features
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

        user = result.json
        assert isinstance(user, dict)
        assert "id" in user
        assert any(field in user for field in ["email", "username", "display_name", "first_name"])


@pytest.mark.e2e
class TestWorkspaceCommands:
    """E2E tests for workspace commands."""

    def test_workspace_members(self) -> None:
        """TC-WORKSPACE-01: List workspace members."""
        skip_if_no_credentials()

        result = run_cli("plane_workspaces.py", "members")

        assert isinstance(result.json, list)
        if len(result.json) > 0:
            member = result.json[0]
            assert "id" in member

    def test_workspace_features(self) -> None:
        """TC-WORKSPACE-02: Get workspace features."""
        skip_if_no_credentials()

        result = run_cli("plane_workspaces.py", "features")

        assert isinstance(result.json, dict)


@pytest.mark.e2e
class TestVerifyCommand:
    """E2E tests for verify command."""

    def test_verify_connection(self) -> None:
        """TC-VERIFY-01: Verify API connection works."""
        skip_if_no_credentials()

        result = run_cli("plane_verify.py")

        assert isinstance(result.json, dict)
        assert "status" in result.json
        assert result.json["status"] in ["ok", "connected"]
