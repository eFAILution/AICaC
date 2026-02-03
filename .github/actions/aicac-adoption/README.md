# AICaC Adoption & Maintenance Action

A comprehensive GitHub Action to help projects adopt and maintain AICaC (AI Context as Code) compliance.

## Features

### 🚀 Setup Mode
Automatically bootstrap AICaC adoption in your project:
- Creates `.ai/` directory structure
- Generates initial `context.yaml` with TODO markers
- Opens a PR with adoption guide
- Future: AI-assisted content generation

### 🔄 Maintain Mode (Default)
Continuously validate and maintain compliance:
- Validates `.ai/` structure
- Checks compliance level (Minimal, Standard, Comprehensive)
- Automatically updates badge in README.md
- Fails CI if compliance drops

## Usage

### Option 1: Bootstrap AICaC (For New Adopters)

Add this workflow to a project that doesn't have `.ai/` yet:

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

      - name: Bootstrap AICaC
        uses: eFAILution/AICaC/.github/actions/aicac-adoption@main
        with:
          mode: setup
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

Run manually to create a PR that adds `.ai/` directory.

### Option 2: Continuous Maintenance (For Existing Adopters)

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
    steps:
      - uses: actions/checkout@v3

      - name: Validate and Update
        uses: eFAILution/AICaC/.github/actions/aicac-adoption@main
        with:
          mode: maintain
          update-badge: 'true'
```

This will:
1. Validate compliance when `.ai/` files change
2. Update badge in README.md to match current level
3. Auto-commit badge updates

### Option 3: Validation Only (No Auto-Updates)

```yaml
- name: Validate AICaC
  uses: eFAILution/AICaC/.github/actions/aicac-adoption@main
  with:
    mode: maintain
    update-badge: 'false'
```

## Inputs

| Input | Description | Default | Required |
|-------|-------------|---------|----------|
| `mode` | Operation mode: `setup` or `maintain` | `maintain` | No |
| `github-token` | GitHub token for creating PRs | `${{ github.token }}` | No |
| `project-path` | Path to project directory | `.` | No |
| `with-ai` | Use AI to populate files (future) | `false` | No |
| `ai-service` | AI service: `github-copilot`, `openai`, `anthropic` | `github-copilot` | No |
| `update-badge` | Auto-update badge in README | `true` | No |

## Outputs

| Output | Description |
|--------|-------------|
| `compliance-level` | Current level: `None`, `Minimal`, `Standard`, `Comprehensive` |
| `badge-url` | Recommended badge URL |
| `pr-number` | PR number if created (setup mode) |
| `setup-needed` | Whether `.ai/` needs to be created |

## Scripts

The action includes three Python scripts in the `scripts/` directory:

### scripts/bootstrap.py
Creates initial `.ai/` structure:
- Analyzes project (package.json, requirements.txt, etc.)
- Generates `context.yaml` with project-specific defaults
- Creates README.md with next steps
- Generates PR description

**Standalone usage:**
```bash
python scripts/bootstrap.py /path/to/project
python scripts/bootstrap.py . --pr-body  # Generate PR description
```

### scripts/validate.py
Validates AICaC compliance:
- Checks for `.ai/` directory
- Validates `context.yaml` structure
- Counts optional files
- Determines compliance level

**Standalone usage:**
```bash
python scripts/validate.py /path/to/project
```

### scripts/update_badge.py
Updates badge in README.md:
- Finds existing AICaC badge or adds new one
- Updates badge to match compliance level
- Preserves other badges and formatting

**Standalone usage:**
```bash
python scripts/update_badge.py Comprehensive --project-path=.
python scripts/update_badge.py Standard --check-only  # Just check, don't update
```

## Testing

Comprehensive pytest test suite in `tests/` directory:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=scripts --cov-report=html

# Run specific test file
pytest tests/test_bootstrap.py -v

# Run specific test
pytest tests/test_validate.py::TestAICaCValidator::test_validate_comprehensive_compliance -v
```

**Test Coverage:**
- `test_bootstrap.py` - Bootstrap functionality tests
- `test_validate.py` - Validation logic tests
- `test_update_badge.py` - Badge updating tests
- `conftest.py` - Shared fixtures and test utilities

Target coverage: 80%+

## Examples

### Full Setup to Maintenance Workflow

**Step 1:** Bootstrap (one-time)
```yaml
# Triggered manually or via workflow_dispatch
- uses: eFAILution/AICaC/.github/actions/aicac-adoption@main
  with:
    mode: setup
```

**Step 2:** Human reviews and merges PR, completes TODOs

**Step 3:** Enable continuous maintenance
```yaml
# Runs on every .ai/ change
- uses: eFAILution/AICaC/.github/actions/aicac-adoption@main
  with:
    mode: maintain
```

### Conditional Setup

Only run setup if `.ai/` doesn't exist:

```yaml
- uses: eFAILution/AICaC/.github/actions/aicac-adoption@main
  id: aicac
  with:
    mode: setup

- name: Notify if PR created
  if: steps.aicac.outputs.setup-needed == 'true'
  run: |
    echo "Created PR #${{ steps.aicac.outputs.pr-number }}"
```

## AI-Assisted Setup (Future)

Future versions will support AI-assisted population of `.ai/` files:

```yaml
- uses: eFAILution/AICaC/.github/actions/aicac-adoption@main
  with:
    mode: setup
    with-ai: 'true'
    ai-service: 'openai'
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

For now, use your AI coding assistant interactively:
1. Action creates `.ai/` with TODO markers
2. Open files in editor with Copilot/Cursor/Claude Code
3. Ask AI to complete based on project analysis
4. Review and refine

## Compliance Levels

| Level | Requirements | Badge |
|-------|-------------|-------|
| **Comprehensive** | All 5 core files | ![Comprehensive](https://img.shields.io/badge/AICaC-Comprehensive-success.svg) |
| **Standard** | `context.yaml` + 2+ optional | ![Standard](https://img.shields.io/badge/AICaC-Standard-brightgreen.svg) |
| **Minimal** | Valid `context.yaml` only | ![Minimal](https://img.shields.io/badge/AICaC-Minimal-green.svg) |
| **None** | No `.ai/` or invalid | ![Not Adopted](https://img.shields.io/badge/AICaC-Not%20Adopted-red.svg) |

## Contributing

Improvements welcome:
- Better AI integration
- Support for more project types
- Additional validation rules
- IDE integrations

Open issues at [AICaC repository](https://github.com/eFAILution/AICaC).

## License

MIT (same as AICaC code)
