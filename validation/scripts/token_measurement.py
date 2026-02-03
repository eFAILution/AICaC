#!/usr/bin/env python3
"""
AICaC Token Efficiency Measurement

Measures token consumption across different documentation formats with
two key metrics:

1. TOTAL CONTEXT (Reality): What AI tools load today out-of-the-box
   - More files = more tokens
   - AICaC adds .ai/ files, so initially MORE tokens than README alone

2. SELECTIVE LOADING (Potential): If tools could load only relevant files
   - Query-specific file selection
   - Shows the opportunity if AI tools evolve

This script is intentionally transparent about both metrics to avoid
misleading claims about AICaC benefits.

Usage:
    python token_measurement.py --all-formats --output results.json
    python token_measurement.py --all-formats --trials 30
"""

import argparse
import json
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional
import statistics

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False
    print("Warning: tiktoken not installed. Install with: pip install tiktoken")

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


@dataclass
class TokenMeasurement:
    """Single measurement result"""
    format: str
    question_id: str
    question: str
    model: str
    token_count: int
    context_length: int
    files_loaded: List[str]
    timestamp: str
    # New fields for transparency
    measurement_type: str = "total_context"  # "total_context" or "selective"
    notes: str = ""


@dataclass
class FormatAnalysis:
    """Analysis for a single format"""
    format: str
    total_tokens_mean: float
    total_tokens_median: float
    selective_tokens_mean: Optional[float] = None
    selective_tokens_median: Optional[float] = None
    file_count: int = 0
    notes: str = ""


# Map question types to relevant .ai/ files
QUESTION_FILE_MAPPING = {
    "IR": ["context.yaml"],  # Information retrieval - project overview
    "AU": ["architecture.yaml", "decisions.yaml"],  # Architecture understanding
    "CW": ["workflows.yaml", "errors.yaml"],  # Common workflows
}


class DocumentationLoader:
    """Loads documentation in different formats"""

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)

    def load_readme_only(self) -> tuple[str, List[str]]:
        """Load only README.md"""
        readme = self.repo_path / "README.md"
        if not readme.exists():
            raise FileNotFoundError(f"README.md not found at {readme}")
        return readme.read_text(), ["README.md"]

    def load_agents_only(self) -> tuple[str, List[str]]:
        """Load README.md + AGENTS.md"""
        files = []
        content = ""

        readme = self.repo_path / "README.md"
        if readme.exists():
            content += readme.read_text() + "\n\n"
            files.append("README.md")

        agents = self.repo_path / "AGENTS.md"
        if agents.exists():
            content += agents.read_text()
            files.append("AGENTS.md")

        return content, files

    def load_aicac_full(self) -> tuple[str, List[str]]:
        """
        Load ALL documentation (README + AGENTS + all .ai/ files)

        This represents the REALITY of how current AI tools work:
        they load everything they find.
        """
        files = []
        content = ""

        # Load README
        readme = self.repo_path / "README.md"
        if readme.exists():
            content += readme.read_text() + "\n\n"
            files.append("README.md")

        # Load AGENTS.md
        agents = self.repo_path / "AGENTS.md"
        if agents.exists():
            content += agents.read_text() + "\n\n"
            files.append("AGENTS.md")

        # Load ALL .ai/ files
        ai_dir = self.repo_path / ".ai"
        if ai_dir.exists():
            for filepath in sorted(ai_dir.glob("*.yaml")):
                content += f"\n# From .ai/{filepath.name}\n\n"
                content += filepath.read_text() + "\n"
                files.append(f".ai/{filepath.name}")

            # Also load .ai/README.md if exists
            ai_readme = ai_dir / "README.md"
            if ai_readme.exists():
                content += f"\n# From .ai/README.md\n\n"
                content += ai_readme.read_text()
                files.append(".ai/README.md")

        return content, files

    def load_aicac_selective(self, question_type: str) -> tuple[str, List[str]]:
        """
        Load AGENTS.md (router) + only the relevant .ai/ file(s).

        This simulates an AI tool that FOLLOWS the AGENTS.md guidance
        to load only relevant context. This works TODAY if AI tools
        actually follow the instructions in AGENTS.md.
        """
        files = []
        content = ""

        # Load AGENTS.md first (the router)
        agents = self.repo_path / "AGENTS.md"
        if agents.exists():
            content += agents.read_text() + "\n\n"
            files.append("AGENTS.md")

        # Load only relevant .ai/ files based on query type
        relevant_files = QUESTION_FILE_MAPPING.get(question_type, ["context.yaml"])

        ai_dir = self.repo_path / ".ai"
        if ai_dir.exists():
            for filename in relevant_files:
                filepath = ai_dir / filename
                if filepath.exists():
                    content += f"# From .ai/{filename}\n\n"
                    content += filepath.read_text() + "\n\n"
                    files.append(f".ai/{filename}")

        return content, files


