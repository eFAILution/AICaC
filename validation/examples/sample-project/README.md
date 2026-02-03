# TaskFlow - Task Management API

A simple REST API for managing tasks and projects, built with FastAPI.

## Features

- Create, read, update, delete tasks
- Organize tasks into projects
- Priority levels and due dates
- Tag-based filtering
- SQLite storage (PostgreSQL optional)

## Installation

```bash
pip install taskflow-api
```

Or from source:

```bash
git clone https://github.com/example/taskflow.git
cd taskflow
pip install -e .
```

## Quick Start

```bash
# Start the API server
taskflow serve

# Or with custom port
taskflow serve --port 8080
```

The API will be available at `http://localhost:8000`. Visit `/docs` for interactive Swagger documentation.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task |
| GET | `/tasks/{id}` | Get a task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |
| GET | `/projects` | List projects |
| POST | `/projects` | Create a project |

## Example Usage

```bash
# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Write docs", "priority": "high"}'

# List tasks
curl http://localhost:8000/tasks

# Filter by tag
curl http://localhost:8000/tasks?tag=urgent
```

## Configuration

Create a `taskflow.yaml` file:

```yaml
database:
  type: sqlite  # or postgresql
  path: ./tasks.db

server:
  host: 0.0.0.0
  port: 8000
  reload: true  # for development
```

## Project Structure

```
src/
├── taskflow/
│   ├── __init__.py
│   ├── main.py           # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── tasks.py      # Task endpoints
│   │   └── projects.py   # Project endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py       # Task model
│   │   └── project.py    # Project model
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py
│   └── db/
│       ├── __init__.py
│       └── database.py   # Database connection
└── tests/
    ├── test_tasks.py
    └── test_projects.py
```

## Adding a New Endpoint

1. Create route handler in `src/taskflow/api/`
2. Add Pydantic models in `src/taskflow/models/`
3. Implement business logic in `src/taskflow/services/`
4. Register router in `src/taskflow/main.py`
5. Add tests in `tests/`

Example:

```python
# src/taskflow/api/tags.py
from fastapi import APIRouter
from taskflow.models.tag import Tag, TagCreate

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/")
def list_tags() -> list[Tag]:
    # Implementation
    pass

@router.post("/")
def create_tag(tag: TagCreate) -> Tag:
    # Implementation
    pass
```

Then register:

```python
# src/taskflow/main.py
from taskflow.api import tags
app.include_router(tags.router)
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with auto-reload
taskflow serve --reload

# Format code
black src/ tests/
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TASKFLOW_DB_PATH` | SQLite database path | `./tasks.db` |
| `TASKFLOW_PORT` | Server port | `8000` |
| `TASKFLOW_DEBUG` | Enable debug mode | `false` |

## License

MIT License
