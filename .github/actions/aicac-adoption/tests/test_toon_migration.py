"""Tests for TOON migration manager."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    from toon_migration import (
        needs_migration,
        compute_savings,
        generate_issue_body,
        check_approval,
        generate_pr_body,
        APPROVAL_CHECKBOX,
        PENDING_CHECKBOX,
        MIGRATION_LABEL,
    )
    from toon_format import encode as toon_encode
    HAS_TOON = True
except ImportError:
    HAS_TOON = False


pytestmark = pytest.mark.skipif(not HAS_TOON, reason="toon_format not installed")


@pytest.fixture
def yaml_project(tmp_path):
    """Project with .ai/ YAML files but no .toon files."""
    ai_dir = tmp_path / ".ai"
    ai_dir.mkdir()
    (ai_dir / "context.yaml").write_text(
        'version: "1.0"\n'
        "project:\n"
        "  name: my-app\n"
        "  type: web-app\n"
        "  framework: fastapi\n"
    )
    (ai_dir / "errors.yaml").write_text(
        "error_patterns:\n"
        '  - pattern: "Port already in use"\n'
        '    context: "Server start"\n'
        "    solutions:\n"
        '      - description: "Kill process"\n'
        '        command: "lsof -ti:8000 | xargs kill"\n'
    )
    return tmp_path


@pytest.fixture
def toon_project(yaml_project):
    """Project with both .ai/ YAML and .toon files (already migrated)."""
    ai_dir = yaml_project / ".ai"
    (ai_dir / "context.toon").write_text("# already migrated\n")
    return yaml_project


@pytest.fixture
def empty_project(tmp_path):
    """Project with no .ai/ directory."""
    return tmp_path


class TestNeedsMigration:
    def test_yaml_only_needs_migration(self, yaml_project):
        assert needs_migration(yaml_project) is True

    def test_already_migrated_does_not_need(self, toon_project):
        assert needs_migration(toon_project) is False

    def test_no_ai_dir_does_not_need(self, empty_project):
        assert needs_migration(empty_project) is False

    def test_empty_ai_dir_does_not_need(self, tmp_path):
        (tmp_path / ".ai").mkdir()
        assert needs_migration(tmp_path) is False


class TestComputeSavings:
    def test_returns_savings_for_yaml_files(self, yaml_project):
        savings = compute_savings(yaml_project)
        assert len(savings) == 2
        for s in savings:
            assert s["yaml_chars"] > 0
            assert s["toon_chars"] > 0
            assert s["reduction_pct"] >= 0

    def test_savings_file_names(self, yaml_project):
        savings = compute_savings(yaml_project)
        names = [s["file"] for s in savings]
        assert "context.yaml" in names
        assert "errors.yaml" in names

    def test_no_ai_dir_returns_empty(self, empty_project):
        assert compute_savings(empty_project) == []

    def test_empty_yaml_skipped(self, yaml_project):
        (yaml_project / ".ai" / "empty.yaml").write_text("")
        savings = compute_savings(yaml_project)
        names = [s["file"] for s in savings]
        assert "empty.yaml" not in names


class TestGenerateIssueBody:
    def test_contains_pending_checkbox(self, yaml_project):
        body = generate_issue_body(yaml_project)
        assert PENDING_CHECKBOX in body

    def test_does_not_contain_approved_checkbox(self, yaml_project):
        body = generate_issue_body(yaml_project)
        assert APPROVAL_CHECKBOX not in body

    def test_contains_savings_table(self, yaml_project):
        body = generate_issue_body(yaml_project)
        assert "context.yaml" in body
        assert "errors.yaml" in body
        assert "Reduction" in body

    def test_contains_toon_explanation(self, yaml_project):
        body = generate_issue_body(yaml_project)
        assert "TOON" in body
        assert "Token-Oriented Object Notation" in body

    def test_explains_close_to_decline(self, yaml_project):
        body = generate_issue_body(yaml_project)
        assert "Close this issue" in body


class TestCheckApproval:
    def test_checked_box_is_approved(self):
        body = f"Some text\n\n{APPROVAL_CHECKBOX}\n\nMore text"
        assert check_approval(body) is True

    def test_unchecked_box_is_not_approved(self):
        body = f"Some text\n\n{PENDING_CHECKBOX}\n\nMore text"
        assert check_approval(body) is False

    def test_empty_body_is_not_approved(self):
        assert check_approval("") is False

    def test_partial_match_is_not_approved(self):
        assert check_approval("- [x] Something else entirely") is False

    def test_real_issue_body_approved(self, yaml_project):
        body = generate_issue_body(yaml_project)
        assert check_approval(body) is False

        approved_body = body.replace(PENDING_CHECKBOX, APPROVAL_CHECKBOX)
        assert check_approval(approved_body) is True


class TestGeneratePrBody:
    def test_contains_closes_directive(self):
        body = generate_pr_body(42)
        assert "Closes #42" in body

    def test_contains_toon_description(self):
        body = generate_pr_body(1)
        assert "TOON" in body
        assert ".toon" in body

    def test_mentions_yaml_unchanged(self):
        body = generate_pr_body(1)
        assert "YAML files are unchanged" in body

    def test_suggests_gitattributes(self):
        body = generate_pr_body(1)
        assert "linguist-generated" in body


class TestMigrationLabel:
    def test_label_is_consistent(self):
        assert MIGRATION_LABEL == "aicac-toon-migration"
