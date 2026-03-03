"""E2E tests for Plane CLI.

This package contains end-to-end tests that verify the CLI works against
a real Plane API instance. These tests require valid API credentials.

To run E2E tests:
    export PLANE_API_KEY="your-api-key"
    export PLANE_WORKSPACE_SLUG="your-workspace"
    pytest tests/e2e/ -v

To skip E2E tests (when credentials unavailable):
    pytest tests/ -v --ignore=tests/e2e

Or use the marker:
    pytest tests/ -v -m "not e2e"
"""
