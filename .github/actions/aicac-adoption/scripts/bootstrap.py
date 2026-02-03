#!/usr/bin/env python3
"""
AICaC Bootstrap Script

Generates initial .ai/ directory structure for projects adopting AICaC.
Can use AI to help populate content based on project analysis.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Optional


class AICaCBootstrap:
    """Bootstrap AICaC structure for a project."""

    def __init__(self, project_path: str = '.'):
        self.project_path = Path(project_path)
        self.ai_dir = self.project_path / '.ai'

    def analyze_project(self) -> Dict:
        """Analyze project to gather context for AI generation."""
        analysis = {
            'project_path': str(self.project_path),
            'has_package_json': (self.project_path / 'package.json').exists(),
            'has_requirements_txt': (self.project_path / 'requirements.txt').exists(),
            'has_cargo_toml': (self.project_path / 'Cargo.toml').exists(),
            'has_go_mod': (self.project_path / 'go.mod').exists(),
            'has_readme': (self.project_path / 'README.md').exists(),
            'has_makefile': (self.project_path / 'Makefile').exists(),
            'languages': [],
            'frameworks': [],
        }

        # Detect languages
        if analysis['has_package_json']:
            analysis['languages'].append('javascript')
            analysis['project_type'] = 'node-app'
        if analysis['has_requirements_txt']:
            analysis['languages'].append('python')
            analysis['project_type'] = 'python-app'
        if analysis['has_cargo_toml']:
            analysis['languages'].append('rust')
            analysis['project_type'] = 'rust-app'
        if analysis['has_go_mod']:
            analysis['languages'].append('go')
            analysis['project_type'] = 'go-app'

        # Try to read project name from various sources
        analysis['project_name'] = self._detect_project_name()

        return analysis

    def _detect_project_name(self) -> str:
        """Try to detect project name from various sources."""
        # Try package.json
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    return data.get('name', self.project_path.name)
            except:
                pass

        # Try Cargo.toml
        cargo_toml = self.project_path / 'Cargo.toml'
        if cargo_toml.exists():
            try:
                import tomli
                with open(cargo_toml, 'rb') as f:
                    data = tomli.load(f)
                    return data.get('package', {}).get('name', self.project_path.name)
            except:
                pass

        # Fallback to directory name
        return self.project_path.name

    def create_minimal_structure(self, analysis: Dict) -> Dict:
        """Create minimal .ai/ structure without AI assistance."""
        os.makedirs(self.ai_dir, exist_ok=True)

        files_created = []

        # Create context.yaml
        context = {
            'version': '1.0',
            'project': {
                'name': analysis['project_name'],
                'type': analysis.get('project_type', 'application'),
                'description': 'TODO: Add project description',
            },
            'entrypoints': {
                'main': 'TODO: Add main entrypoint',
            },
            'common_tasks': {
                'dev': 'TODO: Add development command',
                'test': 'TODO: Add test command',
                'build': 'TODO: Add build command',
            },
        }

        context_path = self.ai_dir / 'context.yaml'
        with open(context_path, 'w') as f:
            yaml.dump(context, f, default_flow_style=False, sort_keys=False)
        files_created.append('context.yaml')

        # Create README.md
        readme_content = f"""# .ai Directory

This directory contains AI-readable project documentation using the AICaC standard.

## Files

- `context.yaml` - Project metadata and overview (REQUIRED)
- `architecture.yaml` - Component relationships (optional)
- `workflows.yaml` - Common tasks and procedures (optional)
- `decisions.yaml` - Architectural decisions (optional)
- `errors.yaml` - Error patterns and solutions (optional)

## Next Steps

1. Review and complete TODO items in `context.yaml`
2. Add additional files as needed for your project
3. Reference this directory from your project's `AGENTS.md`
4. Add an AICaC badge to your README.md

