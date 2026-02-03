# AICaC Validation Quick Start Guide

Get up and running with AICaC validation experiments in 30 minutes.

---

## Prerequisites

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install anthropic tiktoken
```

### 2. Set Up API Keys (Optional but Recommended)

For Claude token counting:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Note:** tiktoken (GPT-4) works without API keys for token counting only.

---

## Phase 1: Token Efficiency Measurement

### Step 1: Prepare Test Repositories

You need 3 versions of your repository. Use the included sample project or your own.

**Option A: Use the included sample project**

```bash
# Create test directory
mkdir -p aicac-validation
cd aicac-validation

# Copy sample project 3 times
cp -r ../validation/examples/sample-project aicac-full
cp -r ../validation/examples/sample-project agents-only
cp -r ../validation/examples/sample-project readme-only

# Remove documentation to create variants
cd readme-only
rm -f AGENTS.md
rm -rf .ai/

cd ../agents-only
rm -rf .ai/

cd ../aicac-full
# Keep everything (has README.md + AGENTS.md + .ai/)

cd ..
```

**Option B: Use your own repository**

```bash
# Clone your repo 3 times
git clone https://github.com/your-org/your-repo readme-only
git clone https://github.com/your-org/your-repo agents-only
git clone https://github.com/your-org/your-repo aicac-full

# Remove documentation to create variants (same as above)
```

### Step 2: Run Token Measurements

```bash
# Quick test (single format)
python token_measurement.py \
    --repo-path ./aicac-full \
    --format AICAC \
    --model gpt4 \
    --output pilot_results.json

# Full experiment (all formats, 10 trials)
python token_measurement.py \
    --repo-path ./readme-only \
    --all-formats \
    --trials 10 \
    --output full_results.json
```

**Expected output:**
```
Running 150 measurements...
Formats: ['README_ONLY', 'AGENTS_ONLY', 'AICAC']
Models: ['gpt4']
Questions: 15
Trials: 10

[1/150] README_ONLY | gpt4 | IR-001
  → 2,847 tokens
[2/150] README_ONLY | gpt4 | IR-002
  → 2,847 tokens
...

ANALYSIS SUMMARY
================================================================

Token Consumption by Format:
----------------------------------------------------------------

README_ONLY:
  Mean:       2,847.0 tokens
  Median:     2,847.0 tokens
  StdDev:         0.0 tokens
  Samples: 50

AGENTS_ONLY:
  Mean:       4,123.0 tokens (-44.8% vs README)
  Median:     4,123.0 tokens
  StdDev:         0.0 tokens
  Samples: 50

AICAC:
  Mean:       1,689.0 tokens (+40.7% vs README)
  Median:     1,689.0 tokens
  StdDev:         0.0 tokens
  Samples: 50
```

### Step 3: Analyze Results

```python
# analyze_results.py
import json
import pandas as pd
import matplotlib.pyplot as plt

# Load results
with open('full_results.json') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data['measurements'])

# Calculate summary statistics
summary = df.groupby('format')['token_count'].agg([
    'mean', 'median', 'std', 'count'
])

print(summary)

# Calculate reduction percentages
baseline = summary.loc['README_ONLY', 'mean']
summary['reduction_pct'] = (
    (baseline - summary['mean']) / baseline * 100
)

print("\nToken Reduction vs README_ONLY:")
print(summary['reduction_pct'])

# Visualize
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Box plot
df.boxplot(column='token_count', by='format', ax=ax1)
ax1.set_title('Token Consumption Distribution')
ax1.set_ylabel('Tokens')

# Bar chart of means
summary['mean'].plot(kind='bar', ax=ax2)
ax2.set_title('Mean Token Consumption by Format')
ax2.set_ylabel('Tokens')
ax2.set_xlabel('Format')

plt.tight_layout()
plt.savefig('token_efficiency_results.png', dpi=300)
print("\nVisualization saved to: token_efficiency_results.png")
```

---

## Phase 2: Task Completion Experiments (Manual)

### Step 1: Define Test Task

Example task: "Add a new scanner"

**Task Definition:**
```yaml
# task_add_scanner.yaml
id: CW-001
name: "Add New Scanner Integration"
description: |
  Implement a Snyk scanner integration following project patterns.
  
