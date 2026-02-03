# AI Assistant Instructions

This project uses **AI Context as Code (AICaC)** - structured YAML in `.ai/` for efficient context loading.

## Context Selection Guide

**IMPORTANT: Load ONLY the file(s) relevant to your current task.**

| Query Type | Load This File | Skip These |
|------------|----------------|------------|
| Project overview, setup, dependencies | `.ai/context.yaml` | architecture, workflows, decisions, errors |
| Architecture, components, data flow | `.ai/architecture.yaml` | context, workflows, decisions, errors |
| How-to, commands, adding features | `.ai/workflows.yaml` | context, architecture, decisions, errors |
| Why decisions were made, trade-offs | `.ai/decisions.yaml` | context, architecture, workflows, errors |
| Errors, debugging, troubleshooting | `.ai/errors.yaml` | context, architecture, workflows, decisions |

**Examples:**
- "How do I add an endpoint?" → Load `.ai/workflows.yaml` only
- "Why FastAPI over Flask?" → Load `.ai/decisions.yaml` only
- "Fix port in use error" → Load `.ai/errors.yaml` only

## Quick Reference

**Project:** TaskFlow - Task Management REST API
**Stack:** Python 3.11+, FastAPI, SQLite
**Entry:** `src/taskflow/main.py`

```bash
taskflow serve --reload  # Dev server
pytest                   # Tests
black src/ tests/        # Format
```

## Directory Structure

```
src/taskflow/
├── main.py        # FastAPI app
├── api/           # Route handlers
├── models/        # Pydantic models
├── services/      # Business logic
└── db/            # Database
```

## Code Style

- Type hints required
- Black formatting
- Pydantic for validation
- Business logic in services/, not routes
