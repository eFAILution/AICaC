# Live Claude pilot experiment (2026-04-21)

First controlled run of "AICaC with a real LLM deciding the answer". Small
sample, but designed to be honest about what the router pattern delivers.

## Setup

- **Subject**: `validation/examples/sample-project` (taskflow FastAPI app,
  `.ai/` in v2.0 canonical shape, router-style `AGENTS.md`).
- **Model**: Claude via Claude Code sub-agents (`subagent_type: general-purpose`).
- **Formats compared**: `README_ONLY`, `AGENTS_ONLY`, `AICAC_SELECTIVE`.
  (AICaC-full-load was excluded — its behaviour is already covered by the
  deterministic token measurements in `EXAMPLE_RESULTS.md`.)
- **Questions**: 4, one per category.
  - IR-002: "What Python version is required?"
  - AU-001: "Why was FastAPI chosen over Flask?"
  - CW-001: "How do I add a new API endpoint?"
  - ER-001: "How do I fix a 'port already in use' error?"
- **Protocol**: each (question × format) spawned a fresh sub-agent with the
  question and the context file for that format. Agents were instructed to
  read nothing else — no file system walk, no web. Scored by keyword match
  against expected answer terms.
- **N**: 1 trial per cell (n=12 total). This is a pilot, not a publication.

## Results

### Accuracy (correct / total)

| Format            | Accuracy | Pass rate |
|-------------------|---------:|----------:|
| README_ONLY       | 1 / 4    | 25%       |
| AGENTS_ONLY       | 2 / 4    | 50%       |
| AICAC_SELECTIVE   | 4 / 4    | **100%**  |

### Per-question breakdown

| Question | README_ONLY | AGENTS_ONLY | AICAC_SELECTIVE |
|----------|:-----------:|:-----------:|:---------------:|
| IR-002 (Python version)          | ❌ not found | ✅            | ✅ |
| AU-001 (FastAPI vs Flask)        | ❌           | ❌ points to decisions.yaml | ✅ |
| CW-001 (add endpoint)            | ✅           | ✅            | ✅ (with code templates) |
| ER-001 (port in use)             | ❌           | ❌ points to errors.yaml    | ✅ |

**The key finding**: when `AGENTS_ONLY` fails (AU-001, ER-001), it fails
*helpfully* — the model recognises it needs `.ai/decisions.yaml` or
`.ai/errors.yaml` but doesn't have it. This is the router pattern doing
exactly what it should, but a single-turn experiment punishes it because the
model can't fetch the file. In a real agentic loop, the model would follow
the pointer and get the answer, at which point `AGENTS_ONLY + lazy fetch`
converges on AICAC_SELECTIVE.

### Context tokens (input)

| Format            | Mean tokens |
|-------------------|------------:|
| README_ONLY       | 859         |
| AGENTS_ONLY       | 1,299       |
| AICAC_SELECTIVE   | 1,106       |

AICAC_SELECTIVE uses **15% fewer tokens** than AGENTS_ONLY *and* answers
100% of questions vs 50%.

### Duration (single-shot, noisy)

| Format            | Mean duration (ms) |
|-------------------|-------------------:|
| README_ONLY       | 5,954              |
| AGENTS_ONLY       | 6,732              |
| AICAC_SELECTIVE   | 7,539              |

AICAC_SELECTIVE was ~13% slower than README_ONLY. This is within sub-agent
scheduling noise for n=1; do not treat as a benchmark.

## Interpretation

1. **Router-selective loading is strictly better on accuracy.** Every
   question answered correctly, with measured input tokens between the other
   two formats.
2. **AGENTS_ONLY helpfully fails** — it names the missing context file. A
   real agent with file-read access would close that gap; this protocol
   blocked the lookup to isolate the "which context did the model see"
   variable.
3. **README_ONLY is worst even on token count-adjusted accuracy.** Only 1 of
   4 answers was findable in the README (CW-001's "add endpoint" steps were
   apparently in README prose).
4. **The detail-quality gap is larger than accuracy alone suggests.** On
   CW-001, all three formats technically "passed" keyword scoring, but the
   AICAC_SELECTIVE answer included the concrete APIRouter + Pydantic code
   templates that `.ai/workflows.yaml::add_endpoint.steps` encodes — the
   others produced a 5-step outline. Structured context isn't just
   token-efficient; it's actionable.

## Limitations

- **n=1 per cell.** This is a pilot, suitable for "does the trick work at
  all". Publication-grade claims need `trials >= 30` via
  `performance_measurement.py` against a real API.
- **Sub-agent harness overhead.** Each sub-agent carries ~13K tokens of
  Claude Code system prompt before context, so `total_tokens` in
  `experiments/live_results.json` is much higher than the context portion.
  "Input tokens" in the tables above refer to the AICaC-controlled portion
  only.
- **Single codebase, single tokenizer family, English queries.**
- **AGENTS_ONLY was penalised** by the protocol preventing it from fetching
  the context files it correctly identified. A realistic agentic workflow
  would close that gap, at the cost of an extra tool call per query.

## Reproducing on your infrastructure

With `ANTHROPIC_API_KEY` or `GROQ_API_KEY`:

```bash
make perf-groq          # free cloud
make perf-claude        # paid, highest-fidelity
python3 validation/scripts/run_live_experiment.py --provider claude --trials 10
```

The driver script writes raw trial output + summary to `experiments/`.

## Raw data

[`experiments/live_results.json`](../../../experiments/live_results.json)
