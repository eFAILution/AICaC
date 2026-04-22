# AI Assistant Instructions (AICaC repo)

This repository specifies and tools the **AI Context as Code (AICaC) v2.0**
convention. It dogfoods itself: `.ai/` holds structured YAML validated against
`spec/v2/` JSON Schemas.

## Router — load ONLY the relevant file

Each `.ai/*.yaml` has a top-level `summary:` field. Read `summary` first to
confirm you've picked the right file before loading the rest. The optional
`.ai/index.yaml` advertises available keys per file without loading content.

| Query intent                                          | Load this file only       |
|-------------------------------------------------------|---------------------------|
| Project overview, entrypoints, dev/test commands      | `.ai/context.yaml`        |
| Components, dependencies, data flow                   | `.ai/architecture.yaml`   |
| How to do X, adoption steps, migration, measurement   | `.ai/workflows.yaml`      |
| Why we did X, trade-offs, ADRs                        | `.ai/decisions.yaml`      |
| Errors, validation failures, troubleshooting          | `.ai/errors.yaml`         |
| Which ids/keys exist in each file                     | `.ai/index.yaml`          |

**Examples:**
- "How do I run the measurements?" → `.ai/workflows.yaml` → `run_token_measurement`
- "Why is v2.0 dict-keyed?" → `.ai/decisions.yaml` → `ADR-008`
- "What does v1.x list form look like?" → `.ai/errors.yaml` → `DEPRECATED_V1_LIST_FORM`
- "What commands can I run?" → `.ai/context.yaml` → `common_tasks`

## Working on this repo

- **Canonical spec lives in `spec/v2/`.** Every `.ai/*.yaml` must validate.
  Run: `python3 .github/actions/aicac-adoption/scripts/validate.py .`
- **Changes to schemas** must include: schema update, whitepaper update, and
  at least one example file update (this repo's `.ai/` and/or
  `validation/examples/sample-project/.ai/`).
- **Cross-references** (`touches_components`, `affects_components`,
  `depends_on`, `superseded_by`) are validator-enforced. Don't add a workflow
  referencing `api` if `api` isn't a component.
- **Token measurements**: `make measure-all`. Results go to
  `experiments/results.json`. Checked-in reference: `validation/examples/results/`.
- **Tests**: `cd .github/actions/aicac-adoption && pytest`
- **Claude Code skill**: [`.claude/skills/aicac/SKILL.md`](.claude/skills/aicac/SKILL.md)
  — the on-ramp for Claude Code users to route, bootstrap, validate, and keep
  `.ai/` in sync.

## Quick facts

- **Languages**: Python (tooling + validation), YAML (context files), Markdown
  (specification + docs).
- **Validator entry point**: `.github/actions/aicac-adoption/scripts/validate.py`
- **Bootstrap entry point**: `.github/actions/aicac-adoption/scripts/bootstrap.py`
- **Measurement entry point**: `validation/scripts/token_measurement.py`
- **Live AI performance measurement**: `validation/scripts/performance_measurement.py`
  (requires an API key — Ollama/Groq free tiers supported).

## Honesty norms

- Efficiency claims must be backed by [`validation/examples/EXAMPLE_RESULTS.md`](validation/examples/EXAMPLE_RESULTS.md)
  or follow-up experiments. Do **not** re-introduce unvalidated "40-60%"
  figures without data.
- Note tokenizer mode (exact vs approximate) when citing measurement numbers.
- `token_measurement.py` is deterministic; variance-based statistics (t-tests,
  Cohen's d) belong with `performance_measurement.py`.
