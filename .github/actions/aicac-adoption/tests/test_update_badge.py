"""
Tests for update_badge.py - README badge updating
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from update_badge import BadgeUpdater


class TestBadgeUpdater:
    """Tests for BadgeUpdater class."""

    def test_initialization(self, temp_project_dir):
        """Test badge updater initialization."""
        updater = BadgeUpdater(str(temp_project_dir))
        assert updater.project_path == temp_project_dir
        assert updater.readme_path == temp_project_dir / 'README.md'

    def test_get_badge_for_level(self):
        """Test badge generation for each level."""
        updater = BadgeUpdater('.')

        badge = updater.get_badge_for_level('Comprehensive')
        assert 'Comprehensive' in badge
        assert 'success' in badge

        badge = updater.get_badge_for_level('Standard')
        assert 'Standard' in badge
        assert 'brightgreen' in badge

        badge = updater.get_badge_for_level('Minimal')
        assert 'Minimal' in badge
        assert 'green' in badge

        badge = updater.get_badge_for_level('None')
        assert 'Not%20Adopted' in badge

    def test_has_badge_true(self, aicac_project):
        """Test badge detection when badge exists."""
        updater = BadgeUpdater(str(aicac_project))
        readme_content = (aicac_project / 'README.md').read_text()
        assert updater.has_badge(readme_content) is True

    def test_has_badge_false(self, readme_without_badge):
        """Test badge detection when badge doesn't exist."""
        updater = BadgeUpdater(str(readme_without_badge))
        readme_content = (readme_without_badge / 'README.md').read_text()
        assert updater.has_badge(readme_content) is False

    def test_update_badge_replace_existing(self, readme_with_outdated_badge):
        """Test updating existing badge."""
        updater = BadgeUpdater(str(readme_with_outdated_badge))
        success, message = updater.update_badge('Comprehensive')

        assert success is True
        assert 'Updated' in message

        # Verify badge was updated
        readme_content = (readme_with_outdated_badge / 'README.md').read_text()
        assert 'Comprehensive' in readme_content
        assert 'success' in readme_content
        # Old badge should be gone
        assert readme_content.count('[![AICaC]') == 1

    def test_update_badge_add_new(self, readme_without_badge):
        """Test adding new badge when none exists."""
        updater = BadgeUpdater(str(readme_without_badge))
        success, message = updater.update_badge('Standard')

        assert success is True
        assert 'Added' in message

        # Verify badge was added
        readme_content = (readme_without_badge / 'README.md').read_text()
        assert '[![AICaC]' in readme_content
        assert 'Standard' in readme_content
        assert 'brightgreen' in readme_content

    def test_update_badge_no_readme(self, temp_project_dir):
        """Test handling when README doesn't exist."""
        updater = BadgeUpdater(str(temp_project_dir))
        success, message = updater.update_badge('Minimal')

        assert success is False
        assert 'README.md not found' in message

    def test_update_badge_preserves_content(self, readme_without_badge):
        """Test that updating badge preserves other content."""
        original_content = (readme_without_badge / 'README.md').read_text()

        updater = BadgeUpdater(str(readme_without_badge))
        updater.update_badge('Minimal')

        new_content = (readme_without_badge / 'README.md').read_text()

        # Original content should still be present
        assert '## Description' in new_content
        assert 'test project' in new_content
        assert '## Installation' in new_content
        # New badge added
        assert '[![AICaC]' in new_content

    def test_update_badge_preserves_other_badges(self, readme_without_badge):
        """Test that other badges are preserved."""
        updater = BadgeUpdater(str(readme_without_badge))
        updater.update_badge('Standard')

        readme_content = (readme_without_badge / 'README.md').read_text()

        # Original badges should still exist
        assert '[![Build]' in readme_content
        assert '[![License]' in readme_content
        # New badge added
        assert '[![AICaC]' in readme_content

    def test_check_badge_accuracy_accurate(self, aicac_project):
        """Test badge accuracy check when badge is correct."""
        updater = BadgeUpdater(str(aicac_project))
        is_accurate, current = updater.check_badge_accuracy('Minimal')

        assert is_accurate is True
        assert current is not None
        assert 'Minimal' in current

    def test_check_badge_accuracy_inaccurate(self, readme_with_outdated_badge):
        """Test badge accuracy check when badge is outdated."""
        updater = BadgeUpdater(str(readme_with_outdated_badge))
        is_accurate, current = updater.check_badge_accuracy('Comprehensive')

        assert is_accurate is False
        assert current is not None
        assert 'Minimal' in current  # Old badge

    def test_check_badge_accuracy_no_badge(self, readme_without_badge):
        """Test badge accuracy check when no badge exists."""
        updater = BadgeUpdater(str(readme_without_badge))
        is_accurate, current = updater.check_badge_accuracy('Standard')

        assert is_accurate is False
        assert current is None

    def test_check_badge_accuracy_no_readme(self, temp_project_dir):
        """Test badge accuracy check when README doesn't exist."""
        updater = BadgeUpdater(str(temp_project_dir))
        is_accurate, current = updater.check_badge_accuracy('Standard')

        assert is_accurate is False
        assert current is None

    def test_badge_placement_after_heading(self, temp_project_dir):
        """Test badge is placed after first heading."""
        readme = """# My Project

Some description.
"""
        readme_path = temp_project_dir / 'README.md'
        readme_path.write_text(readme)

        updater = BadgeUpdater(str(temp_project_dir))
        updater.update_badge('Standard')

        content = readme_path.read_text()
        lines = content.split('\n')

        # Badge should be after heading
        heading_index = next(i for i, line in enumerate(lines) if line.startswith('#'))
        badge_index = next(i for i, line in enumerate(lines) if '[![AICaC]' in line)

        assert badge_index > heading_index

    def test_badge_placement_with_existing_badges(self, readme_without_badge):
        """Test badge is added to existing badge section."""
        updater = BadgeUpdater(str(readme_without_badge))
        updater.update_badge('Minimal')

        content = (readme_without_badge / 'README.md').read_text()
        lines = content.split('\n')

        # Find all badge lines
        badge_lines = [i for i, line in enumerate(lines) if '[![' in line]

        # Should have 3 badges now (Build, License, AICaC)
        assert len(badge_lines) >= 3

        # AICaC badge should be near other badges
        aicac_index = next(i for i, line in enumerate(lines) if '[![AICaC]' in line)
        assert any(abs(aicac_index - idx) <= 2 for idx in badge_lines[:-1])

    def test_update_badge_idempotency(self, readme_without_badge):
        """Test that updating badge multiple times with same level is safe."""
        updater = BadgeUpdater(str(readme_without_badge))

        # Update first time
        success1, msg1 = updater.update_badge('Standard')
        assert success1 is True
        assert 'Added' in msg1

        content1 = (readme_without_badge / 'README.md').read_text()

        # Update second time with same level
        success2, msg2 = updater.update_badge('Standard')
        assert success2 is True
        assert 'Updated' in msg2

        content2 = (readme_without_badge / 'README.md').read_text()

        # Should still have exactly one AICaC badge
        assert content2.count('[![AICaC]') == 1
        assert 'Standard' in content2

    def test_update_badge_different_levels(self, readme_without_badge):
        """Test updating badge through different compliance levels."""
        updater = BadgeUpdater(str(readme_without_badge))
        readme_path = readme_without_badge / 'README.md'

        # Start with Minimal
        updater.update_badge('Minimal')
        content = readme_path.read_text()
        assert 'Minimal' in content
        assert 'green' in content

        # Upgrade to Standard
        updater.update_badge('Standard')
        content = readme_path.read_text()
        assert 'Standard' in content
        assert 'brightgreen' in content
        assert 'Minimal' not in content

        # Upgrade to Comprehensive
        updater.update_badge('Comprehensive')
        content = readme_path.read_text()
        assert 'Comprehensive' in content
        assert 'success' in content
        assert 'Standard' not in content
