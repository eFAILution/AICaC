"""
Additional tests for bootstrap.py to improve coverage.
Focuses on edge cases, error handling, and less-common code paths.
"""

import pytest
import sys
import yaml
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from bootstrap import AICaCBootstrap


class TestBootstrapCoverage:
    """Additional tests for code coverage."""

    def test_detect_project_name_with_cargo_toml(self, temp_project_dir):
        """Test project name detection from Cargo.toml."""
        # Create Cargo.toml
        cargo_content = """[package]
name = "rust-test-project"
version = "0.1.0"
edition = "2021"
"""
        with open(temp_project_dir / 'Cargo.toml', 'w') as f:
            f.write(cargo_content)

        bootstrap = AICaCBootstrap(str(temp_project_dir))
        # Note: This requires tomli library, so it may fall back to directory name
        name = bootstrap._detect_project_name()
        # Should either detect from Cargo.toml or fallback to directory name
        assert name in ['rust-test-project', temp_project_dir.name]

    def test_analyze_rust_project(self, temp_project_dir):
        """Test project analysis for Rust project."""
        # Create Cargo.toml
        cargo_content = """[package]
name = "rust-project"
version = "0.1.0"
"""
        with open(temp_project_dir / 'Cargo.toml', 'w') as f:
            f.write(cargo_content)

        bootstrap = AICaCBootstrap(str(temp_project_dir))
        analysis = bootstrap.analyze_project()

        assert analysis['has_cargo_toml'] is True
        assert 'rust' in analysis['languages']
        assert analysis['project_type'] == 'rust-app'

    def test_analyze_go_project(self, temp_project_dir):
        """Test project analysis for Go project."""
        # Create go.mod
        with open(temp_project_dir / 'go.mod', 'w') as f:
            f.write('module example.com/myproject\n\ngo 1.21\n')

        bootstrap = AICaCBootstrap(str(temp_project_dir))
        analysis = bootstrap.analyze_project()

        assert analysis['has_go_mod'] is True
        assert 'go' in analysis['languages']
        assert analysis['project_type'] == 'go-app'

    def test_analyze_project_with_makefile(self, temp_project_dir):
        """Test project analysis detects Makefile."""
        with open(temp_project_dir / 'Makefile', 'w') as f:
            f.write('all:\n\techo "Building..."\n')

        bootstrap = AICaCBootstrap(str(temp_project_dir))
        analysis = bootstrap.analyze_project()

        assert analysis['has_makefile'] is True

    def test_analyze_project_with_readme(self, temp_project_dir):
        """Test project analysis detects README."""
        with open(temp_project_dir / 'README.md', 'w') as f:
            f.write('# Test Project\n')

        bootstrap = AICaCBootstrap(str(temp_project_dir))
        analysis = bootstrap.analyze_project()

        assert analysis['has_readme'] is True

    def test_create_minimal_structure_with_project_type_fallback(self, temp_project_dir):
        """Test structure creation when project type isn't detected."""
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        analysis = {
            'project_path': str(temp_project_dir),
            'has_package_json': False,
            'has_requirements_txt': False,
            'has_cargo_toml': False,
            'has_go_mod': False,
            'languages': [],
            'project_name': 'test-project',
        }

        result = bootstrap.create_minimal_structure(analysis)

        assert result['status'] == 'success'

        # Check context.yaml has fallback type
        context_path = temp_project_dir / '.ai' / 'context.yaml'
        with open(context_path) as f:
            context = yaml.safe_load(f)

        assert context['project']['type'] == 'application'  # Fallback

    def test_create_with_ai_placeholder(self, temp_project_dir):
        """Test create_with_ai returns minimal structure for now."""
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        analysis = bootstrap.analyze_project()

        # Call create_with_ai (currently just calls create_minimal_structure)
        result = bootstrap.create_with_ai(analysis, 'openai')

        assert result['status'] == 'success'
        assert 'context.yaml' in result['files_created']

    def test_detect_package_json_with_invalid_json(self, temp_project_dir):
        """Test handling of invalid package.json."""
        # Create invalid package.json
        with open(temp_project_dir / 'package.json', 'w') as f:
            f.write('{ invalid json }')

        bootstrap = AICaCBootstrap(str(temp_project_dir))
        name = bootstrap._detect_project_name()

        # Should fallback to directory name
        assert name == temp_project_dir.name

    def test_pr_body_includes_all_sections(self, temp_project_dir):
        """Test PR body has all required sections."""
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        result = {
            'status': 'success',
            'files_created': ['context.yaml', 'README.md'],
            'ai_dir': str(temp_project_dir / '.ai'),
        }

        pr_body = bootstrap.generate_pr_body(result)

        # Check for key sections
        assert 'AICaC' in pr_body
        assert 'Next Steps' in pr_body
        assert 'Resources' in pr_body
        assert 'Files Created' in pr_body
        assert 'badge' in pr_body.lower()
        assert 'architecture.yaml' in pr_body
        assert 'workflows.yaml' in pr_body
        assert 'decisions.yaml' in pr_body
        assert 'errors.yaml' in pr_body

    def test_ai_dir_creation_when_already_exists(self, aicac_project):
        """Test handling when .ai directory already exists."""
        bootstrap = AICaCBootstrap(str(aicac_project))
        analysis = bootstrap.analyze_project()

        # .ai already exists, should still succeed
        result = bootstrap.create_minimal_structure(analysis)

        assert result['status'] == 'success'

    def test_context_yaml_description_is_todo(self, temp_project_dir):
        """Test that generated context.yaml has TODO for description."""
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        analysis = {
            'project_path': str(temp_project_dir),
            'project_name': 'test',
            'project_type': 'app',
            'languages': [],
        }

        bootstrap.create_minimal_structure(analysis)

        context_path = temp_project_dir / '.ai' / 'context.yaml'
        with open(context_path) as f:
            context = yaml.safe_load(f)

        assert 'TODO' in context['project']['description']

    def test_entrypoints_has_todo_marker(self, temp_project_dir):
        """Test that entrypoints has TODO marker for user to fill."""
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        analysis = {
            'project_path': str(temp_project_dir),
            'project_name': 'test',
            'project_type': 'app',
            'languages': [],
        }

        bootstrap.create_minimal_structure(analysis)

        context_path = temp_project_dir / '.ai' / 'context.yaml'
        with open(context_path) as f:
            context = yaml.safe_load(f)

        assert 'TODO' in context['entrypoints']['main']

    def test_common_tasks_have_todo_markers(self, temp_project_dir):
        """Test that common_tasks have TODO markers."""
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        analysis = {
            'project_path': str(temp_project_dir),
            'project_name': 'test',
            'project_type': 'app',
            'languages': [],
        }

        bootstrap.create_minimal_structure(analysis)

        context_path = temp_project_dir / '.ai' / 'context.yaml'
        with open(context_path) as f:
            context = yaml.safe_load(f)

        for task in context['common_tasks'].values():
            assert 'TODO' in task
