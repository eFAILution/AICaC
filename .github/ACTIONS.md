# GitHub Integrations

GitHub Actions for AICaC adoption and maintenance.

## Action: aicac-adoption

A comprehensive GitHub Action that helps projects adopt and maintain AICaC compliance.

### Smart Auto-Mode Detection (Recommended)

The action automatically detects whether to bootstrap or maintain based on `.ai/` directory presence:

```yaml
name: AICaC Adoption

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  aicac:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v3

      - name: Check if .ai exists
        id: check
        run: |
          if [ -d ".ai" ]; then
            echo "mode=maintain" >> $GITHUB_OUTPUT
          else
            echo "mode=setup" >> $GITHUB_OUTPUT
          fi

      - uses: eFAILution/AICaC/.github/actions/aicac-adoption@v0.1.0
        with:
          mode: ${{ steps.check.outputs.mode }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          update-badge: 'true'
```

**Benefits:**
- One workflow for entire lifecycle
- No manual mode switching needed
- Automatically creates PR when .ai/ missing
- Validates and maintains after adoption

### Manual Mode Selection

You can also explicitly set the mode:

#### 1. Setup Mode - Bootstrap Adoption
Creates a PR to adopt AICaC in projects without `.ai/` directory:

```yaml
- uses: eFAILution/AICaC/.github/actions/aicac-adoption@v0.1.0
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
- uses: eFAILution/AICaC/.github/actions/aicac-adoption@v0.1.0
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

**Prerequisites:**
1. Enable Actions to create PRs in your repository:
   - Go to: **Settings** > **Actions** > **General**
   - Scroll to **Workflow permissions**
   - Check: **"Allow GitHub Actions to create and approve pull requests"**
   - Click **Save**

**Setup:**
1. Add the workflow above to `.github/workflows/aicac.yml`
2. Commit and push to trigger the workflow

**What happens:**
- **First run** (no .ai/): Creates PR to bootstrap adoption
- **After PR merge**: Automatically validates and maintains
- **On changes**: Updates badge to reflect compliance level

**Manual Mode Selection:**
- Use `mode: setup` to force PR creation
- Use `mode: maintain` to force validation only
- Useful for debugging or custom workflows

## Complete Workflow Example

Save this as `.github/workflows/aicac.yml` in your repository:

```yaml
name: AICaC Adoption

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
  workflow_dispatch:

jobs:
  aicac:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v3

      - name: Check if .ai directory exists
        id: check-aicac
        run: |
          if [ -d ".ai" ]; then
            echo "mode=maintain" >> $GITHUB_OUTPUT
            echo "📁 .ai/ directory found - running in maintain mode"
          else
            echo "mode=setup" >> $GITHUB_OUTPUT
            echo "🚀 .ai/ directory not found - running in setup mode"
          fi

      - name: Run AICaC Action
        uses: eFAILution/AICaC/.github/actions/aicac-adoption@v0.1.0
        with:
          mode: ${{ steps.check-aicac.outputs.mode }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          update-badge: 'true'
```

**What happens:**
1. First run (no .ai/): Creates PR to bootstrap adoption
2. After PR merge: Validates and maintains badge automatically
3. On changes: Updates badge to reflect compliance level

## Scripts

The action includes three Python scripts (can be used standalone):

- **bootstrap.py** - Create `.ai/` structure
- **validate.py** - Check compliance
- **update_badge.py** - Update README badge

See [actions/aicac-adoption/README.md](actions/aicac-adoption/README.md) for usage.

## Troubleshooting

### Error: "GitHub Actions is not permitted to create or approve pull requests"

**Cause:** Repository workflow permissions not configured.

**Solution:**
1. Go to repository **Settings** > **Actions** > **General**
2. Under **Workflow permissions**, enable:
   - ✅ "Allow GitHub Actions to create and approve pull requests"
3. Click **Save**
4. Re-run the workflow

### Badge not updating

**Cause:** Workflow not triggering on changes.

**Solution:**
- Ensure workflow triggers include `push` on your main branch
- Check that `update-badge: 'true'` is set
- Verify `contents: write` permission is granted

### Action runs but nothing happens

**Cause:** Mode detection might be incorrect.

**Solution:**
- Check workflow logs for mode detection output
- Verify `.ai/` directory presence
- Try manual mode: `mode: setup` or `mode: maintain`

## Contributing

Ideas for enhancement:
- OpenAI/Anthropic API integration for AI-assisted setup
- IDE/editor plugins
- Pre-commit hooks
- More project type detection

Open issues or PRs at [AICaC repository](https://github.com/eFAILution/AICaC)!
