# AICaC Testing Framework: Empirical Validation Strategy

**Version:** 1.0  
**Date:** February 2026  
**Purpose:** Design rigorous, reproducible experiments to prove AICaC delivers measurable improvements over prose-based documentation

---

## Executive Summary

To publish AICaC credibly, we need empirical evidence across three dimensions:

1. **Token Efficiency** - Quantitative measurement of context consumption
2. **Task Performance** - Success rate and completion time for common development tasks
3. **Quality Metrics** - Accuracy, completeness, and maintainability of AI-generated solutions

Inspired by the NeurIPS 2025 paper "Measuring AI Ability to Complete Long Software Tasks", we'll measure **50%-task-completion time** and **success rates** across controlled experiments.

---

## Table of Contents

1. [Testing Dimensions](#testing-dimensions)
2. [Experimental Design](#experimental-design)
3. [Test Suite Design](#test-suite-design)
4. [Methodology](#methodology)
5. [Success Criteria](#success-criteria)
6. [Implementation Plan](#implementation-plan)
7. [Publication Strategy](#publication-strategy)

---

## Testing Dimensions

### 1. Token Efficiency (Primary Metric)

**What we're measuring:** Raw context window consumption for equivalent information

**Hypothesis:** AICaC reduces token consumption by 40-60% for common queries

**Test approach:**
```
For each documentation format (README.md, AGENTS.md, AICaC):
  - Count tokens consumed to answer specific questions
  - Measure with multiple tokenizers (GPT-4, Claude, Llama)
  - Calculate reduction percentage
```

### 2. Task Completion Performance (Impact Metric)

**What we're measuring:** AI assistant success rate and time to complete real-world tasks

**Hypothesis:** AICaC improves task success rate by 20-30% and reduces completion time by 15-25%

**Test approach:**
```
For each documentation format:
  - Run AI coding assistant on standardized tasks
  - Measure: success rate, completion time, attempts needed
  - Compare outcomes across formats
```

### 3. Response Quality (Validation Metric)

**What we're measuring:** Accuracy, completeness, and correctness of AI-generated solutions

**Hypothesis:** AICaC produces more accurate responses with fewer hallucinations

**Test approach:**
```
For each AI response:
  - Validate technical accuracy against ground truth
  - Check for hallucinations (invented functions, incorrect paths)
  - Measure completeness (all required steps present)
```

---

## Experimental Design

### Control Variables

**Constant across all tests:**
- Same AI model (Claude Sonnet 4, GPT-4o, others)
- Same base codebase (hardening-workflows)
- Same task definitions
- Same evaluation rubric
- Same temperature/sampling parameters

**Independent Variable:**
- Documentation format: README.md only | AGENTS.md only | AICaC (.ai/ directory)

**Dependent Variables:**
- Token consumption
- Task success rate
- Task completion time
- Response accuracy score
- Hallucination rate

### Statistical Rigor

- **Sample size:** Minimum 30 trials per task per format (n=30)
- **Significance level:** α = 0.05
- **Statistical tests:** 
  - Paired t-test for token consumption
  - Chi-square test for success rates
  - ANOVA for completion times
- **Effect size:** Cohen's d for practical significance

---

## Test Suite Design

### Task Categories

We'll test across 5 categories of increasing complexity:

#### Category 1: Information Retrieval (Baseline)
**Time estimate:** 2-5 minutes  
**Tasks:**
1. "What command runs a local security scan?"
2. "Which scanners are available?"
3. "What's the project's primary purpose?"
4. "Where is the scanner registry located?"
5. "What Python version is required?"

**Success criteria:** Correct answer extracted, no hallucinations

---

#### Category 2: Architectural Understanding (Medium)
**Time estimate:** 5-15 minutes  
**Tasks:**
1. "Explain the data flow from user input to report generation"
2. "What are the dependencies between scanner-orchestrator and report-generator?"
3. "Why was Dagger chosen over GitHub Actions nested workflows?"
4. "Describe the plugin architecture for compliance checks"
5. "How do scanners communicate their results?"

**Success criteria:** Accurate explanation, correct component relationships, reasoning matches ADRs

---

#### Category 3: Common Developer Workflows (Complex)
**Time estimate:** 15-45 minutes  
**Tasks:**
1. **Add a new scanner**: "Implement a Snyk scanner integration following project patterns"
   - Must: create class, inherit BaseScanner, register in registry, add tests
   - Validate: code compiles, tests pass, follows project structure

2. **Fix a common error**: "Resolve 'token doesn't have packages:write' error for Dependabot"
   - Must: identify root cause, provide correct solution
   - Validate: solution matches documented fix

3. **Local development setup**: "Set up local development environment and run a test scan"
   - Must: install dependencies, configure environment, execute scan
   - Validate: scan completes successfully

4. **Add compliance plugin**: "Create a new FedRAMP compliance check plugin"
   - Must: follow plugin architecture, implement interface, register plugin
   - Validate: plugin loads and executes

5. **Troubleshoot registry error**: "Debug and fix 'registry tag already exists' error"
   - Must: explain root cause, implement fix with unique tags
   - Validate: solution prevents error recurrence

**Success criteria:** Working code, all tests pass, follows project conventions, no security issues

---

#### Category 4: Cross-Cutting Modifications (Expert)
**Time estimate:** 45-90 minutes  
**Tasks:**
1. "Add support for a new CI platform (GitLab CI) while maintaining GHES compatibility"
2. "Refactor the scanner orchestrator to support parallel execution"
3. "Implement caching strategy for scan results to reduce redundant work"
4. "Add support for custom report templates with user-defined formats"

**Success criteria:** Multi-file changes, architectural consistency maintained, backward compatibility, tests pass

---

#### Category 5: Greenfield Implementation (Advanced)
**Time estimate:** 2-4 hours  
**Tasks:**
1. "Implement a complete vulnerability remediation workflow that:
   - Detects CVEs from scan results
   - Proposes fixes (version bumps, patches)
   - Creates PRs with fixes
   - Validates fixes with re-scanning"

**Success criteria:** Complete feature implementation, follows all project patterns, production-ready code

---

## Methodology

### Phase 1: Token Efficiency Measurement

**Objective:** Quantify raw token consumption differences

**Procedure:**
```python
# Pseudo-code for token measurement
for documentation_format in [README_ONLY, AGENTS_ONLY, AICAC]:
    for question in INFORMATION_RETRIEVAL_TASKS:
        context = load_documentation(documentation_format)
        tokens_consumed = count_tokens(context, question)
        record_measurement(documentation_format, question, tokens_consumed)
```

**Tools:**
- `tiktoken` (OpenAI tokenizer)
- `anthropic.count_tokens()` (Claude tokenizer)
- Custom token counters for other models

**Output:**
- CSV with: `task_id, format, model, token_count`
- Statistical summary: mean, median, std dev, reduction %

---

### Phase 2: Controlled AI Task Execution

**Objective:** Measure task completion with different documentation formats

**Setup:**

1. **Prepare test environments:**
   - Create 3 identical copies of hardening-workflows repo
   - Version A: README.md only (remove AGENTS.md, .ai/)
   - Version B: README.md + AGENTS.md (remove .ai/)
   - Version C: README.md + AGENTS.md + .ai/ (full AICaC)

2. **Configure AI assistants:**
   - Claude Sonnet 4 (primary)
   - GPT-4o (secondary validation)
   - Cursor with Claude (real-world usage)
   - Claude Code CLI (command-line usage)

3. **Standardize prompts:**
   ```
   System: You are helping develop the hardening-workflows project. 
   Use available documentation to complete tasks accurately.
   
   User: {TASK_DESCRIPTION}
   
   Evaluate your solution before submitting.
   ```

**Procedure:**

```python
for ai_model in [CLAUDE_SONNET_4, GPT4O, CURSOR]:
    for doc_format in [README_ONLY, AGENTS_ONLY, AICAC]:
        for task in ALL_TASKS:
            for trial in range(30):  # 30 trials per condition
                start_time = time()
                
                # Run task with AI assistant
                result = run_ai_task(
                    model=ai_model,
                    documentation=doc_format,
                    task=task,
                    timeout=TASK_TIMEOUT
                )
                
                completion_time = time() - start_time
                
                # Evaluate result
                success = evaluate_task_result(result, task.rubric)
                accuracy_score = score_accuracy(result, task.ground_truth)
                hallucinations = detect_hallucinations(result)
                
                # Record metrics
                record_trial(
                    model=ai_model,
                    format=doc_format,
                    task=task.id,
                    success=success,
                    time=completion_time,
                    accuracy=accuracy_score,
                    hallucinations=hallucinations
                )
```

**Key measurement points:**
- **Task initialization:** Time from prompt to first action
- **Context retrieval:** How many times AI queries documentation
- **Iteration count:** Number of failed attempts before success
- **Final validation:** Automated test suite execution

---

### Phase 3: Human Baseline Comparison

**Objective:** Establish human performance benchmarks (inspired by NeurIPS paper)

**Procedure:**

1. **Recruit participants:**
   - 10-15 software engineers with varying experience (junior to senior)
   - Domain expertise: Python, DevOps, security tooling
   - NOT familiar with hardening-workflows (cold start)

2. **Time human task completion:**
   ```
   For each participant:
       For each task (randomized order):
           - Provide documentation (format varies)
           - Time from start to completion
           - Record: completion time, success, questions asked
           - Measure: lines of code, correctness
   ```

3. **Calculate 50%-task-completion horizon:**
   - Sort tasks by median human completion time
   - Find task where AI has ~50% success rate
   - This is the "AI time horizon" benchmark

**Expected outcome:**
- "AI with AICaC can complete tasks that typically take humans X minutes with 50% success rate"
- Direct comparison: "30% faster than AGENTS.md only"

---

### Phase 4: Real-World Validation

**Objective:** Validate findings in production environments

**Approach:**

1. **Public experiment:**
   - Open source 3 versions of hardening-workflows docs
   - Track GitHub issues/PRs from new contributors
   - Measure: setup time, first contribution time, questions asked

2. **Instrumented usage:**
   - Partner with teams already using AI coding assistants
   - Deploy AICaC to their repos
   - Instrument their AI tools to measure:
     - Documentation access patterns
     - Task success rates
     - Time-to-completion for feature requests

3. **A/B testing with Claude.ai users:**
   - Partner with Anthropic (if possible)
   - Randomly assign users to repos with/without AICaC
   - Measure aggregate performance differences

---

## Success Criteria

### Minimum Viable Evidence (Required for Publication)

**Token Efficiency:**
- ✅ ≥30% reduction in token consumption for information retrieval tasks
- ✅ ≥40% reduction for architectural understanding tasks
- ✅ Statistical significance: p < 0.05

**Task Performance:**
- ✅ ≥15% improvement in task success rate for common workflows
- ✅ ≥10% reduction in median completion time
- ✅ Effect size: Cohen's d > 0.5 (medium effect)

**Quality Metrics:**
- ✅ ≤50% hallucination rate vs. prose-only (relative reduction)
- ✅ ≥90% accuracy on ground truth validation
- ✅ Zero regression in code quality (linting, security scans)

### Stretch Goals (Compelling Evidence)

**Advanced Performance:**
- 🎯 50% token reduction on complex tasks
- 🎯 25% task success rate improvement
- 🎯 20% completion time reduction
- 🎯 AI time horizon improvement: tasks that take humans 30 min → AI completes with 50% success

**Generalization:**
- 🎯 Results replicate across 3+ different codebases
- 🎯 Results hold for 3+ different AI models
- 🎯 Results validated by independent research team

---

## Implementation Plan

### Timeline: 8-12 Weeks

#### Week 1-2: Setup & Instrumentation
- [ ] Build test harness for automated AI task execution
- [ ] Create token counting infrastructure
- [ ] Prepare 3 documentation variants of hardening-workflows
- [ ] Write automated evaluation scripts
- [ ] IRB approval for human studies (if required)

#### Week 3-4: Phase 1 - Token Efficiency
- [ ] Run token measurement experiments (n=30 per condition)
- [ ] Analyze results, generate visualizations
- [ ] Draft findings: token efficiency section

#### Week 5-7: Phase 2 - AI Task Execution
- [ ] Execute controlled experiments (3 formats × 5 categories × 30 trials)
- [ ] Run multiple AI models for validation
- [ ] Collect performance metrics
- [ ] Statistical analysis

#### Week 8-9: Phase 3 - Human Baseline
- [ ] Recruit and schedule participants
- [ ] Run human task timing experiments
- [ ] Calculate 50%-task-completion horizons
- [ ] Compare AI vs. human performance

#### Week 10-11: Phase 4 - Real-World Validation
- [ ] Deploy public experiment
- [ ] Partner with production teams
- [ ] Collect field data

#### Week 12: Analysis & Write-Up
- [ ] Complete statistical analysis
- [ ] Create publication-quality visualizations
- [ ] Write results section
- [ ] Prepare supplementary materials

---

## Data Collection Instruments

### 1. Token Measurement Script

```python
#!/usr/bin/env python3
"""
Token efficiency measurement for AICaC validation
"""
import anthropic
import tiktoken
from pathlib import Path
import json

class TokenMeasurement:
    def __init__(self, format_type: str):
        self.format = format_type
        self.results = []
        
    def load_context(self, question: str) -> str:
        """Load documentation relevant to question"""
        if self.format == "README_ONLY":
            return Path("README.md").read_text()
        elif self.format == "AGENTS_ONLY":
            return (Path("README.md").read_text() + 
                   Path("AGENTS.md").read_text())
        elif self.format == "AICAC":
            context = Path("README.md").read_text()
            context += Path("AGENTS.md").read_text()
            # Load relevant .ai/ files based on question
            ai_files = self.select_relevant_files(question)
            for f in ai_files:
                context += Path(f".ai/{f}").read_text()
            return context
    
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens for different tokenizers"""
        if model == "claude":
            client = anthropic.Anthropic()
            return client.count_tokens(text)
        elif model == "gpt4":
            enc = tiktoken.encoding_for_model("gpt-4")
            return len(enc.encode(text))
    
    def measure(self, question: str, model: str) -> dict:
        """Measure tokens for a single question"""
        context = self.load_context(question)
        tokens = self.count_tokens(context, model)
        
        result = {
            "format": self.format,
            "question": question,
            "model": model,
            "token_count": tokens,
            "context_length": len(context)
        }
        self.results.append(result)
        return result
```

### 2. Task Execution Harness

```python
#!/usr/bin/env python3
"""
Automated AI task execution and evaluation
"""
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class TaskResult:
    task_id: str
    format: str
    model: str
    success: bool
    completion_time: float
    accuracy_score: float
    hallucinations: int
    iterations: int

class TaskExecutor:
    def __init__(self, model: str, doc_format: str):
        self.model = model
        self.format = doc_format
        
    def execute_task(self, task: dict, timeout: int = 3600) -> TaskResult:
        """Execute a single task with AI assistant"""
        start_time = time.time()
        
        # Prepare environment
        self.setup_environment(task)
        
        # Run AI assistant
        result = self.run_ai_agent(
            task_description=task["prompt"],
            timeout=timeout
        )
        
        # Evaluate result
        success = self.evaluate_success(result, task["rubric"])
        accuracy = self.score_accuracy(result, task["ground_truth"])
        hallucinations = self.detect_hallucinations(result)
        
        completion_time = time.time() - start_time
        
        return TaskResult(
            task_id=task["id"],
            format=self.format,
            model=self.model,
            success=success,
            completion_time=completion_time,
            accuracy_score=accuracy,
            hallucinations=hallucinations,
            iterations=result.get("iterations", 1)
        )
    
    def evaluate_success(self, result: dict, rubric: dict) -> bool:
        """Evaluate if task completed successfully"""
        # Run automated tests
        tests_pass = self.run_test_suite() == 0
        
        # Check required files created
        required_files = all(
            Path(f).exists() for f in rubric["required_files"]
        )
        
        # Validate code quality
        linting_pass = self.run_linter() == 0
        
        return tests_pass and required_files and linting_pass
```

### 3. Statistical Analysis Scripts

```python
#!/usr/bin/env python3
"""
Statistical analysis of AICaC experiments
"""
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

class AICaCAnalysis:
    def __init__(self, results_df: pd.DataFrame):
        self.df = results_df
        
    def token_efficiency_analysis(self):
        """Analyze token consumption reduction"""
        # Group by format and task category
        grouped = self.df.groupby(['format', 'task_category'])
        
        # Calculate mean tokens and std dev
        token_stats = grouped['token_count'].agg(['mean', 'std', 'median'])
        
        # Calculate reduction percentages
        baseline = token_stats.loc['README_ONLY', 'mean']
        token_stats['reduction_pct'] = (
            (baseline - token_stats['mean']) / baseline * 100
        )
        
        # Statistical significance tests
        readme_tokens = self.df[self.df['format'] == 'README_ONLY']['token_count']
        aicac_tokens = self.df[self.df['format'] == 'AICAC']['token_count']
        
        t_stat, p_value = stats.ttest_ind(readme_tokens, aicac_tokens)
        cohen_d = self.cohens_d(readme_tokens, aicac_tokens)
        
        return {
            'token_stats': token_stats,
            't_statistic': t_stat,
            'p_value': p_value,
            'effect_size': cohen_d
        }
    
    def task_performance_analysis(self):
        """Analyze task completion success and time"""
        # Success rate by format
        success_rates = self.df.groupby('format')['success'].mean()
        
        # Completion time analysis
        time_stats = self.df.groupby('format')['completion_time'].agg([
            'mean', 'median', 'std'
        ])
        
        # Chi-square test for success rates
        contingency_table = pd.crosstab(
            self.df['format'], 
            self.df['success']
        )
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        # ANOVA for completion times
        formats = self.df['format'].unique()
        time_groups = [
            self.df[self.df['format'] == f]['completion_time'] 
            for f in formats
        ]
        f_stat, anova_p = stats.f_oneway(*time_groups)
        
        return {
            'success_rates': success_rates,
            'time_stats': time_stats,
            'chi2_test': {'chi2': chi2, 'p_value': p_value},
            'anova_test': {'f_stat': f_stat, 'p_value': anova_p}
        }
    
    @staticmethod
    def cohens_d(group1, group2):
        """Calculate Cohen's d effect size"""
        n1, n2 = len(group1), len(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
        return (np.mean(group1) - np.mean(group2)) / pooled_std
    
    def generate_visualizations(self):
        """Create publication-quality figures"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Token efficiency comparison
        sns.boxplot(
            data=self.df, 
            x='format', 
            y='token_count',
            ax=axes[0, 0]
        )
        axes[0, 0].set_title('Token Consumption by Format')
        
        # Success rate comparison
        success_data = self.df.groupby('format')['success'].mean()
        success_data.plot(kind='bar', ax=axes[0, 1])
        axes[0, 1].set_title('Task Success Rate by Format')
        
        # Completion time distribution
        sns.violinplot(
            data=self.df,
            x='format',
            y='completion_time',
            ax=axes[1, 0]
        )
        axes[1, 0].set_title('Task Completion Time Distribution')
        
        # Accuracy scores
        sns.boxplot(
            data=self.df,
            x='format',
            y='accuracy_score',
            ax=axes[1, 1]
        )
        axes[1, 1].set_title('Response Accuracy by Format')
        
        plt.tight_layout()
        return fig
```

---

## Publication Strategy

### Target Venues

#### 1. **Academic Conferences (Primary)**

**NeurIPS 2026 - Datasets and Benchmarks Track**
- Deadline: ~May 2026
- Focus: Novel benchmark for AI documentation understanding
- Strengths: Rigorous methodology, inspired by accepted work
- Submission type: Dataset + empirical study

**ICSE 2027 - International Conference on Software Engineering**
- Deadline: ~September 2026
- Focus: Software engineering tools and practices
- Strengths: Real-world impact, developer productivity
- Submission type: Full research paper

**MSR 2026 - Mining Software Repositories**
- Deadline: ~December 2025/January 2026
- Focus: Empirical studies of development practices
- Strengths: Large-scale empirical validation
- Submission type: Full paper or data showcase

#### 2. **Preprint Servers (Immediate)**

**arXiv.org**
- Category: cs.SE (Software Engineering)
- Timeline: Publish immediately after initial results
- Benefits: Early visibility, community feedback, citable

**Papers with Code**
- Link arXiv paper with GitHub repo
- Include benchmarks and leaderboards
- Community engagement

#### 3. **Industry Publications**

**ACM Queue / Communications of ACM**
- Practitioner-focused writeup
- Focus on adoption and impact
- Timeline: After academic publication

**IEEE Software**
- Practical guide for implementing AICaC
- Tool/methodology focus

#### 4. **Open Source Release**

**GitHub Repository: aicac-dev/aicac**
- Full specification
- Validation datasets
- Testing frameworks
- Example implementations
- Community contributions

---

## Supplementary Materials Checklist

For publication, we need to provide:

### Data & Code
- [ ] Raw experimental data (CSV/JSON)
- [ ] Token measurement scripts
- [ ] Task execution harness
- [ ] Statistical analysis notebooks
- [ ] Visualization generation code
- [ ] All task definitions and rubrics

### Documentation
- [ ] Experimental protocol (step-by-step)
- [ ] IRB approval documents (if required)
- [ ] Participant consent forms
- [ ] Detailed methodology writeup
- [ ] Limitations and threats to validity

### Reproducibility
- [ ] Docker containers for test environments
- [ ] Requirements.txt for all dependencies
- [ ] Seed values for random number generators
- [ ] Version pins for all AI models used
- [ ] Complete replication instructions

### Examples
- [ ] 3 versions of hardening-workflows (README/AGENTS/AICaC)
- [ ] Example AICaC implementations (5+ diverse repos)
- [ ] Annotated "good" vs "bad" AICaC examples

---

## Budget Estimate

### Computing Costs
- **AI API costs:** $2,000-5,000
  - Claude API: ~30 trials × 25 tasks × 3 formats × $0.50/task = ~$1,100
  - GPT-4 API: Similar costs
  - Buffer for debugging/iterations
  
### Human Participant Costs
- **Compensation:** $2,000-3,000
  - 15 participants × 4 hours × $40/hour = $2,400
  
### Total: $4,000-8,000

*Note: Could seek academic or industry sponsorship to offset costs*

---

## Risk Mitigation

### Threat to Validity #1: Selection Bias

**Risk:** Choosing tasks that favor AICaC

**Mitigation:**
- Include tasks proposed by external reviewers
- Test on repos we didn't create
- Blind evaluation where possible

### Threat to Validity #2: Overfitting to One Codebase

**Risk:** Results specific to hardening-workflows

**Mitigation:**
- Replicate across 3-5 diverse codebases:
  - Different languages (Python, TypeScript, Go)
  - Different domains (web app, CLI tool, library)
  - Different sizes (small/medium/large)

### Threat to Validity #3: AI Model Variability

**Risk:** Results depend on specific model version

**Mitigation:**
- Test multiple models (Claude, GPT-4, open source)
- Pin exact model versions
- Rerun experiments when models update
- Report variance across models

### Threat to Validity #4: Experimenter Bias

**Risk:** We unconsciously design AICaC-friendly tasks

**Mitigation:**
- External task design committee
- Blind evaluation of results
- Independent replication by another team
- Preregister hypothesis and methodology

---

## Next Steps (Immediate Actions)

### This Week
1. [ ] Set up GitHub repo: `aicac-dev/validation`
2. [ ] Implement token measurement script
3. [ ] Create 3 documentation variants of hardening-workflows
4. [ ] Define first 5 information retrieval tasks
5. [ ] Run pilot token efficiency experiment

### Next Week
1. [ ] Build task execution harness
2. [ ] Recruit beta testers for human baseline
3. [ ] Write IRB protocol (if needed)
4. [ ] Start Phase 1 experiments

### Month 1 Goal
- Complete token efficiency experiments
- Draft methodology section
- Begin Phase 2 task execution

---

## Conclusion

This testing framework provides a rigorous, reproducible path to validating AICaC's claims. By combining:

1. **Quantitative token measurements** (objective, easily reproducible)
2. **Controlled AI task experiments** (real-world impact)
3. **Human baseline comparisons** (contextualizes AI capabilities)
4. **Statistical rigor** (publishable results)

We can produce compelling evidence that AICaC delivers on its promises. The methodology is directly inspired by accepted academic work (NeurIPS 2025), giving us a proven template for success.

**The data will speak for itself** - if AICaC truly reduces tokens by 40-60% and improves task performance by 15-25%, these results will be impossible to ignore.
