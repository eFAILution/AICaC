#!/usr/bin/env python3
"""
AICaC Token Efficiency Measurement - Phase 1 Pilot
Measures token consumption across different documentation formats

Usage:
    python token_measurement.py --format AICAC --output results.json
    python token_measurement.py --all-formats --trials 30
"""

import argparse
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional
import statistics

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False
    print("Warning: tiktoken not installed. GPT-4 token counting unavailable.")

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("Warning: anthropic not installed. Claude token counting unavailable.")


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


class DocumentationLoader:
    """Loads documentation in different formats"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self.format_loaders = {
            "README_ONLY": self._load_readme_only,
            "AGENTS_ONLY": self._load_agents_only,
            "AICAC": self._load_aicac
        }
    
    def _load_readme_only(self) -> tuple[str, List[str]]:
        """Load only README.md"""
        readme = self.repo_path / "README.md"
        if not readme.exists():
            raise FileNotFoundError(f"README.md not found at {readme}")
        
        content = readme.read_text()
        return content, ["README.md"]
    
    def _load_agents_only(self) -> tuple[str, List[str]]:
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
        else:
            print("Warning: AGENTS.md not found, using README only")
        
        return content, files
    
    def _load_aicac(self, question: Optional[str] = None) -> tuple[str, List[str]]:
        """Load README.md + AGENTS.md + relevant .ai/ files"""
        files = []
        content = ""
        
        # Always include README and AGENTS
        readme = self.repo_path / "README.md"
        if readme.exists():
            content += readme.read_text() + "\n\n"
            files.append("README.md")
        
        agents = self.repo_path / "AGENTS.md"
        if agents.exists():
            content += agents.read_text() + "\n\n"
            files.append("AGENTS.md")
        
        # Load .ai/ directory
        ai_dir = self.repo_path / ".ai"
        if not ai_dir.exists():
            print(f"Warning: .ai/ directory not found at {ai_dir}")
            return content, files
        
        # Determine which .ai/ files to load based on question
        ai_files = self._select_ai_files(question)
        
        for filename in ai_files:
            filepath = ai_dir / filename
            if filepath.exists():
                content += f"\n\n# From .ai/{filename}\n\n"
                content += filepath.read_text()
                files.append(f".ai/{filename}")
        
        return content, files
    
    def _select_ai_files(self, question: Optional[str]) -> List[str]:
        """Select relevant .ai/ files based on question keywords"""
        # Smart selection based on question content
        # For now, load all core files. Could optimize with keyword matching.
        
        core_files = [
            "context.yaml",
            "architecture.yaml", 
            "workflows.yaml",
            "decisions.yaml",
            "errors.yaml"
        ]
        
        # If question contains specific keywords, prioritize certain files
        if question:
            question_lower = question.lower()
            
            # Prioritize based on keywords
            if any(word in question_lower for word in ["workflow", "command", "run", "execute", "how to"]):
                core_files.insert(0, core_files.pop(core_files.index("workflows.yaml")))
            
            if any(word in question_lower for word in ["error", "fix", "debug", "problem", "issue"]):
                core_files.insert(0, core_files.pop(core_files.index("errors.yaml")))
            
            if any(word in question_lower for word in ["why", "decision", "chose", "reason"]):
                core_files.insert(0, core_files.pop(core_files.index("decisions.yaml")))
            
            if any(word in question_lower for word in ["architecture", "component", "flow", "dependency"]):
                core_files.insert(0, core_files.pop(core_files.index("architecture.yaml")))
        
        return core_files
    
    def load(self, format: str, question: Optional[str] = None) -> tuple[str, List[str]]:
        """Load documentation in specified format"""
        if format not in self.format_loaders:
            raise ValueError(f"Unknown format: {format}")
        
        if format == "AICAC":
            return self._load_aicac(question)
        else:
            return self.format_loaders[format]()


class TokenCounter:
    """Counts tokens using different tokenizers"""
    
    def __init__(self):
        self.counters = {}
        
        if HAS_TIKTOKEN:
            self.counters["gpt4"] = self._count_gpt4
        
        if HAS_ANTHROPIC:
            self.counters["claude"] = self._count_claude
    
    def _count_gpt4(self, text: str) -> int:
        """Count tokens using GPT-4 tokenizer"""
        enc = tiktoken.encoding_for_model("gpt-4")
        return len(enc.encode(text))
    
    def _count_claude(self, text: str) -> int:
        """Count tokens using Claude tokenizer"""
        client = anthropic.Anthropic()
        return client.count_tokens(text)
    
    def count(self, text: str, model: str) -> int:
        """Count tokens for specified model"""
        if model not in self.counters:
            available = list(self.counters.keys())
            raise ValueError(
                f"Model {model} not available. "
                f"Available models: {available}"
            )
        
        return self.counters[model](text)


# Test questions organized by category
TEST_QUESTIONS = {
    "information_retrieval": [
        {
            "id": "IR-001",
            "question": "What command runs a local security scan?"
        },
        {
            "id": "IR-002", 
            "question": "Which scanners are available in this project?"
        },
        {
            "id": "IR-003",
            "question": "What is the project's primary purpose?"
        },
        {
            "id": "IR-004",
            "question": "Where is the scanner registry located?"
        },
        {
            "id": "IR-005",
            "question": "What Python version is required?"
        }
    ],
    "architectural_understanding": [
        {
            "id": "AU-001",
            "question": "Explain the data flow from user input to report generation"
        },
        {
            "id": "AU-002",
            "question": "What are the dependencies between scanner-orchestrator and report-generator?"
        },
        {
            "id": "AU-003",
            "question": "Why was Dagger chosen over GitHub Actions nested workflows?"
        },
        {
            "id": "AU-004",
            "question": "Describe the plugin architecture for compliance checks"
        },
        {
            "id": "AU-005",
            "question": "How do scanners communicate their results?"
        }
    ],
    "common_workflows": [
        {
            "id": "CW-001",
            "question": "How do I add a new scanner integration?"
        },
        {
            "id": "CW-002",
            "question": "How do I fix the 'token doesn't have packages:write' error?"
        },
        {
            "id": "CW-003",
            "question": "How do I set up local development environment?"
        },
        {
            "id": "CW-004",
            "question": "How do I add a new compliance plugin?"
        },
        {
            "id": "CW-005",
            "question": "How do I fix 'registry tag already exists' error?"
        }
    ]
}


class TokenExperiment:
    """Runs token measurement experiments"""
    
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
        model: str
    ) -> TokenMeasurement:
        """Run single measurement"""
        
        # Load documentation
        content, files_loaded = self.loader.load(format, question["question"])
        
        # Count tokens
        token_count = self.counter.count(content, model)
        
        # Create measurement
        measurement = TokenMeasurement(
            format=format,
            question_id=question["id"],
            question=question["question"],
            model=model,
            token_count=token_count,
            context_length=len(content),
            files_loaded=files_loaded,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.results.append(measurement)
        return measurement
    
    def run_experiment(
        self,
        formats: List[str],
        categories: Optional[List[str]] = None,
        models: Optional[List[str]] = None,
        trials: int = 1
    ):
        """Run full experiment across formats, questions, and models"""
        
        if models is None:
            models = list(self.counter.counters.keys())
        
        if not models:
            raise RuntimeError("No tokenizer models available. Install tiktoken or anthropic.")
        
        if categories is None:
            categories = list(TEST_QUESTIONS.keys())
        
        # Collect all questions from specified categories
        questions = []
        for category in categories:
            if category in TEST_QUESTIONS:
                questions.extend(TEST_QUESTIONS[category])
        
        total_measurements = len(formats) * len(questions) * len(models) * trials
        current = 0
        
        print(f"Running {total_measurements} measurements...")
        print(f"Formats: {formats}")
        print(f"Models: {models}")
        print(f"Questions: {len(questions)}")
        print(f"Trials: {trials}")
        print()
        
        for trial in range(trials):
            for format in formats:
                for question in questions:
                    for model in models:
                        current += 1
                        print(f"[{current}/{total_measurements}] {format} | {model} | {question['id']}")
                        
                        try:
                            measurement = self.run_measurement(format, question, model)
                            print(f"  → {measurement.token_count:,} tokens")
                        except Exception as e:
                            print(f"  → ERROR: {e}")
                        
        print(f"\nExperiment complete! {len(self.results)} measurements collected.")
    
    def save_results(self):
        """Save results to JSON"""
        data = {
            "metadata": {
                "repo_path": str(self.repo_path),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_measurements": len(self.results)
            },
            "measurements": [asdict(m) for m in self.results]
        }
        
        self.output_file.write_text(json.dumps(data, indent=2))
        print(f"\nResults saved to: {self.output_file}")
    
    def analyze_results(self):
        """Generate summary statistics"""
        if not self.results:
            print("No results to analyze")
            return
        
        print("\n" + "="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)
        
        # Group by format
        by_format = {}
        for result in self.results:
            if result.format not in by_format:
                by_format[result.format] = []
            by_format[result.format].append(result.token_count)
        
        # Calculate statistics
        print("\nToken Consumption by Format:")
        print("-" * 60)
        
        baseline_mean = None
        for format in sorted(by_format.keys()):
            tokens = by_format[format]
            mean = statistics.mean(tokens)
            median = statistics.median(tokens)
            stdev = statistics.stdev(tokens) if len(tokens) > 1 else 0
            
            if format == "README_ONLY":
                baseline_mean = mean
            
            reduction = ""
            if baseline_mean and format != "README_ONLY":
                pct = ((baseline_mean - mean) / baseline_mean) * 100
                reduction = f" ({pct:+.1f}% vs README)"
            
            print(f"\n{format}:")
            print(f"  Mean:   {mean:>10,.1f} tokens{reduction}")
            print(f"  Median: {median:>10,.1f} tokens")
            print(f"  StdDev: {stdev:>10,.1f} tokens")
            print(f"  Samples: {len(tokens)}")
        
        # Group by question category
        print("\n\nToken Consumption by Question Category:")
        print("-" * 60)
        
        by_category = {}
        for result in self.results:
            category = result.question_id.split("-")[0]
            if category not in by_category:
                by_category[category] = {}
            
            if result.format not in by_category[category]:
                by_category[category][result.format] = []
            
            by_category[category][result.format].append(result.token_count)
        
        for category in sorted(by_category.keys()):
            print(f"\n{category}:")
            for format in sorted(by_category[category].keys()):
                tokens = by_category[category][format]
                mean = statistics.mean(tokens)
                print(f"  {format:15s} {mean:>10,.1f} tokens")


def main():
    parser = argparse.ArgumentParser(
        description="Measure token efficiency across documentation formats"
    )
    parser.add_argument(
        "--repo-path",
        type=Path,
        default=Path.cwd(),
        help="Path to repository (default: current directory)"
    )
    parser.add_argument(
        "--format",
        choices=["README_ONLY", "AGENTS_ONLY", "AICAC"],
        help="Single format to test"
    )
    parser.add_argument(
        "--all-formats",
        action="store_true",
        help="Test all formats"
    )
    parser.add_argument(
        "--model",
        choices=["gpt4", "claude"],
        help="Tokenizer model to use"
    )
    parser.add_argument(
        "--category",
        choices=list(TEST_QUESTIONS.keys()),
        help="Question category to test"
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=1,
        help="Number of trials per measurement"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("token_results.json"),
        help="Output file for results"
    )
    
    args = parser.parse_args()
    
    # Determine formats to test
    if args.all_formats:
        formats = ["README_ONLY", "AGENTS_ONLY", "AICAC"]
    elif args.format:
        formats = [args.format]
    else:
        print("Error: Specify --format or --all-formats")
        return 1
    
    # Determine models to test
    models = [args.model] if args.model else None
    
    # Determine categories
    categories = [args.category] if args.category else None
    
    # Run experiment
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
