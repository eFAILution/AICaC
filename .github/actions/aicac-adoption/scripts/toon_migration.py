#!/usr/bin/env python3
"""
AICaC TOON Migration Manager

Manages the TOON migration lifecycle for projects using the AICaC action:
  1. Detects if a project has .ai/ YAML files but no .toon files
  2. Computes per-file token savings to populate the migration issue
  3. Generates issue body with opt-in checkbox
  4. Parses existing issue body to detect checkbox state
  5. Generates PR body when migration is approved

The actual GitHub API calls (issue creation, PR creation) are handled
by the action.yml shell steps using `gh` CLI. This script provides
the content and decision logic.

Usage:
  python toon_migration.py <project_path> --needs-migration
  python toon_migration.py <project_path> --issue-body
  python toon_migration.py <project_path> --check-approval <issue_body_text>
  python toon_migration.py <project_path> --pr-body <issue_number>
"""

import re
import sys
from pathlib import Path
from typing import Optional

import yaml


MIGRATION_LABEL = "aicac-toon-migration"

APPROVAL_CHECKBOX = "- [x] Migrate my `.ai/` directory to include TOON files"
PENDING_CHECKBOX = "- [ ] Migrate my `.ai/` directory to include TOON files"

REBASE_CHECKBOX = "- [x] Rebase/regenerate this PR"
REBASE_PENDING_CHECKBOX = "- [ ] Rebase/regenerate this PR"


def needs_migration(project_path: Path) -> bool:
    """Check if project has .ai/ YAML files but no .toon files."""
    ai_dir = project_path / ".ai"
    if not ai_dir.exists():
        return False

    yaml_files = list(ai_dir.glob("*.yaml"))
    toon_files = list(ai_dir.glob("*.toon"))

    return len(yaml_files) > 0 and len(toon_files) == 0


def compute_savings(project_path: Path) -> list[dict]:
    """Compute per-file character savings for the migration issue.

    Uses character counts (not tokens) to avoid requiring tiktoken.
    Character counts are a reasonable proxy and keep dependencies minimal.
    """
    ai_dir = project_path / ".ai"
    if not ai_dir.exists():
        return []

    try:
        from toon_format import encode as toon_encode
    except ImportError:
        return []

    results = []
    for yaml_path in sorted(ai_dir.glob("*.yaml")):
        try:
            yaml_text = yaml_path.read_text()
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
            if data is None:
                continue
            toon_text = toon_encode(data)

            yaml_chars = len(yaml_text)
            toon_chars = len(toon_text)
            reduction = (1 - toon_chars / yaml_chars) * 100 if yaml_chars > 0 else 0.0

            results.append({
                "file": yaml_path.name,
                "yaml_chars": yaml_chars,
                "toon_chars": toon_chars,
                "reduction_pct": round(reduction, 1),
            })
        except Exception:
            continue

    return results


def _format_savings_table(savings: list[dict]) -> str:
    """Format savings data as a markdown table."""
    if not savings:
        return "_Could not compute savings (toon_format not available)._"

    lines = [
        "| File | YAML | TOON | Reduction |",
        "|------|------|------|-----------|",
    ]
    total_yaml = 0
    total_toon = 0
    for s in savings:
        lines.append(
            f"| `{s['file']}` | {s['yaml_chars']:,} chars | "
            f"{s['toon_chars']:,} chars | **{s['reduction_pct']}%** |"
        )
        total_yaml += s["yaml_chars"]
        total_toon += s["toon_chars"]

    if total_yaml > 0:
        total_pct = round((1 - total_toon / total_yaml) * 100, 1)
        lines.append(
            f"| **Total** | **{total_yaml:,}** | **{total_toon:,}** | **{total_pct}%** |"
        )

    return "\n".join(lines)


def generate_issue_body(project_path: Path) -> str:
    """Generate the migration issue body with savings data and opt-in checkbox."""
    savings = compute_savings(project_path)
    savings_table = _format_savings_table(savings)

    return f"""## Migrate to TOON for more efficient AI context

Your project uses [AICaC](https://github.com/eFAILution/AICaC) with YAML files in `.ai/`. \
TOON (Token-Oriented Object Notation) is a compact encoding that reduces token usage \
when AI coding assistants read your project context.

### What changes?

- Your `.ai/*.yaml` files stay exactly as they are (source of truth)
- New `.ai/*.toon` files are generated alongside them (optimized for AI)
- AI tools that support TOON will automatically use the more efficient format
- No changes to your workflow — the action regenerates `.toon` files on each run

### Savings for your project

{savings_table}

### How to migrate

Check the box below and the AICaC action will open a PR with the generated `.toon` files \
on its next run:

{PENDING_CHECKBOX}

### What if I don't want this?

Close this issue. The action will not suggest TOON migration again.

---
_This issue was created by the [AICaC Adoption Action](https://github.com/eFAILution/AICaC). \
Learn more about [TOON](https://github.com/toon-format/spec)._
"""