requirements:
  - Create scanner class inheriting from BaseScanner
  - Implement scan() and parse_results() methods
  - Register in scanner_registry.py
  - Add unit tests
  - Follow existing naming conventions

success_criteria:
  - Code compiles without errors
  - Tests pass
  - Follows project structure
  - No security issues (bandit/semgrep pass)

estimated_time_human: "30-45 minutes"
```

### Step 2: Test with AI Assistant

Using Claude (via API or Cursor/Claude Code):

```python
# test_ai_task.py
import time
from anthropic import Anthropic

client = Anthropic()

# Load documentation context
with open('README.md') as f:
    readme = f.read()

# For AICAC format, also load .ai/ files
with open('.ai/workflows.yaml') as f:
    workflows = f.read()

context = f"""
# Project Documentation

{readme}

# Workflows
{workflows}
"""

# Define task
task = """
Add a new scanner integration for Snyk that:
1. Creates a SnykScanner class in src/scanners/
2. Inherits from BaseScanner
3. Implements scan() and parse_results() methods
4. Registers in src/scanner_registry.py
5. Adds tests in tests/scanners/

Follow existing patterns from TrivyScanner.
"""

# Run task
start_time = time.time()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    system=context,
    messages=[
        {"role": "user", "content": task}
    ]
)

completion_time = time.time() - start_time

print(f"Task completed in {completion_time:.2f} seconds")
print("\nGenerated code:")
print(response.content[0].text)

# Evaluate success (manual for pilot)
```

### Step 3: Record Results

```python
# Record in results.json
result = {
    "task_id": "CW-001",
    "format": "AICAC",
    "model": "claude-sonnet-4",
    "completion_time": completion_time,
    "success": True,  # Manual evaluation
    "accuracy_score": 0.95,  # Manual scoring
    "notes": "Code compiled, tests passed, followed conventions"
}
```

---

## Phase 3: Statistical Analysis

### Step 1: Combine Results

```python
# statistical_analysis.py
import pandas as pd
import numpy as np
from scipy import stats

# Load token measurements
with open('full_results.json') as f:
    token_data = json.load(f)

df = pd.DataFrame(token_data['measurements'])

# T-test: README_ONLY vs AICAC
readme_tokens = df[df['format'] == 'README_ONLY']['token_count']
aicac_tokens = df[df['format'] == 'AICAC']['token_count']

t_stat, p_value = stats.ttest_ind(readme_tokens, aicac_tokens)

print(f"T-statistic: {t_stat:.4f}")
print(f"P-value: {p_value:.4e}")

if p_value < 0.05:
    print("✓ Result is statistically significant (p < 0.05)")
else:
    print("✗ Result is NOT statistically significant")

# Calculate Cohen's d (effect size)
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

d = cohens_d(readme_tokens, aicac_tokens)
print(f"\nCohen's d: {d:.4f}")

if abs(d) > 0.8:
    print("✓ Large effect size (|d| > 0.8)")
elif abs(d) > 0.5:
    print("✓ Medium effect size (|d| > 0.5)")
else:
    print("✗ Small effect size (|d| < 0.5)")
```

### Step 2: Generate Publication Figures

```python
# publication_figures.py
import matplotlib.pyplot as plt
import seaborn as sns

# Set publication style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("colorblind")

fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# 1. Token efficiency comparison
df.boxplot(column='token_count', by='format', ax=axes[0, 0])
axes[0, 0].set_title('(a) Token Consumption by Format')
axes[0, 0].set_ylabel('Token Count')
axes[0, 0].set_xlabel('Documentation Format')

# 2. Reduction percentages
summary = df.groupby('format')['token_count'].mean()
baseline = summary['README_ONLY']
reductions = ((baseline - summary) / baseline * 100)
reductions.plot(kind='bar', ax=axes[0, 1])
axes[0, 1].set_title('(b) Token Reduction vs Baseline')
axes[0, 1].set_ylabel('Reduction (%)')
axes[0, 1].axhline(y=0, color='black', linestyle='--', alpha=0.3)

# 3. By question category
category_data = df.copy()
category_data['category'] = category_data['question_id'].str.split('-').str[0]
sns.violinplot(data=category_data, x='category', y='token_count', 
               hue='format', ax=axes[1, 0])
