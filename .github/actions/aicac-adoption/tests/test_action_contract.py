"""Behavior contracts for the composite Action's compliance step."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


ACTION_PATH = Path(__file__).resolve().parents[1] / "action.yml"
VALIDATOR_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate.py"


def _compliance_script() -> str:
    action = yaml.safe_load(ACTION_PATH.read_text())
    return next(
        step["run"]
        for step in action["runs"]["steps"]
        if step.get("id") == "check-compliance"
    )


def _fake_action(tmp_path: Path) -> tuple[Path, Path]:
    action_path = tmp_path / "action"
    scripts = action_path / "scripts"
    scripts.mkdir(parents=True)
    counter = tmp_path / "validator-invocations"
    (scripts / "validate.py").write_text(
        """from __future__ import annotations

import json
import os
import sys
from pathlib import Path

strict = "--strict" in sys.argv
forced_error = os.environ.get("FAKE_VALIDATOR_ERROR") == "true"
errors = ["schema failure"] if forced_error else []
warnings = ["warning-only result"] if not forced_error else []
valid = not forced_error and not strict
result = {
    "valid": valid,
    "compliance_level": "Minimal" if valid else "None",
    "errors": errors,
    "warnings": warnings,
}
output_index = sys.argv.index("--json-output") + 1
Path(sys.argv[output_index]).write_text(json.dumps(result))
with Path(os.environ["VALIDATOR_COUNTER"]).open("a") as stream:
    stream.write("called\\n")
print("warning-only result" if warnings else "schema failure")
raise SystemExit(0 if valid else 1)
""",
        encoding="utf-8",
    )
    return action_path, counter


def _run_compliance(
    tmp_path: Path,
    *,
    strict: bool,
    migration_needed: bool = False,
    forced_error: bool = False,
    mode: str = "maintain",
) -> tuple[subprocess.CompletedProcess[str], dict[str, str], int]:
    action_path, counter = _fake_action(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    github_output = tmp_path / "github-output"
    script = _compliance_script().replace("${{ github.action_path }}", str(action_path))
    env = os.environ.copy()
    env.update(
        {
            "PROJECT_PATH": str(project),
            "MODE": mode,
            "STRICT": str(strict).lower(),
            "MIGRATION_NEEDED": str(migration_needed).lower(),
            "AUTO_MIGRATE": "true",
            "FAKE_VALIDATOR_ERROR": str(forced_error).lower(),
            "VALIDATOR_COUNTER": str(counter),
            "GITHUB_OUTPUT": str(github_output),
        }
    )

    result = subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    outputs = dict(
        line.split("=", 1)
        for line in github_output.read_text(encoding="utf-8").splitlines()
    )
    invocations = len(counter.read_text(encoding="utf-8").splitlines())
    return result, outputs, invocations


def test_warning_only_non_strict_run_succeeds_from_one_result(tmp_path: Path) -> None:
    result, outputs, invocations = _run_compliance(tmp_path, strict=False)

    assert result.returncode == 0, result.stderr
    assert "warning-only result" in result.stdout
    assert outputs["level"] == "Minimal"
    assert outputs["schema-violations"] == "0"
    assert outputs["badge"].endswith("AICaC-Minimal-green.svg")
    assert invocations == 1


def test_strict_warning_fails_even_when_migration_is_needed(tmp_path: Path) -> None:
    result, outputs, invocations = _run_compliance(
        tmp_path, strict=True, migration_needed=True
    )

    assert result.returncode == 1
    assert outputs["level"] == "None"
    assert outputs["schema-violations"] == "0"
    assert outputs["badge"].endswith("AICaC-Not%20Adopted-red.svg")
    assert all("AICaC-Migrating" not in value for value in outputs.values())
    assert invocations == 1


def test_non_strict_maintain_migration_can_open_for_manual_cleanup(tmp_path: Path) -> None:
    result, outputs, invocations = _run_compliance(
        tmp_path, strict=False, migration_needed=True, forced_error=True
    )

    assert result.returncode == 0, result.stderr
    assert outputs["level"] == "None"
    assert outputs["schema-violations"] == "1"
    assert outputs["badge"].endswith("AICaC-Migrating-yellow.svg")
    assert invocations == 1


def test_validate_mode_never_uses_migration_success_exception(tmp_path: Path) -> None:
    result, outputs, invocations = _run_compliance(
        tmp_path,
        strict=False,
        migration_needed=True,
        forced_error=True,
        mode="validate",
    )

    assert result.returncode == 1
    assert outputs["badge"].endswith("AICaC-Not%20Adopted-red.svg")
    assert invocations == 1


def test_validate_mode_does_not_stage_migration() -> None:
    action = yaml.safe_load(ACTION_PATH.read_text())
    stage_migration = next(
        step
        for step in action["runs"]["steps"]
        if step.get("name") == "Stage v2.0 migration in working tree"
    )

    assert "inputs.mode == 'maintain'" in stage_migration["if"]
    assert "inputs.mode == 'validate'" not in stage_migration["if"]


def test_validate_mode_keeps_local_action_checkout_clean(tmp_path: Path) -> None:
    repo = tmp_path / "consumer"
    local_action = repo / ".github" / "actions" / "aicac-adoption"
    local_scripts = local_action / "scripts"
    local_scripts.mkdir(parents=True)
    shutil.copy2(ACTION_PATH, local_action / "action.yml")
    for source in ACTION_PATH.parent.joinpath("scripts").glob("*.py"):
        target = local_scripts / source.name
        shutil.copy2(source, target)
        target.chmod(0o644)

    subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Action Contract Test"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "action@example.test"],
        check=True,
    )
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "--quiet", "-m", "fixture"],
        check=True,
    )

    action = yaml.safe_load((local_action / "action.yml").read_text())
    for step in action["runs"]["steps"]:
        script = step.get("run", "")
        if "chmod " not in script or "${{ github.action_path }}" not in script:
            continue
        result = subprocess.run(
            [
                "bash",
                "-c",
                script.replace("${{ github.action_path }}", str(local_action)),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr

    status = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert status.stdout == ""


def test_validator_can_write_json_sidecar_with_human_report(
    aicac_project: Path, tmp_path: Path
) -> None:
    sidecar = tmp_path / "validation.json"

    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR_PATH),
            str(aicac_project),
            "--json-output",
            str(sidecar),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "AICaC Compliance Validation Report" in result.stdout
    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    assert payload["valid"] is True
    assert payload["compliance_level"] == "Minimal"
