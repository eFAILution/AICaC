# In-harness v2.0 validation protocol (deferred)

Draft protocol for replicating the n=12 pilot at larger scale using a Claude
Code session as the test harness, for cases where direct API access isn't
available (e.g. Claude Enterprise without self-serve API tokens).

**Status**: Drafted 2026-04-21, execution deferred pending token/time budget.

## Why this exists

The n=12 pilot (`validation/examples/results/2026-04-live-claude-pilot.md`)
showed `AICAC_SELECTIVE` answering 100% vs `AGENTS_ONLY` 50% vs `README_ONLY`
25%. That's a promising signal from a small sample. Before claiming anything
public, we want a larger replication. The gold standard is
`performance_measurement.py` against the Anthropic API; this protocol is the
fallback when that isn't reachable.

## How this differs from API-based eval

| Dimension           | API eval (`performance_measurement.py`) | In-harness (this protocol) |
|---------------------|:---------------------------------------:|:--------------------------:|
| Independent Claude  | ✅ per call                             | ✅ per subagent            |
| Exact token usage   | ✅ `response.usage`                     | ⚠️ char/4 proxy only       |
| Wall-clock latency  | ✅ clean                                | ❌ scheduling noise        |
| Blinded grader      | ✅ scripted rubric                      | ✅ scripted rubric         |
| Scalable to N=100+  | ✅                                      | ❌ subagent budget limits  |

## Design

### Conditions

Four formats, same loader as `performance_measurement.py:194`:

1. `README_ONLY` — `README.md` only
2. `AGENTS_ONLY` — `AGENTS.md` router only, no fetch
3. `AICAC_SELECTIVE` — `AGENTS.md` + the single relevant `.ai/*.yaml`
4. `AICAC_FULL` — `AGENTS.md` + all `.ai/*.yaml` files

The pilot skipped `AICAC_FULL`; including it here directly tests whether the
router buys something over "just dump everything".

### Questions

Reuse all 12 from `performance_measurement.py:105-185` verbatim:

- Information Retrieval ×3 (IR-001, IR-002, IR-003)
- Architectural Understanding ×3 (AU-001, AU-002, AU-003)
- Common Workflows ×3 (CW-001, CW-002, CW-003)
- Error Resolution ×3 (ER-001, ER-002, ER-003)

Keyword rubrics are pre-committed on those lines — no post-hoc grading risk.

### Trial budget (pick one)

| Option | Trials/cell | Total subagent calls | Est. wall clock* |
|--------|------------:|---------------------:|-----------------:|
| A      | 2           | 96                   | ~30–60 min       |
| B      | 3           | 144                  | ~45–90 min       |
| C      | 5           | 240                  | ~75–150 min      |

\*Each subagent invocation spends ~13k tokens of Claude Code system prompt
before context is even loaded, plus context + answer. Conservative estimate:
15–25k tokens per call. At 144 calls that's roughly **2–4M tokens burned in
one session**. This is the reason the protocol is deferred.

### Per-call procedure

1. Main session precomputes context string using the same loader logic as
   `performance_measurement.py:194`. Deterministic size measurement.
2. Spawn fresh `general-purpose` Agent with:
   - The precomputed context
   - The question
   - Strict instruction: answer from context only, do not read files, do not
     search the repo
3. Subagent returns answer text.
4. Main session scores with existing keyword rubric
   (`performance_measurement.py:441`).
5. Trial order randomized across all cells to defeat order effects.

### Measurements

Captured per trial:
- ✅ Accuracy (keyword match, deterministic)
- ✅ Input context size (chars + char/4 token proxy)
- ✅ Answer text (for optional qualitative review)

Not captured:
- ❌ API-reported token usage (subagents don't expose)
- ❌ Wall-clock latency (subagent scheduling dominates signal)

### Bias controls

- Rubric frozen before any trials run (reusing existing committed rubric)
- No qualitative grading; pure keyword match
- Fresh subagent per call — no cross-contamination
- Questions + context strings fixed before execution
- Order randomized across the full trial matrix

### Outputs

- `validation/examples/results/YYYY-MM-inharness-n{N}.json` — raw per-trial
  data (condition, question_id, answer, score, context_size)
- `validation/examples/results/YYYY-MM-inharness-n{N}.md` — summary tables,
  per-condition accuracy, context size distributions, limitations section

## When to execute

Run this when:
- You have a session budget that can absorb 2–4M tokens
- You want replication evidence before a public claim
- API-based eval isn't available (no `ANTHROPIC_API_KEY` / `GROQ_API_KEY`)

Skip this and go straight to API eval when:
- You have `GROQ_API_KEY` (free tier) — same methodology, cleaner data, no
  subagent token burn, `make perf-groq`
- You have `ANTHROPIC_API_KEY` — `make perf-claude`

## Framing if we run it

"In-harness replication of the n=12 pilot, not a controlled API benchmark.
Evidence is supporting, not definitive; API-based eval remains the gold
standard claim."

## Open questions

- Is `AICAC_FULL` actually interesting at this budget, or should we drop it
  to 3 conditions and spend the saved budget on more trials per cell?
- Worth swapping keyword-match scoring for a second blind subagent as judge?
  Adds realism, adds cost, adds a second bias source.
- Should we vary question order per condition, or hold it constant so
  order-effects cancel cleanly?
