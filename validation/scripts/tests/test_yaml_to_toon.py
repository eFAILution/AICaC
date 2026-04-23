"""Tests for YAML-to-TOON conversion layer."""

import sys
from pathlib import Path

import pytest
import yaml

# Add validation/scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from yaml_to_toon import (
    yaml_file_to_toon,
    convert_ai_directory,
    convert_selective,
    measure_savings,
    HAS_TOON,
)


pytestmark = pytest.mark.skipif(not HAS_TOON, reason="toon_format not installed")


class TestYamlFileToToon:
    """Tests for single-file YAML to TOON conversion."""

    def test_converts_context_yaml(self, sample_ai_dir):
        result = yaml_file_to_toon(sample_ai_dir / "context.yaml")
        assert len(result) > 0
        assert "taskflow" in result.lower()
        assert "fastapi" in result.lower()

    def test_converts_errors_yaml(self, sample_ai_dir):
        result = yaml_file_to_toon(sample_ai_dir / "errors.yaml")
        assert len(result) > 0
        assert "Port already in use" in result

    def test_converts_architecture_yaml(self, sample_ai_dir):
        result = yaml_file_to_toon(sample_ai_dir / "architecture.yaml")
        assert len(result) > 0
        assert "api" in result

    def test_preserves_data_fidelity(self, sample_ai_dir):
        """TOON encoding should preserve all data values from the YAML source."""
        from toon_format import decode

        yaml_path = sample_ai_dir / "context.yaml"
        with open(yaml_path) as f:
            original = yaml.safe_load(f)

        toon_text = yaml_file_to_toon(yaml_path)
        roundtripped = decode(toon_text)

        assert roundtripped["project"]["name"] == original["project"]["name"]
        assert roundtripped["project"]["type"] == original["project"]["type"]
        assert roundtripped["project"]["primary_language"] == original["project"]["primary_language"]

    def test_toon_output_is_shorter_than_yaml(self, sample_ai_dir):
        """TOON should produce fewer characters than YAML for structured data."""
        yaml_path = sample_ai_dir / "context.yaml"
        yaml_text = yaml_path.read_text()
        toon_text = yaml_file_to_toon(yaml_path)

        assert len(toon_text) < len(yaml_text), (
            f"TOON ({len(toon_text)} chars) should be shorter than "
            f"YAML ({len(yaml_text)} chars)"
        )

    def test_empty_yaml_returns_empty_string(self, tmp_path):
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("")
        assert yaml_file_to_toon(empty_file) == ""

    def test_temp_ai_dir_fixture(self, temp_ai_dir):
        result = yaml_file_to_toon(temp_ai_dir / "context.yaml")
        assert "test-project" in result


class TestConvertAiDirectory:
    """Tests for converting an entire .ai/ directory to TOON."""

    def test_converts_all_yaml_files(self, sample_ai_dir):
        result = convert_ai_directory(sample_ai_dir)
        assert "# From .ai/context.yaml" in result
        assert "# From .ai/architecture.yaml" in result
        assert "# From .ai/errors.yaml" in result
        assert "# From .ai/workflows.yaml" in result
        assert "# From .ai/decisions.yaml" in result

    def test_nonexistent_directory_returns_empty(self, tmp_path):
        result = convert_ai_directory(tmp_path / "nonexistent")
        assert result == ""

    def test_output_shorter_than_yaml_concatenation(self, sample_ai_dir):
        """Combined TOON output should be shorter than combined YAML."""
        yaml_total = 0
        for fp in sorted(sample_ai_dir.glob("*.yaml")):
            yaml_total += len(fp.read_text())

        toon_output = convert_ai_directory(sample_ai_dir)
        # Strip headers for fair comparison
        toon_data_only = "\n".join(
            line for line in toon_output.split("\n")
            if not line.startswith("# From ")
        )

        assert len(toon_data_only) < yaml_total


class TestConvertSelective:
    """Tests for selective TOON conversion of specific files."""

    def test_converts_single_file(self, sample_ai_dir):
        result = convert_selective(sample_ai_dir, ["context.yaml"])
        assert "# From .ai/context.yaml" in result
        assert "# From .ai/architecture.yaml" not in result

    def test_converts_multiple_files(self, sample_ai_dir):
        result = convert_selective(
            sample_ai_dir, ["architecture.yaml", "decisions.yaml"]
        )
        assert "# From .ai/architecture.yaml" in result
        assert "# From .ai/decisions.yaml" in result

    def test_skips_missing_files(self, sample_ai_dir):
        result = convert_selective(
            sample_ai_dir, ["context.yaml", "nonexistent.yaml"]
        )
        assert "# From .ai/context.yaml" in result
        assert "nonexistent" not in result

    def test_empty_filelist_returns_empty(self, sample_ai_dir):
        result = convert_selective(sample_ai_dir, [])
        assert result == ""


class TestMeasureSavings:
    """Tests for token savings measurement."""

    def test_measures_savings_for_context_yaml(self, sample_ai_dir):
        result = measure_savings(sample_ai_dir / "context.yaml")
        assert result is not None
        assert result["file"] == "context.yaml"
        assert result["yaml_tokens"] > 0
        assert result["toon_tokens"] > 0
        assert result["toon_tokens"] < result["yaml_tokens"]
        assert result["reduction_pct"] > 0
        assert result["tokens_saved"] > 0

    def test_aggregate_savings_across_ai_dir(self, sample_ai_dir):
        """TOON should reduce tokens in aggregate across a realistic .ai/ dir.

        Per-file behavior varies — workflows.yaml in particular encodes
        multi-line code templates via YAML block scalars, which TOON has to
        re-encode as escaped single-line strings and can end up slightly
        larger. The directional claim is about the directory as a whole.
        """
        yaml_total = 0
        toon_total = 0
        for yaml_path in sorted(sample_ai_dir.glob("*.yaml")):
            result = measure_savings(yaml_path)
            assert result is not None, f"Failed to measure {yaml_path.name}"
            yaml_total += result["yaml_tokens"]
            toon_total += result["toon_tokens"]

        assert toon_total < yaml_total, (
            f"TOON ({toon_total} tokens) should be smaller than "
            f"YAML ({yaml_total} tokens) in aggregate"
        )
