"""Tests for TOON format integration in token and performance measurement."""

import sys
from pathlib import Path

import pytest

# Add validation/scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from yaml_to_toon import HAS_TOON
except ImportError:
    HAS_TOON = False

from token_measurement import DocumentationLoader, QUESTION_FILE_MAPPING

SAMPLE_PROJECT = Path(__file__).parent.parent.parent / "examples" / "sample-project"

pytestmark = pytest.mark.skipif(not HAS_TOON, reason="toon_format not installed")


class TestDocumentationLoaderToon:
    """Tests for TOON loading methods in DocumentationLoader."""

    @pytest.fixture
    def loader(self):
        return DocumentationLoader(SAMPLE_PROJECT)

    def test_load_aicac_toon_returns_content(self, loader):
        content, files = loader.load_aicac_toon()
        assert len(content) > 0
        assert any("TOON" in f for f in files)

    def test_load_aicac_toon_includes_readme(self, loader):
        content, files = loader.load_aicac_toon()
        assert "README.md" in files

    def test_load_aicac_toon_includes_agents(self, loader):
        content, files = loader.load_aicac_toon()
        assert "AGENTS.md" in files

    def test_load_aicac_toon_has_toon_encoded_files(self, loader):
        content, files = loader.load_aicac_toon()
        toon_files = [f for f in files if "(TOON)" in f]
        assert len(toon_files) >= 5, (
            f"Expected at least 5 TOON-encoded files, got {len(toon_files)}: {toon_files}"
        )

    def test_load_aicac_toon_shorter_than_yaml(self, loader):
        """TOON full load should use fewer characters than YAML full load."""
        yaml_content, _ = loader.load_aicac_full()
        toon_content, _ = loader.load_aicac_toon()
        assert len(toon_content) < len(yaml_content), (
            f"TOON ({len(toon_content)}) should be shorter than YAML ({len(yaml_content)})"
        )

    def test_load_aicac_toon_selective_returns_content(self, loader):
        content, files = loader.load_aicac_toon_selective("IR")
        assert len(content) > 0
        assert "AGENTS.md" in files

    def test_load_aicac_toon_selective_loads_correct_files(self, loader):
        for q_type, expected_files in QUESTION_FILE_MAPPING.items():
            content, files = loader.load_aicac_toon_selective(q_type)
            for expected in expected_files:
                toon_name = f".ai/{expected} (TOON)"
                assert toon_name in files, (
                    f"Expected {toon_name} for question type {q_type}, "
                    f"got files: {files}"
                )

    def test_load_aicac_toon_selective_shorter_than_yaml_selective(self, loader):
        """TOON selective should use fewer characters than YAML selective."""
        for q_type in QUESTION_FILE_MAPPING:
            yaml_content, _ = loader.load_aicac_selective(q_type)
            toon_content, _ = loader.load_aicac_toon_selective(q_type)
            assert len(toon_content) <= len(yaml_content), (
                f"TOON selective ({len(toon_content)}) should not exceed "
                f"YAML selective ({len(yaml_content)}) for {q_type}"
            )

    def test_toon_content_preserves_key_data(self, loader):
        """TOON encoded content should still contain key project data."""
        content, _ = loader.load_aicac_toon()
        assert "taskflow" in content
        assert "fastapi" in content
        assert "python" in content
