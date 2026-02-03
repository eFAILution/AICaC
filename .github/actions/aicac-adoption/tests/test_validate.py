"""
Tests for validate.py - AICaC compliance validation
"""

import pytest
import sys
import yaml
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from validate import AICaCValidator


class TestAICaCValidator:
    """Tests for AICaCValidator class."""

    def test_initialization(self, temp_project_dir):
        """Test validator initialization."""
        validator = AICaCValidator(str(temp_project_dir))
        assert validator.project_path == temp_project_dir
        assert validator.ai_dir == temp_project_dir / '.ai'

    def test_validate_no_ai_directory(self, temp_project_dir):
        """Test validation when .ai/ doesn't exist."""
        validator = AICaCValidator(str(temp_project_dir))
        result = validator.validate()

        assert result['valid'] is False
        assert result['compliance_level'] == 'None'
        assert '.ai/ directory not found' in result['error']

    def test_validate_minimal_compliance(self, aicac_project):
        """Test validation of minimal compliance."""
        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()

        assert result['valid'] is True
        assert result['compliance_level'] == 'Minimal'
        assert result['context_valid'] is True
        assert result['found_files']['context.yaml'] is True

    def test_validate_comprehensive_compliance(self, comprehensive_aicac_project):
        """Test validation of comprehensive compliance."""
        validator = AICaCValidator(str(comprehensive_aicac_project))
        result = validator.validate()

        assert result['valid'] is True
        assert result['compliance_level'] == 'Comprehensive'
        assert result['found_files']['context.yaml'] is True
        assert result['found_files']['architecture.yaml'] is True
        assert result['found_files']['workflows.yaml'] is True
        assert result['found_files']['decisions.yaml'] is True
        assert result['found_files']['errors.yaml'] is True

    def test_validate_standard_compliance(self, aicac_project):
        """Test validation of standard compliance."""
        ai_dir = aicac_project / '.ai'

        # Add two optional files
        (ai_dir / 'architecture.yaml').write_text('components: {}')
        (ai_dir / 'workflows.yaml').write_text('workflows: {}')

        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()

        assert result['valid'] is True
        assert result['compliance_level'] == 'Standard'

    def test_validate_context_structure(self, aicac_project):
        """Test context.yaml validation."""
        validator = AICaCValidator(str(aicac_project))
        assert validator._validate_context() is True

    def test_validate_context_missing_version(self, aicac_project):
        """Test validation fails without version."""
        ai_dir = aicac_project / '.ai'
        context_path = ai_dir / 'context.yaml'

        # Write context without version
        with open(context_path, 'w') as f:
            yaml.dump({
                'project': {'name': 'test', 'type': 'app'},
                'entrypoints': {'main': 'index.js'},
                'common_tasks': {'dev': 'npm run dev'}
            }, f)

        validator = AICaCValidator(str(aicac_project))
        assert validator._validate_context() is False
        assert any('version' in err for err in validator.errors)

    def test_validate_context_missing_project_name(self, aicac_project):
        """Test validation fails without project name."""
        ai_dir = aicac_project / '.ai'
        context_path = ai_dir / 'context.yaml'

        with open(context_path, 'w') as f:
            yaml.dump({
                'version': '1.0',
                'project': {'type': 'app'},
                'entrypoints': {'main': 'index.js'},
                'common_tasks': {'dev': 'npm run dev'}
            }, f)

        validator = AICaCValidator(str(aicac_project))
        assert validator._validate_context() is False
        assert any('project.name' in err for err in validator.errors)

    def test_validate_context_missing_entrypoints(self, aicac_project):
        """Test validation fails without entrypoints."""
        ai_dir = aicac_project / '.ai'
        context_path = ai_dir / 'context.yaml'

        with open(context_path, 'w') as f:
            yaml.dump({
                'version': '1.0',
                'project': {'name': 'test', 'type': 'app'},
                'common_tasks': {'dev': 'npm run dev'}
            }, f)

        validator = AICaCValidator(str(aicac_project))
        assert validator._validate_context() is False
        assert any('entrypoint' in err for err in validator.errors)

    def test_validate_context_invalid_yaml(self, aicac_project):
        """Test validation handles invalid YAML."""
        ai_dir = aicac_project / '.ai'
        context_path = ai_dir / 'context.yaml'

        # Write invalid YAML
        with open(context_path, 'w') as f:
            f.write("invalid: yaml: syntax: [[[")

        validator = AICaCValidator(str(aicac_project))
        assert validator._validate_context() is False
        assert any('YAML' in err for err in validator.errors)

    def test_check_files(self, comprehensive_aicac_project):
        """Test file checking."""
        validator = AICaCValidator(str(comprehensive_aicac_project))
        found_files = validator._check_files()

        assert found_files['context.yaml'] is True
        assert found_files['architecture.yaml'] is True
        assert found_files['workflows.yaml'] is True
        assert found_files['decisions.yaml'] is True
        assert found_files['errors.yaml'] is True

    def test_determine_compliance_none(self, temp_project_dir):
        """Test compliance determination when no .ai/ exists."""
        validator = AICaCValidator(str(temp_project_dir))
        level = validator._determine_compliance({}, False)
        assert level == 'None'

    def test_determine_compliance_minimal(self):
        """Test compliance determination for minimal."""
        validator = AICaCValidator('.')
        found_files = {
            'context.yaml': True,
            'architecture.yaml': False,
            'workflows.yaml': False,
            'decisions.yaml': False,
            'errors.yaml': False,
        }
        level = validator._determine_compliance(found_files, True)
        assert level == 'Minimal'

    def test_determine_compliance_standard(self):
        """Test compliance determination for standard."""
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

    def test_determine_compliance_comprehensive(self):
        """Test compliance determination for comprehensive."""
        validator = AICaCValidator('.')
        found_files = {
            'context.yaml': True,
            'architecture.yaml': True,
            'workflows.yaml': True,
            'decisions.yaml': True,
            'errors.yaml': True,
        }
        level = validator._determine_compliance(found_files, True)
        assert level == 'Comprehensive'

    def test_get_badge_recommendation(self):
        """Test badge URL generation."""
        validator = AICaCValidator('.')

        badge = validator._get_badge_recommendation('Comprehensive')
        assert 'Comprehensive' in badge
        assert 'success' in badge

        badge = validator._get_badge_recommendation('Standard')
        assert 'Standard' in badge
        assert 'brightgreen' in badge

        badge = validator._get_badge_recommendation('Minimal')
        assert 'Minimal' in badge
        assert 'green' in badge

    def test_get_badge_markdown(self):
        """Test badge markdown generation."""
        validator = AICaCValidator('.')
        markdown = validator._get_badge_markdown('Comprehensive')

        assert markdown.startswith('[![AICaC]')
        assert 'https://img.shields.io/badge/' in markdown
        assert 'Comprehensive' in markdown
        assert 'https://github.com/eFAILution/AICaC' in markdown

    def test_full_validation_result_structure(self, comprehensive_aicac_project):
        """Test complete validation result structure."""
        validator = AICaCValidator(str(comprehensive_aicac_project))
        result = validator.validate()

        # Check all expected keys
        assert 'valid' in result
        assert 'compliance_level' in result
        assert 'found_files' in result
        assert 'context_valid' in result
        assert 'errors' in result
        assert 'badge' in result
        assert 'badge_markdown' in result

        # Check types
        assert isinstance(result['valid'], bool)
        assert isinstance(result['compliance_level'], str)
        assert isinstance(result['found_files'], dict)
        assert isinstance(result['errors'], list)
