# AICaC MCP Server

Model Context Protocol (MCP) server for [AI Context as Code (AICaC) v2.0](https://github.com/eFAILution/AICaC).

Provides AICaC validation, bootstrap, migration, and sync capabilities as MCP tools and resources for any MCP-compatible AI coding assistant (Claude Code, Cursor, Windsurf, Continue, Zed, Aider, etc.).

## Features

### Tools (side-effecting)

All tools default to dry-run mode (`apply: false`) for safety.

- **`aicac_validate`** — Validate `.ai/` against v2.0 schemas, cross-references, and content quality
- **`aicac_bootstrap`** — Create a fresh `.ai/` structure with project-specific skeletons
- **`aicac_generate_index`** — Regenerate `.ai/index.yaml` (token-cheap routing table)
- **`aicac_migrate`** — Migrate v1.x `.ai/` to v2.0 (list→dict, `common_commands`→`common_tasks`, etc.)
- **`aicac_sync_suggest`** — Suggest which `.ai/` files may need updates after code changes

### Resources (read-only)

- **JSON Schemas** — `aicac://spec/v2/{context,architecture,workflows,decisions,errors,index}.schema.json`
- **Skill content** — `aicac://skill/{router,bootstrap,validate,sync,migrate}` serving procedural knowledge from `.claude/skills/aicac/*.md`

## Installation

The package includes all necessary assets (schemas, skills, scripts) and works standalone without requiring the full monorepo checkout.

### Via uvx (recommended)

```bash
uvx --from git+https://github.com/eFAILution/AICaC aicac-mcp
```

### Via pip

```bash
pip install git+https://github.com/eFAILution/AICaC#subdirectory=packages/aicac-mcp
```

### Development install

```bash
cd packages/aicac-mcp
pip install -e .
```

### Environment override

For development with a monorepo checkout, set `AICAC_REPO_ROOT` to use live schemas/scripts instead of packaged copies:

```bash
export AICAC_REPO_ROOT=/path/to/AICaC
```

## Usage

### Cursor

Add to your MCP configuration (Cursor Settings > MCP):

```json
{
  "mcpServers": {
    "aicac": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/eFAILution/AICaC", "aicac-mcp"]
    }
  }
}
```

Or for local development:

```json
{
  "mcpServers": {
    "aicac": {
      "command": "python",
      "args": ["-m", "aicac_mcp.server"]
    }
  }
}
```

### Claude Code / Claude Desktop

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "aicac": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/eFAILution/AICaC", "aicac-mcp"]
    }
  }
}
```

### Other MCP clients

Use the same pattern — all MCP-capable tools use stdio transport. Consult your tool's MCP configuration documentation.

## Tool usage examples

### Validate a project

```python
# Via MCP tool call
{
  "tool": "aicac_validate",
  "arguments": {
    "project_path": ".",
    "strict": false
  }
}
```

Returns:
```json
{
  "valid": true,
  "compliance_level": "Standard",
  "errors": [],
  "warnings": [],
  "found_files": {
    "context.yaml": true,
    "architecture.yaml": true,
    "workflows.yaml": true
  }
}
```

### Bootstrap a new project (dry-run)

```python
{
  "tool": "aicac_bootstrap",
  "arguments": {
    "project_path": ".",
    "compliance_level": "minimal",
    "apply": false
  }
}
```

Returns what would be created without writing files.

### Apply bootstrap

```python
{
  "tool": "aicac_bootstrap",
  "arguments": {
    "project_path": ".",
    "apply": true
  }
}
```

Creates `.ai/context.yaml` and `.ai/README.md` with TODO markers.

### Migrate v1.x to v2.0 (dry-run)

```python
{
  "tool": "aicac_migrate",
  "arguments": {
    "project_path": ".",
    "apply": false
  }
}
```

Shows what would change. Set `"apply": true` to write.

### Check which .ai/ files might need updates

```python
{
  "tool": "aicac_sync_suggest",
  "arguments": {
    "project_path": ".",
    "changed_files": ["src/api/router.py", "src/models/user.py"]
  }
}
```

Returns candidate `.ai/` files and a prompt for the model to decide.

## Design

This server is **local and filesystem-bound by design**. AICaC operations read/write a specific project's `.ai/` directory, so local scope is the natural fit.

- **Language:** Python (reuses existing `validate.py`, `bootstrap.py`, `migrate_v2.py`, `generate_index.py` as libraries)
- **SDK:** `mcp` (official Python MCP SDK)
- **Transport:** stdio only (standard for local MCP)
- **Versioning:** Pinned to AICaC spec version (`aicac-mcp@2.x` for spec v2.0)

See [`validation/docs/mcp-server-design.md`](../../validation/docs/mcp-server-design.md) for the full design rationale.

## Limitations

- **Standalone packaging** — all required assets (schemas, skills, scripts) are vendored in `data/` subdirectories. No monorepo checkout required. (Addresses [#22](https://github.com/eFAILution/AICaC/issues/22))
- **Local filesystem only** — no remote/HTTP transport (see design doc rationale)
- **Dry-run default** — all write operations require explicit `apply: true`
- **No PyPI publish yet** — install via git URL until first stable release

## Contributing

See the main [AICaC repository](https://github.com/eFAILution/AICaC) for contribution guidelines.

## License

MIT (see [LICENSE-CODE](../../LICENSE-CODE) in the repository root)
