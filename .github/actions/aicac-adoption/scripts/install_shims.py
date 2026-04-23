#!/usr/bin/env python3
"""
Write platform-specific shim files that point at AGENTS.md.

AICaC's router pattern lives in AGENTS.md — the emerging cross-vendor
convention. Each platform-specific adopter file (Cursor rules, Copilot
instructions, Windsurf rules, etc.) is a thin 5–10 line pointer that
tells that platform's AI to follow AGENTS.md. This avoids duplicating
the router logic into every platform's native format.

Usage:
    python3 install_shims.py <project_path> --platforms=cursor,copilot
    python3 install_shims.py . --platforms=all
    python3 install_shims.py . --platforms=cursor --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SHIM_BODY = """\
# AICaC adopter

Before answering any question about this project, read `AGENTS.md` at
the repository root. It is the router for `.ai/*.yaml` — AICaC structured
context files. Load only the `.ai/` file relevant to the current intent;
do not load them all at once.

Intent → load:
- Project overview, dev commands → `.ai/context.yaml`
- Components, dependencies, data flow → `.ai/architecture.yaml`
- How-to, adding features → `.ai/workflows.yaml`
- Why a decision was made → `.ai/decisions.yaml`
- Errors, troubleshooting → `.ai/errors.yaml`

Before loading any full file, check its `summary:` field or `.ai/index.yaml`
to confirm the routing target.
"""


def _cursor_shim() -> str:
    """Cursor uses `.cursor/rules/*.mdc` with MDC frontmatter."""
    frontmatter = """\
---
description: AICaC router — always read AGENTS.md first
alwaysApply: true
---

"""
    return frontmatter + SHIM_BODY


PLATFORMS: dict[str, tuple[str, str]] = {
    # name -> (relative_path, content)
    "cursor":   (".cursor/rules/aicac.mdc",           _cursor_shim()),
    "copilot":  (".github/copilot-instructions.md",   SHIM_BODY),
    "windsurf": (".windsurfrules",                    SHIM_BODY),
    "aider":    ("CONVENTIONS.md",                    SHIM_BODY),
}


def parse_platforms(value: str) -> list[str]:
    if not value:
        return []
    if value == "all":
        return list(PLATFORMS)
    requested = [p.strip() for p in value.split(",") if p.strip()]
    unknown = [p for p in requested if p not in PLATFORMS]
    if unknown:
        raise ValueError(
            f"Unknown platforms: {unknown}. "
            f"Valid: {list(PLATFORMS)} or 'all'."
        )
    return requested


def write_shim(project_path: Path, platform: str, dry_run: bool) -> tuple[str, bool]:
    """Return (relative_path, wrote_file). wrote_file is False if it already existed."""
    rel, content = PLATFORMS[platform]
    target = project_path / rel

    if target.exists():
        return rel, False

    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    return rel, True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", nargs="?", default=".")
    parser.add_argument(
        "--platforms",
        default="",
        help="Comma-separated list, or 'all'. "
             f"Valid: {','.join(PLATFORMS)}",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        platforms = parse_platforms(args.platforms)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    if not platforms:
        print("No platforms selected. Use --platforms=<list> or --platforms=all.",
              file=sys.stderr)
        return 2

    project = Path(args.project_path).resolve()
    prefix = "(dry-run) " if args.dry_run else ""

    written = 0
    skipped = 0
    for platform in platforms:
        rel, wrote = write_shim(project, platform, args.dry_run)
        if wrote:
            print(f"{prefix}wrote {rel}")
            written += 1
        else:
            print(f"skipped {rel} (already exists)")
            skipped += 1

    print(f"\n{prefix}{written} written, {skipped} skipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
