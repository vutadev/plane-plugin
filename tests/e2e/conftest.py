"""E2E test configuration and utilities for Plane CLI tests.

This module provides:
- Test fixtures for API credentials and workspace configuration
- Helper functions for running CLI commands
- Test data management and cleanup utilities
- Skip conditions for when credentials are not available
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import pytest

# Project root (repo root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Path to the skill scripts
SKILL_ROOT = PROJECT_ROOT / "skills" / "plane"
SCRIPTS_DIR = SKILL_ROOT / "scripts"

# Required environment variables for E2E tests
REQUIRED_ENV_VARS = ["PLANE_WORKSPACE_SLUG"]
API_AUTH_VARS = ["PLANE_API_KEY", "PLANE_ACCESS_TOKEN"]


class E2EError(Exception):
    """Custom exception for E2E test errors."""

    pass


class CLIResult:
    """Result of a CLI command execution."""

    def __init__(self, returncode: int, stdout: str, stderr: str):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self._json: Any | None = None

    @property
    def json(self) -> Any:
        """Parse stdout as JSON (cached)."""
        if self._json is None:
            self._json = json.loads(self.stdout)
        return self._json

    def __repr__(self) -> str:
        return f"CLIResult(returncode={self.returncode}, stdout={self.stdout[:200]}...)"


def _parse_planerc() -> dict[str, str]:
    """Parse .planerc file from project root and return key-value pairs."""
    rc_path = PROJECT_ROOT / ".planerc"
    config: dict[str, str] = {}
    if rc_path.is_file():
        for line in rc_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip()
    return config


def has_credentials() -> bool:
    """Check if required API credentials are available via env vars or .planerc."""
    has_auth = any(os.environ.get(var) for var in API_AUTH_VARS)
    has_workspace = bool(os.environ.get("PLANE_WORKSPACE_SLUG"))
    if has_auth and has_workspace:
        return True
    # Fallback: check .planerc
    rc = _parse_planerc()
    return bool(rc.get("api_key")) and bool(rc.get("workspace"))


def skip_if_no_credentials() -> None:
    """Skip test if credentials are not available."""
    if not has_credentials():
        pytest.skip("E2E tests require PLANE_API_KEY or PLANE_ACCESS_TOKEN and PLANE_WORKSPACE_SLUG")


def run_cli(script_name: str, *args: str, check: bool = True) -> CLIResult:
    """Run a CLI script and return the result.

    Args:
        script_name: Name of the script (e.g., "plane_projects.py")
        *args: Command line arguments
        check: If True, raise E2EError on non-zero exit code

    Returns:
        CLIResult with returncode, stdout, stderr

    Raises:
        E2EError: If check=True and returncode != 0
    """
    script_path = SCRIPTS_DIR / script_name
    cmd = [sys.executable, str(script_path)] + list(args)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=PROJECT_ROOT,
    )

    cli_result = CLIResult(
        returncode=result.returncode,
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
    )

    if check and result.returncode != 0:
        raise E2EError(
            f"Command failed: {' '.join(cmd)}\n"
            f"stdout: {cli_result.stdout}\n"
            f"stderr: {cli_result.stderr}"
        )

    return cli_result


def generate_test_name(prefix: str) -> str:
    """Generate a unique test resource name with timestamp.

    Args:
        prefix: Resource type prefix (e.g., "test-project", "test-issue")

    Returns:
        Unique name like "test-project-20260301-123045-abc123"
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    return f"{prefix}-{timestamp}-{unique_id}"


@pytest.fixture(scope="session")
def test_workspace() -> str:
    """Get the test workspace slug from environment or .planerc."""
    skip_if_no_credentials()
    workspace = os.environ.get("PLANE_WORKSPACE_SLUG")
    if not workspace:
        workspace = _parse_planerc().get("workspace")
    if not workspace:
        pytest.skip("Workspace slug not found in env vars or .planerc")
    return workspace


@pytest.fixture(scope="session")
def base_url() -> str:
    """Get the base URL (defaults to cloud)."""
    return os.environ.get("PLANE_BASE_URL", "https://api.plane.so/api/v1")


