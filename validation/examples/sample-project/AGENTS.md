# AI Assistant Instructions

Instructions for AI coding assistants working with this codebase.

## Structured Context Available

This project uses **AI Context as Code (AICaC)** for efficient documentation.
Tools that support structured context should read `.ai/` directory files.

- **Project overview**: `.ai/context.yaml`
- **Architecture**: `.ai/architecture.yaml`
- **Workflows**: `.ai/workflows.yaml`
- **Decisions**: `.ai/decisions.yaml`
- **Error solutions**: `.ai/errors.yaml`

## Quick Reference

### Project Type
Python REST API using FastAPI with SQLite storage.

### Key Directories
- `src/taskflow/` - Main source code
- `src/taskflow/api/` - Route handlers
- `src/taskflow/models/` - Pydantic models
- `src/taskflow/services/` - Business logic
- `tests/` - Test suite

### Common Tasks

**Run tests:**
```bash
pytest
```

**Start dev server:**
```bash
taskflow serve --reload
```

**Add new endpoint:**
1. Create router in `src/taskflow/api/`
2. Add models in `src/taskflow/models/`
3. Add service in `src/taskflow/services/`
4. Register in `src/taskflow/main.py`
5. Add tests

### Code Style
- Python 3.11+
- Type hints required
- Black for formatting
- Pydantic for validation
