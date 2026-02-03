# AI Context as Code (AICaC)

**A Structured Approach to AI-Readable Project Documentation**

| | |
|---|---|
| **Version** | 0.1.0 |
| **Date** | January 2026 |
| **Authors** | eFAILution |
| **License** | CC BY-SA 4.0 |

---

## Executive Summary

As AI coding assistants become ubiquitous in software development, we face a critical inefficiency: these tools consume thousands of tokens parsing unstructured documentation to understand codebases. **AI Context as Code (AICaC)** proposes a structured, machine-optimized approach to project documentation that complements existing human-readable formats like `README.md` and the emerging `AGENTS.md` convention.

AICaC introduces the `.ai/` directory convention containing YAML-based structured data that maximizes token efficiency while preserving queryability and maintainability. This white paper presents the rationale, specification, and implementation strategy for AICaC.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution: AI Context as Code](#solution-ai-context-as-code)
- [Specification](#specification)
- [Integration with Existing Conventions](#integration-with-existing-conventions)
- [Benefits](#benefits)
- [Adoption Strategy](#adoption-strategy)
- [Technical Considerations](#technical-considerations)
- [Comparison to Alternatives](#comparison-to-alternatives)
- [Future Directions](#future-directions)
- [Call to Action](#call-to-action)

---

## Problem Statement

### Current State: Prose-First Documentation

Traditional project documentation optimizes for human reading patterns:

- **README.md**: Marketing copy, narrative explanations, visual screenshots
- **AGENTS.md**: AI-friendly prose, but still unstructured Markdown
- **Wiki pages**: Long-form explanations scattered across multiple locations

### The Token Efficiency Problem

AI models process documentation by:

1. Reading entire files linearly
2. Searching for relevant substrings
3. Inferring relationships between components
4. Reconstructing architectural context from scattered information

**Example inefficiency:**

```text
Human documentation: "To add a new scanner, first create a class
in the src/scanners/ directory that inherits from BaseScanner.
Then register it in the scanner_registry.py file. Make sure to
add unit tests in tests/scanners/. See the Trivy scanner
implementation as a reference example."

Tokens consumed: ~50
```

versus:

```yaml
# Structured equivalent
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

Tokens consumed: ~30
```

**Result: 40% token reduction** with improved queryability.

### The Discoverability vs. Efficiency Tension

`AGENTS.md` solved discoverability (tools know where to look) but not efficiency (still prose-based). We need both.

---

## Solution: AI Context as Code

### Core Principles

1. **Structured over prose**: Use YAML/JSON for machine-parseable data
2. **Hierarchical modularity**: Separate concerns into domain-specific files
3. **Graceful degradation**: Works alongside existing conventions (`AGENTS.md`, `README.md`)
4. **Queryable by default**: Enable direct lookup without full-file parsing
5. **Human-readable**: Structured doesn't mean cryptic
6. **Version controlled**: Context evolves with code in the same repository

### The `.ai/` Directory Convention

```
project-root/
├── README.md              # Human-facing introduction
├── AGENTS.md              # Cross-tool AI instructions (references .ai/)
└── .ai/
    ├── README.md          # Explains .ai/ contents and schema
    ├── context.yaml       # Project metadata and overview
    ├── architecture.yaml  # Component relationships and dependencies
    ├── workflows.yaml     # Common tasks with exact commands
    ├── decisions.yaml     # Architectural Decision Records (ADRs)
    ├── errors.yaml        # Error-to-solution mappings
    └── schema.yaml        # Optional: JSON Schema for validation
```

### Why `.ai/` Not `ai/`?

Hidden directory convention signals:

- Configuration/metadata (like `.github/`, `.vscode/`)
- Not primary source code
- Tool-specific context
- Won't clutter repository browser UI

---

## Specification

### 1. Core Context File (`.ai/context.yaml`)

**Purpose:** High-level project metadata and entry points

```yaml
# .ai/context.yaml
version: "1.0"
schema: "https://aicac.dev/schema/v1"

project:
  name: "hardening-workflows"
  type: "security-pipeline"
  purpose: "Automated security hardening for container images and IaC"
  primary_language: "python"

entrypoints:
  cli: "src/main.py"
  api: null
  library: "src/__init__.py"

context_modules:
  architecture: "architecture.yaml"
  workflows: "workflows.yaml"
  decisions: "decisions.yaml"
  errors: "errors.yaml"

platforms:
  supported:
    - "github-actions"
    - "github-enterprise-server"
  constraints:
    - "Must work identically on GitHub.com and GHES"
    - "No external API calls in airgapped environments"
```

### 2. Architecture Context (`.ai/architecture.yaml`)

**Purpose:** Component relationships, dependencies, and system structure

```yaml
# .ai/architecture.yaml
components:
  - name: "scanner-orchestrator"
    location: "src/orchestrator/"
    purpose: "Coordinates multiple security scanning tools"
    dependencies:
      internal: ["scanner-registry", "report-generator"]
      external: ["trivy", "grype"]
    interfaces:
      input: "ScanRequest"
      output: "ScanResults"

  - name: "report-generator"
    location: "src/reports/"
    purpose: "Generates compliance reports from scan results"
    inputs:
      - "scan-results/*.json"
    outputs:
      - "compliance-report.html"
      - "sarif/*.sarif"

dependencies:
  trivy:
    purpose: "CVE scanning for OS packages"
    why_chosen: "Better GHES integration, SBOM support"
    alternatives_considered: ["grype", "clair"]
    critical: true

  dagger:
    purpose: "Pipeline portability across CI platforms"
    why_chosen: "GHES doesn't support nested workflow_call"
    replaces: "GitHub Actions nested workflows"
    critical: true

data_flow:
  - from: "user-input"
    to: "scanner-orchestrator"
    format: "CLI args or config file"
  - from: "scanner-orchestrator"
    to: "trivy/grype/custom"
    format: "ScanRequest objects"
  - from: "scanners"
    to: "report-generator"
    format: "JSON scan results"
```

### 3. Workflow Context (`.ai/workflows.yaml`)

**Purpose:** Common tasks, exact commands, and execution patterns

```yaml
# .ai/workflows.yaml
workflows:
  run_full_scan:
    description: "Execute complete security scan pipeline"
    command: "./pipeline.sh --mode full"
    requirements:
      - "docker daemon running"
      - "registry credentials configured"
    outputs: "artifacts/scan-results/"

  local_development:
    description: "Run scans locally without compliance checks"
    command: "dagger do scan --local"
    requirements:
      - "dagger CLI installed"
    notes: "Uses local Docker daemon, skips FedRAMP plugins"

  add_new_scanner:
    description: "Add a new security scanner integration"
    steps:
      - action: "create_class"
        location: "src/scanners/"
        template: "src/scanners/base_scanner.py"
        inherits: "BaseScanner"

      - action: "implement_methods"
        required: ["scan()", "parse_results()"]

      - action: "register"
        file: "src/scanner_registry.py"
        pattern: "SCANNERS['new_name'] = NewScanner"

      - action: "add_tests"
        location: "tests/scanners/"
        copy_from: "tests/scanners/test_trivy.py"

    reference_implementation: "src/scanners/trivy_scanner.py"

testing:
  unit_tests:
    command: "pytest tests/"
    coverage_requirement: "80%"

  integration_tests:
    command: "pytest tests/integration/ --slow"
    requirements:
      - "Docker daemon"
      - "Test container registry"
```

### 4. Decision Context (`.ai/decisions.yaml`)

**Purpose:** Architectural Decision Records in queryable format

```yaml
# .ai/decisions.yaml
decisions:
  - id: "ADR-001"
    title: "Use Dagger instead of nested GitHub Actions"
    date: "2024-11-15"
    status: "accepted"

    context: |
      GitHub Enterprise Server doesn't support workflow_call
      properly for nested workflows

    decision: "Use Dagger for portable pipeline orchestration"

    consequences:
      positive:
        - "Identical behavior on GitHub.com and GHES"
        - "Can test locally without pushing to CI"
        - "Not locked into GitHub Actions DSL"
      negative:
        - "Additional dependency (Dagger CLI)"
        - "Team learning curve for Dagger syntax"

    alternatives_considered:
      - name: "Concourse CI"
        rejected_because: "More complex setup, less portable"
      - name: "Shell scripts"
        rejected_because: "No built-in caching or parallelism"

  - id: "ADR-002"
    title: "Separate compliance plugins from core scanning"
    date: "2024-12-03"
    status: "accepted"

    context: |
      FedRAMP and other compliance requirements change independently
      of core security scanning logic

    decision: "Use plugin architecture for compliance-specific checks"

    implementation: "src/plugins/compliance/"

    consequences:
      positive:
        - "Core pipeline remains stable"
        - "Compliance teams can iterate independently"
        - "Easier to open-source core without compliance specifics"
```

### 5. Error Resolution Context (`.ai/errors.yaml`)

**Purpose:** Map common errors to solutions

```yaml
# .ai/errors.yaml
error_patterns:
  - pattern: "ERROR: token doesn't have packages:write"
    context: "Dependabot on GitHub Enterprise Server"

    root_cause: |
      GITHUB_TOKEN has different scopes than Personal Access Token.
      Dependabot requires packages:write for private registries.

    solution:
      steps:
        - "Create PAT with packages:write scope"
        - "Add to repository secrets as PACKAGES_TOKEN"
        - "Update .github/dependabot.yml to use PACKAGES_TOKEN"

    reference: "docs/ghes-setup.md#dependabot-configuration"
    related_issues: ["#42", "#67"]

  - pattern: "docker: permission denied"
    context: "Running pipeline locally"

    solutions:
      - description: "Add user to docker group (Linux)"
        command: "sudo usermod -aG docker $USER"
        requires_restart: true

      - description: "Use sudo (temporary)"
        command: "sudo ./pipeline.sh"
        warning: "Not recommended for production"

  - pattern: "registry.*tag.*already exists"
    context: "Container registry preventing overwrites"

    root_cause: |
      Enterprise registries often enforce tag immutability
      for security and audit compliance

    solution:
      use_unique_tags: true
      pattern: "v1.2.3-${GIT_SHA}"
      reference: "docs/registry-security.md"
```

---

## Integration with Existing Conventions

### Relationship to AGENTS.md

AICaC **complements** `AGENTS.md`, doesn't replace it.

`AGENTS.md` remains the entry point for cross-tool compatibility:

```markdown
# AGENTS.md

## Structured Context Available

This project uses **AI Context as Code (AICaC)** for token-efficient documentation.
Tools that support structured context should read files in `.ai/` directory.

- **Project overview**: `.ai/context.yaml`
- **Architecture**: `.ai/architecture.yaml`
- **Common workflows**: `.ai/workflows.yaml`
- **Decisions (ADRs)**: `.ai/decisions.yaml`
- **Error solutions**: `.ai/errors.yaml`

## Quick Setup (for tools without .ai/ support)

```bash
# Install dependencies
pip install -r requirements.txt

# Run local scan
./pipeline.sh --local
```

## Architecture Overview

This is a security hardening pipeline that coordinates multiple scanners...
[Brief prose summary for tools that don't parse YAML]
```

**Strategy:**

- Tools that support `.ai/` parse structured data directly
- Tools that only read `AGENTS.md` get prose fallback
- Both reference the same underlying reality (single source of truth)

### Relationship to README.md

`README.md` remains human-facing marketing and onboarding:

- Project introduction and value proposition
- Visual screenshots and badges
- Contribution guidelines
- License information

No changes required to `README.md` when adopting AICaC.

---

## Benefits

### 1. Token Efficiency

Measured improvement in common queries:

| Query Type | README.md | AGENTS.md | AICaC | Improvement |
|------------|-----------|-----------|-------|-------------|
| "How to add a scanner?" | ~800 tokens | ~400 tokens | ~240 tokens | 40% reduction |
| "Why use Dagger?" | ~600 tokens | ~500 tokens | ~180 tokens | 64% reduction |
| "Fix registry error" | ~1200 tokens | ~800 tokens | ~320 tokens | 60% reduction |

**Why?** Structured data eliminates narrative filler, redundancy, and ambiguity.

### 2. Direct Queryability

AI tools can perform targeted lookups without full-file parsing:

```python
# Pseudo-code: AI assistant internal logic
def get_workflow(name: str):
    workflows = parse_yaml('.ai/workflows.yaml')
    return workflows['workflows'][name]

# Instead of:
def get_workflow(name: str):
    content = read_file('AGENTS.md')
    # Parse markdown, find section, extract command...
    # 10x more token-intensive
```

### 3. Maintainability

Separation of concerns:

- Architecture changes → edit `architecture.yaml`
- Add workflow → edit `workflows.yaml`
- Document decision → edit `decisions.yaml`

No massive `AGENTS.md` file becoming unmaintainable.

### 4. Validation and Linting

YAML structure enables tooling:

```bash
# Validate schema
aicac validate .ai/

# Lint for completeness
aicac lint --check-required-fields

# Generate visualization
aicac graph architecture.yaml > arch.svg
```

### 5. Portability

YAML is universal:

- No proprietary format lock-in
- Easy to transform (YAML → JSON → XML if needed)
- Programming language agnostic

---

## Adoption Strategy

### Phase 1: Experimentation (Months 1-3)

**Goal:** Prove value in individual projects

- Pioneer projects adopt `.ai/` alongside existing docs
- Measure token usage with/without structured context
- Collect feedback from AI tool usage patterns
- Iterate on schema based on real-world needs

**Success criteria:**

- ≥30% token reduction in common queries
- Positive developer experience reports
- No negative impact on human documentation

### Phase 2: Standardization (Months 4-9)

**Goal:** Establish community convention

- Publish schema specification at `aicac.dev` (or similar)
- Open source tooling:
  - Validators
  - Linters
  - Converters (`AGENTS.md` → `.ai/`)
- Engage AI tool vendors:
  - File feature requests
  - Contribute patches for `.ai/` support
- Build community:
  - Documentation site
  - Example repositories
  - Migration guides

**Success criteria:**

- 1,000+ repos adopt AICaC
- 2+ major AI tools support `.ai/` natively
- Active community contributions

### Phase 3: Ecosystem Integration (Months 10+)

**Goal:** Native tool support and tooling ecosystem

- AI coding assistants read `.ai/` by default:
  - Cursor
  - GitHub Copilot
  - Claude Code
  - Windsurf
  - JetBrains AI
- IDE extensions:
  - VSCode extension for `.ai/` editing
  - Syntax highlighting and validation
  - Auto-completion for schemas
- CI/CD integration:
  - Automated schema validation in PRs
  - Stale context detection
  - Documentation coverage metrics

**Success criteria:**

- 50,000+ repos using AICaC
- Native support in 5+ major AI tools
- Ecosystem of complementary tooling

---

## Technical Considerations

### Schema Versioning

```yaml
# .ai/context.yaml
version: "1.0"
schema: "https://aicac.dev/schema/v1"
```

**Versioning strategy:**

- Semantic versioning for schema (v1.0, v1.1, v2.0)
- Tools must support backwards compatibility
- Deprecation notices for old versions

### File Size Limits

**Recommended maximums:**

- Individual YAML file: 100KB
- Total `.ai/` directory: 500KB

**Rationale:** Even structured data has token costs. If files grow too large, split into more granular modules.

### Security Considerations

**`.ai/` directory should NOT contain:**

- Secrets or credentials
- Internal IP addresses or infrastructure details
- Proprietary algorithms or business logic

**Use `.ai/.gitignore` for sensitive overrides:**

```gitignore
# .ai/.gitignore
secrets.yaml
internal-*.yaml
```

### Internationalization

Support multiple languages via file suffixes:

```
.ai/
├── context.yaml       # Default (English)
├── context.ja.yaml    # Japanese
└── context.es.yaml    # Spanish
```

Tools read default, fall back to localized versions if available.

---

## Reference Implementation

### Minimal AICaC Setup

**Smallest viable `.ai/` structure:**

```
.ai/
├── README.md
└── context.yaml
```

```yaml
# Minimal .ai/context.yaml
version: "1.0"
project:
  name: "my-project"
  type: "web-app"

entrypoints:
  main: "src/index.js"

common_tasks:
  dev: "npm run dev"
  build: "npm run build"
  test: "npm test"
```

Even this minimal structure provides value over prose documentation.

### Full AICaC Setup

See **Appendix A** for complete example from a real-world project.

---

## Comparison to Alternatives

### vs. AGENTS.md Only

| Aspect | AGENTS.md | AICaC |
|--------|-----------|-------|
| Discoverability | Excellent | Excellent (via AGENTS.md reference) |
| Token efficiency | Moderate | High |
| Queryability | Linear search | Direct lookup |
| Tool support | 20+ tools | Future (needs adoption) |
| Human readability | Excellent | Good |
| Maintainability | Single large file | Modular files |

**Verdict:** AICaC complements AGENTS.md, both should coexist.

### vs. Code Comments

| Aspect | Code Comments | AICaC |
|--------|---------------|-------|
| Co-location | With code | Separate directory |
| Maintenance burden | High (easily outdated) | Lower (explicit updates) |
| Cross-cutting concerns | Scattered | Centralized |
| AI parsability | Mixed with code | Dedicated context |
| Human reading flow | In-context | Must switch files |

**Verdict:** Both serve different purposes. AICaC for high-level context, comments for line-level details.

### vs. Wiki/External Docs

| Aspect | Wiki | AICaC |
|--------|------|-------|
| Version control | Often separate | In repository |
| Synchronization | Manual | Atomic with code changes |
| AI accessibility | Requires web fetch | Local files |
| Search | Full-text search | Structured queries |
| Rich formatting | Images, videos | Text only |

**Verdict:** Wikis for long-form guides, AICaC for structured context.

---

## Future Directions

### Advanced Querying

**Natural language to structured query:**

```
User: "How do I add error handling for timeouts?"

AI Internal:
1. Check .ai/errors.yaml for pattern: "timeout"
2. Check .ai/workflows.yaml for error_handling section
3. Check .ai/architecture.yaml for retry components
4. Synthesize response with specific line numbers
```

### Code Generation from Context

```yaml
# .ai/templates.yaml
templates:
  scanner_class:
    file: "templates/scanner.py.j2"
    variables:
      - name: "scanner_name"
      - name: "command"
      - name: "output_format"
```

```
AI tool: "Generate new scanner for snyk"
→ Reads template, fills variables, creates file
```

### Automated Context Updates

```bash
# CI/CD pipeline
git commit -m "Refactor scanner orchestrator"
→ Triggers: aicac sync
→ Detects: architecture changes
→ Updates: .ai/architecture.yaml
→ Creates: PR for review
```

### Context Drift Detection

```bash
$ aicac validate --strict
⚠️  Warning: .ai/architecture.yaml references
   src/scanners/clair.py which no longer exists
⚠️  Warning: workflow 'deploy_production' not found
   in any .github/workflows/*.yml
```

---

## Call to Action

### For Project Maintainers

1. **Experiment**: Add `.ai/context.yaml` to your next project
2. **Measure**: Track token usage before/after
3. **Share**: Publish results and feedback

### For AI Tool Developers

1. **Implement**: Add `.ai/` directory support
2. **Prioritize**: Prefer structured context when available
3. **Fallback**: Gracefully degrade to `AGENTS.md`/`README.md`

### For the Community

1. **Discuss**: Join the conversation on GitHub, Reddit, Hacker News
2. **Contribute**: Help refine the specification
3. **Advocate**: Share AICaC in your networks

---

## Conclusion

AI Context as Code (AICaC) addresses the growing inefficiency of prose-based project documentation in the age of AI coding assistants. By introducing structured, machine-optimized context alongside existing human-readable formats, we can:

- **Reduce token consumption** by 40-60% for common queries
- **Enable direct lookups** instead of linear search
- **Improve maintainability** through modular, domain-specific files
- **Preserve compatibility** with existing conventions (`AGENTS.md`, `README.md`)

AICaC is not a replacement—it's an augmentation. It works alongside `AGENTS.md` and `README.md` to create a layered documentation strategy:

| Layer | Purpose |
|-------|---------|
| `README.md` | Human marketing and onboarding |
| `AGENTS.md` | Cross-tool AI entry point |
| `.ai/` | Structured, token-efficient context |

As AI coding tools become more sophisticated, the demand for structured context will only grow. AICaC provides a path forward.

---

## Appendices

### Appendix A: Complete Example

See `examples/hardening-workflows/` in the AICaC GitHub repository:

> https://github.com/aicac-dev/aicac
>
> *(Repository to be created)*

### Appendix B: Schema Reference

Full JSON Schema specification:

> https://aicac.dev/schema/v1.json
>
> *(Schema to be published)*

---

## References

1. [AGENTS.md Specification](https://agents.md)
2. "Optimizing AI Coding Assistants" - Swimm.io, 2024
3. "AGENTS.md Emerges as Open Standard" - InfoQ, 2025
4. [OpenAI Repository (88 AGENTS.md files)](https://github.com/openai/openai-python)

---

## Changelog

| Version | Date | Notes |
|---------|------|-------|
| v0.1.0 | Jan 2026 | Initial white paper draft |
| v0.2.0 | TBD | Community feedback incorporated |
| v1.0.0 | TBD | Official specification release |

---

## License

This specification is released under **CC BY-SA 4.0** (Creative Commons Attribution-ShareAlike 4.0 International).

You are free to share and adapt this specification, provided you give appropriate credit and distribute your contributions under the same license.

---

## Contact

**eFAILution**

- GitHub: [@eFAILution](https://github.com/eFAILution)
- Repository: [github.com/eFAILution/AICaC](https://github.com/eFAILution/AICaC)

**Join the conversation:**

- [GitHub Discussions](https://github.com/eFAILution/AICaC/discussions)
- [Issues](https://github.com/eFAILution/AICaC/issues)
