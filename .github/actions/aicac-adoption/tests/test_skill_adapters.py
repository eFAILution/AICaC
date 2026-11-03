"""
Contract tests for the harness-neutral AICaC skill layout.

Canonical body: skills/aicac/
Adapters (symlinks): .claude/skills/aicac/, .agents/skills/aicac/
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
CANONICAL = REPO_ROOT / "skills" / "aicac"
ADAPTERS = (
    REPO_ROOT / ".claude" / "skills" / "aicac",
    REPO_ROOT / ".agents" / "skills" / "aicac",
)
REQUIRED_ENTRIES = (
    "SKILL.md",
    "bootstrap.md",
    "migrate.md",
    "router.md",
    "sync.md",
    "validate.md",
    "schemas",
)
REQUIRED_SCHEMAS = (
    "architecture.schema.json",
    "context.schema.json",
    "decisions.schema.json",
    "errors.schema.json",
    "index.schema.json",
    "workflows.schema.json",
)


@pytest.fixture(scope="module")
def canonical() -> Path:
    assert CANONICAL.is_dir(), f"missing canonical skill body at {CANONICAL}"
    return CANONICAL


class TestCanonicalSkillBody:
    def test_required_entries_present(self, canonical: Path):
        missing = [name for name in REQUIRED_ENTRIES if not (canonical / name).exists()]
        assert missing == [], f"canonical skill missing entries: {missing}"

    def test_schemas_present(self, canonical: Path):
        schemas = canonical / "schemas"
        missing = [name for name in REQUIRED_SCHEMAS if not (schemas / name).is_file()]
        assert missing == [], f"canonical schemas missing: {missing}"

    def test_skill_frontmatter(self, canonical: Path):
        text = (canonical / "SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
        match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
        assert match, "SKILL.md frontmatter fence not closed"
        frontmatter = match.group(1)
        assert re.search(r"(?m)^name:\s*aicac\s*$", frontmatter)
        desc = re.search(r"(?m)^description:\s*(.+)$", frontmatter)
        assert desc and desc.group(1).strip(), "description must be non-empty"


class TestSkillAdapters:
    @pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
    def test_adapter_directory_exists(self, adapter: Path):
        assert adapter.is_dir(), f"missing adapter directory {adapter}"

    @pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
    def test_adapter_required_entries_present(self, adapter: Path):
        adapter_names = {p.name for p in adapter.iterdir()}
        missing = [name for name in REQUIRED_ENTRIES if name not in adapter_names]
        assert missing == [], f"{adapter.relative_to(REPO_ROOT)} missing: {missing}"

    @pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
    @pytest.mark.parametrize("entry", REQUIRED_ENTRIES)
    def test_adapter_entries_are_symlinks_to_canonical(
        self, adapter: Path, entry: str, canonical: Path
    ):
        link = adapter / entry
        assert link.is_symlink(), f"{link.relative_to(REPO_ROOT)} must be a symlink"
        resolved = link.resolve()
        expected = (canonical / entry).resolve()
        assert resolved == expected, (
            f"{link.relative_to(REPO_ROOT)} resolves to {resolved}, "
            f"expected {expected}"
        )

    @pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda p: str(p.relative_to(REPO_ROOT)))
    def test_adapter_skill_readable_via_symlink(self, adapter: Path, canonical: Path):
        adapter_text = (adapter / "SKILL.md").read_text(encoding="utf-8")
        canonical_text = (canonical / "SKILL.md").read_text(encoding="utf-8")
        assert adapter_text == canonical_text
