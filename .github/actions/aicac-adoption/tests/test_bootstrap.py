"""
Tests for bootstrap.py - AICaC structure creation
"""

import pytest
import sys
import yaml
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from bootstrap import AICaCBootstrap


class TestAICaCBootstrap:
    """Tests for AICaCBootstrap class."""

    def test_initialization(self, temp_project_dir):
        """Test bootstrap initialization."""
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        assert bootstrap.project_path == temp_project_dir
        assert bootstrap.ai_dir == temp_project_dir / '.ai'

    def test_analyze_node_project(self, node_project):
        """Test project analysis for Node.js project."""
        bootstrap = AICaCBootstrap(str(node_project))
        analysis = bootstrap.analyze_project()

        assert analysis['has_package_json'] is True
        assert 'javascript' in analysis['languages']
        assert analysis['project_type'] == 'node-app'
        assert analysis['project_name'] == 'test-node-project'

    def test_analyze_python_project(self, python_project):
        """Test project analysis for Python project."""
        bootstrap = AICaCBootstrap(str(python_project))
        analysis = bootstrap.analyze_project()

        assert analysis['has_requirements_txt'] is True
        assert 'python' in analysis['languages']
        assert analysis['project_type'] == 'python-app'

    def test_detect_project_name_from_package_json(self, node_project):
        """Test project name detection from package.json."""
        bootstrap = AICaCBootstrap(str(node_project))
        name = bootstrap._detect_project_name()
        assert name == 'test-node-project'

    def test_detect_project_name_fallback(self, temp_project_dir):
        """Test project name fallback to directory name."""
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        name = bootstrap._detect_project_name()
        assert name == temp_project_dir.name

    def test_create_minimal_structure(self, node_project):
        """Test creating minimal .ai/ structure."""
        bootstrap = AICaCBootstrap(str(node_project))
        analysis = bootstrap.analyze_project()
        result = bootstrap.create_minimal_structure(analysis)

        assert result['status'] == 'success'
        assert 'context.yaml' in result['files_created']
        assert 'README.md' in result['files_created']

        # Verify .ai directory created
        ai_dir = node_project / '.ai'
        assert ai_dir.exists()
        assert ai_dir.is_dir()

        # Verify context.yaml
        context_path = ai_dir / 'context.yaml'
        assert context_path.exists()

        with open(context_path) as f:
            context = yaml.safe_load(f)

        assert context['version'] == '1.0'
        assert context['project']['name'] == 'test-node-project'
        assert context['project']['type'] == 'node-app'
        assert 'entrypoints' in context
        assert 'common_tasks' in context

        # Verify README.md
        readme_path = ai_dir / 'README.md'
        assert readme_path.exists()
        readme_content = readme_path.read_text()
        assert 'AICaC' in readme_content
        assert 'context.yaml' in readme_content

    def test_create_minimal_structure_creates_directory(self, temp_project_dir):
        """Test that .ai directory is created if it doesn't exist."""
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        analysis = bootstrap.analyze_project()

        ai_dir = temp_project_dir / '.ai'
        assert not ai_dir.exists()

        result = bootstrap.create_minimal_structure(analysis)

        assert ai_dir.exists()
        assert result['status'] == 'success'

    def test_generate_pr_body(self, temp_project_dir):
        """Test PR body generation."""
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        result = {
            'status': 'success',
            'files_created': ['context.yaml', 'README.md'],
            'ai_dir': str(temp_project_dir / '.ai'),
        }

        pr_body = bootstrap.generate_pr_body(result)

        assert 'AICaC' in pr_body
        assert 'context.yaml' in pr_body
        assert 'README.md' in pr_body
        assert 'Next Steps' in pr_body
        assert 'badge' in pr_body.lower()

    def test_context_yaml_has_all_required_fields(self, node_project):
        """Test that generated context.yaml has all required fields."""
        bootstrap = AICaCBootstrap(str(node_project))
        analysis = bootstrap.analyze_project()
        bootstrap.create_minimal_structure(analysis)

        context_path = node_project / '.ai' / 'context.yaml'
        with open(context_path) as f:
            context = yaml.safe_load(f)

        # Required fields
        assert 'version' in context
        assert 'project' in context
        assert 'name' in context['project']
        assert 'type' in context['project']
        assert 'entrypoints' in context
        assert 'common_tasks' in context

        # Ensure at least one entrypoint
        assert len(context['entrypoints']) > 0

        # Ensure at least one common task
        assert len(context['common_tasks']) > 0

    def test_idempotency(self, node_project):
        """Test that creating structure multiple times doesn't break."""
        bootstrap = AICaCBootstrap(str(node_project))
        analysis = bootstrap.analyze_project()

        # Create once
        result1 = bootstrap.create_minimal_structure(analysis)
        assert result1['status'] == 'success'

        # Create again (should still succeed but overwrite)
        result2 = bootstrap.create_minimal_structure(analysis)
        assert result2['status'] == 'success'

        # Verify files still valid
        context_path = node_project / '.ai' / 'context.yaml'
        assert context_path.exists()
        with open(context_path) as f:
            context = yaml.safe_load(f)
        assert context['version'] == '1.0'
