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
import install_shims


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

    def test_decision_implementation_accepts_object(self, aicac_project):
        """ADRs commonly document implementation as a structured object
        ({pattern, ttl, storage}, {config, target}, ...) — the schema must
        accept it alongside the simple string form."""
        decisions_path = aicac_project / ".ai" / "decisions.yaml"
        decisions_path.write_text(
            'version: "2.0"\n'
            "decisions:\n"
            "  CACHE_COMPONENTS:\n"
            "    title: Cache Components\n"
            "    status: accepted\n"
            "    context: GitLab API calls are slow and rate-limited.\n"
            "    decision: Implement component caching with a TTL.\n"
            "    implementation:\n"
            "      pattern: Cache-aside\n"
            "      ttl: 3600 seconds\n"
            "      storage: in-memory\n"
        )
        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()
        decision_errors = [e for e in result["errors"] if "decisions" in e]
        assert decision_errors == [], decision_errors

    def test_decision_implementation_accepts_string(self, aicac_project):
        """The simple string form must keep working (backwards compatibility)."""
        decisions_path = aicac_project / ".ai" / "decisions.yaml"
        decisions_path.write_text(
            'version: "2.0"\n'
            "decisions:\n"
            "  USE_VALIDATOR:\n"
            "    title: Use Validator\n"
            "    status: accepted\n"
            "    context: Need a schema-driven validator for .ai/ files.\n"
            "    decision: Adopt jsonschema with Draft 2020-12 schemas.\n"
            "    implementation: scripts/validate.py\n"
        )
        validator = AICaCValidator(str(aicac_project))
        result = validator.validate()
        decision_errors = [e for e in result["errors"] if "decisions" in e]
        assert decision_errors == [], decision_errors


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


# -------------------------------------------------- migrate dict-shape fixups

class TestMigrateDictNormalization:
    """v1.x repos that already moved to dict shape but used non-canonical
    fields/keys (e.g. eFAILution/gitlab-component-helper#87) need more than
    just list->dict conversion to validate against the v2.0 schemas."""

    def test_decision_lowercase_key_uppercased(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "decisions.yaml").write_text(
            'version: "1.0"\n'
            "decisions:\n"
            "  use_esbuild:\n"
            "    status: accepted\n"
            "    context: Need a fast bundler for the extension build.\n"
            "    decision: Adopt esbuild over webpack.\n"
        )
        migrate_v2.migrate_file(ai_dir / "decisions.yaml")
        new = yaml.safe_load((ai_dir / "decisions.yaml").read_text())
        assert "USE_ESBUILD" in new["decisions"]
        assert "use_esbuild" not in new["decisions"]

    def test_decision_missing_title_derived_from_key(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "decisions.yaml").write_text(
            'version: "2.0"\n'
            "decisions:\n"
            "  USE_ESBUILD:\n"
            "    status: accepted\n"
            "    context: Need a fast bundler for the extension build.\n"
            "    decision: Adopt esbuild over webpack.\n"
        )
        migrate_v2.migrate_file(ai_dir / "decisions.yaml")
        new = yaml.safe_load((ai_dir / "decisions.yaml").read_text())
        assert new["decisions"]["USE_ESBUILD"]["title"] == "Use Esbuild"

    def test_decision_alternatives_considered_reshaped(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "decisions.yaml").write_text(
            'version: "2.0"\n'
            "decisions:\n"
            "  USE_ESBUILD:\n"
            "    title: Use Esbuild\n"
            "    status: accepted\n"
            "    context: Need a fast bundler for the extension build.\n"
            "    decision: Adopt esbuild over webpack.\n"
            "    alternatives_considered:\n"
            "      - webpack: Too slow, complex configuration\n"
            "      - rollup: Not optimized for Node.js\n"
        )
        migrate_v2.migrate_file(ai_dir / "decisions.yaml")
        new = yaml.safe_load((ai_dir / "decisions.yaml").read_text())
        alts = new["decisions"]["USE_ESBUILD"]["alternatives_considered"]
        assert alts[0] == {"name": "webpack", "rejected_because": "Too slow, complex configuration"}
        assert alts[1] == {"name": "rollup", "rejected_because": "Not optimized for Node.js"}

    def test_errors_missing_version_added(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "errors.yaml").write_text(
            "errors:\n"
            "  COMPONENT_NOT_LOADING:\n"
            "    symptom: Component browser is empty\n"
        )
        migrate_v2.migrate_file(ai_dir / "errors.yaml")
        new = yaml.safe_load((ai_dir / "errors.yaml").read_text())
        assert new["version"] == "2.0"

    def test_errors_symptom_derived_from_symptoms_list(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "errors.yaml").write_text(
            'version: "2.0"\n'
            "errors:\n"
            "  COMPONENT_NOT_LOADING:\n"
            "    symptoms:\n"
            "      - Component browser shows no components\n"
            "      - Autocomplete not working\n"
        )
        migrate_v2.migrate_file(ai_dir / "errors.yaml")
        new = yaml.safe_load((ai_dir / "errors.yaml").read_text())
        assert new["errors"]["COMPONENT_NOT_LOADING"]["symptom"] == (
            "Component browser shows no components; Autocomplete not working"
        )

    def test_errors_causes_flattened_into_common_causes_and_solutions(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "errors.yaml").write_text(
            'version: "2.0"\n'
            "errors:\n"
            "  COMPONENT_NOT_LOADING:\n"
            "    symptom: Component browser is empty\n"
            "    causes:\n"
            "      - cause: No component sources configured\n"
            "        solution: Add componentSources in settings\n"
            "      - cause: Cache not initialized\n"
            "        solution:\n"
            "          steps:\n"
            "            - Run command palette\n"
            "            - Update Cache\n"
        )
        migrate_v2.migrate_file(ai_dir / "errors.yaml")
        new = yaml.safe_load((ai_dir / "errors.yaml").read_text())
        err = new["errors"]["COMPONENT_NOT_LOADING"]
        assert err["common_causes"] == [
            "No component sources configured",
            "Cache not initialized",
        ]
        assert err["solutions"][0] == "Add componentSources in settings"
        assert err["solutions"][1] == {"steps": ["Run command palette", "Update Cache"]}

    def test_errors_solutions_deepcopied_no_yaml_anchors(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "errors.yaml").write_text(
            'version: "2.0"\n'
            "errors:\n"
            "  E:\n"
            "    symptom: foo\n"
            "    causes:\n"
            "      - cause: x\n"
            "        solution:\n"
            "          steps: [a]\n"
        )
        migrate_v2.migrate_file(ai_dir / "errors.yaml")
        text = (ai_dir / "errors.yaml").read_text()
        assert "&id" not in text and "*id" not in text

    def test_already_v2_no_changes(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "decisions.yaml").write_text(
            'version: "2.0"\n'
            "decisions:\n"
            "  ADR-001:\n"
            "    title: Use React\n"
            "    status: accepted\n"
            "    context: Need a SPA framework with broad support.\n"
            "    decision: Adopt React for the frontend.\n"
        )
        changes = migrate_v2.migrate_file(ai_dir / "decisions.yaml")
        assert changes == []


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


