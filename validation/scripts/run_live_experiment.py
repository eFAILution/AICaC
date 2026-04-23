#!/usr/bin/env python3
"""
End-to-end live Claude experiment runner.

Runs the performance experiment against the taskflow sample project across
three format configurations (README_ONLY, AGENTS_ONLY, AICAC_SELECTIVE) and
emits a combined report with:

  - input tokens      (size of the context the model received)
  - output tokens     (size of the model's answer)
  - response_time_ms  (wall-clock latency per call)
  - accuracy          (keyword-based scoring against expected answers)

Requires a working AI provider. Options, in order of cost:

    make perf-ollama       # free, local; requires Ollama running
    make perf-groq         # free cloud tier; requires GROQ_API_KEY
    make perf-claude       # paid; requires ANTHROPIC_API_KEY
    make perf-openai       # paid; requires OPENAI_API_KEY

Usage:
    python run_live_experiment.py --provider claude --trials 3
    python run_live_experiment.py --provider groq --trials 10
    python run_live_experiment.py --estimate-cost
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess  # nosec B404 - this script is a test-harness driver that shells out to performance_measurement.py with hardcoded argv; no user input reaches the subprocess call
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PROJECT = REPO_ROOT / "validation" / "examples" / "sample-project"
RESULTS_DIR = REPO_ROOT / "experiments"
PERF_SCRIPT = Path(__file__).parent / "performance_measurement.py"


PROVIDERS = {
    "ollama":    {"env_var": None,               "cost_per_1k_in": 0.0,    "cost_per_1k_out": 0.0},
    "groq":      {"env_var": "GROQ_API_KEY",     "cost_per_1k_in": 0.0,    "cost_per_1k_out": 0.0},
    "anthropic": {"env_var": "ANTHROPIC_API_KEY","cost_per_1k_in": 0.003,  "cost_per_1k_out": 0.015},
    "openai":    {"env_var": "OPENAI_API_KEY",   "cost_per_1k_in": 0.0025, "cost_per_1k_out": 0.010},
}


def estimate_cost(trials: int) -> None:
    """Print a rough cost estimate for each provider (no API calls)."""
    formats = ["README_ONLY", "AGENTS_ONLY", "AICAC_SELECTIVE"]
    questions = 12  # IR:3 + AU:3 + CW:3 + ER:3 in performance_measurement.py
    calls = trials * len(formats) * questions

    # Rough per-call token estimate from token_measurement results
    avg_input = 1500
    avg_output = 250

    print(f"Plan: {trials} trials × {len(formats)} formats × {questions} questions = {calls} calls")
    print(f"Assumed avg: {avg_input} input tokens, {avg_output} output tokens per call\n")

    for name, info in PROVIDERS.items():
        input_cost = calls * avg_input / 1000 * info["cost_per_1k_in"]
        output_cost = calls * avg_output / 1000 * info["cost_per_1k_out"]
        total = input_cost + output_cost
        env = info["env_var"] or "— (local)"
        print(f"  {name:<10} env={env:<20} ~${total:.2f} total")


def check_provider(provider: str) -> bool:
    info = PROVIDERS.get(provider)
    if not info:
        print(f"Unknown provider: {provider}", file=sys.stderr)
        return False
    if info["env_var"] and not os.environ.get(info["env_var"]):
        print(f"Missing env var: {info['env_var']}", file=sys.stderr)
        return False
    return True


def run(provider: str, trials: int) -> int:
    RESULTS_DIR.mkdir(exist_ok=True)
    output = RESULTS_DIR / f"live_{provider}_{trials}trials.json"
    cmd = [
        sys.executable, str(PERF_SCRIPT),
        "--repo-path", str(SAMPLE_PROJECT),
        "--provider", provider,
        "--trials", str(trials),
        "--output", str(output),
    ]
    print("Running:", " ".join(cmd), flush=True)
    # cmd is built entirely from CLI args (provider is validated via argparse
    # choices, trials is int-coerced) and hard-coded script paths. shell=False
    # (the default) means no shell interpolation, so even malicious values
    # can only become argv tokens to the known Python script.
    return subprocess.call(cmd)  # nosec B603


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--provider", choices=list(PROVIDERS.keys()))
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--estimate-cost", action="store_true", help="Print cost estimate and exit.")
    args = parser.parse_args()

    if args.estimate_cost:
        estimate_cost(args.trials)
        return 0

    if not args.provider:
        print("Must specify --provider (or --estimate-cost).", file=sys.stderr)
        return 2

    if not check_provider(args.provider):
        return 2

    return run(args.provider, args.trials)


if __name__ == "__main__":
    sys.exit(main())
