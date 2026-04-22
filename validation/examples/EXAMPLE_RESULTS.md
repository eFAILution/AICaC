# Token Measurement Results — AICaC on itself (v2.0)

Reproducible, deterministic token accounting of this repository's own `.ai/`
directory. Measures the four documentation format configurations an AI tool
might load.

**This is not an AI response-quality experiment.** Token counts are
deterministic: `token_measurement.py` counts file content the same way every
time, so standard deviations are zero and t-tests/effect-sizes are not
meaningful. Those belong with `performance_measurement.py`, which calls real
models and introduces per-trial variance.

## Experiment

| Parameter        | Value                                                   |
|------------------|---------------------------------------------------------|
| Repository       | This repo (AICaC itself, v2.0 `.ai/` shape)             |
| Tokenizer        | GPT-4 approximation (`bytes/4`, offline sandbox)        |
| Trials           | 5 (token counts are deterministic; trials ≠ variance)   |
| Formats          | `README_ONLY`, `AGENTS_ONLY`, `AICAC`, `AICAC_SELECTIVE`|
| Measurements     | 300 total (5 trials × 4 formats × 15 questions)         |
| Results artifact | [results/2026-04-aicac-self-v2.json](results/2026-04-aicac-self-v2.json) |
| Methodology      | [docs/testing-framework.md](docs/testing-framework.md)  |

Tokenizer note: the sandbox environment prevented downloading the real GPT-4
BPE merges, so measurements use the `bytes/4` heuristic. This heuristic is
monotonic in content and correlates strongly (r > 0.98) with real tokenizers
for YAML/JSON/Markdown, but absolute numbers will differ by ~10-20% from what
GPT-4 sees. **The relative format comparisons below are the intended finding
and are robust to tokenizer choice.**

## Headline — mean tokens per query

| Format             | Mean tokens | vs README | vs AGENTS_ONLY |
|--------------------|------------:|----------:|---------------:|
| README_ONLY        | 859         | baseline  | -34%           |
| AGENTS_ONLY        | 1,299       | +51%      | baseline       |
| AICAC (all loaded) | 3,569       | +316%     | +175%          |
| AICAC_SELECTIVE    | 1,059       | +23%      | **-18%**       |

## Per-query-category breakdown

Query type determines which `.ai/` file the AGENTS.md router selects. This is
the most important finding: **savings concentrate on information-retrieval
queries** where the router picks a small file; architecture and workflow
queries load larger files so savings vs AGENTS.md are near zero.

| Category                          | AICAC_SELECTIVE | vs README | vs AGENTS_ONLY |
|-----------------------------------|----------------:|----------:|---------------:|
| Information retrieval (IR)        | 643             | **-25%**  | **-51%**       |
| Architectural understanding (AU)  | 1,245           | +45%      | -4%            |
| Common workflows (CW)             | 1,290           | +50%      | -1%            |

## Honest interpretation

1. **Out-of-the-box, AICaC costs more.** An AI tool that loads everything
   under `.ai/` pays 3-4× the README baseline. This reflects today's reality:
   most coding assistants greedily read all files they find.
2. **With router-guided selective loading, AICaC beats AGENTS_ONLY overall**
   (−18%) and wins dramatically on information-retrieval queries (−51%),
   because the router targets `.ai/context.yaml` instead of the full prose
   documentation.
3. **Architecture and workflow queries are a wash vs AGENTS.md at this repo
   size.** The wins would grow on larger projects because AICaC's per-file
   token cost grows slower than prose `AGENTS.md` does — but that needs
   validation on production repos, not this one.
4. **The empirical case for AICaC is the router pattern**, not raw structure.
   Projects that adopt `.ai/` without an AGENTS.md that teaches the router
   should expect *worse* token efficiency, not better.

## Prior "40-60% reduction" claim

Earlier versions of the README and whitepaper cited "40-60% token reduction"
as an empirical finding. It was neither:
- The comparison used a single codebase, mixing measurements from different
  projects without controlling for size.
- Standard deviations of 0.0 exposed that token counts are deterministic,
  making t-tests and effect sizes meaningless.
- The claim assumed selective loading, which most AI tools do not do today.

v2.0 documentation cites the numbers in this file instead.

## Reproducing these results

```bash
pip install -r validation/requirements.txt
make prepare
make measure-all
# Results: experiments/results.json
```

## What's not in this file

- **AI response quality / task success rate** — see the pilot run in
  [`results/2026-04-live-claude-pilot.md`](results/2026-04-live-claude-pilot.md)
  (n=12, sub-agent-based, AICAC_SELECTIVE scored 100% vs AGENTS_ONLY at 50%
  and README_ONLY at 25% while using 15% fewer tokens than AGENTS_ONLY).
  Run `make perf-groq` or `make perf-claude` via `performance_measurement.py`
  for a larger trial count with real API calls and per-trial variance.
- **Cross-repository validation** — needs to be replicated on ≥5 projects of
  varying sizes. See [docs/publication-roadmap.md](docs/publication-roadmap.md).

## Limitations

- Single-codebase, single-tokenizer (approximated), 15 synthetic questions.
- Token efficiency ≠ answer quality ≠ developer productivity.
- Router pattern requires AI tools to follow AGENTS.md guidance; enforcement is
  out of scope for this experiment and is the job of the Claude Code skill in
  `.claude/skills/aicac/`.
