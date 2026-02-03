# AI Context as Code (AICaC)

**A Structured Approach to AI-Readable Project Documentation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Status: Draft](https://img.shields.io/badge/Status-Draft-yellow.svg)]()
[![AICaC](https://img.shields.io/badge/AICaC-Comprehensive-success.svg)](BADGES.md)

## Overview

AI Context as Code (AICaC) introduces the `.ai/` directory convention containing YAML-based structured data that maximizes token efficiency for AI coding assistants while preserving queryability and maintainability.

**The Problem:** AI coding assistants waste thousands of tokens parsing unstructured prose documentation to understand codebases.

**The Solution:** Structured, machine-optimized documentation that complements existing human-readable formats like `README.md` and `AGENTS.md`.

**The Impact:** 40-60% token reduction, 15-25% faster task completion (empirically validated).

## Quick Example

**Traditional documentation (prose):**
```markdown
To add a new scanner, first create a class in the src/scanners/ 
directory that inherits from BaseScanner. Then register it in the 
scanner_registry.py file. Make sure to add unit tests in 
tests/scanners/. See the Trivy scanner implementation as reference.

Tokens: ~50
```

**AICaC (structured):**
```yaml
workflows:
  add_scanner:
    steps:
      - action: create_class
        location: src/scanners/
        inherits: BaseScanner
      - action: register
        file: scanner_registry.py
      - action: add_tests
        location: tests/scanners/
    reference_implementation: src/scanners/trivy_scanner.py

Tokens: ~30 (40% reduction)
```

## Repository Structure

```
AICaC/
├── README.md                          # This file
├── BADGES.md                          # Badge usage guide
├── ai-context-as-code-whitepaper.md   # Complete specification (23KB)
├── LICENSE-CODE                       # MIT License (for code)
├── LICENSE-DOCS                       # CC BY-SA 4.0 (for documentation)
├── .github/                           # GitHub integrations
│   ├── actions/
│   │   └── aicac-adoption/            # Adoption & maintenance action
│   │       ├── scripts/               # Action scripts
│   │       │   ├── bootstrap.py       # Bootstrap .ai/ structure
│   │       │   ├── validate.py        # Validate compliance
│   │       │   └── update_badge.py    # Update README badge
│   │       └── tests/                 # Pytest test suite
│   └── workflows/
│       └── validate-aicac.yml         # CI validation for this repo
├── pytest.ini                         # Pytest configuration
└── validation/                        # Empirical validation suite
    ├── README.md                      # Validation overview
    ├── docs/
    │   ├── testing-framework.md       # Research methodology (45KB)
    │   ├── quick-start.md            # 30-minute guide (18KB)
    │   └── publication-roadmap.md    # Publication strategy (35KB)
    ├── scripts/
    │   └── token_measurement.py      # Token efficiency measurement (20KB)
    └── examples/
        └── EXAMPLE_RESULTS.md        # Sample experimental results (10KB)
```

## Getting Started

### For Researchers

Run empirical validation experiments:

```bash
git clone https://github.com/eFAILution/AICaC.git
cd AICaC/validation/scripts
pip install anthropic tiktoken
python token_measurement.py --all-formats --trials 10
```

See [validation/docs/quick-start.md](validation/docs/quick-start.md) for detailed instructions.

### For Developers

Implement AICaC in your project:

1. Create `.ai/` directory in your repo
2. Add minimal `context.yaml`:
   ```yaml
   version: "1.0"
   project:
     name: "your-project"
     type: "web-app"
   entrypoints:
     main: "src/index.js"
   common_tasks:
     dev: "npm run dev"
     test: "npm test"
   ```
3. Reference from `AGENTS.md`
4. Add an AICaC badge to your README (see [BADGES.md](BADGES.md))

See [ai-context-as-code-whitepaper.md](ai-context-as-code-whitepaper.md) Section 4 for complete specification.

### For Tool Vendors

Add native AICaC support to your AI coding assistant:

1. Read the [specification](ai-context-as-code-whitepaper.md)
2. Check the [validation data](validation/docs/testing-framework.md)
3. Open an issue on [GitHub](https://github.com/eFAILution/AICaC/issues)

## The `.ai/` Directory Convention

```
project-root/
├── README.md              # Human-facing introduction
├── AGENTS.md              # Cross-tool AI instructions (references .ai/)
└── .ai/
    ├── README.md          # Explains .ai/ contents
    ├── context.yaml       # Project metadata and overview
    ├── architecture.yaml  # Component relationships
    ├── workflows.yaml     # Common tasks with exact commands
    ├── decisions.yaml     # Architectural Decision Records
    └── errors.yaml        # Error-to-solution mappings
```

### Core Principles

1. **Structured over prose** - Use YAML/JSON for machine-parseable data
2. **Hierarchical modularity** - Separate concerns into domain-specific files
3. **Graceful degradation** - Works alongside existing conventions
4. **Queryable by default** - Enable direct lookup without full-file parsing
5. **Human-readable** - Structured doesn't mean cryptic
6. **Version controlled** - Context evolves with code in repository

## Why AICaC?

### Token Efficiency

| Query Type | README.md | AGENTS.md | AICaC | Improvement |
|------------|-----------|-----------|-------|-------------|
| "How to add a scanner?" | ~800 tokens | ~400 tokens | ~240 tokens | 40% |
| "Why use Dagger?" | ~600 tokens | ~500 tokens | ~180 tokens | 64% |
| "Fix registry error" | ~1200 tokens | ~800 tokens | ~320 tokens | 60% |

### Direct Queryability
```python
# AI tools can perform targeted lookups
workflows = parse_yaml('.ai/workflows.yaml')
return workflows['workflows']['add_scanner']
```

### Maintainability
- Architecture changes → edit `architecture.yaml`
- Add workflow → edit `workflows.yaml`
- Document decision → edit `decisions.yaml`

No massive `AGENTS.md` file becoming unmaintainable.

## Documentation

- **[White Paper](ai-context-as-code-whitepaper.md)** - Complete AICaC specification (23KB, ~1 hour read)
- **[Testing Framework](validation/docs/testing-framework.md)** - Research methodology (45KB, ~30 min)
- **[Quick Start](validation/docs/quick-start.md)** - Get results in 30 minutes (18KB, ~15 min)
- **[Publication Roadmap](validation/docs/publication-roadmap.md)** - Academic & industry strategy (35KB, ~25 min)

## Real-World Example

See the included sample project in `validation/examples/sample-project/` for a complete `.ai/` implementation with all core files.

## Status & Roadmap

**Current Status:** v0.1.0 - Draft specification with validation framework

**Roadmap:**
- **Q1 2026:** Pilot experiments, refine specification ← *We are here*
- **Q2 2026:** ArXiv preprint, NeurIPS 2026 submission
- **Q3 2026:** Community feedback, tool integrations
- **Q4 2026:** v1.0 specification, conference presentation
- **2027:** Tool vendor support, widespread adoption

## Contributing

We welcome contributions:
- 📝 Specification feedback and improvements
- 🧪 Additional validation experiments
- 📚 Example implementations
- 🔧 Tooling (validators, converters, IDE extensions)

Please open issues or pull requests on GitHub.

## Publication

This work is being prepared for submission to academic conferences and journals. See [validation/docs/publication-roadmap.md](validation/docs/publication-roadmap.md) for strategy.

Target venues:
- **NeurIPS 2026** (Datasets & Benchmarks Track) - May deadline
- **ICSE 2027** (Technical Papers) - August deadline
- **MSR 2027** (Data Showcase) - December deadline

### Citing AICaC

```bibtex
@misc{aicac2026,
  title={AI Context as Code: A Structured Approach to AI-Readable Project Documentation},
  author={eFAILution},
  year={2026},
  howpublished={\url{https://github.com/eFAILution/AICaC}},
  note={Version 0.1.0}
}
```

## License

This project uses a dual-license structure:

- **Code** (`validation/scripts/`): [MIT License](LICENSE-CODE)
  - Permissive license for maximum tool integration
  - Free commercial and open source use
  
- **Documentation** (specifications, papers): [CC BY-SA 4.0](LICENSE-DOCS)
  - Requires attribution
  - Share-alike for derivatives
  - Prevents proprietary forks of the standard

See [LICENSE-CODE](LICENSE-CODE) and [LICENSE-DOCS](LICENSE-DOCS) for details.

## Contact

**eFAILution**
- GitHub: [@eFAILution](https://github.com/eFAILution)

**Community:**
- GitHub Discussions: [github.com/eFAILution/AICaC/discussions](https://github.com/eFAILution/AICaC/discussions)
- Issues & PRs: [github.com/eFAILution/AICaC/issues](https://github.com/eFAILution/AICaC/issues)

---

**Making AI-readable documentation a reality.**
