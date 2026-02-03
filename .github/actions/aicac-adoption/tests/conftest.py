"""
Pytest configuration and fixtures for AICaC adoption tests.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def node_project(temp_project_dir):
    """Create a minimal Node.js project structure."""
    # Create package.json
    package_json = {
        "name": "test-node-project",
        "version": "1.0.0",
        "description": "Test project",
        "main": "index.js",
        "scripts": {
            "dev": "node index.js",
            "test": "jest",
            "build": "webpack"
        }
    }
    with open(temp_project_dir / "package.json", "w") as f:
        json.dump(package_json, f, indent=2)

    # Create README.md
    readme = """# Test Node Project

A test project for AICaC testing.

## Installation

npm install
"""
    with open(temp_project_dir / "README.md", "w") as f:
        f.write(readme)

    # Create src directory
    src_dir = temp_project_dir / "src"
    src_dir.mkdir()
    (src_dir / "index.js").write_text("console.log('Hello');")

    return temp_project_dir


@pytest.fixture
def python_project(temp_project_dir):
    """Create a minimal Python project structure."""
    # Create requirements.txt
    requirements = """flask==2.3.0
pytest==7.4.0
black==23.7.0
"""
    with open(temp_project_dir / "requirements.txt", "w") as f:
        f.write(requirements)

    # Create README.md
    readme = """# Test Python Project

A test project for AICaC testing.

## Installation

pip install -r requirements.txt
"""
    with open(temp_project_dir / "README.md", "w") as f:
        f.write(readme)

    # Create src directory
    src_dir = temp_project_dir / "src"
    src_dir.mkdir()
    (src_dir / "app.py").write_text("print('Hello')")

    return temp_project_dir


@pytest.fixture
def aicac_project(temp_project_dir):
    """Create a project with existing .ai/ directory."""
    ai_dir = temp_project_dir / ".ai"
    ai_dir.mkdir()

    # Create minimal context.yaml
    context = """version: "1.0"
project:
  name: test-project
  type: web-app
  description: Test project with AICaC

entrypoints:
  main: src/index.js

common_tasks:
  dev: npm run dev
  test: npm test
  build: npm run build
"""
    with open(ai_dir / "context.yaml", "w") as f:
        f.write(context)

    # Create README with badge
    readme = """# Test Project

[![Build](https://img.shields.io/badge/build-passing-green.svg)](https://example.com)
[![AICaC](https://img.shields.io/badge/AICaC-Minimal-green.svg)](https://github.com/eFAILution/AICaC)

Test project.
"""
    with open(temp_project_dir / "README.md", "w") as f:
        f.write(readme)

    return temp_project_dir


@pytest.fixture
def comprehensive_aicac_project(aicac_project):
    """Create a project with comprehensive AICaC adoption."""
    ai_dir = aicac_project / ".ai"

    # Add architecture.yaml
    architecture = """components:
  frontend:
    path: src/frontend
    type: react-app
  backend:
    path: src/backend
    type: api-server
"""
    with open(ai_dir / "architecture.yaml", "w") as f:
        f.write(architecture)

    # Add workflows.yaml
    workflows = """workflows:
  add_feature:
    steps:
      - action: create_component
        location: src/components/
      - action: add_tests
        location: tests/
"""
    with open(ai_dir / "workflows.yaml", "w") as f:
        f.write(workflows)

    # Add decisions.yaml
    decisions = """decisions:
  - id: "001"
    title: Use React
    status: accepted
    date: "2024-01-01"
"""
    with open(ai_dir / "decisions.yaml", "w") as f:
        f.write(decisions)

    # Add errors.yaml
    errors = """errors:
  - pattern: "Module not found"
    solution: "Run npm install"
"""
    with open(ai_dir / "errors.yaml", "w") as f:
        f.write(errors)

    return aicac_project


@pytest.fixture
def readme_without_badge(temp_project_dir):
    """Create a README without AICaC badge."""
    readme = """# Test Project

[![Build](https://img.shields.io/badge/build-passing-green.svg)](https://example.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Description

This is a test project.

## Installation

npm install
"""
    with open(temp_project_dir / "README.md", "w") as f:
        f.write(readme)

    return temp_project_dir


@pytest.fixture
def readme_with_outdated_badge(temp_project_dir):
    """Create a README with outdated AICaC badge."""
    readme = """# Test Project

[![Build](https://img.shields.io/badge/build-passing-green.svg)](https://example.com)
[![AICaC](https://img.shields.io/badge/AICaC-Minimal-green.svg)](https://github.com/eFAILution/AICaC)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Description

This is a test project.
"""
    with open(temp_project_dir / "README.md", "w") as f:
        f.write(readme)

    return temp_project_dir
