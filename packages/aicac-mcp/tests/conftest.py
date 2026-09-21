"""Shared test fixtures for aicac-mcp tests."""

import pytest


@pytest.fixture
def sample_changed_files():
    """Sample list of changed files for testing sync_suggest."""
    return [
        "src/api/router.py",
        "src/models/user.py",
        "tests/test_api.py",
    ]
