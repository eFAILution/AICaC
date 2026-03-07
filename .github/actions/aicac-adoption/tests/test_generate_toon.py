"""Tests for TOON generation script."""

import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from generate_toon import generate, clean, yaml_to_toon, HAS_TOON
except ImportError:
    HAS_TOON = False

pytestmark = pytest.mark.skipif(not HAS_TOON, reason="toon_format not installed")


@pytest.fixture
def ai_project(tmp_path):
    """Create a minimal project with .ai/ YAML files."""
    ai_dir = tmp_path / ".ai"
    ai_dir.mkdir()

    (ai_dir / "context.yaml").write_text(
        'version: "1.0"\n'
        "project:\n"
        "  name: test-project\n"
        "  type: web-app\n"
    )

    (ai_dir / "errors.yaml").write_text(
        "error_patterns:\n"
        '  - pattern: "Port in use"\n'
        '    solution: "Kill process"\n'
    )

    return tmp_path


class TestGenerate:
    def test_generates_toon_files(self, ai_project):
        result = generate(ai_project)
        assert result["generated"] == 2
        assert (ai_project / ".ai" / "context.toon").exists()
        assert (ai_project / ".ai" / "errors.toon").exists()

    def test_skips_unchanged_files(self, ai_project):
        generate(ai_project)
        result = generate(ai_project)
        assert result["generated"] == 0
        assert result["skipped"] == 2

    def test_check_mode_does_not_write(self, ai_project):
        result = generate(ai_project, check_only=True)
        assert result["stale"]
        assert not (ai_project / ".ai" / "context.toon").exists()

    def test_check_mode_passes_when_up_to_date(self, ai_project):
        generate(ai_project)
        result = generate(ai_project, check_only=True)
        assert not result["stale"]

    def test_no_ai_dir_returns_zeros(self, tmp_path):
        result = generate(tmp_path)
        assert result["generated"] == 0

    def test_empty_yaml_skipped(self, ai_project):
        (ai_project / ".ai" / "empty.yaml").write_text("")
        result = generate(ai_project)
        assert result["skipped"] >= 1

    def test_toon_header_present(self, ai_project):
        generate(ai_project)
        content = (ai_project / ".ai" / "context.toon").read_text()
        assert "AUTO-GENERATED" in content
        assert "context.yaml" in content


class TestClean:
    def test_removes_toon_files(self, ai_project):
        generate(ai_project)
        removed = clean(ai_project)
        assert removed == 2
        assert not (ai_project / ".ai" / "context.toon").exists()

    def test_clean_no_toon_files(self, ai_project):
        removed = clean(ai_project)
        assert removed == 0

    def test_clean_no_ai_dir(self, tmp_path):
        removed = clean(tmp_path)
        assert removed == 0


class TestYamlToToon:
    def test_converts_yaml(self, ai_project):
        result = yaml_to_toon(ai_project / ".ai" / "context.yaml")
        assert result is not None
        assert "test-project" in result

    def test_empty_yaml_returns_none(self, tmp_path):
        empty = tmp_path / "empty.yaml"
        empty.write_text("")
        assert yaml_to_toon(empty) is None
