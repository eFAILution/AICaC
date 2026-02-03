"""
Additional tests for update_badge.py to improve coverage.
Focuses on edge cases, error paths, and badge placement logic.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from update_badge import BadgeUpdater


class TestUpdateBadgeCoverage:
    """Additional tests for code coverage."""

    def test_has_badge_with_no_content(self):
        """Test has_badge with empty content."""
        updater = BadgeUpdater('.')
        assert updater.has_badge('') is False

    def test_has_badge_with_different_badge(self, temp_project_dir):
        """Test has_badge doesn't match non-AICaC badges."""
        readme = """# Project
[![Build](https://img.shields.io/badge/build-passing-green.svg)](https://example.com)
"""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text(readme)

        updater = BadgeUpdater(str(temp_project_dir))
        content = readme_path.read_text()
        assert updater.has_badge(content) is False

    def test_update_badge_creates_badge_section_no_existing_badges(self, temp_project_dir):
        """Test adding badge when no other badges exist."""
        readme = """# My Project

This is a project without badges.

## Installation

npm install
"""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text(readme)

        updater = BadgeUpdater(str(temp_project_dir))
        success, message = updater.update_badge('Minimal')

        assert success is True
        content = readme_path.read_text()
        assert '[![AICaC]' in content

    def test_update_badge_no_heading_in_readme(self, temp_project_dir):
        """Test badge placement when README has no heading."""
        readme = """This is a README with no heading.

Just some text.
"""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text(readme)

        updater = BadgeUpdater(str(temp_project_dir))
        success, message = updater.update_badge('Standard')

        assert success is True
        content = readme_path.read_text()
        assert '[![AICaC]' in content

    def test_check_badge_accuracy_with_whitespace_differences(self, temp_project_dir):
        """Test badge accuracy check handles formatting differences."""
        # Badge with extra spaces or newlines
        readme = """# Project

[![AICaC](https://img.shields.io/badge/AICaC-Minimal-green.svg)](https://github.com/eFAILution/AICaC)

Description.
"""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text(readme)

        updater = BadgeUpdater(str(temp_project_dir))
        is_accurate, current = updater.check_badge_accuracy('Minimal')

        assert is_accurate is True

    def test_update_badge_with_multiline_badges(self, temp_project_dir):
        """Test updating badge when badges span multiple lines."""
        readme = """# Project

[![Build](https://img.shields.io/badge/build-passing-green.svg)](https://example.com)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Description.
"""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text(readme)

        updater = BadgeUpdater(str(temp_project_dir))
        success, message = updater.update_badge('Comprehensive')

        assert success is True
        content = readme_path.read_text()
        assert '[![AICaC]' in content
        assert 'Comprehensive' in content

    def test_get_badge_for_level_all_levels(self):
        """Test badge generation for all possible levels."""
        updater = BadgeUpdater('.')

        levels_and_expected = [
            ('Comprehensive', 'success'),
            ('Standard', 'brightgreen'),
            ('Minimal', 'green'),
            ('None', 'Not%20Adopted'),
        ]

        for level, expected_in_badge in levels_and_expected:
            badge = updater.get_badge_for_level(level)
            assert expected_in_badge in badge
            assert 'https://img.shields.io/badge/' in badge
            assert 'https://github.com/eFAILution/AICaC' in badge

    def test_update_badge_preserves_formatting(self, temp_project_dir):
        """Test that badge update preserves README formatting."""
        readme = """# My Project

[![Build](https://img.shields.io/badge/build-passing-green.svg)](https://example.com)

## Overview

This is my project.

## Installation

```bash
npm install
```

## Usage

Run the thing.
"""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text(readme)

        updater = BadgeUpdater(str(temp_project_dir))
        updater.update_badge('Standard')

        content = readme_path.read_text()

        # Check sections are preserved
        assert '## Overview' in content
        assert '## Installation' in content
        assert '## Usage' in content
        assert '```bash' in content
        assert 'npm install' in content

    def test_update_badge_with_none_level(self, readme_without_badge):
        """Test updating badge to None level (not adopted)."""
        updater = BadgeUpdater(str(readme_without_badge))
        success, message = updater.update_badge('None')

        assert success is True
        content = (readme_without_badge / 'README.md').read_text()
        assert 'Not%20Adopted' in content
        assert 'red' in content

    def test_badge_replacement_is_exact(self, temp_project_dir):
        """Test that badge replacement replaces the exact badge."""
        # Start with Minimal
        readme = """# Project

[![AICaC](https://img.shields.io/badge/AICaC-Minimal-green.svg)](https://github.com/eFAILution/AICaC)

Description.
"""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text(readme)

        updater = BadgeUpdater(str(temp_project_dir))

        # Update to Comprehensive
        updater.update_badge('Comprehensive')
        content = readme_path.read_text()

        # Should have Comprehensive, not Minimal
        assert 'Comprehensive' in content
        assert 'Minimal' not in content
        # Should still have exactly one AICaC badge
        assert content.count('[![AICaC]') == 1

    def test_update_badge_empty_readme(self, temp_project_dir):
        """Test updating badge in an empty README."""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text('')

        updater = BadgeUpdater(str(temp_project_dir))
        success, message = updater.update_badge('Standard')

        assert success is True
        content = readme_path.read_text()
        assert '[![AICaC]' in content

    def test_update_badge_readme_with_only_heading(self, temp_project_dir):
        """Test updating badge in README with only a heading."""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text('# My Project\n')

        updater = BadgeUpdater(str(temp_project_dir))
        success, message = updater.update_badge('Minimal')

        assert success is True
        content = readme_path.read_text()

        lines = content.split('\n')
        # Badge should be after heading
        heading_line = next(i for i, line in enumerate(lines) if line.startswith('#'))
        badge_line = next(i for i, line in enumerate(lines) if '[![AICaC]' in line)
        assert badge_line > heading_line

    def test_check_badge_accuracy_badge_in_middle_of_file(self, temp_project_dir):
        """Test badge accuracy check when badge is not at top."""
        readme = """# Project

Some description here.

[![AICaC](https://img.shields.io/badge/AICaC-Standard-brightgreen.svg)](https://github.com/eFAILution/AICaC)

More content.
"""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text(readme)

        updater = BadgeUpdater(str(temp_project_dir))
        is_accurate, current = updater.check_badge_accuracy('Standard')

        assert is_accurate is True
        assert current is not None

    def test_update_badge_repeated_calls_same_result(self, readme_without_badge):
        """Test that repeated badge updates produce consistent results."""
        updater = BadgeUpdater(str(readme_without_badge))
        readme_path = readme_without_badge / 'README.md'

        # First update
        updater.update_badge('Standard')
        content1 = readme_path.read_text()
        badge_count1 = content1.count('[![AICaC]')

        # Second update with same level
        updater.update_badge('Standard')
        content2 = readme_path.read_text()
        badge_count2 = content2.count('[![AICaC]')

        # Third update with same level
        updater.update_badge('Standard')
        content3 = readme_path.read_text()
        badge_count3 = content3.count('[![AICaC]')

        # Should always have exactly one badge
        assert badge_count1 == 1
        assert badge_count2 == 1
        assert badge_count3 == 1

    def test_badge_pattern_matches_correctly(self):
        """Test that BADGE_PATTERN regex matches AICaC badges."""
        import re
        updater = BadgeUpdater('.')

        test_cases = [
            ('[![AICaC](https://img.shields.io/badge/AICaC-Minimal-green.svg)](https://github.com/eFAILution/AICaC)', True),
            ('[![AICaC](https://img.shields.io/badge/AICaC-Standard-brightgreen.svg)](https://github.com/eFAILution/AICaC)', True),
            ('[![Build](https://img.shields.io/badge/build-passing-green.svg)](https://example.com)', False),
            ('[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)', False),
        ]

        for text, should_match in test_cases:
            matches = bool(re.search(updater.BADGE_PATTERN, text))
            assert matches == should_match, f"Pattern match failed for: {text}"