See [AICaC specification](https://github.com/eFAILution/AICaC) for details.

## AI-Assisted Completion

To get help populating these files with AI:

### Using GitHub Copilot
Open files in your editor with Copilot enabled and use inline suggestions.

### Using Claude Code or Cursor
Ask your AI assistant to analyze your project and populate the .ai/ files:
```
Based on my project structure, help me complete the .ai/context.yaml file
and add relevant architecture.yaml and workflows.yaml files.
```

### Using Free AI (via API)
Run the bootstrap script with AI assistance:
```bash
python .github/actions/aicac-adoption/bootstrap.py --with-ai --api-key=YOUR_KEY
```
"""

        readme_path = self.ai_dir / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        files_created.append('README.md')

        return {
            'status': 'success',
            'files_created': files_created,
            'ai_dir': str(self.ai_dir),
        }

    def create_with_ai(self, analysis: Dict, ai_service: str = 'github-copilot') -> Dict:
        """Create structure with AI assistance (placeholder for future implementation)."""
        # TODO: Implement AI-assisted generation
        # This would call OpenAI API, Anthropic API, or use GitHub Copilot
        # to generate more complete content based on project analysis

        print("AI-assisted generation coming soon!")
        print("For now, using minimal structure with TODO markers.")
        print("\nYou can use your AI assistant to help complete the files:")
        print("1. Open .ai/context.yaml in your editor")
        print("2. Ask GitHub Copilot or your AI assistant to complete the TODOs")
        print("3. Have your AI analyze your project structure to suggest architecture")

        return self.create_minimal_structure(analysis)

    def generate_pr_body(self, result: Dict) -> str:
        """Generate PR description for AICaC adoption."""
        body = f"""## 🤖 Adopt AICaC (AI Context as Code)

This PR introduces the [AICaC standard](https://github.com/eFAILution/AICaC) to improve how AI coding assistants understand your project.

### What is AICaC?

AICaC introduces a `.ai/` directory with structured, machine-readable documentation that:
- Reduces AI token usage by 40-60%
- Provides direct queryability for AI assistants
- Maintains single source of truth alongside your code

### Files Created

"""
        for file in result['files_created']:
            body += f"- `.ai/{file}`\n"

        body += """
### Next Steps

1. **Review `.ai/context.yaml`** - Complete the TODO items with your project details
2. **Add optional files** (recommended):
   - `.ai/architecture.yaml` - Component structure and relationships
   - `.ai/workflows.yaml` - Common development tasks
   - `.ai/decisions.yaml` - Architectural decision records
   - `.ai/errors.yaml` - Common errors and solutions

3. **Use AI to help** - Ask GitHub Copilot, Claude Code, or Cursor to:
   ```
   Based on my project, help me populate the .ai/ directory files
   ```

4. **Add AICaC badge** to your README.md:
   ```markdown
   [![AICaC](https://img.shields.io/badge/AICaC-Minimal-green.svg)](https://github.com/eFAILution/AICaC)
   ```

5. **Reference from AGENTS.md** (if you have one):
   ```markdown
   For structured project context, see the `.ai/` directory.
   ```

### Resources

- [AICaC Specification](https://github.com/eFAILution/AICaC/blob/main/ai-context-as-code-whitepaper.md)
- [Badge Guide](https://github.com/eFAILution/AICaC/blob/main/BADGES.md)
- [Example Implementation](https://github.com/eFAILution/AICaC/tree/main/validation/examples/sample-project)

---
*This PR was automatically generated by the [AICaC Adoption Action](https://github.com/eFAILution/AICaC)*
"""
        return body


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Bootstrap AICaC structure')
    parser.add_argument('project_path', nargs='?', default='.',
                       help='Path to project (default: current directory)')
    parser.add_argument('--with-ai', action='store_true',
                       help='Use AI to help generate content')
    parser.add_argument('--ai-service', default='github-copilot',
                       choices=['github-copilot', 'openai', 'anthropic'],
                       help='AI service to use')
    parser.add_argument('--pr-body', action='store_true',
                       help='Generate PR body text')

    args = parser.parse_args()

    bootstrap = AICaCBootstrap(args.project_path)

    # Analyze project
    analysis = bootstrap.analyze_project()

    # Create structure
    if args.with_ai:
        result = bootstrap.create_with_ai(analysis, args.ai_service)
    else:
        result = bootstrap.create_minimal_structure(analysis)

    # Output
    if args.pr_body:
        print(bootstrap.generate_pr_body(result))
    else:
        print(f"✅ AICaC structure created at {result['ai_dir']}")
        print(f"📁 Files created: {', '.join(result['files_created'])}")
        print("\n📝 Next: Review and complete TODO items in .ai/context.yaml")


if __name__ == '__main__':
    main()
