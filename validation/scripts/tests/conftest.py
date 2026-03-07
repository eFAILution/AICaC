"""Fixtures for TOON integration tests."""

import pytest
from pathlib import Path


SAMPLE_PROJECT = Path(__file__).parent.parent.parent / "examples" / "sample-project"


@pytest.fixture
def sample_ai_dir():
    """Path to the sample project's .ai/ directory."""
    ai_dir = SAMPLE_PROJECT / ".ai"
    assert ai_dir.exists(), f"Sample .ai/ not found at {ai_dir}"
    return ai_dir


@pytest.fixture
def sample_project_dir():
    """Path to the full sample project directory."""
    assert SAMPLE_PROJECT.exists(), f"Sample project not found at {SAMPLE_PROJECT}"
    return SAMPLE_PROJECT


@pytest.fixture
def temp_ai_dir(tmp_path):
    """Create a temporary .ai/ directory with YAML files for testing."""
    ai_dir = tmp_path / ".ai"
    ai_dir.mkdir()

    (ai_dir / "context.yaml").write_text(
        'version: "1.0"\n'
        "project:\n"
        "  name: test-project\n"
        "  type: web-app\n"
        "entrypoints:\n"
        "  main: src/index.js\n"
        "common_tasks:\n"
        "  dev: npm run dev\n"
    )

    (ai_dir / "errors.yaml").write_text(
        "error_patterns:\n"
        '  - pattern: "Port already in use"\n'
        '    context: "Server start"\n'
        "    solutions:\n"
        '      - description: "Kill process"\n'
        '        command: "lsof -ti:8000 | xargs kill"\n'
    )

    return ai_dir
