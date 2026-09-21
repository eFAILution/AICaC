"""
Wrapper functions for AICaC validation, bootstrap, and migration scripts.

These functions provide a library interface to the scripts in
.github/actions/aicac-adoption/scripts/ for use by the MCP server.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any

from . import assets


def _load_module(script_name: str):
    """Dynamically load a script module from package or monorepo."""
    try:
        scripts_dir = assets.get_scripts_dir()
    except FileNotFoundError as e:
        raise ImportError(f"Cannot load {script_name}: {e}") from e
    
    script_path = scripts_dir / f"{script_name}.py"
    if not script_path.exists():
        raise ImportError(f"Script not found: {script_path}")
    
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {script_name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[script_name] = module
    spec.loader.exec_module(module)
    return module


# Load modules lazily to provide better error messages
_validate_module = None
_bootstrap_module = None
_generate_index_module = None
_migrate_v2_module = None


def _get_validate_module():
    global _validate_module
    if _validate_module is None:
        _validate_module = _load_module("validate")
    return _validate_module


def _get_bootstrap_module():
    global _bootstrap_module
    if _bootstrap_module is None:
        _bootstrap_module = _load_module("bootstrap")
    return _bootstrap_module


def _get_generate_index_module():
    global _generate_index_module
    if _generate_index_module is None:
        _generate_index_module = _load_module("generate_index")
    return _generate_index_module


def _get_migrate_v2_module():
    global _migrate_v2_module
    if _migrate_v2_module is None:
        _migrate_v2_module = _load_module("migrate_v2")
    return _migrate_v2_module


def validate_project(project_path: str = ".", strict: bool = False) -> dict[str, Any]:
    """
    Validate a project's .ai/ directory against v2.0 schemas.
    
    Returns dict with:
        - valid: bool
        - compliance_level: str (None, Minimal, Standard, Comprehensive)
        - errors: list[str]
        - warnings: list[str]
        - found_files: dict[str, bool]
    """
    try:
        validate_module = _get_validate_module()
        # Override schema dir to use package assets
        schema_dir = assets.get_schemas_dir()
        validator = validate_module.AICaCValidator(project_path, schema_dir=schema_dir, strict=strict)
        return validator.validate()
    except (ImportError, FileNotFoundError) as e:
        return {
            "valid": False,
            "compliance_level": "None",
            "errors": [f"Validation unavailable: {e}"],
            "warnings": [],
            "found_files": {},
        }


def bootstrap_project(
    project_path: str = ".",
    compliance_level: str = "minimal",
    apply: bool = False
) -> dict[str, Any]:
    """
    Bootstrap a fresh .ai/ directory structure.
    
    Args:
        project_path: Path to project root
        compliance_level: "minimal", "standard", or "comprehensive"
        apply: If False, dry-run only (returns what would be created)
    
    Returns dict with:
        - files_created: list[str]
        - files_skipped: list[str]
        - detected_type: str
        - next_steps: list[str]
    """
    try:
        bootstrap_module = _get_bootstrap_module()
        bootstrap = bootstrap_module.AICaCBootstrap(project_path)
        analysis = bootstrap.analyze_project()
        
        if not apply:
            return {
                "status": "dry_run",
                "files_created": ["context.yaml", "README.md"],
                "files_skipped": [],
                "detected_type": analysis.get("project_type", "unknown"),
                "next_steps": [
                    "Review and complete TODO items in .ai/context.yaml",
                    "Add optional files (architecture.yaml, workflows.yaml, etc.)",
                    "Run aicac_validate to check compliance",
                ],
            }
        
        result = bootstrap.create_minimal_structure(analysis)
        return {
            "status": result["status"],
            "files_created": result["files_created"],
            "files_skipped": [],
            "detected_type": analysis.get("project_type", "unknown"),
            "next_steps": [
                "Review and complete TODO items in .ai/context.yaml",
                "Add optional files (architecture.yaml, workflows.yaml, etc.)",
                "Run aicac_validate to check compliance",
            ],
        }
    except (ImportError, FileNotFoundError) as e:
        return {
            "status": "error",
            "files_created": [],
            "files_skipped": [],
            "detected_type": "unknown",
            "next_steps": [],
            "error": f"Bootstrap unavailable: {e}",
        }


def generate_index(project_path: str = ".", apply: bool = False) -> dict[str, Any]:
    """
    Generate or regenerate .ai/index.yaml.
    
    Args:
        project_path: Path to project root
        apply: If False, dry-run only
    
    Returns dict with:
        - ids_by_file: dict mapping file to list of ids
        - changed: bool
    """
    try:
        generate_index_module = _get_generate_index_module()
        _build_index = generate_index_module.build_index
        
        ai_dir = Path(project_path) / ".ai"
        if not ai_dir.exists():
            return {
                "error": "No .ai/ directory found",
                "ids_by_file": {},
                "changed": False,
            }
        
        idx = _build_index(ai_dir)
        ids_by_file = idx.get("keys", {})
        
        import yaml
        new_content = yaml.safe_dump(idx, default_flow_style=False, sort_keys=False)
        new_content = "# AUTO-GENERATED by generate_index.py. Do not hand-edit.\n" + new_content
        
        index_path = ai_dir / "index.yaml"
        existing = index_path.read_text() if index_path.exists() else ""
        changed = existing.strip() != new_content.strip()
        
        if apply and changed:
            index_path.write_text(new_content)
        
        return {
            "ids_by_file": ids_by_file,
            "changed": changed,
        }
    except (ImportError, FileNotFoundError) as e:
        return {
            "error": f"Index generation unavailable: {e}",
            "ids_by_file": {},
            "changed": False,
        }


def migrate_project(project_path: str = ".", apply: bool = False) -> dict[str, Any]:
    """
    Migrate .ai/ from v1.x to v2.0.
    
    Args:
        project_path: Path to project root
        apply: If False, dry-run only (shows what would change)
    
    Returns dict with:
        - changes: list of dicts with {file, operations}
        - diff: str (human-readable summary)
    """
    try:
        migrate_v2_module = _get_migrate_v2_module()
        migrate_file = migrate_v2_module.migrate_file
        MIGRATORS = migrate_v2_module.MIGRATORS
        
        ai_dir = Path(project_path) / ".ai"
        if not ai_dir.exists():
            return {
                "error": "No .ai/ directory found",
                "changes": [],
                "diff": "",
            }
        
        changes = []
        diff_lines = []
        
        for filename in MIGRATORS:
            path = ai_dir / filename
            file_changes = migrate_file(path, dry_run=not apply)
            if file_changes:
                changes.append({
                    "file": filename,
                    "operations": file_changes,
                })
                diff_lines.append(f".ai/{filename}:")
                for change in file_changes:
                    diff_lines.append(f"  • {change}")
        
        if not changes:
            diff_lines.append("Already v2.0-compliant (or .ai/ is empty).")
        elif not apply:
            diff_lines.append("\nDry-run complete. Set apply=true to write changes.")
        else:
            diff_lines.append(f"\nMigrated {len(changes)} file(s) to v2.0.")
        
        return {
            "changes": changes,
            "diff": "\n".join(diff_lines),
        }
    except (ImportError, FileNotFoundError) as e:
        return {
            "error": f"Migration unavailable: {e}",
            "changes": [],
            "diff": "",
        }


def sync_suggest(
    project_path: str = ".",
    changed_files: list[str] | None = None
) -> dict[str, Any]:
    """
    Suggest which .ai/ files might need updating after code changes.
    
    This is intentionally a simple stub that returns candidates without
    scoring or ranking. The AI model makes the final decision.
    
    Args:
        project_path: Path to project root
        changed_files: List of changed source files (if None, uses git diff HEAD)
    
    Returns dict with:
        - changed_files: list[str]
        - candidate_ai_files: list[str] (all .ai/*.yaml files)
        - prompt: str (guidance for the model)
    """
    import subprocess
    
    if changed_files is None:
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True,
            )
            changed_files = [f for f in result.stdout.strip().split("\n") if f]
        except subprocess.CalledProcessError:
            changed_files = []
    
    ai_dir = Path(project_path) / ".ai"
    candidate_files = []
    if ai_dir.exists():
        candidate_files = sorted(
            f.name for f in ai_dir.glob("*.yaml")
            if f.name != "index.yaml"
        )
    
    prompt = """Given the changed files below, determine which .ai/ files need updates:

Changed files:
{changed_files}

Available .ai/ files:
{candidates}

Guidance:
- context.yaml: project metadata, entrypoints, common tasks
- architecture.yaml: components, dependencies, data flow
- workflows.yaml: development procedures, how-to steps
- decisions.yaml: architectural decision records (ADRs)
- errors.yaml: common error patterns and solutions

Update only the files that are directly affected by the changes.
Do not update files based on speculation.
""".format(
        changed_files="\n".join(f"  - {f}" for f in changed_files) or "  (none)",
        candidates="\n".join(f"  - {f}" for f in candidate_files) or "  (none)",
    )
    
    return {
        "changed_files": changed_files,
        "candidate_ai_files": candidate_files,
        "prompt": prompt,
    }
