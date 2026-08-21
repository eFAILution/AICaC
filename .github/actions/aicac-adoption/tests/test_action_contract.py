"""Static contracts for behavior implemented in the composite action shell."""

from pathlib import Path

import yaml


ACTION_PATH = Path(__file__).resolve().parents[1] / "action.yml"


def _compliance_script() -> str:
    action = yaml.safe_load(ACTION_PATH.read_text())
    return next(
        step["run"]
        for step in action["runs"]["steps"]
        if step.get("id") == "check-compliance"
    )


def test_strict_input_is_forwarded_to_both_validator_runs() -> None:
    script = _compliance_script()

    assert "VALIDATE_ARGS=()" in script
    assert 'VALIDATE_ARGS+=(--strict)' in script
    assert script.count('"${VALIDATE_ARGS[@]}"') == 2


def test_strict_mode_does_not_use_errors_only_postprocessing() -> None:
    script = _compliance_script()

    assert '[ "$STRICT" = "true" ] && [ "$VIOLATIONS" -gt 0 ]' not in script
