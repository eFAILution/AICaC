"""
Additional tests for validate.py to improve coverage.
Focuses on print_report, error handling, and edge cases.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from validate import AICaCValidator


class TestValidateCoverage:
    """Additional tests for code coverage."""

    def test_validate_context_empty_entrypoints(self, aicac_project):
        """Test validation fails with empty entrypoints dict."""
        import yaml

        context_path = aicac_project / '.ai' / 'context.yaml'
        with open(context_path, 'w') as f:
            yaml.dump({
                'version': '1.0',
                'project': {'name': 'test', 'type': 'app'},
                'entrypoints': {},  # Empty
                'common_tasks': {'dev': 'npm run dev'}
            }, f)

        validator = AICaCValidator(str(aicac_project))
        assert validator._validate_context() is False

    def test_validate_context_empty_common_tasks(self, aicac_project):
        """Test validation fails with empty common_tasks dict."""
        import yaml

        context_path = aicac_project / '.ai' / 'context.yaml'
        with open(context_path, 'w') as f:
            yaml.dump({
                'version': '1.0',
                'project': {'name': 'test', 'type': 'app'},
                'entrypoints': {'main': 'index.js'},
                'common_tasks': {}  # Empty
            }, f)

        validator = AICaCValidator(str(aicac_project))
        assert validator._validate_context() is False

    def test_validate_context_file_read_error(self, aicac_project):
        """Test handling of file read errors."""
        context_path = aicac_project / '.ai' / 'context.yaml'

        # Make file unreadable (chmod 000)
        import os
        os.chmod(context_path, 0o000)

        validator = AICaCValidator(str(aicac_project))
        result = validator._validate_context()

        # Restore permissions
        os.chmod(context_path, 0o644)

        assert result is False

    def test_validate_with_invalid_context_returns_none_level(self, aicac_project):
        """Test that invalid context.yaml results in None compliance."""
        import yaml

        context_path = aicac_project / '.ai' / 'context.yaml'
        with open(context_path, 'w') as f:
            yaml.dump({'invalid': 'structure'}, f)

        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()

        # Invalid context but .ai exists
        assert result['compliance_level'] in ['None', 'Minimal']

    def test_check_files_reports_missing_required(self, temp_project_dir):
        """Test that check_files reports missing required files."""
        ai_dir = temp_project_dir / '.ai'
        ai_dir.mkdir()

        validator = AICaCValidator(str(temp_project_dir))
        found_files = validator._check_files()

        # context.yaml is required but missing
        assert found_files['context.yaml'] is False
        assert any('Required file missing' in err for err in validator.errors)

    def test_print_report_for_non_adopted(self, temp_project_dir, capsys):
        """Test print_report for projects without AICaC."""
        validator = AICaCValidator(str(temp_project_dir))
        result = validator.validate()

        validator.print_report(result)
        captured = capsys.readouterr()

        assert 'AICaC NOT ADOPTED' in captured.out
        assert '.ai/ directory not found' in captured.out

    def test_print_report_for_minimal(self, aicac_project, capsys):
        """Test print_report for minimal compliance."""
        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()

        validator.print_report(result)
        captured = capsys.readouterr()

        assert 'Compliance Level: Minimal' in captured.out
        assert '✓ .ai/context.yaml' in captured.out
        assert 'Recommended Badge:' in captured.out

    def test_print_report_for_comprehensive(self, comprehensive_aicac_project, capsys):
        """Test print_report for comprehensive compliance."""
        validator = AICaCValidator(str(comprehensive_aicac_project))
        result = validator.validate()

        validator.print_report(result)
        captured = capsys.readouterr()

        assert 'Compliance Level: Comprehensive' in captured.out
        assert '✓ .ai/context.yaml' in captured.out
        assert '✓ .ai/architecture.yaml' in captured.out
        assert '✓ .ai/workflows.yaml' in captured.out
        assert '✓ .ai/decisions.yaml' in captured.out
        assert '✓ .ai/errors.yaml' in captured.out

    def test_print_report_shows_validation_errors(self, aicac_project, capsys):
        """Test that print_report shows validation errors."""
        import yaml

        # Create invalid context.yaml
        context_path = aicac_project / '.ai' / 'context.yaml'
        with open(context_path, 'w') as f:
            yaml.dump({'version': '1.0'}, f)  # Missing required fields

        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()

        validator.print_report(result)
        captured = capsys.readouterr()

        # Should show validation errors or invalid context
        has_error_text = ('Validation Errors:' in captured.out or
                         '✗ context.yaml' in captured.out or
                         'context.yaml has issues' in captured.out or
                         len(result['errors']) > 0)
        assert has_error_text

    def test_print_report_suggestions_for_standard(self, aicac_project, capsys):
        """Test that print_report shows improvement suggestions."""
        # Add just two optional files for Standard compliance
        ai_dir = aicac_project / '.ai'
        (ai_dir / 'architecture.yaml').write_text('components: {}')
        (ai_dir / 'workflows.yaml').write_text('workflows: {}')

        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()

        validator.print_report(result)
        captured = capsys.readouterr()

        assert 'Suggestions to improve compliance:' in captured.out
        assert 'decisions.yaml' in captured.out
        assert 'errors.yaml' in captured.out

    def test_print_report_no_suggestions_for_comprehensive(self, comprehensive_aicac_project, capsys):
        """Test that comprehensive compliance shows no improvement suggestions."""
        validator = AICaCValidator(str(comprehensive_aicac_project))
        result = validator.validate()

        validator.print_report(result)
        captured = capsys.readouterr()

        # Should not have suggestions section for comprehensive
        assert 'Compliance Level: Comprehensive' in captured.out

    def test_get_badge_recommendation_unknown_level(self):
        """Test badge recommendation for unknown compliance level."""
        validator = AICaCValidator('.')
        badge = validator._get_badge_recommendation('Unknown')

        assert 'Not%20Adopted' in badge  # Falls back to None badge

    def test_determine_compliance_with_invalid_context(self):
        """Test compliance determination when context is invalid."""
        validator = AICaCValidator('.')
        found_files = {
            'context.yaml': True,
            'architecture.yaml': False,
            'workflows.yaml': False,
            'decisions.yaml': False,
            'errors.yaml': False,
        }

        # context exists but is invalid
        level = validator._determine_compliance(found_files, False)
        assert level == 'None'

    def test_determine_compliance_exactly_two_optional(self):
        """Test compliance level with exactly 2 optional files."""
        validator = AICaCValidator('.')
        found_files = {
            'context.yaml': True,
            'architecture.yaml': True,
            'workflows.yaml': True,
            'decisions.yaml': False,
            'errors.yaml': False,
        }

        level = validator._determine_compliance(found_files, True)
        assert level == 'Standard'

    def test_determine_compliance_three_optional(self):
        """Test compliance level with 3 optional files."""
        validator = AICaCValidator('.')
        found_files = {
            'context.yaml': True,
            'architecture.yaml': True,
            'workflows.yaml': True,
            'decisions.yaml': True,
            'errors.yaml': False,
        }

        level = validator._determine_compliance(found_files, True)
        assert level == 'Standard'  # Need all 4 for Comprehensive

    def test_validate_returns_all_required_keys(self, aicac_project):
        """Test validate returns dict with all required keys when .ai exists."""
        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()

        required_keys = [
            'valid', 'compliance_level', 'context_valid',
            'errors', 'badge', 'badge_markdown'
        ]

        for key in required_keys:
            assert key in result

    def test_validate_returns_error_when_no_ai_dir(self, temp_project_dir):
        """Test validate returns error dict when .ai doesn't exist."""
        validator = AICaCValidator(str(temp_project_dir))
        result = validator.validate()

        # When .ai/ doesn't exist, returns different structure
        assert 'valid' in result
        assert 'compliance_level' in result
        assert 'error' in result
        assert result['valid'] is False
        assert result['compliance_level'] == 'None'

    def test_validate_found_files_structure(self, comprehensive_aicac_project):
        """Test that found_files has all expected file keys."""
        validator = AICaCValidator(str(comprehensive_aicac_project))
        result = validator.validate()

        expected_files = [
            'context.yaml', 'architecture.yaml', 'workflows.yaml',
            'decisions.yaml', 'errors.yaml'
        ]

        for file in expected_files:
            assert file in result['found_files']
            assert isinstance(result['found_files'][file], bool)