axes[1, 0].set_title('(c) Token Usage by Question Category')
axes[1, 0].set_ylabel('Token Count')
axes[1, 0].set_xlabel('Category')

# 4. Cumulative distribution
for format in df['format'].unique():
    format_data = df[df['format'] == format]['token_count'].sort_values()
    cumulative = np.arange(1, len(format_data) + 1) / len(format_data)
    axes[1, 1].plot(format_data, cumulative, label=format, linewidth=2)

axes[1, 1].set_title('(d) Cumulative Distribution')
axes[1, 1].set_xlabel('Token Count')
axes[1, 1].set_ylabel('Cumulative Probability')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('publication_figure_1.png', dpi=300, bbox_inches='tight')
print("Figure saved: publication_figure_1.png")
```

---

## Quick Results Interpretation

### What to Look For

**Strong Evidence:**
- Token reduction: ≥40% for AICaC vs README_ONLY
- P-value: < 0.01 (highly significant)
- Cohen's d: > 0.8 (large effect)

**Moderate Evidence:**
- Token reduction: 20-40%
- P-value: < 0.05 (significant)
- Cohen's d: 0.5-0.8 (medium effect)

**Weak/Inconclusive:**
- Token reduction: < 20%
- P-value: > 0.05 (not significant)
- Cohen's d: < 0.5 (small effect)

---

## Next Steps After Pilot

1. **If results are strong:**
   - Scale up: Run 30+ trials
   - Add more task categories
   - Test multiple AI models
   - Run Phase 2 (task completion)

2. **If results are moderate:**
   - Refine AICaC implementation
   - Add more structured data
   - Test with more diverse questions
   - Iterate and re-test

3. **If results are weak:**
   - Analyze why (wrong questions? Poor AICaC design?)
   - Interview AI tool developers
   - Reconsider hypothesis
   - Pivot approach

---

## Troubleshooting

### Error: "No tokenizer models available"

Install at least one:
```bash
pip install tiktoken  # For GPT-4 token counting
pip install anthropic  # For Claude token counting
```

### Error: "README.md not found"

Make sure you're running from the repository directory:
```bash
cd /path/to/your/repo
python token_measurement.py --format AICAC
```

### Results look wrong

Check:
- Are all .ai/ files present?
- Is AGENTS.md pointing to .ai/?
- Are YAML files properly formatted?

### Low token reduction

This might mean:
- AICaC needs refinement
- Questions aren't leveraging structure
- Baseline (README) is already efficient
- Need better question selection

---

## Budget-Friendly Tips

1. **Start with tiktoken (free):**
   - No API costs
   - Good proxy for other models

2. **Use Claude batch API:**
   - 50% cheaper than real-time
   - Perfect for experiments

3. **Run pilot first:**
   - 10 trials = ~$5-10
   - Validates approach before scaling

4. **Cache contexts:**
   - Claude prompt caching
   - Can reduce costs by 90%

---

## Expected Timeline

- **Day 1:** Setup + pilot experiment (10 trials)
- **Day 2-3:** Analyze pilot, refine questions
- **Week 1:** Full Phase 1 (30 trials × all formats)
- **Week 2:** Phase 2 task experiments
- **Week 3:** Statistical analysis + write-up

---

## Success Checklist

Phase 1 Complete:
- [ ] 30+ trials per format
- [ ] P-value < 0.05
- [ ] Token reduction ≥ 30%
- [ ] Results visualized
- [ ] Raw data exported

Ready for Publication:
- [ ] Methodology documented
- [ ] Code published (GitHub)
- [ ] Results reproducible
- [ ] Limitations discussed
- [ ] Statistical tests passed

---

## Support & Questions

- **GitHub Issues:** [github.com/eFAILution/AICaC/issues](https://github.com/eFAILution/AICaC/issues)
- **Discussions:** [github.com/eFAILution/AICaC/discussions](https://github.com/eFAILution/AICaC/discussions)
- **Discussions:** github.com/aicac-dev/aicac/discussions

---

## Quick Command Reference

```bash
# Quick pilot (5 minutes)
python token_measurement.py --format AICAC --category information_retrieval

# Full experiment (30 minutes)
python token_measurement.py --all-formats --trials 10

# Analyze results
python analyze_results.py full_results.json

# Generate figures
python publication_figures.py full_results.json
```

Ready to prove AICaC works! 🚀