class TokenCounter:
    """Counts tokens using different tokenizers"""

    def __init__(self):
        self.counters = {}

        if HAS_TIKTOKEN:
            self.counters["gpt4"] = self._count_gpt4

        if HAS_ANTHROPIC:
            self.counters["claude"] = self._count_claude

    def _count_gpt4(self, text: str) -> int:
        enc = tiktoken.encoding_for_model("gpt-4")
        return len(enc.encode(text))

    def _count_claude(self, text: str) -> int:
        client = anthropic.Anthropic()
        return client.count_tokens(text)

    def count(self, text: str, model: str) -> int:
        if model not in self.counters:
            available = list(self.counters.keys())
            raise ValueError(f"Model {model} not available. Available: {available}")
        return self.counters[model](text)


# Test questions organized by category
TEST_QUESTIONS = {
    "information_retrieval": [
        {"id": "IR-001", "question": "What command runs the development server?"},
        {"id": "IR-002", "question": "What is the project's primary purpose?"},
        {"id": "IR-003", "question": "What Python version is required?"},
        {"id": "IR-004", "question": "What are the main dependencies?"},
        {"id": "IR-005", "question": "Where is the main entry point?"},
    ],
    "architectural_understanding": [
        {"id": "AU-001", "question": "Explain the data flow for creating a task"},
        {"id": "AU-002", "question": "What are the dependencies between components?"},
        {"id": "AU-003", "question": "Why was FastAPI chosen over Flask?"},
        {"id": "AU-004", "question": "Describe the service layer architecture"},
        {"id": "AU-005", "question": "How do the API routes communicate with services?"},
    ],
    "common_workflows": [
        {"id": "CW-001", "question": "How do I add a new API endpoint?"},
        {"id": "CW-002", "question": "How do I fix a 'port already in use' error?"},
        {"id": "CW-003", "question": "How do I set up the development environment?"},
        {"id": "CW-004", "question": "How do I run the tests?"},
        {"id": "CW-005", "question": "How do I add a new database model?"},
    ]
}


