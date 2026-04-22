---
name: aicac
description: Use when the working directory contains a `.ai/` directory, or when the user asks to adopt AICaC (AI Context as Code), validate `.ai/` compliance, populate `.ai/` files, answer questions using AICaC structured context, or keep `.ai/` in sync after code changes. Routes queries to the single relevant `.ai/*.yaml` file (context/architecture/workflows/decisions/errors) using `AGENTS.md` + `.ai/index.yaml` rather than loading all documentation.
---

# AICaC Skill

Enables selective, router-driven loading of AICaC `.ai/` directories so that
Claude Code spends tokens on the right structured file instead of greedily
reading every docs file.

Canonical spec: `spec/v2/` JSON Schemas (dict-keyed-by-id shapes).

## Triggers

Prefer this skill when any of these is true:
- `.ai/` directory exists in the working tree
- User asks about adopting AICaC, validating `.ai/`, bootstrapping a
  `.ai/` structure, or migrating v1.x → v2.0
- User asks a project-context question ("how do I run tests?", "why FastAPI?",
  "fix this error") and an `.ai/` directory is available to route to
- User asks to keep `.ai/` in sync after a code change (new component,
  new workflow, ADR-worthy decision)

## Routing (the core behavior)

When `.ai/` is present, **read `AGENTS.md` first** (if it exists) — it
advertises the router table. Otherwise default to the mapping below.

Before loading a full file, read the `summary:` field (single line) and/or
`.ai/index.yaml` (tiny, lists available ids per file) to confirm you're
loading the right one.

| Query intent                                 | Load ONLY               |
|----------------------------------------------|-------------------------|
| Project overview, dev commands, entrypoints  | `.ai/context.yaml`      |
| Components, dependencies, data flow          | `.ai/architecture.yaml` |
| How-to, adding features, commands            | `.ai/workflows.yaml`    |
| Why decisions were made, trade-offs, ADRs    | `.ai/decisions.yaml`    |
| Errors, debugging, troubleshooting           | `.ai/errors.yaml`       |
| What keys/ids exist (cheap discovery)        | `.ai/index.yaml`        |

Do **not** load the other files unless the first file explicitly references
them (via `touches_components`, `affects_components`, `reference`, etc.).

## Capabilities

For any of the following user intents, follow the matching lazy-loaded recipe:

- **Bootstrap `.ai/` in a new project** → [`bootstrap.md`](bootstrap.md)
- **Validate `.ai/` compliance** → [`validate.md`](validate.md)
- **Answer a question using the router** → [`router.md`](router.md)
- **Keep `.ai/` in sync after a code change** → [`sync.md`](sync.md)
- **Migrate v1.x → v2.0** → [`migrate.md`](migrate.md)

Each recipe file is short; load only the one you need.

## Common guardrails

- **Never put secrets** in `.ai/` files. Reject suggestions to include API
  keys, internal IPs, or proprietary algorithms.
- **Every schema change** must touch: the schema file, the whitepaper, and
  at least one example (repo `.ai/` or `validation/examples/sample-project/`).
- **Cross-references** (`touches_components`, `affects_components`,
  `depends_on`, `superseded_by`) must resolve to real ids. The validator will
  reject typos and dangling references.
- **v2.0 is canonical.** When writing new files, use dict-keyed-by-id shape.
  When reading v1.x list-form files, offer migration via `migrate_v2.py`
  instead of hand-editing.

## Minimum-viable response

If you only have time/tokens for one thing: **run the validator and report the
compliance level** — it's cheap, gives the user a clear next action, and
surfaces broken cross-refs.

```bash
python3 .github/actions/aicac-adoption/scripts/validate.py .
```

## Schemas (for reference)

- [`schemas/context.schema.json`](schemas/context.schema.json)
- [`schemas/architecture.schema.json`](schemas/architecture.schema.json)
- [`schemas/workflows.schema.json`](schemas/workflows.schema.json)
- [`schemas/decisions.schema.json`](schemas/decisions.schema.json)
- [`schemas/errors.schema.json`](schemas/errors.schema.json)
- [`schemas/index.schema.json`](schemas/index.schema.json)

The skill's schemas are symlinked/copied from `spec/v2/` so external projects
that drop this skill in place still get correct validation shapes.
