# Router recipe — answer a question using AICaC selective loading

When a user asks a project-context question in a repo that has `.ai/`:

## Step 1: cheap discovery (≤1K tokens)

Read **one** of these (whichever is smaller / more available):
1. `AGENTS.md` — authored router table
2. `.ai/index.yaml` — auto-generated key index
3. The top 5-10 lines of each `.ai/*.yaml` (look for `summary:` field)

## Step 2: classify the intent

| User intent heuristic                                        | File to load          |
|--------------------------------------------------------------|-----------------------|
| "what is this project" / "how to run" / "deps" / "entry"     | `context.yaml`        |
| "how does X work" / "architecture" / "components" / "flow"   | `architecture.yaml`   |
| "how do I do X" / "add Y" / "run Z"                          | `workflows.yaml`      |
| "why" / "rationale" / "trade-off" / "ADR"                    | `decisions.yaml`      |
| error message / "fix" / "debug" / "troubleshoot"             | `errors.yaml`         |

If ambiguous, bias toward `context.yaml` first (smallest, often contains the
answer or points to the right file via `context_modules`).

## Step 3: direct lookup

Each v2.0 file is a dict keyed by stable id:
- `architecture.yaml::components.<component_id>`
- `workflows.yaml::workflows.<workflow_id>`
- `decisions.yaml::decisions.<adr_id>` (e.g. `ADR-001`)
- `errors.yaml::errors.<error_id>`

Scan `.ai/index.yaml::keys` for id candidates that fuzzy-match the query
before reading the full file. This avoids loading `workflows.yaml` just to
discover none of its workflows matches.

## Step 4: answer and cite

Cite by `path::key`, e.g. `.ai/workflows.yaml::workflows.add_scanner`. Users
can then navigate directly to the source.

## Anti-patterns to avoid

- **Loading all `.ai/` files upfront.** Defeats the point of the convention.
  Measured cost: 3× README on this repo. If you already did this, stop and
  restart the answer from the router.
- **Loading README.md + AGENTS.md + every `.ai/` file.** Worst case. Do not
  do this unless the user explicitly asks for a full repo overview.
- **Ignoring cross-refs.** If `workflows.yaml::add_scanner.touches_components`
  lists `scanner_registry`, load that one component from `architecture.yaml`,
  not the whole file.

## When no `.ai/` exists

If the user is in a repo without `.ai/`, offer to bootstrap via
[`bootstrap.md`](bootstrap.md) — but only if they've asked a project-context
question recently. Do not proactively suggest AICaC on every unrelated query.