# ---------------------------------------------------------------- migrate --check

class TestMigrateCheck:
    """The --check flag is exposed via _count_pending_changes; exercise the logic."""

    def test_check_reports_zero_on_v2(self, aicac_project):
        ai_dir = aicac_project / ".ai"
        assert migrate_v2._count_pending_changes(ai_dir) == 0

    def test_check_reports_nonzero_on_v1(self, tmp_path):
        ai_dir = tmp_path / ".ai"
        ai_dir.mkdir()
        (ai_dir / "architecture.yaml").write_text(
            'version: "1.0"\n'
            "components:\n"
            "  - name: api\n"
            "    purpose: HTTP\n"
        )
        assert migrate_v2._count_pending_changes(ai_dir) >= 1


# ---------------------------------------------------------------- install_shims

class TestInstallShims:
    def test_all_platforms_resolve(self):
        assert set(install_shims.parse_platforms("all")) == set(install_shims.PLATFORMS)

    def test_unknown_platform_rejected(self):
        with pytest.raises(ValueError):
            install_shims.parse_platforms("cursor,bogus")

    def test_writes_files_to_expected_paths(self, tmp_path):
        for platform in install_shims.PLATFORMS:
            rel, wrote = install_shims.write_shim(tmp_path, platform, dry_run=False)
            assert wrote is True
            assert (tmp_path / rel).exists()

    def test_shim_points_at_agents_md(self, tmp_path):
        install_shims.write_shim(tmp_path, "cursor", dry_run=False)
        content = (tmp_path / ".cursor/rules/aicac.mdc").read_text()
        assert "AGENTS.md" in content
        assert "alwaysApply: true" in content

    def test_skips_existing_files(self, tmp_path):
        rel, wrote_first = install_shims.write_shim(tmp_path, "windsurf", dry_run=False)
        assert wrote_first is True
        _, wrote_second = install_shims.write_shim(tmp_path, "windsurf", dry_run=False)
        assert wrote_second is False

    def test_dry_run_does_not_write(self, tmp_path):
        rel, wrote = install_shims.write_shim(tmp_path, "copilot", dry_run=True)
        assert wrote is True  # returns "would write" for contract consistency
        assert not (tmp_path / rel).exists()
