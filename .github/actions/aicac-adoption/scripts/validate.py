#!/usr/bin/env python3
"""
AICaC Badge Validator

Validates AICaC compliance and recommends appropriate badge.
Usage: python badge_validator.py [path_to_project]
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple


class AICaCValidator:
    """Validates AICaC compliance and suggests appropriate badge."""

    REQUIRED_FILES = {
        'context.yaml': True,  # Required
        'architecture.yaml': False,
        'workflows.yaml': False,
        'decisions.yaml': False,
        'errors.yaml': False,
    }

    REQUIRED_CONTEXT_FIELDS = [
        'version',
        'project.name',
        'project.type',
    ]

    def __init__(self, project_path: str = '.'):
        self.project_path = Path(project_path)
        self.ai_dir = self.project_path / '.ai'
        self.results = {}
        self.errors = []

    def validate(self) -> Dict:
        """Run validation and return results."""
        if not self.ai_dir.exists():
            return {
                'valid': False,
                'compliance_level': 'None',
                'error': '.ai/ directory not found',
                'recommendation': 'Create .ai/ directory and add context.yaml'
            }

        # Check for required and optional files
        found_files = self._check_files()

        # Validate context.yaml if present
        context_valid = self._validate_context()

        # Determine compliance level
        compliance_level = self._determine_compliance(found_files, context_valid)

        # Get badge recommendation
        badge = self._get_badge_recommendation(compliance_level)

        return {
            'valid': compliance_level != 'None',
            'compliance_level': compliance_level,
            'found_files': found_files,
            'context_valid': context_valid,
            'errors': self.errors,
            'badge': badge,
            'badge_markdown': self._get_badge_markdown(compliance_level)
        }

    def _check_files(self) -> Dict[str, bool]:
        """Check which AICaC files are present."""
        found = {}
        for filename, required in self.REQUIRED_FILES.items():
            filepath = self.ai_dir / filename
            exists = filepath.exists()
            found[filename] = exists

            if required and not exists:
                self.errors.append(f"Required file missing: .ai/{filename}")

        return found

    def _validate_context(self) -> bool:
        """Validate context.yaml structure."""
        context_path = self.ai_dir / 'context.yaml'

        if not context_path.exists():
            return False

        try:
            with open(context_path, 'r') as f:
                context = yaml.safe_load(f)

            # Check required fields
            if not context.get('version'):
                self.errors.append("context.yaml: 'version' field is required")
                return False

            project = context.get('project', {})
            if not project.get('name'):
                self.errors.append("context.yaml: 'project.name' field is required")
                return False

            if not project.get('type'):
                self.errors.append("context.yaml: 'project.type' field is required")
                return False

            # Check for at least one entrypoint
            entrypoints = context.get('entrypoints', {})
            if not entrypoints:
                self.errors.append("context.yaml: at least one 'entrypoint' is required")
                return False

            # Check for at least one common task
            common_tasks = context.get('common_tasks', {})
            if not common_tasks:
                self.errors.append("context.yaml: at least one 'common_task' is required")
                return False

            return True

        except yaml.YAMLError as e:
            self.errors.append(f"context.yaml: Invalid YAML syntax - {e}")
            return False
        except Exception as e:
            self.errors.append(f"context.yaml: Error reading file - {e}")
            return False

    def _determine_compliance(self, found_files: Dict[str, bool],
                            context_valid: bool) -> str:
        """Determine compliance level based on files present."""
        if not found_files.get('context.yaml') or not context_valid:
            return 'None'

        # Count optional files
        optional_count = sum(1 for f in ['architecture.yaml', 'workflows.yaml',
                                        'decisions.yaml', 'errors.yaml']
                           if found_files.get(f))

        if optional_count >= 4:
            return 'Comprehensive'
        elif optional_count >= 2:
            return 'Standard'
        else:
            return 'Minimal'

    def _get_badge_recommendation(self, compliance_level: str) -> str:
        """Get shields.io badge URL for compliance level."""
        badges = {
            'Comprehensive': 'https://img.shields.io/badge/AICaC-Comprehensive-success.svg',
            'Standard': 'https://img.shields.io/badge/AICaC-Standard-brightgreen.svg',
            'Minimal': 'https://img.shields.io/badge/AICaC-Minimal-green.svg',
            'None': 'https://img.shields.io/badge/AICaC-Not%20Adopted-red.svg'
        }
        return badges.get(compliance_level, badges['None'])

    def _get_badge_markdown(self, compliance_level: str) -> str:
        """Get markdown for the badge."""
        badge_url = self._get_badge_recommendation(compliance_level)
        return f"[![AICaC]({badge_url})](https://github.com/eFAILution/AICaC)"

    def print_report(self, results: Dict):
        """Print a formatted report of validation results."""
        print("=" * 60)
        print("AICaC Compliance Validation Report")
        print("=" * 60)
        print()

        if not results['valid']:
            print("❌ AICaC NOT ADOPTED")
            print(f"   {results.get('error', 'Unknown error')}")
            print()
            print(f"Recommendation: {results.get('recommendation', 'See BADGES.md')}")
            return

        print(f"Compliance Level: {results['compliance_level']}")
        print()

        print("Files Found:")
        for filename, found in results['found_files'].items():
            status = "✓" if found else "✗"
            print(f"  {status} .ai/{filename}")
        print()

        if results['errors']:
            print("Validation Errors:")
            for error in results['errors']:
                print(f"  ⚠️  {error}")
            print()

        if results['context_valid']:
            print("✓ context.yaml is valid")
        else:
            print("✗ context.yaml has issues (see errors above)")
        print()

        print("Recommended Badge:")
        print(f"  {results['badge_markdown']}")
        print()

        # Suggestions for improvement
        if results['compliance_level'] != 'Comprehensive':
            print("Suggestions to improve compliance:")
            missing = [f for f, found in results['found_files'].items()
                      if not found and f != 'context.yaml']
            for filename in missing:
                print(f"  • Add .ai/{filename}")
            print()

        print("=" * 60)


def main():
    """Main entry point."""
    project_path = sys.argv[1] if len(sys.argv) > 1 else '.'

    validator = AICaCValidator(project_path)
    results = validator.validate()
    validator.print_report(results)

    # Exit with appropriate code
    sys.exit(0 if results['valid'] else 1)


if __name__ == '__main__':
    main()
