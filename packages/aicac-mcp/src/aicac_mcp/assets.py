"""
Asset resolution for AICaC MCP server.

Prefers package-local vendored assets, falls back to monorepo paths for dev.
"""

import os
from pathlib import Path
from typing import Optional


def _get_package_root() -> Path:
    """Get the aicac_mcp package root directory."""
    return Path(__file__).parent


def _get_monorepo_root() -> Optional[Path]:
    """Get monorepo root if available (for development)."""
    # Start from package and walk up looking for telltale files
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "spec" / "v2").is_dir() and (parent / ".github" / "actions" / "aicac-adoption").is_dir():
            return parent
    
    # Check AICAC_REPO_ROOT env override
    if "AICAC_REPO_ROOT" in os.environ:
        repo_root = Path(os.environ["AICAC_REPO_ROOT"])
        if repo_root.is_dir():
            return repo_root
    
    return None


def get_schemas_dir() -> Path:
    """Get schemas directory, preferring package-local."""
    # Try package-local first
    package_schemas = _get_package_root() / "data" / "schemas"
    if package_schemas.is_dir() and list(package_schemas.glob("*.json")):
        return package_schemas
    
    # Fall back to monorepo
    monorepo = _get_monorepo_root()
    if monorepo:
        monorepo_schemas = monorepo / "spec" / "v2"
        if monorepo_schemas.is_dir():
            return monorepo_schemas
    
    raise FileNotFoundError(
        "Schemas not found. Expected package-local at aicac_mcp/data/schemas/ "
        "or monorepo at spec/v2/. Set AICAC_REPO_ROOT to override."
    )


def get_skills_dir() -> Path:
    """Get skills directory, preferring package-local."""
    # Try package-local first
    package_skills = _get_package_root() / "data" / "skills"
    if package_skills.is_dir() and list(package_skills.glob("*.md")):
        return package_skills
    
    # Fall back to monorepo
    monorepo = _get_monorepo_root()
    if monorepo:
        monorepo_skills = monorepo / ".claude" / "skills" / "aicac"
        if monorepo_skills.is_dir():
            return monorepo_skills
    
    raise FileNotFoundError(
        "Skills not found. Expected package-local at aicac_mcp/data/skills/ "
        "or monorepo at .claude/skills/aicac/. Set AICAC_REPO_ROOT to override."
    )


def get_scripts_dir() -> Path:
    """Get scripts directory, preferring package-local."""
    # Try package-local first
    package_scripts = _get_package_root() / "data" / "scripts"
    if package_scripts.is_dir() and list(package_scripts.glob("*.py")):
        return package_scripts
    
    # Fall back to monorepo
    monorepo = _get_monorepo_root()
    if monorepo:
        monorepo_scripts = monorepo / ".github" / "actions" / "aicac-adoption" / "scripts"
        if monorepo_scripts.is_dir():
            return monorepo_scripts
    
    raise FileNotFoundError(
        "Scripts not found. Expected package-local at aicac_mcp/data/scripts/ "
        "or monorepo at .github/actions/aicac-adoption/scripts/. Set AICAC_REPO_ROOT to override."
    )
