# AICaC Badges

Display your project's adoption of AI Context as Code with official badges.

## Available Badges

### Basic Adoption Badge

**Standard:**
```markdown
[![AICaC](https://img.shields.io/badge/AICaC-Adopted-blue.svg)](https://github.com/eFAILution/AICaC)
```
[![AICaC](https://img.shields.io/badge/AICaC-Adopted-blue.svg)](https://github.com/eFAILution/AICaC)

**With Version:**
```markdown
[![AICaC](https://img.shields.io/badge/AICaC-v1.0-blue.svg)](https://github.com/eFAILution/AICaC)
```
[![AICaC](https://img.shields.io/badge/AICaC-v1.0-blue.svg)](https://github.com/eFAILution/AICaC)

### Compliance Level Badges

**Minimal Compliance** (has `.ai/context.yaml` only):
```markdown
[![AICaC](https://img.shields.io/badge/AICaC-Minimal-green.svg)](https://github.com/eFAILution/AICaC)
```
[![AICaC](https://img.shields.io/badge/AICaC-Minimal-green.svg)](https://github.com/eFAILution/AICaC)

**Standard Compliance** (has context.yaml + 2+ optional files):
```markdown
[![AICaC](https://img.shields.io/badge/AICaC-Standard-brightgreen.svg)](https://github.com/eFAILution/AICaC)
```
[![AICaC](https://img.shields.io/badge/AICaC-Standard-brightgreen.svg)](https://github.com/eFAILution/AICaC)

**Comprehensive Compliance** (has all 5 core files):
```markdown
[![AICaC](https://img.shields.io/badge/AICaC-Comprehensive-success.svg)](https://github.com/eFAILution/AICaC)
```
[![AICaC](https://img.shields.io/badge/AICaC-Comprehensive-success.svg)](https://github.com/eFAILution/AICaC)

### Status Badges

**In Progress:**
```markdown
[![AICaC](https://img.shields.io/badge/AICaC-In%20Progress-yellow.svg)](https://github.com/eFAILution/AICaC)
```
[![AICaC](https://img.shields.io/badge/AICaC-In%20Progress-yellow.svg)](https://github.com/eFAILution/AICaC)

**Validated:**
```markdown
[![AICaC](https://img.shields.io/badge/AICaC-Validated-brightgreen.svg)](https://github.com/eFAILution/AICaC)
```
[![AICaC](https://img.shields.io/badge/AICaC-Validated-brightgreen.svg)](https://github.com/eFAILution/AICaC)

## Compliance Levels Explained

### Minimal (Green)
Your project has:
- `.ai/context.yaml` with required fields:
  - `version`
  - `project.name`
  - `project.type`
  - At least one `entrypoint`
  - At least one `common_task`

### Standard (Bright Green)
Your project has:
- `.ai/context.yaml` (required)
- Plus 2 or more of:
  - `.ai/architecture.yaml`
  - `.ai/workflows.yaml`
  - `.ai/decisions.yaml`
  - `.ai/errors.yaml`

### Comprehensive (Success)
Your project has all 5 core files:
- `.ai/context.yaml`
- `.ai/architecture.yaml`
- `.ai/workflows.yaml`
- `.ai/decisions.yaml`
- `.ai/errors.yaml`

## Badge Placement

Add the badge to your `README.md` near the top, alongside other status badges:

```markdown
# Your Project Name

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/workflow/status/yourname/yourproject/CI)](https://github.com/yourname/yourproject/actions)
[![AICaC](https://img.shields.io/badge/AICaC-Standard-brightgreen.svg)](https://github.com/eFAILution/AICaC)

Your project description...
```

## Custom Badges

You can create custom badges using [shields.io](https://shields.io) with this format:

```
https://img.shields.io/badge/<LABEL>-<MESSAGE>-<COLOR>.svg
```

Examples:
```markdown
<!-- Custom version -->
[![AICaC](https://img.shields.io/badge/AICaC-v0.1.0-blue.svg)](https://github.com/eFAILution/AICaC)

<!-- Custom color scheme -->
[![AICaC](https://img.shields.io/badge/AICaC-Adopted-purple.svg)](https://github.com/eFAILution/AICaC)

<!-- With logo (if available) -->
[![AICaC](https://img.shields.io/badge/AICaC-v1.0-blue.svg?logo=data:image/svg+xml;base64,...)](https://github.com/eFAILution/AICaC)
```

## Validation Tool

You can validate your AICaC compliance using the action scripts:

```bash
# Clone the AICaC repo (if not already cloned)
git clone https://github.com/eFAILution/AICaC.git

# Run validator on your project
python AICaC/.github/actions/aicac-adoption/scripts/validate.py /path/to/your/project

# Or from within your project directory
python /path/to/AICaC/.github/actions/aicac-adoption/scripts/validate.py .
```

Example output:
```
============================================================
AICaC Compliance Validation Report
============================================================

Compliance Level: Standard

Files Found:
  ✓ .ai/context.yaml
  ✓ .ai/architecture.yaml
  ✓ .ai/workflows.yaml
  ✗ .ai/decisions.yaml
  ✗ .ai/errors.yaml

✓ context.yaml is valid

Recommended Badge:
  [![AICaC](https://img.shields.io/badge/AICaC-Standard-brightgreen.svg)](https://github.com/eFAILution/AICaC)

Suggestions to improve compliance:
  • Add .ai/decisions.yaml
  • Add .ai/errors.yaml

============================================================
```

## Badge Evolution

As your project's AICaC implementation improves, update your badge:

```markdown
<!-- Start with minimal -->
[![AICaC](https://img.shields.io/badge/AICaC-Minimal-green.svg)](https://github.com/eFAILution/AICaC)

<!-- Upgrade to standard when you add more files -->
[![AICaC](https://img.shields.io/badge/AICaC-Standard-brightgreen.svg)](https://github.com/eFAILution/AICaC)

<!-- Achieve comprehensive when all files present -->
[![AICaC](https://img.shields.io/badge/AICaC-Comprehensive-success.svg)](https://github.com/eFAILution/AICaC)
```

## GitHub Action for Adoption & Maintenance

### For New Adopters (Bootstrap)

Create a workflow to bootstrap AICaC in your project:

```yaml
# .github/workflows/adopt-aicac.yml
name: Adopt AICaC

on:
  workflow_dispatch:  # Manual trigger

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: eFAILution/AICaC/.github/actions/aicac-adoption@main
        with:
          mode: setup
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

This creates a PR with `.ai/` directory structure and adoption guide.

### For Existing Adopters (Maintenance)

Add continuous validation and badge maintenance:

```yaml
# .github/workflows/aicac-maintenance.yml
name: AICaC Maintenance

on:
  push:
    paths:
      - '.ai/**'
  pull_request:
    paths:
      - '.ai/**'

jobs:
  maintain:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v3
      - uses: eFAILution/AICaC/.github/actions/aicac-adoption@main
        with:
          mode: maintain
          update-badge: 'true'
```

This validates compliance and automatically updates your badge when `.ai/` files change.

## Dynamic Badges (Advanced)

For projects hosted on GitHub, you can use GitHub Actions to generate dynamic badges that reflect your current compliance:

```yaml
# .github/workflows/aicac-badge.yml
name: AICaC Badge

on:
  push:
    paths:
      - '.ai/**'

jobs:
  update-badge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check AICaC Compliance
        id: compliance
        run: |
          # Check for files and set compliance level
          if [ -f ".ai/context.yaml" ] && [ -f ".ai/architecture.yaml" ] && \
             [ -f ".ai/workflows.yaml" ] && [ -f ".ai/decisions.yaml" ] && \
             [ -f ".ai/errors.yaml" ]; then
            echo "level=Comprehensive" >> $GITHUB_OUTPUT
            echo "color=success" >> $GITHUB_OUTPUT
          elif [ -f ".ai/context.yaml" ] && [ $(find .ai -name "*.yaml" | wc -l) -ge 3 ]; then
            echo "level=Standard" >> $GITHUB_OUTPUT
            echo "color=brightgreen" >> $GITHUB_OUTPUT
          else
            echo "level=Minimal" >> $GITHUB_OUTPUT
            echo "color=green" >> $GITHUB_OUTPUT
          fi
      - name: Create Badge
        uses: schneegans/dynamic-badges-action@v1.6.0
        with:
          auth: ${{ secrets.GIST_TOKEN }}
          gistID: your-gist-id
          filename: aicac-badge.json
          label: AICaC
          message: ${{ steps.compliance.outputs.level }}
          color: ${{ steps.compliance.outputs.color }}
```

Then use the dynamic badge in your README:
```markdown
[![AICaC](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/yourname/your-gist-id/raw/aicac-badge.json)](https://github.com/eFAILution/AICaC)
```

## Community Recognition

Projects displaying AICaC badges may be featured in:
- The [AICaC Showcase](https://github.com/eFAILution/AICaC/wiki/Showcase)
- Monthly community highlights
- Research case studies

## Questions?

- Open an issue: [github.com/eFAILution/AICaC/issues](https://github.com/eFAILution/AICaC/issues)
- Discussions: [github.com/eFAILution/AICaC/discussions](https://github.com/eFAILution/AICaC/discussions)

---

**Badge Format:** Powered by [shields.io](https://shields.io)
**License:** CC BY-SA 4.0 (same as AICaC documentation)
