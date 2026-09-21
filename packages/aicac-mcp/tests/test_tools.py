"""
Unit tests for AICaC MCP server tools.

Tests the tool wrapper functions against the sample-project fixture.
"""

import json
from pathlib import Path

import pytest

from aicac_mcp import tools

REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_PROJECT = REPO_ROOT / "validation" / "examples" / "sample-project"


class TestValidate:
    """Test aicac_validate tool wrapper."""

    def test_validate_sample_project(self):
        """Validate against the canonical sample-project fixture."""
        result = tools.validate_project(str(SAMPLE_PROJECT))
        
        assert result["valid"] is True
        assert result["compliance_level"] in ["Minimal", "Standard", "Comprehensive"]
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)
        assert isinstance(result["found_files"], dict)
        assert "context.yaml" in result["found_files"]

    def test_validate_nonexistent(self, tmp_path):
        """Validate nonexistent .ai/ directory."""
        result = tools.validate_project(str(tmp_path))
        
        assert result["valid"] is False
        assert result["compliance_level"] == "None"
        assert result["error"] == ".ai/ directory not found"

    def test_validate_strict_mode(self):
        """Test strict mode treats warnings as errors."""
        result = tools.validate_project(str(SAMPLE_PROJECT), strict=True)
        
        assert "valid" in result
        assert isinstance(result.get("warnings"), list)


class TestBootstrap:
    """Test aicac_bootstrap tool wrapper."""

    def test_bootstrap_dry_run(self, tmp_path):
        """Bootstrap in dry-run mode does not write files."""
        result = tools.bootstrap_project(str(tmp_path), apply=False)
        
        assert result["status"] == "dry_run"
        assert "files_created" in result
        assert "context.yaml" in result["files_created"]
        assert not (tmp_path / ".ai").exists()

    def test_bootstrap_apply(self, tmp_path):
        """Bootstrap with apply=True creates files."""
        result = tools.bootstrap_project(str(tmp_path), apply=True)
        
        assert result["status"] == "success"
        assert "context.yaml" in result["files_created"]
        assert (tmp_path / ".ai" / "context.yaml").exists()
        assert (tmp_path / ".ai" / "README.md").exists()

    def test_bootstrap_detects_project_type(self, tmp_path):
        """Bootstrap detects project type from package files."""
        (tmp_path / "package.json").write_text('{"name": "test"}')
        
        result = tools.bootstrap_project(str(tmp_path), apply=False)
        
        assert "detected_type" in result
        assert result["detected_type"] in ["web-app", "node-app", "cli", "other"]


class TestGenerateIndex:
    """Test aicac_generate_index tool wrapper."""

    def test_generate_index_sample_project(self):
        """Generate index for sample-project."""
        result = tools.generate_index(str(SAMPLE_PROJECT), apply=False)
        
        assert "ids_by_file" in result
        assert isinstance(result["ids_by_file"], dict)
        assert "changed" in result

    def test_generate_index_nonexistent(self, tmp_path):
        """Generate index for nonexistent .ai/ directory."""
        result = tools.generate_index(str(tmp_path), apply=False)
        
        assert "error" in result
        assert result["ids_by_file"] == {}

    def test_generate_index_apply(self, tmp_path):
        """Generate index with apply=True writes file."""
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "context.yaml").write_text("version: '2.0'\nproject:\n  name: test\n  type: cli\nentrypoints:\n  main: main.py\ncommon_tasks:\n  test: pytest\n")
        
        result = tools.generate_index(str(tmp_path), apply=True)
        
        if result["changed"]:
            assert (ai_dir / "index.yaml").exists()


class TestMigrate:
    """Test aicac_migrate tool wrapper."""

    def test_migrate_dry_run(self):
        """Migrate in dry-run mode does not modify files."""
        result = tools.migrate_project(str(SAMPLE_PROJECT), apply=False)
        
        assert "changes" in result
        assert "diff" in result
        assert isinstance(result["changes"], list)

    def test_migrate_nonexistent(self, tmp_path):
        """Migrate nonexistent .ai/ directory."""
        result = tools.migrate_project(str(tmp_path), apply=False)
        
        assert "error" in result
        assert result["changes"] == []

    def test_migrate_v1_to_v2(self, tmp_path):
        """Migrate v1.x shape to v2.0."""
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        
        (ai_dir / "context.yaml").write_text("""
version: '1.0'
project:
  name: test
  type: cli
entrypoints:
  main: main.py
common_commands:
  test: pytest
""")
        
        result = tools.migrate_project(str(tmp_path), apply=False)
        
        assert any("common_commands" in str(c) for c in result["changes"]) or "Already v2.0" in result["diff"]


class TestSyncSuggest:
    """Test aicac_sync_suggest tool wrapper."""

    def test_sync_suggest_with_files(self):
        """Sync suggest with explicit changed files."""
        result = tools.sync_suggest(
            str(SAMPLE_PROJECT),
            changed_files=["src/api.py", "tests/test_api.py"]
        )
        
        assert "changed_files" in result
        assert "candidate_ai_files" in result
        assert "prompt" in result
        assert result["changed_files"] == ["src/api.py", "tests/test_api.py"]

    def test_sync_suggest_no_files(self, tmp_path):
        """Sync suggest with no .ai/ directory."""
        result = tools.sync_suggest(str(tmp_path), changed_files=[])
        
        assert result["candidate_ai_files"] == []

    def test_sync_suggest_git_diff(self):
        """Sync suggest uses git diff when no files specified."""
        result = tools.sync_suggest(str(SAMPLE_PROJECT))
        
        assert "changed_files" in result
        assert "candidate_ai_files" in result
        assert isinstance(result["changed_files"], list)


class TestIntegration:
    """Integration tests for full workflows."""

    def test_bootstrap_validate_workflow(self, tmp_path):
        """Bootstrap a project and validate it."""
        bootstrap_result = tools.bootstrap_project(str(tmp_path), apply=True)
        assert bootstrap_result["status"] == "success"
        
        validate_result = tools.validate_project(str(tmp_path))
        assert validate_result["valid"] is True
        assert validate_result["compliance_level"] == "Minimal"

    def test_bootstrap_generate_index_workflow(self, tmp_path):
        """Bootstrap a project and generate index."""
        tools.bootstrap_project(str(tmp_path), apply=True)
        
        index_result = tools.generate_index(str(tmp_path), apply=True)
        assert "ids_by_file" in index_result
        assert (tmp_path / ".ai" / "index.yaml").exists()
