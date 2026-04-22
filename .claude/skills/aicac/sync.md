# Sync recipe — keep `.ai/` in sync with code changes

When the user has just completed a code change that is likely to affect
`.ai/`, offer to update the relevant file(s) in the same PR.

## Change signals and which file to update

| You just did this                          | Update this file (and why)                       |
|--------------------------------------------|--------------------------------------------------|
| Added a new top-level `src/*/` directory   | `architecture.yaml` — add a component            |
| Added a new CLI command / API endpoint     | `workflows.yaml` — add an `add_<X>` workflow    |
| Changed a `package.json` script            | `context.yaml::common_tasks`                     |
| Renamed a component directory              | `architecture.yaml` + all cross-refs             |
| Switched a framework / made an ADR-worthy choice | `decisions.yaml` — new ADR                  |
| Fixed a recurring error users hit          | `errors.yaml` — add entry                        |
| Dropped a dependency                       | `architecture.yaml::dependencies`                |

## Minimal sync loop

1. Read the diff. Classify each changed hunk against the table above.
2. Load **only** the relevant `.ai/` file(s).
3. Make the smallest correct change.
4. Regenerate the index: `python3 .github/actions/aicac-adoption/scripts/generate_index.py .`
5. Validate: `python3 .github/actions/aicac-adoption/scripts/validate.py .`
6. Include the `.ai/` diff in the same commit/PR as the code change.

## What NOT to sync automatically

- **Internal refactors that don't cross component boundaries.** If you just
  renamed a private function, don't touch `.ai/`.
- **Whitespace / formatting changes.**
- **Generated files that already track the source** (`.ai/index.yaml` is
  auto-generated; update it explicitly but don't invent content for it).

## ADR creation heuristic

A change is ADR-worthy if at least two of these are true:
- It affects multiple components
- It's hard to reverse
- Reasonable engineers would pick a different option
- The rationale isn't visible from the code alone (e.g. "why not Flask?")

If ADR-worthy, add a new `ADR-NNN` entry with:
- `title`, `status: accepted`, `date: YYYY-MM`
- `context` — what was the situation
- `decision` — what we chose
- `rationale` — 2-5 bullet points
- `consequences.positive` / `consequences.negative`
- `affects_components` (validator-enforced cross-ref)

## Stale detection

If you spot a cross-reference to a component that no longer exists, flag it
to the user; don't silently delete it without confirming. Validator will catch
this in CI anyway.
