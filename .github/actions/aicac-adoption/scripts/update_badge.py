#!/usr/bin/env python3
"""
Update AICaC Badge in README

Ensures README.md has the correct AICaC badge for current compliance level.
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional, Tuple


class BadgeUpdater:
    """Updates AICaC badge in README.md"""

    BADGE_PATTERN = r'\[\!\[AICaC\]\([^\)]+\)\]\([^\)]+\)'

    BADGE_TEMPLATES = {
        'Comprehensive': '[![AICaC](https://img.shields.io/badge/AICaC-Comprehensive-success.svg)](https://github.com/eFAILution/AICaC)',
        'Standard': '[![AICaC](https://img.shields.io/badge/AICaC-Standard-brightgreen.svg)](https://github.com/eFAILution/AICaC)',
        'Minimal': '[![AICaC](https://img.shields.io/badge/AICaC-Minimal-green.svg)](https://github.com/eFAILution/AICaC)',
        'None': '[![AICaC](https://img.shields.io/badge/AICaC-Not%20Adopted-red.svg)](https://github.com/eFAILution/AICaC)',
    }

    def __init__(self, project_path: str = '.'):
        self.project_path = Path(project_path)
        self.readme_path = self.project_path / 'README.md'

    def get_badge_for_level(self, compliance_level: str) -> str:
        """Get badge markdown for compliance level."""
        return self.BADGE_TEMPLATES.get(compliance_level, self.BADGE_TEMPLATES['None'])

    def has_badge(self, content: str) -> bool:
        """Check if README already has AICaC badge."""
        return bool(re.search(self.BADGE_PATTERN, content))

    def update_badge(self, compliance_level: str) -> Tuple[bool, str]:
        """Update badge in README.md."""
        if not self.readme_path.exists():
            return False, "README.md not found"

        with open(self.readme_path, 'r') as f:
            content = f.read()

        new_badge = self.get_badge_for_level(compliance_level)

        if self.has_badge(content):
            # Replace existing badge
            updated_content = re.sub(self.BADGE_PATTERN, new_badge, content)
            action = "Updated"
        else:
            # Add badge after first heading or at top
            lines = content.split('\n')
            insert_index = 0

            # Find first heading
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    insert_index = i + 1
                    break

            # Find existing badges (lines with [![)
            badge_end_index = insert_index
            for i in range(insert_index, len(lines)):
                if '[![' in lines[i] or (i > insert_index and lines[i].strip() == ''):
                    badge_end_index = i + 1
                else:
                    break

            # Insert new badge
            if badge_end_index > insert_index:
                # Add to existing badge section
                lines.insert(badge_end_index, new_badge)
            else:
                # Create new badge section after heading
                lines.insert(insert_index, '')
                lines.insert(insert_index + 1, new_badge)
                lines.insert(insert_index + 2, '')

            updated_content = '\n'.join(lines)
            action = "Added"

        # Write back
        with open(self.readme_path, 'w') as f:
            f.write(updated_content)

        return True, f"{action} badge for compliance level: {compliance_level}"

    def check_badge_accuracy(self, compliance_level: str) -> Tuple[bool, Optional[str]]:
        """Check if existing badge matches compliance level."""
        if not self.readme_path.exists():
            return False, None

        with open(self.readme_path, 'r') as f:
            content = f.read()

        if not self.has_badge(content):
            return False, None

        expected_badge = self.get_badge_for_level(compliance_level)
        current_badge_match = re.search(self.BADGE_PATTERN, content)

        if current_badge_match:
            current_badge = current_badge_match.group(0)
            return current_badge == expected_badge, current_badge

        return False, None


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Update AICaC badge in README')
    parser.add_argument('compliance_level',
                       choices=['None', 'Minimal', 'Standard', 'Comprehensive'],
                       help='Current compliance level')
    parser.add_argument('--project-path', default='.',
                       help='Path to project (default: current directory)')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check if badge is accurate, don\'t update')

    args = parser.parse_args()

    updater = BadgeUpdater(args.project_path)

    if args.check_only:
        is_accurate, current = updater.check_badge_accuracy(args.compliance_level)
        if is_accurate:
            print(f"✅ Badge is accurate for {args.compliance_level}")
            sys.exit(0)
        else:
            print(f"❌ Badge needs update to {args.compliance_level}")
            if current:
                print(f"   Current: {current}")
            sys.exit(1)
    else:
        success, message = updater.update_badge(args.compliance_level)
        if success:
            print(f"✅ {message}")
            sys.exit(0)
        else:
            print(f"❌ {message}")
            sys.exit(1)


if __name__ == '__main__':
    main()
