"""E2E tests for Plane label commands.

Covers:
- label:list - List labels in a project
- label:create - Create a new label
- label:get - Get label details
- label:update - Update label
- label:delete - Delete a label
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.e2e.conftest import generate_test_name, run_cli, skip_if_no_credentials


# Common label colors for testing
LABEL_COLORS = [
    "#ef4444",  # red
    "#22c55e",  # green
    "#3b82f6",  # blue
    "#f59e0b",  # amber
    "#8b5cf6",  # violet
]


def get_test_color() -> str:
    """Return a test color (cycles through predefined colors)."""
    import random
    return random.choice(LABEL_COLORS)


@pytest.mark.e2e
class TestLabelCommands:
    """E2E tests for label management commands."""

    def test_label_list(self, test_project: dict[str, Any]) -> None:
        """TC-LABEL-01: List labels in a project."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_labels.py",
            "list",
            "--project-id", test_project["id"],
        )

        assert isinstance(result.json, list)

    def test_label_create_and_delete(self, test_project: dict[str, Any]) -> None:
        """TC-LABEL-02: Create label then delete it."""
        skip_if_no_credentials()

        label_name = generate_test_name("test-label")
        color = get_test_color()

        create_result = run_cli(
            "plane_labels.py",
            "create",
            "--project-id", test_project["id"],
            "--name", label_name,
            "--color", color,
        )

        label = create_result.json
        assert label["name"] == label_name
        assert "id" in label

        label_id = label["id"]

        # Get label
        get_result = run_cli(
            "plane_labels.py",
            "get",
            "--project-id", test_project["id"],
            "--label-id", label_id,
        )
        assert get_result.json["id"] == label_id

        # Delete
        delete_result = run_cli(
            "plane_labels.py",
            "delete",
            "--project-id", test_project["id"],
            "--label-id", label_id,
            "--confirm",
        )
        assert delete_result.json["status"] == "deleted"

    def test_label_update(self, test_project: dict[str, Any]) -> None:
        """TC-LABEL-03: Update label fields."""
        skip_if_no_credentials()

        label_name = generate_test_name("update-label")
        color = get_test_color()

        create_result = run_cli(
            "plane_labels.py",
            "create",
            "--project-id", test_project["id"],
            "--name", label_name,
            "--color", color,
        )

        label_id = create_result.json["id"]

        try:
            new_name = generate_test_name("updated-label")
            new_color = get_test_color()

            update_result = run_cli(
                "plane_labels.py",
                "update",
                "--project-id", test_project["id"],
                "--label-id", label_id,
                "--name", new_name,
                "--color", new_color,
            )

            updated = update_result.json
            assert updated["name"] == new_name
            assert updated["color"] == new_color
        finally:
            run_cli(
                "plane_labels.py",
                "delete",
                "--project-id", test_project["id"],
                "--label-id", label_id,
                "--confirm",
                check=False,
            )

    def test_label_create_with_description(self, test_project: dict[str, Any]) -> None:
        """TC-LABEL-04: Create label with description."""
        skip_if_no_credentials()

        label_name = generate_test_name("desc-label")
        color = get_test_color()
        description = "This is a test label description"

        result = run_cli(
            "plane_labels.py",
            "create",
            "--project-id", test_project["id"],
            "--name", label_name,
            "--color", color,
            "--description", description,
        )

        label = result.json
        assert label["name"] == label_name

        label_id = label["id"]

        # Cleanup
        run_cli(
            "plane_labels.py",
            "delete",
            "--project-id", test_project["id"],
            "--label-id", label_id,
            "--confirm",
            check=False,
        )

    def test_label_delete_without_confirm(self, test_project: dict[str, Any]) -> None:
        """TC-LABEL-05: Delete without --confirm fails."""
        skip_if_no_credentials()

        result = run_cli(
            "plane_labels.py",
            "delete",
            "--project-id", test_project["id"],
            "--label-id", "some-uuid",
            check=False,
        )

        assert result.returncode != 0
        assert "--confirm" in result.stderr

    def test_label_create_duplicate_name(self, test_project: dict[str, Any]) -> None:
        """TC-LABEL-06: Create label with duplicate name fails."""
        skip_if_no_credentials()

        label_name = generate_test_name("dup-label")
        color = get_test_color()

        # Create first label
        result1 = run_cli(
            "plane_labels.py",
            "create",
            "--project-id", test_project["id"],
            "--name", label_name,
            "--color", color,
        )
        label_id = result1.json["id"]

        try:
            # Try to create duplicate
            result2 = run_cli(
                "plane_labels.py",
                "create",
                "--project-id", test_project["id"],
                "--name", label_name,
                "--color", color,
                check=False,
            )

            assert result2.returncode != 0
        finally:
            run_cli(
                "plane_labels.py",
                "delete",
                "--project-id", test_project["id"],
                "--label-id", label_id,
                "--confirm",
                check=False,
            )


@pytest.mark.e2e
class TestLabelEdgeCases:
    """Edge case tests for label commands."""

    def test_label_create_invalid_color(self, test_project: dict[str, Any]) -> None:
        """TC-LABEL-EDGE-01: Create label with invalid color format."""
        skip_if_no_credentials()

        label_name = generate_test_name("color-label")
        invalid_colors = [
            "red",  # named color
            "FF0000",  # missing #
            "#FF0000",  # uppercase (might be valid)
            "rgb(255,0,0)",  # rgb format
        ]

        for color in invalid_colors:
            result = run_cli(
                "plane_labels.py",
                "create",
                "--project-id", test_project["id"],
                "--name", generate_test_name(f"color-{color[:5]}"),
                "--color", color,
                check=False,
            )

            if result.returncode == 0:
                label_id = result.json["id"]
                run_cli(
                    "plane_labels.py",
                    "delete",
                    "--project-id", test_project["id"],
                    "--label-id", label_id,
                    "--confirm",
                    check=False,
                )

    def test_label_create_unicode_name(self, test_project: dict[str, Any]) -> None:
        """TC-LABEL-EDGE-02: Create label with unicode name."""
        skip_if_no_credentials()

        unicode_name = f"标签-{generate_test_name('').split('-')[-1]}"
        color = get_test_color()

        result = run_cli(
            "plane_labels.py",
            "create",
            "--project-id", test_project["id"],
            "--name", unicode_name,
            "--color", color,
            check=False,
        )

        if result.returncode == 0:
            label_id = result.json["id"]
            run_cli(
                "plane_labels.py",
                "delete",
                "--project-id", test_project["id"],
                "--label-id", label_id,
                "--confirm",
                check=False,
            )

    def test_label_create_very_long_name(self, test_project: dict[str, Any]) -> None:
        """TC-LABEL-EDGE-03: Create label with very long name."""
        skip_if_no_credentials()

        long_name = "A" * 100
        color = get_test_color()

        result = run_cli(
            "plane_labels.py",
            "create",
            "--project-id", test_project["id"],
            "--name", long_name,
            "--color", color,
            check=False,
        )

        if result.returncode == 0:
            label_id = result.json["id"]
            run_cli(
                "plane_labels.py",
                "delete",
                "--project-id", test_project["id"],
                "--label-id", label_id,
                "--confirm",
                check=False,
            )
