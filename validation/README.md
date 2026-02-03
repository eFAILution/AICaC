# AICaC Validation Suite

This directory contains all materials for empirically validating the AI Context as Code (AICaC) specification.

## Quick Start

```bash
cd scripts
pip install anthropic tiktoken
python token_measurement.py --all-formats --trials 10
```

## Directory Structure

```
validation/
├── README.md                      # This file
├── docs/                          # Documentation
│   ├── testing-framework.md       # Comprehensive testing methodology
│   ├── quick-start.md            # Get started in 30 minutes
│   └── publication-roadmap.md    # Academic & industry publication strategy
├── scripts/                       # Executable code
│   └── token_measurement.py      # Token efficiency measurement tool
└── examples/                      # Example outputs and test data
    └── EXAMPLE_RESULTS.md        # Sample experimental results
```

## Documentation Overview

### 📊 [Testing Framework](docs/testing-framework.md)
Comprehensive experimental design inspired by NeurIPS 2025 research:
- 3 measurement dimensions (token efficiency, task performance, quality)
- 5 task categories (information retrieval → greenfield implementation)
- Statistical rigor (30+ trials, significance testing, effect sizes)
- 4 validation phases

**Expected outcomes:**
- 40-60% token reduction vs prose documentation
- 15-25% improvement in task success rate
- Publishable results with p < 0.05 significance

### 🚀 [Quick Start Guide](docs/quick-start.md)
Get experimental results in 30 minutes:
- Setup instructions
- Running experiments
- Analyzing results
- Budget-friendly tips
- Troubleshooting

### 🎓 [Publication Roadmap](docs/publication-roadmap.md)
18-month strategy for academic and industry publication:
- **Academic:** NeurIPS 2026, ICSE 2027, MSR 2027
- **Preprints:** ArXiv, Papers with Code
- **Industry:** ACM Queue, IEEE Software, InfoQ
- **Budget:** $10k-17k (with cost reduction strategies)

## Key Findings (Expected)

Based on preliminary analysis and hypothesis:

| Metric | README Only | AGENTS.md | AICaC | Improvement |
|--------|-------------|-----------|-------|-------------|
| Tokens (Info Retrieval) | ~800 | ~400 | ~240 | 40% |
| Tokens (Architecture) | ~600 | ~500 | ~180 | 64% |
| Task Success Rate | Baseline | +10% | +25% | 2.5x |
| Completion Time | Baseline | -5% | -20% | 4x faster |

## Timeline

- **Week 1:** Pilot experiments (validate approach)
- **Week 2-3:** Full experiments (30 trials × all formats)
- **Week 4:** Statistical analysis & write-up
- **Month 2:** ArXiv preprint publication
- **Month 3:** NeurIPS 2026 submission (May deadline)
- **Month 6:** Real-world validation
- **Month 12:** Conference presentation

## Success Criteria

### Minimum Viable Evidence
- ✅ ≥30% token reduction (statistically significant)
- ✅ ≥15% task success improvement
- ✅ p-value < 0.05
- ✅ Cohen's d > 0.5 (medium effect)

### Strong Evidence (Ideal)
- 🎯 50%+ token reduction
- 🎯 25%+ task improvement
- 🎯 p < 0.01 (highly significant)
- 🎯 Cohen's d > 0.8 (large effect)

## Running Experiments

### Install Dependencies

```bash
pip install anthropic tiktoken pandas scipy matplotlib
```

### Token Efficiency Measurement

```bash
# Quick test
python scripts/token_measurement.py --format AICAC --trials 10

# Full experiment
python scripts/token_measurement.py --all-formats --trials 30 --output results.json
```

### Expected Output

```
Running 450 measurements...
Formats: ['README_ONLY', 'AGENTS_ONLY', 'AICAC']
Models: ['gpt4']
Questions: 15
Trials: 30

[1/450] README_ONLY | gpt4 | IR-001
  → 2,847 tokens
[2/450] AGENTS_ONLY | gpt4 | IR-001
  → 4,123 tokens
[3/450] AICAC | gpt4 | IR-001
  → 1,456 tokens

ANALYSIS SUMMARY
================================================================

Token Consumption by Format:
README_ONLY:  Mean: 2,847.0 tokens
AGENTS_ONLY:  Mean: 4,123.0 tokens (-44.8% vs README)
AICAC:        Mean: 1,689.0 tokens (+40.7% vs README)
```

## Contributing

We welcome contributions to:
- Additional test tasks
- Alternative tokenizers
- Statistical analysis improvements
- Visualization enhancements

## Citation

If you use this validation framework, please cite:

```bibtex
@misc{aicac2026,
  title={AI Context as Code: Token-Efficient Documentation for AI Coding Assistants},
  author={eFAILution},
  year={2026},
  howpublished={\url{https://github.com/eFAILution/AICaC}},
  note={Validation framework v0.1.0}
}
```

## License

- Code: MIT License
- Documentation: CC BY-SA 4.0

See [LICENSE-CODE](../LICENSE-CODE) and [LICENSE-DOCS](../LICENSE-DOCS) for details.

## Contact

- **GitHub:** [@eFAILution](https://github.com/eFAILution)
- **Issues:** [github.com/eFAILution/AICaC/issues](https://github.com/eFAILution/AICaC/issues)
- **Discussions:** [github.com/eFAILution/AICaC/discussions](https://github.com/eFAILution/AICaC/discussions)
