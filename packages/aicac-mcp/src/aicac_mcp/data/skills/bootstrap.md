# Bootstrap recipe — adopt AICaC in a project

## Detect project type

Read the following (in order, stopping on first match) to infer
`project.type`:

| Detected file               | Canonical type  | Primary language |
|-----------------------------|-----------------|------------------|
| `package.json`              | `web-app`       | javascript       |
| `pyproject.toml`            | `library`       | python           |
| `requirements.txt` only     | `cli`           | python           |
| `Cargo.toml`                | `cli`           | rust             |
| `go.mod`                    | `cli`           | go               |
| `Dockerfile` only           | `infrastructure`| <detect>         |
| `setup.py`                  | `library`       | python           |
| nothing canonical           | `other`         | <infer>          |

If ambiguous, ask the user. If `package.json` has `"main": "electron.js"` or
similar, prefer `desktop-app`.

## Generate `.ai/context.yaml`

Fields you must populate (not with TODOs — actually look):

- `project.name` — from `package.json.name`, `pyproject.toml::[project].name`,
  `Cargo.toml::[package].name`, or the directory name.
- `project.type` — from the table above.
- `project.description` — from `package.json.description`, first paragraph of
  README.md, or **ask the user if unclear** (≥ 10 chars required).
- `summary` — one-sentence router-friendly summary (≤ 280 chars). Derive from
  description + primary feature.
- `entrypoints` — scan for `main`, `bin`, known entry files (`src/index.js`,
  `src/main.py`, `cmd/*/main.go`, `src/main.rs`). At least one required.
- `common_tasks` — extract from `package.json.scripts`,
  `Makefile`, `noxfile.py`, `justfile`. At least one required.

## Generate `.ai/architecture.yaml` (optional but recommended)

Scan the top-level of `src/` (or language equivalent). One component per
directory under `src/`. Purpose = infer from directory name / file contents.
Use the **dict-keyed-by-id** shape from v2.0.

```yaml
version: "2.0"
summary: <one-line>
components:
  <component_id>:
    location: src/<component_id>/
    purpose: <inferred purpose>
    depends_on: [<other component ids>]
```

## Generate `.ai/workflows.yaml` (optional but recommended)

One workflow per `common_task` plus:
- `add_<primary_extension_point>` (e.g. `add_endpoint`, `add_command`,
  `add_model`) — look at one existing example in the repo and extract the
  steps.
- `run_tests`, `format_code`, `deploy` — if present in `package.json.scripts`
  / `Makefile`.

## Validate + badge

```bash
python3 .github/actions/aicac-adoption/scripts/validate.py .
python3 .github/actions/aicac-adoption/scripts/update_badge.py <LEVEL>
python3 .github/actions/aicac-adoption/scripts/generate_index.py .
```

Commit with:

```
chore: adopt AICaC v2.0 structured context
```

## Anti-patterns

- **Don't emit TODO-only files.** The validator rejects majority-TODO files
  under the content-quality heuristic. Either populate, or don't create the
  file yet.
- **Don't copy the whitepaper examples verbatim.** They reference non-existent
  components. Generate from the actual repo.
- **Don't skip `summary:`.** It's the field the router reads first; omitting
  it forces callers to load the full file.
