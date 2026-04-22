# AI Context as Code (AICaC)

**A Structured Approach to AI-Readable Project Documentation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Status: Draft](https://img.shields.io/badge/Status-Draft-yellow.svg)]()
[![AICaC](https://img.shields.io/badge/AICaC-Comprehensive-success.svg)](https://github.com/eFAILution/AICaC)

## Overview

AICaC defines the `.ai/` directory convention: structured YAML files,
validated against [JSON Schemas](spec/v2/), that describe a project's context
in a form AI coding assistants can query directly.

**The problem:** AI coding assistants parse prose documentation linearly to
understand codebases. Greedy tools load everything they find, which scales
poorly.

**The approach:** Pair a small router (`AGENTS.md`) with per-topic structured
files (`.ai/context.yaml`, `.ai/architecture.yaml`, `.ai/workflows.yaml`,
`.ai/decisions.yaml`, `.ai/errors.yaml`) so tools can load only what the
current query needs.

**Current status:** Specification v2.0, JSON Schemas, a validator with
cross-reference checks, a bootstrap/maintenance GitHub Action, and a Claude
Code skill at [`.claude/skills/aicac/`](.claude/skills/aicac/) that teaches
agents to route instead of loading everything.

## Does it actually save tokens?

**It depends entirely on whether the AI tool follows the router.** Measured
on this repository (details in [validation/examples/EXAMPLE_RESULTS.md](validation/examples/EXAMPLE_RESULTS.md)):

| Format                           | Tokens | vs README | vs AGENTS.md |
|----------------------------------|-------:|----------:|-------------:|
| README only                      |    859 | baseline  | -34%         |
| README + AGENTS.md               |  1,299 | +51%      | baseline     |
| README + AGENTS.md + all `.ai/`  |  3,569 | +316%     | +175%        |
| Router-selective load            |  1,059 | +23%      | **-18%**     |

Per-query-category wins differ sharply:

- **Information-retrieval queries** (what's the dev command, entry point,
  dependencies): router-selective is **-51% vs AGENTS.md**.
- **Architecture / workflow queries**: within ~5% of AGENTS.md. Wins would
  likely grow on larger projects but that needs cross-repo replication.

### Live Claude pilot (n=12)

A small sub-agent-based live run ([`results/2026-04-live-claude-pilot.md`](validation/examples/results/2026-04-live-claude-pilot.md))
gives an early read on *answer quality*, not just token count:

| Format            | Accuracy  | Context tokens | Notes                                |
|-------------------|----------:|---------------:|--------------------------------------|
| README_ONLY       | 25%       | 859            | Answered only the one "how-to" that prose covered |
| AGENTS_ONLY       | 50%       | 1,299          | *Helpfully* failed by naming the `.ai/` file it needed |
| AICAC_SELECTIVE   | **100%**  | 1,106          | 15% fewer tokens than AGENTS.md, twice the accuracy |

Caveat: n=1 per cell; publication-grade numbers need ≥30 trials via
`performance_measurement.py` against a real API.

**Honest headline:** AICaC without a router makes things worse. With the
router pattern demonstrated in [`sample-project/AGENTS.md`](validation/examples/sample-project/AGENTS.md),
the current pilot data shows it wins on both token count and answer
accuracy.

*Prior versions of this README cited a "40-60% token reduction" figure that
was not empirically grounded. v2.0 replaces that claim with the measurements
above. See [EXAMPLE_RESULTS.md](validation/examples/EXAMPLE_RESULTS.md) for
methodology and limitations.*

## Quick example

**Prose:**
```markdown
To add a new scanner, first create a class in the src/scanners/ directory that
inherits from BaseScanner. Then register it in the scanner_registry.py file.
Make sure to add unit tests in tests/scanners/.
```

**AICaC (v2.0):**
```yaml
# .ai/workflows.yaml
version: "2.0"
workflows:
  add_scanner:
    description: Add a new security scanner integration
    steps:
      - action: create_class
        location: src/scanners/
        inherits: BaseScanner
      - action: register
        file: scanner_registry.py
      - action: add_tests
        location: tests/scanners/
    touches_components: [scanner_registry]
```

The AI asks "how do I add a scanner?" → router picks `workflows.yaml` →
direct lookup of the `add_scanner` key. No prose parsing.

## Repository structure

```
AICaC/
├── README.md                           # This file
├── AGENTS.md                           # Router that teaches tools to selectively load .ai/
├── BADGES.md                           # Badge usage guide
├── ai-context-as-code-whitepaper.md    # Full specification narrative
├── .ai/                                # This repo's own .ai/ (v2.0)
├── spec/
│   └── v2/                             # JSON Schemas for every file
├── .claude/skills/aicac/               # Claude Code skill: router / bootstrap / validate / sync
├── .github/
│   ├── actions/aicac-adoption/         # Composite action: bootstrap, validate, badge, TOON
│   └── workflows/validate-aicac.yml    # CI for this repo
└── validation/
    ├── README.md
    ├── docs/                           # Methodology, quick-start, publication roadmap
    ├── scripts/                        # token_measurement.py, performance_measurement.py, yaml_to_toon.py
    └── examples/
        ├── EXAMPLE_RESULTS.md          # Real measurement results, honestly framed
        ├── results/                    # Committed raw JSON results
        └── sample-project/             # Minimal .ai/ + router AGENTS.md example
```

## Getting started

### Use AICaC in your project

**Option 1: Claude Code skill (interactive)**

Clone this repo and point Claude Code at it, or copy `.claude/skills/aicac/`
into your own repo. When Claude Code sees `.ai/` or is asked to adopt AICaC,
it will bootstrap, validate, and keep the files in sync.

**Option 2: GitHub Action (automated)**

```yaml
# .github/workflows/aicac.yml
- uses: eFAILution/AICaC/.github/actions/aicac-adoption@main
  with:
    mode: setup  # or: maintain
```

**Option 3: Manual**

```bash
python3 .github/actions/aicac-adoption/scripts/bootstrap.py /path/to/project
python3 .github/actions/aicac-adoption/scripts/validate.py /path/to/project
```

### Validate

```bash
pip install pyyaml jsonschema
python3 .github/actions/aicac-adoption/scripts/validate.py .
```

The validator checks, in order:
1. Required files present (`.ai/context.yaml`)
2. JSON Schema conformance per file (`spec/v2/*.schema.json`)
3. Cross-references (workflows → components, decisions → components, ADR supersession)
4. Content-quality heuristics (rejects majority-TODO files)

### Measure

```bash
pip install -r validation/requirements.txt
make measure-all
```

Writes real token counts to `experiments/results.json`.

## The `.ai/` directory (v2.0)

```
project-root/
├── README.md
├── AGENTS.md                    # Router — tells AI tools which .ai/ file to load per intent
└── .ai/
    ├── context.yaml             # Project metadata and routing map (REQUIRED)
    ├── architecture.yaml        # Components, dependencies, data flow
    ├── workflows.yaml           # Common tasks with exact commands
    ├── decisions.yaml           # ADRs keyed by id
    ├── errors.yaml              # Error patterns keyed by id
    └── index.yaml               # Auto-generated: token-cheap routing keys
```

### Canonical shape (v2.0)

Every multi-entry file is a **dict keyed by stable id** (component_id,
workflow_id, ADR id, error id). Direct lookup is token-cheap, ids are stable
cross-reference targets, and merge conflicts stay local.

v1.x list forms (`components: [- name: api, ...]`) are accepted with a
deprecation warning. `migrate_v2.py` rewrites them automatically.

### Principles

1. **Structured over prose** — YAML/JSON, not Markdown
2. **Modular** — one concern per file
3. **Router-first** — AGENTS.md teaches tools *which* file to load
4. **Graceful degradation** — works alongside existing docs
5. **Schema-validated** — every file must pass `spec/v2/*.schema.json`
6. **Version-controlled** — evolves with code

## Compliance levels & badge

| Level         | Requirements                                   |
|---------------|------------------------------------------------|
| Minimal       | Valid `.ai/context.yaml`                       |
| Standard      | `context.yaml` + 2 optional files              |
| Comprehensive | `context.yaml` + all 4 optional files          |

Files that are majority-TODO don't count. See [BADGES.md](BADGES.md).

## Documentation

- **[Whitepaper](ai-context-as-code-whitepaper.md)** — full narrative
- **[Spec README](spec/README.md)** — schemas and migration guide
- **[Validation methodology](validation/docs/testing-framework.md)**
- **[Quick start](validation/docs/quick-start.md)**
- **[Publication roadmap](validation/docs/publication-roadmap.md)**
- **[Claude Code skill](.claude/skills/aicac/SKILL.md)**

## Status & roadmap

**v0.4.0 — Spec v2.0** (current): JSON Schemas, cross-ref validator, honest
empirical framing, Claude Code skill.

**Near-term:**
- Cross-repository measurement (≥5 production projects)
- Response-quality experiments via `performance_measurement.py`
- Publish schemas at `aicac.dev` for external consumption

**Long-term:**
- Native `.ai/` support in AI coding tools (GitHub Copilot, Cursor, etc.)
- IDE extensions for authoring and linting

## Contributing

Specification proposals, empirical replication, example implementations,
and tooling improvements all welcome. Issues and PRs at [GitHub](https://github.com/eFAILution/AICaC/issues).

## License

- **Code** (validation scripts, action, skill): [MIT](LICENSE-CODE)
- **Specification & docs**: [CC BY-SA 4.0](LICENSE-DOCS)

## Citation

```bibtex
@misc{aicac2026,
  title={AI Context as Code: A Structured, Schema-Validated Approach to AI-Readable Project Documentation},
  author={eFAILution},
  year={2026},
  howpublished={\url{https://github.com/eFAILution/AICaC}},
  note={v0.4.0 — spec v2.0}
}
```