@pytest.fixture
def test_project() -> dict[str, Any]:
    """Create a test project and yield it, then cleanup.

    Yields:
        Project data dictionary with at least 'id' and 'name' keys
    """
    skip_if_no_credentials()

    project_name = generate_test_name("e2e-project")
    identifier = f"E2E{uuid.uuid4().hex[:4].upper()}"

    # Create project
    result = run_cli(
        "plane_projects.py",
        "create",
        "--name", project_name,
        "--identifier", identifier,
        "--description", "E2E test project - auto-created",
    )

    project = result.json
    yield project

    # Cleanup - delete the test project
    try:
        run_cli(
            "plane_projects.py",
            "delete",
            "--project-id", project["id"],
            "--confirm",
        )
    except E2EError:
        # Ignore cleanup errors
        pass


@pytest.fixture
def test_issue(test_project: dict[str, Any]) -> dict[str, Any]:
    """Create a test work item (issue) and yield it, then cleanup.

    Args:
        test_project: The project fixture to create the issue in

    Yields:
        Issue data dictionary
    """
    issue_name = generate_test_name("e2e-issue")

    result = run_cli(
        "plane_work_items.py",
        "create",
        "--project-id", test_project["id"],
        "--name", issue_name,
        "--description", "<p>E2E test issue - auto-created</p>",
        "--priority", "medium",
    )

    issue = result.json
    yield issue

    # Cleanup
    try:
        run_cli(
            "plane_work_items.py",
            "delete",
            "--project-id", test_project["id"],
            "--work-item-id", issue["id"],
            "--confirm",
        )
    except E2EError:
        pass


@pytest.fixture
def cleanup_registry() -> list[dict[str, Any]]:
    """Registry for resources to cleanup after test.

    Usage:
        def test_something(cleanup_registry):
            # Create resource
            result = run_cli(...)
            resource = result.json

            # Register for cleanup
            cleanup_registry.append({
                "type": "issue",
                "project_id": project_id,
                "id": resource["id"],
            })

    The cleanup happens automatically after the test.
    """
    registry: list[dict[str, Any]] = []
    yield registry

    # Cleanup in reverse order
    for item in reversed(registry):
        try:
            if item["type"] == "issue":
                run_cli(
                    "plane_work_items.py",
                    "delete",
                    "--project-id", item["project_id"],
                    "--work-item-id", item["id"],
                    "--confirm",
                    check=False,
                )
            elif item["type"] == "project":
                run_cli(
                    "plane_projects.py",
                    "delete",
                    "--project-id", item["id"],
                    "--confirm",
                    check=False,
                )
            elif item["type"] == "cycle":
                run_cli(
                    "plane_cycles.py",
                    "delete",
                    "--project-id", item["project_id"],
                    "--cycle-id", item["id"],
                    "--confirm",
                    check=False,
                )
            elif item["type"] == "module":
                run_cli(
                    "plane_modules.py",
                    "delete",
                    "--project-id", item["project_id"],
                    "--module-id", item["id"],
                    "--confirm",
                    check=False,
                )
            elif item["type"] == "label":
                run_cli(
                    "plane_labels.py",
                    "delete",
                    "--project-id", item["project_id"],
                    "--label-id", item["id"],
                    "--confirm",
                    check=False,
                )
            elif item["type"] == "milestone":
                run_cli(
                    "plane_milestones.py",
                    "delete",
                    "--project-id", item["project_id"],
                    "--milestone-id", item["id"],
                    "--confirm",
                    check=False,
                )
            elif item["type"] == "sticky":
                run_cli(
                    "plane_stickies.py",
                    "delete",
                    "--sticky-id", item["id"],
                    "--confirm",
                    check=False,
                )
            elif item["type"] == "teamspace":
                run_cli(
                    "plane_teamspaces.py",
                    "delete",
                    "--teamspace-id", item["id"],
                    "--confirm",
                    check=False,
                )
        except Exception:
            # Ignore cleanup errors
            pass
