#!/usr/bin/env python3
"""
AICaC Performance Measurement - Phase 2

Measures AI response quality and speed across documentation formats.
Unlike token_measurement.py (free), this CALLS AI APIs and costs money.

Supported providers:
  - anthropic: Claude (requires ANTHROPIC_API_KEY)
  - openai: GPT-4 (requires OPENAI_API_KEY)
  - ollama: Local models (free, requires Ollama running)

Usage:
    # Estimate cost first (no API calls)
    python performance_measurement.py --estimate-cost

    # Run with Claude
    python performance_measurement.py --provider anthropic --trials 3

    # Run with local Ollama (free)
    python performance_measurement.py --provider ollama --model llama3

    # Run specific format only
    python performance_measurement.py --provider anthropic --format AICAC_SELECTIVE
"""

import argparse
import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional
import statistics

# Provider imports (optional)
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False


# Approximate costs per 1M tokens (as of 2026)
COST_PER_1M_TOKENS = {
    "anthropic": {"input": 3.00, "output": 15.00},  # Claude Sonnet
    "openai": {"input": 2.50, "output": 10.00},     # GPT-4o
    "ollama": {"input": 0.00, "output": 0.00},      # Local, free
}

# Default models per provider
DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
    "ollama": "llama3",
}


@dataclass
class PerformanceMeasurement:
    """Single performance measurement result"""
    format: str
    question_id: str
    question: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    response_time_ms: int
    answer: str
    answer_found: bool  # Did the answer address the question?
    files_loaded: List[str]
    timestamp: str


# Questions with expected answers for validation
TEST_QUESTIONS = [
    {
        "id": "IR-001",
        "question": "What command starts the development server?",
        "expected_keywords": ["taskflow", "serve", "reload"],
        "category": "information_retrieval"
    },
    {
        "id": "AU-001",
        "question": "Why was FastAPI chosen over Flask?",
        "expected_keywords": ["openapi", "pydantic", "async", "validation", "type"],
        "category": "architectural_understanding"
    },
    {
        "id": "CW-001",
        "question": "How do I add a new API endpoint?",
        "expected_keywords": ["router", "api", "main.py", "register"],
        "category": "common_workflows"
    },
    {
        "id": "ER-001",
        "question": "How do I fix a 'port already in use' error?",
        "expected_keywords": ["kill", "port", "8000", "lsof"],
        "category": "error_resolution"
    },
]


class DocumentationLoader:
    """Loads documentation (reused from token_measurement.py)"""

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)

    def load(self, format: str, question_id: str = None) -> tuple[str, List[str]]:
        """Load documentation in specified format"""
        if format == "README_ONLY":
            return self._load_readme_only()
        elif format == "AICAC_SELECTIVE":
            q_type = question_id.split("-")[0] if question_id else "IR"
            return self._load_selective(q_type)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _load_readme_only(self) -> tuple[str, List[str]]:
        readme = self.repo_path / "README.md"
        if readme.exists():
            return readme.read_text(), ["README.md"]
        return "", []

    def _load_selective(self, question_type: str) -> tuple[str, List[str]]:
        """Load AGENTS.md + relevant .ai/ file"""
        content = ""
        files = []

        # Load AGENTS.md (router)
        agents = self.repo_path / "AGENTS.md"
        if agents.exists():
            content += agents.read_text() + "\n\n"
            files.append("AGENTS.md")

        # Map question type to relevant files
        file_mapping = {
            "IR": ["context.yaml"],
            "AU": ["architecture.yaml", "decisions.yaml"],
            "CW": ["workflows.yaml"],
            "ER": ["errors.yaml"],
        }

        ai_dir = self.repo_path / ".ai"
        for filename in file_mapping.get(question_type, ["context.yaml"]):
            filepath = ai_dir / filename
            if filepath.exists():
                content += f"# From .ai/{filename}\n\n"
                content += filepath.read_text() + "\n\n"
                files.append(f".ai/{filename}")

        return content, files


class AIProvider:
    """Abstract AI provider interface"""

    def __init__(self, model: str = None):
        self.model = model

    def query(self, context: str, question: str) -> dict:
        """Send query and return response with metrics"""
        raise NotImplementedError


class AnthropicProvider(AIProvider):
    """Claude via Anthropic API"""

    def __init__(self, model: str = None):
        super().__init__(model or DEFAULT_MODELS["anthropic"])
        self.client = anthropic.Anthropic()

    def query(self, context: str, question: str) -> dict:
        start = time.time()

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=f"You are answering questions about a codebase. Use ONLY the provided documentation to answer. Be concise.\n\n{context}",
            messages=[{"role": "user", "content": question}]
        )

        elapsed_ms = int((time.time() - start) * 1000)

        return {
            "answer": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "response_time_ms": elapsed_ms,
        }


