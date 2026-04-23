#!/usr/bin/env python3
"""
AICaC v1.x -> v2.0 migration helper.

Rewrites .ai/ files in place:
  - architecture.yaml  components: [{name, ...}]  -> components: {name: {...}}
  - decisions.yaml     decisions: [{id, ...}]     -> decisions: {id: {...}}
  - errors.yaml        error_patterns: [{pattern, ...}] -> errors: {pattern: {...}}
  - context.yaml       common_commands             -> common_tasks
  - all files          version '1.x'               -> '2.0' (when present)

Always prints a diff-like summary. Use --dry-run to preview.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


def _slugify(text: str) -> str:
    """Build a stable id from a free-form name/pattern."""
    safe = "".join(c if c.isalnum() else "_" for c in text).strip("_").upper()
    return safe or "ITEM"


def migrate_architecture(data: dict) -> list[str]:
    changed: list[str] = []
    components = data.get("components")
    if isinstance(components, list):
        new = {}
        for item in components:
            if not isinstance(item, dict) or "name" not in item:
                continue
            name = item.pop("name")
            new[name] = item
        data["components"] = new
        changed.append(f"components: list -> dict[{len(new)}]")
    return changed


def migrate_decisions(data: dict) -> list[str]:
    changed: list[str] = []
    decisions = data.get("decisions")
    if isinstance(decisions, list):
        new = {}
        for item in decisions:
            if not isinstance(item, dict):
                continue
            adr_id = item.pop("id", None) or f"ADR-{len(new)+1:03d}"
            new[adr_id] = item
        data["decisions"] = new
        changed.append(f"decisions: list -> dict[{len(new)}]")
    return changed


def migrate_errors(data: dict) -> list[str]:
    changed: list[str] = []
    if isinstance(data.get("error_patterns"), list):
        new = {}
        for item in data["error_patterns"]:
            if not isinstance(item, dict):
                continue
            pattern = item.pop("pattern", None) or f"ERROR_{len(new)+1:03d}"
            eid = _slugify(pattern)
            item.setdefault("symptom", pattern)
            new[eid] = item
        data["errors"] = {**new, **(data.get("errors") or {})}
        del data["error_patterns"]
        changed.append(f"error_patterns -> errors dict[{len(new)}]")
    elif isinstance(data.get("errors"), list):
        new = {}
        for item in data["errors"]:
            if not isinstance(item, dict):
                continue
            pattern = item.pop("pattern", None) or f"ERROR_{len(new)+1:03d}"
            eid = _slugify(pattern)
            item.setdefault("symptom", pattern)
            new[eid] = item
        data["errors"] = new
        changed.append(f"errors: list -> dict[{len(new)}]")
    return changed


def migrate_context(data: dict) -> list[str]:
    changed: list[str] = []
    if "common_commands" in data and "common_tasks" not in data:
        data["common_tasks"] = data.pop("common_commands")
        changed.append("common_commands -> common_tasks")
    return changed


def bump_version(data: dict) -> list[str]:
    v = data.get("version")
    if isinstance(v, str) and v.startswith("1."):
        data["version"] = "2.0"
        return [f"version {v!r} -> '2.0'"]
    return []


MIGRATORS = {
    "context.yaml": [migrate_context, bump_version],
    "architecture.yaml": [migrate_architecture, bump_version],
    "decisions.yaml": [migrate_decisions, bump_version],
    "errors.yaml": [migrate_errors, bump_version],
    "workflows.yaml": [bump_version],
}


def migrate_file(path: Path, dry_run: bool = False) -> list[str]:
    if not path.exists():
        return []
    with open(path) as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        return []
    changes: list[str] = []
    for migrator in MIGRATORS.get(path.name, []):
        changes.extend(migrator(data))
    if changes and not dry_run:
        with open(path, "w") as fh:
            yaml.safe_dump(data, fh, default_flow_style=False, sort_keys=False)
    return changes


def _count_pending_changes(ai_dir: Path) -> int:
    """Count files that would be rewritten. Non-destructive."""
    total = 0
    for filename in MIGRATORS:
        if migrate_file(ai_dir / filename, dry_run=True):
            total += 1
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate .ai/ from v1.x to v2.0")
    parser.add_argument("project_path", nargs="?", default=".")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 0 if .ai/ is already v2.0, 1 if migration needed. Non-destructive.",
    )
    args = parser.parse_args()

    ai_dir = Path(args.project_path) / ".ai"
    if not ai_dir.exists():
        print(f"No .ai/ directory at {ai_dir}", file=sys.stderr)
        return 1

    if args.check:
        pending = _count_pending_changes(ai_dir)
        if pending == 0:
            print("Already v2.0-compliant.")
            return 0
        print(f"v1.x shape detected in {pending} file(s). Migration needed.")
        return 1

    total = 0
    for filename in MIGRATORS:
        path = ai_dir / filename
        changes = migrate_file(path, args.dry_run)
        if changes:
            prefix = "(dry-run) " if args.dry_run else ""
            print(f"{prefix}.ai/{filename}:")
            for c in changes:
                print(f"  • {c}")
            total += 1

    if total == 0:
        print("Already v2.0-compliant (or .ai/ is empty).")
    elif args.dry_run:
        print(f"\nWould migrate {total} file(s). Re-run without --dry-run to apply.")
    else:
        print(f"\nMigrated {total} file(s) to v2.0. Run validate.py to confirm.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
