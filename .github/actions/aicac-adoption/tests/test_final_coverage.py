"""
Final tests to push coverage over 80%.
Covers remaining edge cases and exception handling.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from bootstrap import AICaCBootstrap
from update_badge import BadgeUpdater


class TestFinalCoverage:
    """Final coverage push tests."""

    def test_detect_project_name_cargo_toml_without_tomli(self, temp_project_dir):
        """Test Cargo.toml handling when tomli is not available."""
        # Create Cargo.toml
        cargo_content = """[package]
name = "rust-project"
version = "0.1.0"
"""
        with open(temp_project_dir / 'Cargo.toml', 'w') as f:
            f.write(cargo_content)

        bootstrap = AICaCBootstrap(str(temp_project_dir))

        # This will try to import tomli and may fail, falling back to dir name
        name = bootstrap._detect_project_name()

        # Should either succeed with tomli or fallback
        assert name in ['rust-project', temp_project_dir.name]

    def test_detect_project_name_invalid_cargo_toml(self, temp_project_dir):
        """Test handling of malformed Cargo.toml."""
        # Create invalid Cargo.toml
        with open(temp_project_dir / 'Cargo.toml', 'w') as f:
            f.write('[package\ninvalid toml')

        bootstrap = AICaCBootstrap(str(temp_project_dir))
        name = bootstrap._detect_project_name()

        # Should fallback to directory name
        assert name == temp_project_dir.name

    def test_update_badge_readme_only_badges_no_content(self, temp_project_dir):
        """Test badge update when README only has badges."""
        readme = """# Project
[![Build](https://img.shields.io/badge/build-passing-green.svg)](https://example.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
"""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text(readme)

        updater = BadgeUpdater(str(temp_project_dir))
        success, message = updater.update_badge('Standard')

        assert success is True
        content = readme_path.read_text()
        assert '[![AICaC]' in content
        assert 'Standard' in content

    def test_bootstrap_analyze_project_all_false(self, temp_project_dir):
        """Test project analysis with no recognized files."""
        # Empty directory with no package.json, requirements.txt, etc.
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        analysis = bootstrap.analyze_project()

        assert analysis['has_package_json'] is False
        assert analysis['has_requirements_txt'] is False
        assert analysis['has_cargo_toml'] is False
        assert analysis['has_go_mod'] is False
        assert len(analysis['languages']) == 0

    def test_update_badge_check_only_mode(self, readme_with_outdated_badge):
        """Test check-only mode doesn't modify file."""
        updater = BadgeUpdater(str(readme_with_outdated_badge))
        readme_path = readme_with_outdated_badge / 'README.md'

        original_content = readme_path.read_text()

        # Check accuracy (outdated badge)
        is_accurate, current = updater.check_badge_accuracy('Comprehensive')

        # File should not be modified
        current_content = readme_path.read_text()
        assert current_content == original_content
        assert is_accurate is False

    def test_bootstrap_pr_body_multiple_files(self, temp_project_dir):
        """Test PR body generation with multiple files created."""
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        result = {
            'status': 'success',
            'files_created': [
                'context.yaml',
                'README.md',
                'architecture.yaml',
                'workflows.yaml'
            ],
            'ai_dir': str(temp_project_dir / '.ai'),
        }

        pr_body = bootstrap.generate_pr_body(result)

        # All files should be listed
        for file in result['files_created']:
            assert file in pr_body

    def test_update_badge_level_none(self, temp_project_dir):
        """Test badge generation for None compliance level."""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text('# Project\n\nDescription.\n')

        updater = BadgeUpdater(str(temp_project_dir))
        badge = updater.get_badge_for_level('None')

        assert 'Not%20Adopted' in badge
        assert 'red' in badge

    def test_bootstrap_context_yaml_has_description(self, temp_project_dir):
        """Test that generated context.yaml includes description field."""
        bootstrap = AICaCBootstrap(str(temp_project_dir))
        analysis = {
            'project_path': str(temp_project_dir),
            'project_name': 'test-project',
            'project_type': 'web-app',
            'languages': ['javascript'],
        }

        result = bootstrap.create_minimal_structure(analysis)

        import yaml
        context_path = temp_project_dir / '.ai' / 'context.yaml'
        with open(context_path) as f:
            context = yaml.safe_load(f)

        assert 'description' in context['project']
        assert context['project']['description'] is not None
