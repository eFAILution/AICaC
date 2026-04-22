# AI Assistant Instructions

This project uses **AI Context as Code (AICaC) v2.0** — structured YAML in `.ai/` validated against JSON Schemas in `spec/v2/`.

## Router: load ONLY the relevant file

| Query intent                                 | Load this file only    |
|----------------------------------------------|------------------------|
| Project overview, setup, dependencies        | `.ai/context.yaml`     |
| Architecture, components, data flow, deps    | `.ai/architecture.yaml`|
| How-to, commands, adding features            | `.ai/workflows.yaml`   |
| Why decisions were made, trade-offs          | `.ai/decisions.yaml`   |
| Errors, debugging, troubleshooting           | `.ai/errors.yaml`      |
| Cross-file routing hints                     | `.ai/index.yaml` (if present) |

**Examples:**
- "How do I add an endpoint?" → `.ai/workflows.yaml` only
- "Why FastAPI over Flask?" → `.ai/decisions.yaml` only
- "Fix port in use error" → `.ai/errors.yaml` only

Each file has a top-level `summary:` field — read that first to confirm the file
is the right one before loading the rest.

## Quick reference

- **Project**: TaskFlow — Task management REST API
- **Stack**: Python 3.11+, FastAPI, SQLite
- **Entry**: `src/taskflow/main.py`

```bash
taskflow serve --reload  # dev server
pytest                   # tests
black src/ tests/        # format
```

## Directory structure

```
src/taskflow/
├── main.py        # FastAPI app
├── api/           # Route handlers
├── models/        # Pydantic models
├── services/      # Business logic
└── db/            # Database
```

## Code style

- Type hints required
- Black formatting
- Pydantic for validation
- Business logic in `services/`, not routes