class OpenAIProvider(AIProvider):
    """GPT via OpenAI API"""

    def __init__(self, model: str = None):
        super().__init__(model or DEFAULT_MODELS["openai"])
        self.client = openai.OpenAI()

    def query(self, context: str, question: str) -> dict:
        start = time.time()

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {"role": "system", "content": f"You are answering questions about a codebase. Use ONLY the provided documentation to answer. Be concise.\n\n{context}"},
                {"role": "user", "content": question}
            ]
        )

        elapsed_ms = int((time.time() - start) * 1000)

        return {
            "answer": response.choices[0].message.content,
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "response_time_ms": elapsed_ms,
        }


class OllamaProvider(AIProvider):
    """Local models via Ollama (free)"""

    def __init__(self, model: str = None):
        super().__init__(model or DEFAULT_MODELS["ollama"])

    def query(self, context: str, question: str) -> dict:
        start = time.time()

        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are answering questions about a codebase. Use ONLY the provided documentation to answer. Be concise.\n\n{context}"},
                {"role": "user", "content": question}
            ]
        )

        elapsed_ms = int((time.time() - start) * 1000)

        # Ollama doesn't always report tokens
        return {
            "answer": response["message"]["content"],
            "input_tokens": response.get("prompt_eval_count", 0),
            "output_tokens": response.get("eval_count", 0),
            "response_time_ms": elapsed_ms,
        }


def get_provider(name: str, model: str = None) -> AIProvider:
    """Factory for AI providers"""
    providers = {
        "anthropic": (HAS_ANTHROPIC, AnthropicProvider, "pip install anthropic"),
        "openai": (HAS_OPENAI, OpenAIProvider, "pip install openai"),
        "ollama": (HAS_OLLAMA, OllamaProvider, "pip install ollama"),
    }

    if name not in providers:
        raise ValueError(f"Unknown provider: {name}. Available: {list(providers.keys())}")

    available, cls, install_hint = providers[name]
    if not available:
        raise RuntimeError(f"Provider {name} not available. Install with: {install_hint}")

    return cls(model)


def estimate_cost(formats: List[str], trials: int, provider: str) -> dict:
    """Estimate API cost before running"""
    questions_per_format = len(TEST_QUESTIONS)
    total_calls = len(formats) * questions_per_format * trials

    # Rough estimates
    avg_input_tokens = 1500  # context + question
    avg_output_tokens = 200  # answer

    costs = COST_PER_1M_TOKENS.get(provider, {"input": 0, "output": 0})

    input_cost = (total_calls * avg_input_tokens / 1_000_000) * costs["input"]
    output_cost = (total_calls * avg_output_tokens / 1_000_000) * costs["output"]

    return {
        "total_api_calls": total_calls,
        "estimated_input_tokens": total_calls * avg_input_tokens,
        "estimated_output_tokens": total_calls * avg_output_tokens,
        "estimated_cost_usd": round(input_cost + output_cost, 4),
        "provider": provider,
        "note": "Actual costs may vary. Ollama is free (local)."
    }


def check_answer(answer: str, expected_keywords: List[str]) -> bool:
    """Check if answer contains expected keywords"""
    answer_lower = answer.lower()
    matches = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return matches >= len(expected_keywords) // 2  # At least half


