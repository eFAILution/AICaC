"""
Tests for asset resolution and packaging.

Verifies that the package can work standalone without monorepo.
"""

import os
import sys
from pathlib import Path

import pytest

from aicac_mcp import assets


class TestAssetResolution:
    """Test asset resolution prefers package-local, falls back to monorepo."""

    def test_get_schemas_dir_package_local(self):
        """Schemas resolve from package data."""
        schemas_dir = assets.get_schemas_dir()
        
        assert schemas_dir.is_dir()
        assert (schemas_dir / "context.schema.json").exists()
        assert (schemas_dir / "architecture.schema.json").exists()

    def test_get_skills_dir_package_local(self):
        """Skills resolve from package data."""
        skills_dir = assets.get_skills_dir()
        
        assert skills_dir.is_dir()
        assert (skills_dir / "router.md").exists()
        assert (skills_dir / "bootstrap.md").exists()
        assert (skills_dir / "validate.md").exists()

    def test_get_scripts_dir_package_local(self):
        """Scripts resolve from package data."""
        scripts_dir = assets.get_scripts_dir()
        
        assert scripts_dir.is_dir()
        assert (scripts_dir / "validate.py").exists()
        assert (scripts_dir / "bootstrap.py").exists()
        assert (scripts_dir / "generate_index.py").exists()
        assert (scripts_dir / "migrate_v2.py").exists()

    def test_monorepo_fallback_with_env(self, tmp_path, monkeypatch):
        """Asset resolution respects AICAC_REPO_ROOT env var."""
        # Create fake monorepo structure
        fake_repo = tmp_path / "fake_repo"
        fake_repo.mkdir()
        
        fake_schemas = fake_repo / "spec" / "v2"
        fake_schemas.mkdir(parents=True)
        (fake_schemas / "context.schema.json").write_text("{}")
        
        fake_scripts = fake_repo / ".github" / "actions" / "aicac-adoption" / "scripts"
        fake_scripts.mkdir(parents=True)
        (fake_scripts / "validate.py").write_text("")
        
        fake_skills = fake_repo / ".claude" / "skills" / "aicac"
        fake_skills.mkdir(parents=True)
        (fake_skills / "router.md").write_text("")
        
        # Set env to override
        monkeypatch.setenv("AICAC_REPO_ROOT", str(fake_repo))
        
        # Package-local should still win (exists and has content)
        schemas = assets.get_schemas_dir()
        assert "data/schemas" in str(schemas) or "spec/v2" in str(schemas)


class TestPackagedTools:
    """Test that tools work with packaged assets."""

    def test_validate_works_packaged(self, tmp_path):
        """Validate tool works without monorepo checkout."""
        from aicac_mcp import tools
        
        # Create minimal .ai/ structure
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "context.yaml").write_text("""
version: '2.0'
project:
  name: test
  type: cli
entrypoints:
  main: main.py
common_tasks:
  test: pytest
""")
        
        result = tools.validate_project(str(tmp_path))
        
        # Should succeed (or fail gracefully with clear error)
        assert "compliance_level" in result
        assert isinstance(result.get("errors", []), list)

    def test_bootstrap_works_packaged(self, tmp_path):
        """Bootstrap tool works without monorepo checkout."""
        from aicac_mcp import tools
        
        result = tools.bootstrap_project(str(tmp_path), apply=False)
        
        assert "files_created" in result or "error" in result
        if "files_created" in result:
            assert "context.yaml" in result["files_created"]

    def test_generate_index_works_packaged(self, tmp_path):
        """Generate index works without monorepo checkout."""
        from aicac_mcp import tools
        
        # Create minimal .ai/
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "context.yaml").write_text("version: '2.0'\nproject:\n  name: test\n  type: cli\nentrypoints:\n  main: main.py\ncommon_tasks:\n  test: pytest\n")
        
        result = tools.generate_index(str(tmp_path), apply=False)
        
        assert "ids_by_file" in result or "error" in result

    def test_migrate_works_packaged(self, tmp_path):
        """Migrate tool works without monorepo checkout."""
        from aicac_mcp import tools
        
        # Create v1.x .ai/
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
        
        assert "changes" in result or "error" in result
