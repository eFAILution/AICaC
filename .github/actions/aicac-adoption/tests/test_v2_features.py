"""
Tests for v2.0 features: JSON Schema validation, cross-reference checking,
content-quality heuristics, migration helper, and index generator.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate import AICaCValidator
import migrate_v2
import generate_index


# ---------------------------------------------------------------- schema

class TestSchemaValidation:
    def test_enum_project_type_rejected(self, aicac_project):
        """Unknown project.type values are rejected by v2.0 schema."""
        ctx_path = aicac_project / ".ai" / "context.yaml"
        data = yaml.safe_load(ctx_path.read_text())
        data["project"]["type"] = "definitely-not-a-real-type"
        ctx_path.write_text(yaml.safe_dump(data))

        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()
        assert any("type" in e for e in result["errors"])

    def test_description_too_short_rejected(self, aicac_project):
        ctx_path = aicac_project / ".ai" / "context.yaml"
        data = yaml.safe_load(ctx_path.read_text())
        data["project"]["description"] = "short"
        ctx_path.write_text(yaml.safe_dump(data))

        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()
        assert any("description" in e.lower() for e in result["errors"])

    def test_other_type_escape_hatch_accepted(self, aicac_project):
        ctx_path = aicac_project / ".ai" / "context.yaml"
        data = yaml.safe_load(ctx_path.read_text())
        data["project"]["type"] = "other"
        data["project"]["type_detail"] = "exotic framework"
        ctx_path.write_text(yaml.safe_dump(data))

        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()
        assert result["valid"]


# ---------------------------------------------------------------- xref

class TestXrefValidation:
    def test_workflow_references_unknown_component(self, comprehensive_aicac_project):
        wf_path = comprehensive_aicac_project / ".ai" / "workflows.yaml"
        data = yaml.safe_load(wf_path.read_text())
        data["workflows"]["add_feature"]["touches_components"] = ["nonexistent"]
        wf_path.write_text(yaml.safe_dump(data))

        validator = AICaCValidator(str(comprehensive_aicac_project))
        result = validator.validate()
        assert any("nonexistent" in e for e in result["errors"])

    def test_decision_references_known_component_accepted(self, comprehensive_aicac_project):
        dec_path = comprehensive_aicac_project / ".ai" / "decisions.yaml"
        data = yaml.safe_load(dec_path.read_text())
        data["decisions"]["ADR-001"]["affects_components"] = ["frontend"]
        dec_path.write_text(yaml.safe_dump(data))

        validator = AICaCValidator(str(comprehensive_aicac_project))
        result = validator.validate()
        assert result["valid"]

    def test_component_depends_on_unknown_component(self, comprehensive_aicac_project):
        arch_path = comprehensive_aicac_project / ".ai" / "architecture.yaml"
        data = yaml.safe_load(arch_path.read_text())
        data["components"]["frontend"]["depends_on"] = ["ghost"]
        arch_path.write_text(yaml.safe_dump(data))

        validator = AICaCValidator(str(comprehensive_aicac_project))
        result = validator.validate()
        assert any("ghost" in e for e in result["errors"])

    def test_superseded_by_unknown_adr(self, comprehensive_aicac_project):
        dec_path = comprehensive_aicac_project / ".ai" / "decisions.yaml"
        data = yaml.safe_load(dec_path.read_text())
        data["decisions"]["ADR-001"]["superseded_by"] = "ADR-999"
        dec_path.write_text(yaml.safe_dump(data))

        validator = AICaCValidator(str(comprehensive_aicac_project))
        result = validator.validate()
        assert any("ADR-999" in e for e in result["errors"])


# ---------------------------------------------------------------- quality

class TestQualityHeuristics:
    def test_todo_heavy_file_does_not_count(self, aicac_project):
        """A file that is mostly TODO placeholders is excluded from compliance count."""
        ai_dir = aicac_project / ".ai"
        # Write an optional file that is almost entirely TODOs
        (ai_dir / "architecture.yaml").write_text(
            'version: "2.0"\n'
            "# TODO: map out components\n"
            "components:\n"
            "  TODO1:\n"
            "    location: TODO\n"
            "    purpose: TODO: describe this component\n"
            "# TODO: add more\n"
            "# TODO: cross-refs\n"
        )
        (ai_dir / "workflows.yaml").write_text(
            'version: "2.0"\n'
            "workflows:\n"
            "  run_tests:\n"
            "    description: Run tests\n"
            "    command: pytest\n"
            "  start_dev:\n"
            "    description: Start dev\n"
            "    command: npm run dev\n"
        )

        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()
        # Warning fired, architecture.yaml excluded from optional count
        assert any("majority of lines are TODO" in w for w in result["warnings"])

    def test_common_commands_deprecation_warning(self, aicac_project):
        ctx_path = aicac_project / ".ai" / "context.yaml"
        data = yaml.safe_load(ctx_path.read_text())
        data["common_commands"] = data.pop("common_tasks")
        ctx_path.write_text(yaml.safe_dump(data))

        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()
        assert any("common_commands" in w for w in result["warnings"])


# ---------------------------------------------------------------- migrate

class TestMigrateV2:
    def test_migrate_decisions_list_to_dict(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "decisions.yaml").write_text(
            'version: "1.0"\n'
            "decisions:\n"
            "  - id: ADR-001\n"
            "    title: Use React\n"
            "    status: accepted\n"
            "    context: Need SPA framework\n"
            "    decision: Use React\n"
        )
        changes = migrate_v2.migrate_file(ai_dir / "decisions.yaml")
        assert any("list -> dict" in c for c in changes)

        new = yaml.safe_load((ai_dir / "decisions.yaml").read_text())
        assert isinstance(new["decisions"], dict)
        assert "ADR-001" in new["decisions"]
        assert new["version"] == "2.0"

    def test_migrate_components_list_to_dict(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "architecture.yaml").write_text(
            "components:\n"
            "  - name: api\n"
            "    location: src/api/\n"
            "    purpose: HTTP\n"
            "  - name: db\n"
            "    purpose: Storage\n"
        )
        migrate_v2.migrate_file(ai_dir / "architecture.yaml")
        new = yaml.safe_load((ai_dir / "architecture.yaml").read_text())
        assert set(new["components"].keys()) == {"api", "db"}

    def test_migrate_error_patterns_to_errors(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "errors.yaml").write_text(
            "error_patterns:\n"
            "  - pattern: Port in use\n"
            "    solutions:\n"
            "      - Kill the process\n"
        )
        migrate_v2.migrate_file(ai_dir / "errors.yaml")
        new = yaml.safe_load((ai_dir / "errors.yaml").read_text())
        assert "error_patterns" not in new
        assert "errors" in new
        assert any("PORT" in k for k in new["errors"])

    def test_migrate_common_commands_to_common_tasks(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "context.yaml").write_text(
            'version: "1.0"\n'
            "project:\n"
            "  name: x\n"
            "  type: web-app\n"
            "  description: test project description\n"
            "entrypoints:\n"
            "  main: src/index.js\n"
            "common_commands:\n"
            "  dev: npm run dev\n"
        )
        changes = migrate_v2.migrate_file(ai_dir / "context.yaml")
        assert any("common_commands" in c for c in changes)
        new = yaml.safe_load((ai_dir / "context.yaml").read_text())
        assert "common_tasks" in new
        assert "common_commands" not in new


# ---------------------------------------------------------------- index

class TestGenerateIndex:
    def test_index_lists_component_and_workflow_ids(self, comprehensive_aicac_project):
        ai_dir = comprehensive_aicac_project / ".ai"
        idx = generate_index.build_index(ai_dir)

        assert idx["version"] == "2.0"
        assert "frontend" in idx["keys"]["architecture"]
        assert "backend" in idx["keys"]["architecture"]
        assert "add_feature" in idx["keys"]["workflows"]
        assert "ADR-001" in idx["keys"]["decisions"]

    def test_index_routing_table_present(self, comprehensive_aicac_project):
        ai_dir = comprehensive_aicac_project / ".ai"
        idx = generate_index.build_index(ai_dir)
        assert "project_overview" in idx["routing"]
        assert idx["routing"]["project_overview"] == ["context.yaml"]