def check_approval(issue_body: str) -> bool:
    """Check if the migration checkbox is checked in the issue body."""
    return APPROVAL_CHECKBOX in issue_body


def generate_pr_body(issue_number: int) -> str:
    """Generate the migration PR body that closes the issue."""
    return f"""## Add TOON-encoded `.ai/` files

This PR adds TOON (Token-Oriented Object Notation) files alongside your existing \
`.ai/` YAML files. TOON provides a more compact encoding that reduces token usage \
when AI coding assistants consume your project context.

### Changes

- Generated `.ai/*.toon` files from existing `.ai/*.yaml` sources
- YAML files are unchanged (remain the human-authored source of truth)
- The AICaC action will keep `.toon` files in sync on future runs

### Notes

- `.toon` files are auto-generated — edit the `.yaml` source, not the `.toon` output
- Consider adding `.ai/*.toon` to your `.gitattributes` as generated files:
  ```
  .ai/*.toon linguist-generated=true
  ```

### Maintenance

{REBASE_PENDING_CHECKBOX}

> Check the box above to regenerate TOON files from the current YAML sources. \
The checkbox resets automatically after the update.

Closes #{issue_number}

---
_This PR was created by the [AICaC Adoption Action](https://github.com/eFAILution/AICaC)._
"""


def check_rebase_requested(pr_body: str) -> bool:
    """Check if the rebase/regenerate checkbox is checked in the PR body."""
    return REBASE_CHECKBOX in pr_body


def uncheck_rebase(pr_body: str) -> str:
    """Return the PR body with the rebase checkbox unchecked."""
    return pr_body.replace(REBASE_CHECKBOX, REBASE_PENDING_CHECKBOX)


def mark_rebase_failed(pr_body: str, error_message: str) -> str:
    """Return the PR body with the rebase checkbox unchecked and a failure notice."""
    updated = uncheck_rebase(pr_body)

    failure_notice = (
        "\n> **Rebase failed:** " + error_message + "\n"
        "> To recover, close this PR and delete the `aicac/toon-migration` branch. "
        "The action will recreate both on its next run.\n"
    )

    # Insert failure notice after the rebase checkbox line
    updated = updated.replace(
        REBASE_PENDING_CHECKBOX,
        REBASE_PENDING_CHECKBOX + "\n" + failure_notice,
    )
    return updated


def main():
    import argparse

    parser = argparse.ArgumentParser(description="AICaC TOON migration manager")
    parser.add_argument(
        "project_path", nargs="?", default=".",
        help="Path to project (default: current directory)",
    )
    parser.add_argument(
        "--needs-migration", action="store_true",
        help="Check if project needs TOON migration (exit 0=yes, 1=no)",
    )
    parser.add_argument(
        "--issue-body", action="store_true",
        help="Print the migration issue body to stdout",
    )
    parser.add_argument(
        "--check-approval", metavar="ISSUE_BODY",
        help="Check if checkbox is checked in the given issue body text (exit 0=approved, 1=not)",
    )
    parser.add_argument(
        "--pr-body", metavar="ISSUE_NUMBER", type=int,
        help="Print the migration PR body to stdout",
    )
    parser.add_argument(
        "--check-rebase", metavar="PR_BODY",
        help="Check if rebase checkbox is checked (exit 0=requested, 1=not)",
    )
    parser.add_argument(
        "--uncheck-rebase", action="store_true",
        help="Read PR body from stdin, print with rebase checkbox unchecked",
    )
    parser.add_argument(
        "--rebase-failed", metavar="ERROR_MESSAGE",
        help="Read PR body from stdin, print with failure notice added",
    )

    args = parser.parse_args()
    project_path = Path(args.project_path)

    if args.needs_migration:
        sys.exit(0 if needs_migration(project_path) else 1)

    if args.issue_body:
        print(generate_issue_body(project_path))
        sys.exit(0)

    if args.check_approval is not None:
        sys.exit(0 if check_approval(args.check_approval) else 1)

    if args.pr_body is not None:
        print(generate_pr_body(args.pr_body))
        sys.exit(0)

    if args.check_rebase is not None:
        sys.exit(0 if check_rebase_requested(args.check_rebase) else 1)

    if args.uncheck_rebase:
        pr_body = sys.stdin.read()
        print(uncheck_rebase(pr_body))
        sys.exit(0)

    if args.rebase_failed is not None:
        pr_body = sys.stdin.read()
        print(mark_rebase_failed(pr_body, args.rebase_failed))
        sys.exit(0)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
