# GitHub Integrations

GitHub Actions for AICaC adoption and maintenance.

## Action: aicac-adoption

A comprehensive GitHub Action that helps projects adopt and maintain AICaC compliance.

### Two Modes

#### 1. Setup Mode - Bootstrap Adoption
Creates a PR to adopt AICaC in projects without `.ai/` directory:

```yaml
- uses: eFAILution/AICaC/.github/actions/aicac-adoption@main
  with:
    mode: setup
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

**What it does:**
- Analyzes your project structure
- Creates `.ai/` directory with `context.yaml`
- Generates TODO markers for human completion
- Opens PR with adoption guide
- Future: AI-assisted content generation

#### 2. Maintain Mode - Continuous Validation
Validates compliance and maintains badge accuracy:

```yaml
- uses: eFAILution/AICaC/.github/actions/aicac-adoption@main
  with:
    mode: maintain
    update-badge: 'true'
```

**What it does:**
- Validates `.ai/` structure
- Determines compliance level
- Updates badge in README.md
- Auto-commits badge changes
- Fails CI if compliance drops

### Full Documentation

See [actions/aicac-adoption/README.md](actions/aicac-adoption/README.md) for:
- Complete input/output reference
- Usage examples
- Standalone script usage
- AI-assisted setup (coming soon)

### Quick Start

**For new adopters:**
1. Add workflow with `mode: setup`
2. Trigger manually to create PR
3. Review PR, complete TODOs
4. Merge and enable `mode: maintain`

**For existing adopters:**
1. Add workflow with `mode: maintain`
2. Badge auto-updates on `.ai/` changes

## Workflow: validate-aicac.yml

This repo uses the action to maintain its own compliance:

```yaml
name: AICaC Maintenance

on:
  push:
    paths: ['.ai/**']

jobs:
  maintain:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v3
      - uses: ./.github/actions/aicac-adoption
        with:
          mode: maintain
```

## Scripts

The action includes three Python scripts (can be used standalone):

- **bootstrap.py** - Create `.ai/` structure
- **validate.py** - Check compliance
- **update_badge.py** - Update README badge

See [actions/aicac-adoption/README.md](actions/aicac-adoption/README.md) for usage.

## Contributing

Ideas for enhancement:
- OpenAI/Anthropic API integration for AI-assisted setup
- IDE/editor plugins
- Pre-commit hooks
- More project type detection

Open issues or PRs at [AICaC repository](https://github.com/eFAILution/AICaC)!
