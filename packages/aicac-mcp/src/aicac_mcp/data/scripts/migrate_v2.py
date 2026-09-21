#!/usr/bin/env python3
"""
AICaC v1.x -> v2.0 migration helper.

Rewrites .ai/ files in place. Handles two distinct flavors of v1.x:

  Shape migrations (list -> dict):
    - architecture.yaml  components: [{name, ...}]  -> components: {name: {...}}
    - decisions.yaml     decisions: [{id, ...}]     -> decisions: {id: {...}}
    - errors.yaml        error_patterns: [{pattern, ...}] -> errors: {pattern: {...}}

  Field-level normalization (already-dict but not yet v2.0-conforming):
    - decisions[*]       lowercase keys -> uppercase to match ^[A-Z][A-Z0-9_-]+$
    - decisions[*].title derived from the key when missing
    - decisions[*].alternatives_considered  [{name: reason}] -> [{name, rejected_because}]
    - errors[*].symptom  derived from symptoms[] (joined) or from the id when missing
    - errors[*]          causes: [{cause, solution}] -> common_causes[] + solutions[]

  Generic:
    - context.yaml       common_commands -> common_tasks
    - all canonical files  version '1.x' -> '2.0' (and add 'version: "2.0"' when missing)

Always prints a diff-like summary. Use --dry-run to preview.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from pathlib import Path

import yaml


# v2.0 schema requires decision keys to match this pattern.
DECISION_KEY_RE = re.compile(r"^(ADR[-_][0-9]+|[A-Z][A-Z0-9_-]+)$")


def _slugify(text: str) -> str:
    """Build a stable id from a free-form name/pattern."""
    safe = "".join(c if c.isalnum() else "_" for c in text).strip("_").upper()
    return safe or "ITEM"


def _normalize_decision_key(key: str) -> tuple[str, bool]:
    """Coerce a decision key to match the v2.0 pattern. Returns (new_key, changed)."""
    if DECISION_KEY_RE.match(key):
        return key, False
    normalized = re.sub(r"[^A-Z0-9_-]", "_", key.upper())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    if not normalized or not normalized[0].isalpha():
        normalized = f"DECISION_{normalized}".strip("_") or "DECISION_001"
    return normalized, normalized != key


def _title_from_key(key: str) -> str:
    """USE_ESBUILD -> 'Use Esbuild'."""
    parts = [p for p in re.split(r"[_-]+", key) if p]
    return " ".join(p.capitalize() for p in parts) or key


def _reshape_alternatives(alts: object) -> tuple[object, bool]:
    """[{webpack: 'too slow'}] -> [{name: 'webpack', rejected_because: 'too slow'}]."""
    if not isinstance(alts, list):
        return alts, False
    new_list: list[object] = []
    changed = False
    for item in alts:
        if isinstance(item, dict) and "name" not in item and len(item) == 1:
            (k, v), = item.items()
            new_list.append({"name": str(k), "rejected_because": str(v)})
            changed = True
        else:
            new_list.append(item)
    return new_list, changed


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

    # v1.x list -> dict
    if isinstance(decisions, list):
        new = {}
        for item in decisions:
            if not isinstance(item, dict):
                continue
            adr_id = item.pop("id", None) or f"ADR-{len(new)+1:03d}"
            new[adr_id] = item
        data["decisions"] = new
        decisions = new
        changed.append(f"decisions: list -> dict[{len(new)}]")

    # Normalize dict-shaped data (whether converted above or already dict)
    if isinstance(decisions, dict):
        # Key normalization
        renamed: dict[str, object] = {}
        rename_count = 0
        for old_key, value in decisions.items():
            new_key, was_renamed = _normalize_decision_key(str(old_key))
            if was_renamed:
                rename_count += 1
            # In the rare case of a collision, suffix with -2, -3, ...
            base = new_key
            n = 2
            while new_key in renamed:
                new_key = f"{base}-{n}"
                n += 1
            renamed[new_key] = value
        if rename_count:
            data["decisions"] = renamed
            decisions = renamed
            changed.append(f"decisions: normalized {rename_count} key(s) to v2.0 pattern")

        # Per-decision field fix-ups
        for adr_id, adr in decisions.items():
            if not isinstance(adr, dict):
                continue
            if not adr.get("title"):
                adr["title"] = _title_from_key(adr_id)
                changed.append(f"decisions[{adr_id}]: added derived title")
            if "alternatives_considered" in adr:
                new_alts, alts_changed = _reshape_alternatives(adr["alternatives_considered"])
                if alts_changed:
                    adr["alternatives_considered"] = new_alts
                    changed.append(f"decisions[{adr_id}]: reshaped alternatives_considered")

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

    # Normalize dict-shaped errors (covers both just-converted and already-dict cases)
    errors = data.get("errors")
    if isinstance(errors, dict):
        for err_id, err in errors.items():
            if not isinstance(err, dict):
                continue

            # Derive symptom from symptoms[] or from id
            if not err.get("symptom"):
                symptoms = err.get("symptoms")
                if isinstance(symptoms, list) and symptoms:
                    err["symptom"] = "; ".join(str(s) for s in symptoms)
                    changed.append(f"errors[{err_id}]: symptom <- symptoms[]")
                else:
                    err["symptom"] = _title_from_key(str(err_id))
                    changed.append(f"errors[{err_id}]: symptom <- derived from id")

            # Flatten causes: [{cause, solution}] into common_causes + solutions
            causes = err.get("causes")
            if isinstance(causes, list) and "common_causes" not in err:
                cc: list[str] = []
                sols: list[object] = []
                for c in causes:
                    if isinstance(c, dict):
                        if c.get("cause"):
                            cc.append(str(c["cause"]))
                        sol = c.get("solution")
                        if sol is not None:
                            # Deep-copy dict solutions so the YAML dumper doesn't
                            # emit anchors when the same node is referenced from
                            # both causes[].solution and solutions[].
                            if isinstance(sol, dict):
                                sols.append(copy.deepcopy(sol))
                            elif isinstance(sol, str):
                                sols.append(sol)
                            else:
                                sols.append(str(sol))
                    elif isinstance(c, str):
                        cc.append(c)
                if cc:
                    err["common_causes"] = cc
                    changed.append(f"errors[{err_id}]: common_causes <- causes[].cause")
                if sols and "solutions" not in err:
                    err["solutions"] = sols
                    changed.append(f"errors[{err_id}]: solutions <- causes[].solution")

    return changed


def migrate_context(data: dict) -> list[str]:
    changed: list[str] = []
    if "common_commands" in data and "common_tasks" not in data:
        data["common_tasks"] = data.pop("common_commands")
        changed.append("common_commands -> common_tasks")
    return changed


def bump_version(data: dict) -> list[str]:
    v = data.get("version")
    if v is None:
        data["version"] = "2.0"
        return ["version (missing) -> '2.0'"]
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
