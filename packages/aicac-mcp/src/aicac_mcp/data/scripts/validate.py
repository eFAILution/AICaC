#!/usr/bin/env python3
"""
AICaC v2.0 Compliance Validator

Runs four passes against a project's .ai/ directory:

  1. File presence       — required files exist
  2. Schema validation   — each file matches spec/v2/*.schema.json
  3. Cross-references    — components/workflows/decisions refer to ids that exist
  4. Content quality     — files are not majority-TODO; minimum populated entries

Exits non-zero if any blocking check fails. Emits DEPRECATION warnings for v1.x
shapes (list form, common_commands) but does not fail on them.

Usage:
    python validate.py [path_to_project]
    python validate.py . --json          # machine-readable output
    python validate.py . --strict        # treat warnings as errors
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

try:
    from jsonschema import Draft202012Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR_V2 = REPO_ROOT / "spec" / "v2"

# File-specific schemas (v2.0)
SCHEMA_FILES = {
    "context.yaml": "context.schema.json",
    "architecture.yaml": "architecture.schema.json",
    "workflows.yaml": "workflows.schema.json",
    "decisions.yaml": "decisions.schema.json",
    "errors.yaml": "errors.schema.json",
}

# Required vs optional files
REQUIRED_FILES = {"context.yaml"}
OPTIONAL_FILES = {"architecture.yaml", "workflows.yaml", "decisions.yaml", "errors.yaml"}

BADGE_URLS = {
    "Comprehensive": "https://img.shields.io/badge/AICaC-Comprehensive-success.svg",
    "Standard": "https://img.shields.io/badge/AICaC-Standard-brightgreen.svg",
    "Minimal": "https://img.shields.io/badge/AICaC-Minimal-green.svg",
    "None": "https://img.shields.io/badge/AICaC-Not%20Adopted-red.svg",
}


class AICaCValidator:
    """Validates AICaC compliance against v2.0 schemas with cross-ref and quality checks."""

    # Backward compat: kept for existing tests
    REQUIRED_FILES = {
        "context.yaml": True,
        "architecture.yaml": False,
        "workflows.yaml": False,
        "decisions.yaml": False,
        "errors.yaml": False,
    }

    def __init__(self, project_path: str = ".", schema_dir: Path | None = None,
                 strict: bool = False):
        self.project_path = Path(project_path)
        self.ai_dir = self.project_path / ".ai"
        self.schema_dir = schema_dir or SCHEMA_DIR_V2
        self.strict = strict
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []
        self._parsed: dict[str, Any] = {}

    # ------------------------------------------------------------------ API

    def validate(self) -> dict:
        """Run full validation pipeline. Returns dict with compliance results."""
        if not self.ai_dir.exists():
            return {
                "valid": False,
                "compliance_level": "None",
                "found_files": {},
                "context_valid": False,
                "errors": [],
                "warnings": [],
                "info": [],
                "error": ".ai/ directory not found",
                "recommendation": "Run: python .github/actions/aicac-adoption/scripts/bootstrap.py .",
                "badge": BADGE_URLS["None"],
                "badge_markdown": self._badge_markdown("None"),
            }

        found_files = self._check_files()
        self._parse_files(found_files)
        self._run_schema_validation(found_files)
        self._run_xref_validation(found_files)
        self._run_quality_heuristics(found_files)

        context_valid = self._validate_context()
        if context_valid:
            self._info(f"context.yaml declares version {self._parsed.get('context.yaml', {}).get('version')!r}")

        blocking_errors = list(self.errors)
        if self.strict:
            blocking_errors.extend(self.warnings)

        compliance_level = self._determine_compliance(found_files, context_valid, blocking_errors)

        return {
            "valid": compliance_level != "None",
            "compliance_level": compliance_level,
            "found_files": found_files,
            "context_valid": context_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "error": None if compliance_level != "None" else "AICaC validation failed",
            "recommendation": None if compliance_level != "None" else "Fix the errors above; see spec/README.md",
            "badge": BADGE_URLS.get(compliance_level, BADGE_URLS["None"]),
            "badge_markdown": self._badge_markdown(compliance_level),
        }

    # ------------------------------------------------------------- presence

    def _check_files(self) -> dict[str, bool]:
        found: dict[str, bool] = {}
        for filename in list(self.REQUIRED_FILES.keys()):
            path = self.ai_dir / filename
            found[filename] = path.exists()
            if self.REQUIRED_FILES[filename] and not path.exists():
                self._error(f"Required file missing: .ai/{filename}")
        return found

    # ----------------------------------------------------------------- parse

    def _parse_files(self, found: dict[str, bool]) -> None:
        for filename, exists in found.items():
            if not exists:
                continue
            path = self.ai_dir / filename
            try:
                with open(path) as fh:
                    self._parsed[filename] = yaml.safe_load(fh) or {}
            except yaml.YAMLError as exc:
                self._error(f".ai/{filename}: invalid YAML - {exc}")
                self._parsed[filename] = None
            except Exception as exc:
                self._error(f".ai/{filename}: error reading - {exc}")
                self._parsed[filename] = None

    # ---------------------------------------------------------------- schema

    def _run_schema_validation(self, found: dict[str, bool]) -> None:
        if not HAS_JSONSCHEMA:
            self._warn("jsonschema not installed; schema validation skipped. pip install jsonschema")
            return

        for filename, exists in found.items():
            if not exists or self._parsed.get(filename) is None:
                continue
            schema_file = self.schema_dir / SCHEMA_FILES[filename]
            if not schema_file.exists():
                self._warn(f"Schema missing: {schema_file} — skipping {filename}")
                continue
            try:
                with open(schema_file) as fh:
                    schema = json.load(fh)
            except Exception as exc:
                self._warn(f"Could not load {schema_file.name}: {exc}")
                continue

            validator = Draft202012Validator(schema)
            errs = sorted(validator.iter_errors(self._parsed[filename]),
                          key=lambda e: list(e.absolute_path))
            for err in errs:
                loc = ".".join(str(p) for p in err.absolute_path) or "<root>"
                self._error(f".ai/{filename}: schema[{loc}] {err.message}")

            # version check
            version = self._parsed[filename].get("version", "")
            if isinstance(version, str) and version.startswith("1."):
                self._warn(f".ai/{filename}: declares v{version}; v2.0 is current canonical")

    # ------------------------------------------------------------------ xref

    def _run_xref_validation(self, found: dict[str, bool]) -> None:
        arch = self._parsed.get("architecture.yaml", {}) or {}
        components_field = arch.get("components")
        component_ids: set[str] = set()

        if isinstance(components_field, dict):
            component_ids = set(components_field.keys())
        elif isinstance(components_field, list):
            for item in components_field:
                if isinstance(item, dict) and "name" in item:
                    component_ids.add(item["name"])
            if components_field:
                self._warn("architecture.yaml: components uses deprecated list form; migrate to dict keyed by id (see spec/README.md)")

        # workflows -> components
        workflows = (self._parsed.get("workflows.yaml", {}) or {}).get("workflows")
        if isinstance(workflows, dict):
            for wf_id, wf in workflows.items():
                if not isinstance(wf, dict):
                    continue
                touches = wf.get("touches_components") or []
                for c in touches:
                    if component_ids and c not in component_ids:
                        self._error(
                            f"workflows.yaml[{wf_id}].touches_components references unknown component '{c}'"
                        )

        # decisions -> components
        decisions = (self._parsed.get("decisions.yaml", {}) or {}).get("decisions")
        if isinstance(decisions, dict):
            for adr_id, adr in decisions.items():
                if not isinstance(adr, dict):
                    continue
                affects = adr.get("affects_components") or []
                for c in affects:
                    if component_ids and c not in component_ids:
                        self._error(
                            f"decisions.yaml[{adr_id}].affects_components references unknown component '{c}'"
                        )
                superseded_by = adr.get("superseded_by")
                if superseded_by and superseded_by not in decisions:
                    self._error(
                        f"decisions.yaml[{adr_id}].superseded_by references unknown ADR '{superseded_by}'"
                    )

        # components.depends_on
        if isinstance(components_field, dict):
            for cid, cdef in components_field.items():
                if not isinstance(cdef, dict):
                    continue
                for dep in cdef.get("depends_on") or []:
                    if dep not in components_field:
                        self._error(
                            f"architecture.yaml[{cid}].depends_on references unknown component '{dep}'"
                        )

    # --------------------------------------------------------------- quality

    def _run_quality_heuristics(self, found: dict[str, bool]) -> None:
        context = self._parsed.get("context.yaml", {}) or {}

        # common_commands deprecation
        if "common_commands" in context and "common_tasks" not in context:
            self._warn(
                "context.yaml: 'common_commands' is deprecated in v2.0 — rename to 'common_tasks'"
            )

        # TODO-only detection per file
        for filename in OPTIONAL_FILES:
            if not found.get(filename):
                continue
            path = self.ai_dir / filename
            try:
                text = path.read_text()
            except Exception:
                continue
            non_comment = [l for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]
            todo_lines = [l for l in non_comment if "TODO" in l.upper()]
            if non_comment and len(todo_lines) / max(len(non_comment), 1) > 0.5:
                self._warn(
                    f".ai/{filename}: majority of lines are TODO placeholders — file does not count toward compliance"
                )
                # strip it from found_files so it doesn't count
                found[filename] = False

        # workflows must have at least 2 populated workflows for Standard+
        workflows = (self._parsed.get("workflows.yaml", {}) or {}).get("workflows")
        if isinstance(workflows, dict) and len(workflows) < 2:
            self._warn("workflows.yaml: fewer than 2 workflows defined — consider expanding")

    # --------------------------------------------------------------- context

    def _validate_context(self) -> bool:
        # Support being called directly (without prior .validate()) — auto-parse.
        if "context.yaml" not in self._parsed:
            path = self.ai_dir / "context.yaml"
            if not path.exists():
                return False
            try:
                with open(path) as fh:
                    self._parsed["context.yaml"] = yaml.safe_load(fh) or {}
            except yaml.YAMLError as exc:
                self._error(f"context.yaml: Invalid YAML syntax - {exc}")
                return False
            except Exception as exc:
                self._error(f"context.yaml: Error reading file - {exc}")
                return False

        ctx = self._parsed.get("context.yaml")
        if not ctx:
            return False

        ok = True
        if not ctx.get("version"):
            self._error("context.yaml: 'version' is required")
            ok = False

        project = ctx.get("project") or {}
        if not project.get("name"):
            self._error("context.yaml: 'project.name' is required")
            ok = False
        if not project.get("type"):
            self._error("context.yaml: 'project.type' is required")
            ok = False

        if not ctx.get("entrypoints"):
            self._error("context.yaml: at least one 'entrypoint' is required")
            ok = False

        common = ctx.get("common_tasks") or ctx.get("common_commands") or {}
        if not common:
            self._error("context.yaml: at least one 'common_task' is required")
            ok = False

        return ok

    # ------------------------------------------------------------ compliance

    def _determine_compliance(self, found_files: dict[str, bool], context_valid: bool,
                              blocking_errors: list[str] | None = None) -> str:
        if blocking_errors:
            return "None"
        if not found_files.get("context.yaml") or not context_valid:
            return "None"

        optional_count = sum(1 for f in OPTIONAL_FILES if found_files.get(f))
        if optional_count >= 4:
            return "Comprehensive"
        if optional_count >= 2:
            return "Standard"
        return "Minimal"

    # ---------------------------------------------------------------- output

    def _badge_markdown(self, level: str) -> str:
        return f"[![AICaC]({BADGE_URLS.get(level, BADGE_URLS['None'])})](https://github.com/eFAILution/AICaC)"

    # Backward-compat helpers kept for existing tests
    def _get_badge_recommendation(self, level: str) -> str:
        return BADGE_URLS.get(level, BADGE_URLS["None"])

    def _get_badge_markdown(self, level: str) -> str:
        return self._badge_markdown(level)

    def _error(self, msg: str) -> None:
        self.errors.append(msg)

    def _warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def _info(self, msg: str) -> None:
        self.info.append(msg)

    def print_report(self, results: dict) -> None:
        bar = "=" * 60
        print(bar)
        print("AICaC Compliance Validation Report")
        print(bar)
        print()

        if not results["valid"]:
            print("❌ AICaC NOT ADOPTED")
            if results.get("error"):
                print(f"   {results['error']}")
            if results.get("errors"):
                print("\nErrors:")
                for e in results["errors"]:
                    print(f"  • {e}")
            if results.get("warnings"):
                print("\nWarnings:")
                for w in results["warnings"]:
                    print(f"  ⚠ {w}")
            if results.get("recommendation"):
                print(f"\nRecommendation: {results['recommendation']}")
            return

        print(f"Compliance Level: {results['compliance_level']}")
        print()

        print("Files Found:")
        for filename, present in results["found_files"].items():
            status = "✓" if present else "✗"
            print(f"  {status} .ai/{filename}")
        print()

        if results["errors"]:
            print("Errors:")
            for e in results["errors"]:
                print(f"  ✗ {e}")
            print()

        if results["warnings"]:
            print("Warnings (non-blocking unless --strict):")
            for w in results["warnings"]:
                print(f"  ⚠ {w}")
            print()

        print("Recommended Badge:")
        print(f"  {results['badge_markdown']}")
        print()

        if results["compliance_level"] != "Comprehensive":
            missing = [f for f in OPTIONAL_FILES if not results["found_files"].get(f)]
            if missing:
                print("Suggestions to improve compliance:")
                for f in missing:
                    print(f"  • Add .ai/{f}")
                print()

        print(bar)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AICaC v2.0 compliance")
    parser.add_argument("project_path", nargs="?", default=".")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only")
    args = parser.parse_args()

    validator = AICaCValidator(args.project_path, strict=args.strict)
    results = validator.validate()

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        validator.print_report(results)

    return 0 if results["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