class TokenExperiment:
    """Runs token measurement experiments with full transparency"""

    def __init__(self, repo_path: Path, output_file: Optional[Path] = None):
        self.repo_path = repo_path
        self.output_file = output_file or Path("token_results.json")
        self.loader = DocumentationLoader(repo_path)
        self.counter = TokenCounter()
        self.results: List[TokenMeasurement] = []

    def run_measurement(
        self,
        format: str,
        question: Dict[str, str],
        model: str,
        measurement_type: str = "total_context"
    ) -> TokenMeasurement:
        """Run single measurement"""

        question_type = question["id"].split("-")[0]

        # Load documentation based on format
        if format == "README_ONLY":
            content, files = self.loader.load_readme_only()
            notes = "Single file, minimal context"
        elif format == "AGENTS_ONLY":
            content, files = self.loader.load_agents_only()
            notes = "README + AGENTS.md"
        elif format == "AICAC":
            content, files = self.loader.load_aicac_full()
            notes = "All documentation loaded (current AI tool behavior)"
        elif format == "AICAC_SELECTIVE":
            content, files = self.loader.load_aicac_selective(question_type)
            notes = f"AGENTS.md + relevant .ai/ file for {question_type} (works if AI follows guidance)"
            measurement_type = "selective"
        else:
            raise ValueError(f"Unknown format: {format}")

        token_count = self.counter.count(content, model)

        return TokenMeasurement(
            format=format,
            question_id=question["id"],
            question=question["question"],
            model=model,
            token_count=token_count,
            context_length=len(content),
            files_loaded=files,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            measurement_type=measurement_type,
            notes=notes
        )

    def run_experiment(
        self,
        formats: List[str],
        categories: Optional[List[str]] = None,
        models: Optional[List[str]] = None,
        trials: int = 1
    ):
        """Run full experiment"""

        if models is None:
            models = list(self.counter.counters.keys())

        if not models:
            raise RuntimeError("No tokenizer available. Install tiktoken: pip install tiktoken")

        if categories is None:
            categories = list(TEST_QUESTIONS.keys())

        questions = []
        for category in categories:
            if category in TEST_QUESTIONS:
                questions.extend(TEST_QUESTIONS[category])

        total = len(formats) * len(questions) * len(models) * trials
        current = 0

        print(f"Running {total} measurements...")
        print(f"Formats: {formats}")
        print(f"Models: {models}")
        print(f"Questions: {len(questions)}")
        print(f"Trials: {trials}")
        print()

        for trial in range(trials):
            for fmt in formats:
                for question in questions:
                    for model in models:
                        current += 1
                        try:
                            measurement = self.run_measurement(fmt, question, model)
                            self.results.append(measurement)
                            print(f"[{current}/{total}] {fmt:18} | {question['id']} | {measurement.token_count:,} tokens")
                        except Exception as e:
                            print(f"[{current}/{total}] {fmt:18} | {question['id']} | ERROR: {e}")

        print(f"\nComplete! {len(self.results)} measurements collected.")

    def save_results(self):
        """Save results with full context"""

        # Calculate summary statistics
        summary = self._calculate_summary()

        data = {
            "metadata": {
                "repo_path": str(self.repo_path),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_measurements": len(self.results),
                "methodology_notes": [
                    "TOTAL CONTEXT = What AI tools load when they read all files (reality)",
                    "SELECTIVE = AGENTS.md + relevant .ai/ file only (works if AI follows guidance)",
                    "AICaC adds files, so TOTAL context is HIGHER than README alone",
                    "SELECTIVE can be LOWER if AI tools follow AGENTS.md routing instructions",
                    "Key insight: AGENTS.md can act as a router to guide selective loading"
                ]
            },
            "summary": summary,
            "measurements": [asdict(m) for m in self.results]
        }

        self.output_file.write_text(json.dumps(data, indent=2))
        print(f"\nResults saved to: {self.output_file}")

    def _calculate_summary(self) -> Dict:
        """Calculate summary with honest analysis"""

        by_format = {}
        for r in self.results:
            if r.format not in by_format:
                by_format[r.format] = []
            by_format[r.format].append(r.token_count)

        summary = {"formats": {}, "key_findings": []}

        readme_mean = None
        for fmt, tokens in by_format.items():
            mean = statistics.mean(tokens)
            median = statistics.median(tokens)

            if fmt == "README_ONLY":
                readme_mean = mean

            summary["formats"][fmt] = {
                "mean_tokens": round(mean, 1),
                "median_tokens": round(median, 1),
                "sample_count": len(tokens)
            }

            if readme_mean and fmt != "README_ONLY":
                change = ((mean - readme_mean) / readme_mean) * 100
                summary["formats"][fmt]["vs_readme_pct"] = round(change, 1)

        # Add honest key findings
        if "AICAC" in by_format and readme_mean:
            aicac_mean = statistics.mean(by_format["AICAC"])
            if aicac_mean > readme_mean:
                summary["key_findings"].append(
                    f"AICAC uses {((aicac_mean - readme_mean) / readme_mean * 100):.0f}% MORE tokens than README alone"
                )
                summary["key_findings"].append(
                    "This is expected: more files = more tokens for current AI tools"
                )

        if "AICAC_SELECTIVE" in by_format and readme_mean:
            selective_mean = statistics.mean(by_format["AICAC_SELECTIVE"])
            if selective_mean < readme_mean:
                summary["key_findings"].append(
                    f"SELECTIVE loading uses {((readme_mean - selective_mean) / readme_mean * 100):.0f}% fewer tokens"
                )
                summary["key_findings"].append(
                    "But this requires AI tools to evolve - not available today"
                )

        return summary

    def analyze_results(self):
        """Print transparent analysis"""

        if not self.results:
            print("No results to analyze")
            return

        print("\n" + "=" * 70)
        print("ANALYSIS SUMMARY")
        print("=" * 70)

        print("\n⚠️  IMPORTANT CONTEXT:")
        print("-" * 70)
        print("• TOTAL CONTEXT = What AI tools actually load today (reality)")
        print("• SELECTIVE = What's possible IF tools evolve (aspirational)")
        print("• Current AI tools load ALL documentation they find")
        print("• AICaC adds .ai/ files, so MORE tokens out-of-the-box")

        # Group by format
        by_format = {}
        for r in self.results:
            if r.format not in by_format:
                by_format[r.format] = {"tokens": [], "files": set()}
            by_format[r.format]["tokens"].append(r.token_count)
            by_format[r.format]["files"].update(r.files_loaded)

        print("\n\nTOKEN CONSUMPTION BY FORMAT:")
        print("-" * 70)

        readme_mean = None
        for fmt in ["README_ONLY", "AGENTS_ONLY", "AICAC", "AICAC_SELECTIVE"]:
            if fmt not in by_format:
                continue

            data = by_format[fmt]
            tokens = data["tokens"]
            mean = statistics.mean(tokens)
            median = statistics.median(tokens)
            files = sorted(data["files"])

            if fmt == "README_ONLY":
                readme_mean = mean

            print(f"\n{fmt}:")
            print(f"  Files loaded: {', '.join(files)}")
            print(f"  Mean tokens:  {mean:,.0f}")
            print(f"  Median:       {median:,.0f}")

            if readme_mean and fmt != "README_ONLY":
                change = ((mean - readme_mean) / readme_mean) * 100
                direction = "MORE" if change > 0 else "FEWER"
                print(f"  vs README:    {abs(change):.1f}% {direction} tokens")

        print("\n\nKEY TAKEAWAYS:")
        print("-" * 70)

        if "AICAC" in by_format and readme_mean:
            aicac_mean = statistics.mean(by_format["AICAC"]["tokens"])
            if aicac_mean > readme_mean:
                print("❌ OUT-OF-THE-BOX: AICaC uses MORE tokens than README alone")
                print("   → Current AI tools load all .ai/ files regardless of query")
                print("   → This is the honest reality today")

        if "AICAC_SELECTIVE" in by_format and readme_mean:
            selective_mean = statistics.mean(by_format["AICAC_SELECTIVE"]["tokens"])
            if selective_mean < readme_mean:
                print(f"\n✅ WITH AGENTS.MD GUIDANCE: Selective loading uses {((readme_mean - selective_mean) / readme_mean * 100):.0f}% fewer tokens")
                print("   → Works TODAY if AI tools follow AGENTS.md routing instructions")
                print("   → AGENTS.md tells AI which .ai/ file to load per query type")
            elif selective_mean < statistics.mean(by_format.get("AICAC", {}).get("tokens", [selective_mean])):
                aicac_mean = statistics.mean(by_format["AICAC"]["tokens"])
                print(f"\n⚡ WITH AGENTS.MD GUIDANCE: {((aicac_mean - selective_mean) / aicac_mean * 100):.0f}% fewer tokens than loading all .ai/ files")
                print("   → AGENTS.md acts as a router for selective context loading")

        print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Measure token efficiency with full transparency",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all-formats                    # Test all formats
  %(prog)s --all-formats --trials 30        # 30 trials for statistics
  %(prog)s --format README_ONLY             # Single format
  %(prog)s --include-selective              # Include aspirational selective mode
        """
    )
    parser.add_argument("--repo-path", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=["README_ONLY", "AGENTS_ONLY", "AICAC", "AICAC_SELECTIVE"])
    parser.add_argument("--all-formats", action="store_true", help="Test README, AGENTS, and AICAC")
    parser.add_argument("--include-selective", action="store_true", help="Also test AICAC_SELECTIVE (aspirational)")
    parser.add_argument("--model", choices=["gpt4", "claude"])
    parser.add_argument("--category", choices=list(TEST_QUESTIONS.keys()))
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--output", type=Path, default=Path("token_results.json"))

    args = parser.parse_args()

    # Determine formats
    if args.all_formats:
        formats = ["README_ONLY", "AGENTS_ONLY", "AICAC"]
        if args.include_selective:
            formats.append("AICAC_SELECTIVE")
    elif args.format:
        formats = [args.format]
    else:
        print("Error: Specify --format or --all-formats")
        return 1

    models = [args.model] if args.model else None
    categories = [args.category] if args.category else None

    experiment = TokenExperiment(args.repo_path, args.output)

    try:
        experiment.run_experiment(
            formats=formats,
            categories=categories,
            models=models,
            trials=args.trials
        )
        experiment.analyze_results()
        experiment.save_results()
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