def run_experiment(
    repo_path: Path,
    provider_name: str,
    model: str,
    formats: List[str],
    trials: int,
    output_file: Path
):
    """Run performance experiment"""

    loader = DocumentationLoader(repo_path)
    provider = get_provider(provider_name, model)
    results = []

    total = len(formats) * len(TEST_QUESTIONS) * trials
    current = 0

    print(f"Running {total} measurements with {provider_name}/{model}...")
    print(f"Formats: {formats}")
    print(f"Questions: {len(TEST_QUESTIONS)}")
    print(f"Trials: {trials}")
    print()

    for trial in range(trials):
        for fmt in formats:
            for q in TEST_QUESTIONS:
                current += 1
                print(f"[{current}/{total}] {fmt} | {q['id']}...", end=" ", flush=True)

                try:
                    # Load context
                    context, files = loader.load(fmt, q["id"])

                    # Query AI
                    response = provider.query(context, q["question"])

                    # Check answer
                    answer_found = check_answer(response["answer"], q["expected_keywords"])

                    result = PerformanceMeasurement(
                        format=fmt,
                        question_id=q["id"],
                        question=q["question"],
                        provider=provider_name,
                        model=model,
                        input_tokens=response["input_tokens"],
                        output_tokens=response["output_tokens"],
                        response_time_ms=response["response_time_ms"],
                        answer=response["answer"][:500],  # Truncate for storage
                        answer_found=answer_found,
                        files_loaded=files,
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                    )
                    results.append(result)

                    status = "✓" if answer_found else "✗"
                    print(f"{response['response_time_ms']}ms {status}")

                except Exception as e:
                    print(f"ERROR: {e}")

    # Save results
    data = {
        "metadata": {
            "provider": provider_name,
            "model": model,
            "repo_path": str(repo_path),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_measurements": len(results),
        },
        "summary": calculate_summary(results),
        "measurements": [asdict(r) for r in results]
    }

    output_file.write_text(json.dumps(data, indent=2))
    print(f"\nResults saved to: {output_file}")

    # Print summary
    print_summary(results)


def calculate_summary(results: List[PerformanceMeasurement]) -> dict:
    """Calculate summary statistics"""
    by_format = {}
    for r in results:
        if r.format not in by_format:
            by_format[r.format] = {"times": [], "accuracy": [], "tokens": []}
        by_format[r.format]["times"].append(r.response_time_ms)
        by_format[r.format]["accuracy"].append(1 if r.answer_found else 0)
        by_format[r.format]["tokens"].append(r.input_tokens + r.output_tokens)

    summary = {}
    for fmt, data in by_format.items():
        summary[fmt] = {
            "avg_response_time_ms": round(statistics.mean(data["times"]), 1),
            "accuracy_pct": round(statistics.mean(data["accuracy"]) * 100, 1),
            "avg_total_tokens": round(statistics.mean(data["tokens"]), 1),
            "samples": len(data["times"])
        }

    return summary


def print_summary(results: List[PerformanceMeasurement]):
    """Print formatted summary"""
    summary = calculate_summary(results)

    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)

    print(f"\n{'Format':<20} {'Response Time':>15} {'Accuracy':>12} {'Tokens':>10}")
    print("-" * 60)

    for fmt in ["README_ONLY", "AICAC_SELECTIVE"]:
        if fmt in summary:
            s = summary[fmt]
            print(f"{fmt:<20} {s['avg_response_time_ms']:>12.0f}ms {s['accuracy_pct']:>11.1f}% {s['avg_total_tokens']:>10.0f}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Measure AI response performance (costs money for cloud providers)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--repo-path", type=Path, default=Path("../../experiments/aicac-full"))
    parser.add_argument("--provider", choices=["anthropic", "openai", "ollama"], default="anthropic")
    parser.add_argument("--model", help="Model name (uses provider default if not specified)")
    parser.add_argument("--format", choices=["README_ONLY", "AICAC_SELECTIVE"])
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--output", type=Path, default=Path("performance_results.json"))
    parser.add_argument("--estimate-cost", action="store_true", help="Show cost estimate without running")

    args = parser.parse_args()

    formats = [args.format] if args.format else ["README_ONLY", "AICAC_SELECTIVE"]

    if args.estimate_cost:
        estimate = estimate_cost(formats, args.trials, args.provider)
        print("COST ESTIMATE")
        print("=" * 40)
        print(f"Provider:        {estimate['provider']}")
        print(f"API calls:       {estimate['total_api_calls']}")
        print(f"Est. input:      {estimate['estimated_input_tokens']:,} tokens")
        print(f"Est. output:     {estimate['estimated_output_tokens']:,} tokens")
        print(f"Est. cost:       ${estimate['estimated_cost_usd']:.4f}")
        print(f"\nNote: {estimate['note']}")
        return 0

    # Confirm before running (unless using free Ollama)
    if args.provider != "ollama":
        estimate = estimate_cost(formats, args.trials, args.provider)
        print(f"⚠️  This will make {estimate['total_api_calls']} API calls")
        print(f"   Estimated cost: ${estimate['estimated_cost_usd']:.4f}")
        print()
        response = input("Continue? [y/N] ")
        if response.lower() != "y":
            print("Aborted.")
            return 1

    run_experiment(
        repo_path=args.repo_path,
        provider_name=args.provider,
        model=args.model,
        formats=formats,
        trials=args.trials,
        output_file=args.output
    )

    return 0


if __name__ == "__main__":
    exit(main())
