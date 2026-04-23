# AICaC MCP server — design sketch

Design for a cross-platform AICaC MCP server. Status: **draft, not
implemented**. Companion to `in-harness-eval-protocol.md`.

## Goal

Let any MCP-capable AI tool (Claude Code, Cursor, Windsurf, Continue, Zed,
Aider, etc.) adopt AICaC's *capabilities* — bootstrap, validate, migrate,
sync — without per-platform skill/rules packaging. The router pattern
itself stays in `AGENTS.md` where vendors already converge.

## Scope

| Layer | Delivery | In this doc? |
|---|---|---|
| Router behavior (instructions) | `AGENTS.md` + JSON Schemas | No — already universal |
| Capabilities (side-effecting) | **MCP tools** | Yes |
| Read-only spec content | **MCP resources** | Yes |
| Canned behavior prompts | **MCP prompts** | Yes |
| Per-tool polish (skills, rules files) | Platform-specific shims | No — optional convenience |

## Runtime

- **Language**: Python. Keeps one language across the project; reuses the
  existing `validate.py`, `bootstrap.py`, `migrate_v2.py`, `generate_index.py`
  verbatim as libraries.
- **SDK**: `mcp` (official Python SDK).
- **Packaging**: PyPI only, single package `aicac-mcp`. Install via
  `uvx aicac-mcp` or `pipx install aicac-mcp`. No npm wrapper — an npm
  package that shells out to Python still requires Python on the machine,
  so dual-publishing doubles the maintenance surface for no real reach
  gain.
- **Versioning**: pinned to the AICaC spec version it targets.
  `aicac-mcp@2.x` for spec v2.0; if v3 introduces breaking changes to the
  `.ai/` shape, `aicac-mcp@3.x`. Clients pin the major to match their
  `.ai/` shape.
- **Invocation**: stdio transport (standard for local MCP). Tools register
  the server in their MCP config.

Example client config (Claude Code `~/.claude/mcp.json`):

```json
{
  "mcpServers": {
    "aicac": {
      "command": "uvx",
      "args": ["aicac-mcp"]
    }
  }
}
```

Same pattern for Cursor, Windsurf, Continue — they all consume the same
server binary via their own MCP config UIs.

## Tools (side-effecting)

Every tool takes `project_path: string` (absolute, defaults to `.`). All
write operations default to dry-run; `apply: bool = false` flips them.

### `aicac_bootstrap`

Create a fresh v2.0 `.ai/` structure.

```jsonc
{
  "name": "aicac_bootstrap",
  "description": "Create a v2.0 AICaC structure in a project. Detects project type (node/python/etc.) and emits AGENTS.md + .ai/*.yaml + .ai/index.yaml skeletons.",
  "inputSchema": {
    "project_path": "string (default: cwd)",
    "compliance_level": "enum[minimal,standard,comprehensive] (default: minimal)",
    "apply": "boolean (default: false)"
  },
  "returns": {
    "files_created": "string[]",
    "files_skipped": "string[] (already exist)",
    "detected_type": "string",
    "next_steps": "string[] — human-readable guidance"
  }
}
```

### `aicac_validate`

Run all 4 validation passes. Read-only.

```jsonc
{
  "name": "aicac_validate",
  "description": "Validate .ai/ against v2.0 schemas, cross-references, and content quality heuristics.",
  "inputSchema": {
    "project_path": "string",
    "strict": "boolean (default: false)"
  },
  "returns": {
    "compliance_level": "enum[none,minimal,standard,comprehensive]",
    "errors": "string[]",
    "warnings": "string[]",
    "schema_violations": "{file, path, message}[]",
    "cross_ref_issues": "{from, to, message}[]",
    "content_quality": "{file, issue}[]"
  }
}
```

### `aicac_migrate`

v1.x → v2.0 automated migration.

```jsonc
{
  "name": "aicac_migrate",
  "description": "Migrate a v1.x .ai/ directory to v2.0 canonical shape (list-of-items → dict-keyed-by-id, common_commands → common_tasks, etc.).",
  "inputSchema": {
    "project_path": "string",
    "apply": "boolean (default: false — dry-run returns the proposed diff)"
  },
  "returns": {
    "changes": "{file, op, summary}[]",
    "diff": "string — unified diff if dry-run"
  }
}
```

### `aicac_generate_index`

Build or refresh `.ai/index.yaml`.

```jsonc
{
  "name": "aicac_generate_index",
  "description": "Regenerate .ai/index.yaml — the token-cheap routing table listing ids per file.",
  "inputSchema": {
    "project_path": "string",
    "apply": "boolean (default: false)"
  },
  "returns": {
    "ids_by_file": "{file: string[]}",
    "changed": "boolean"
  }
}
```

### `aicac_sync_suggest`

Given a code change (staged diff or explicit file list), hand the model a
structured prompt listing the changed paths and the `.ai/` files that
*could* be affected, without picking for it. Initial implementation is
intentionally a prompt-stub — no heuristics baked in. If real usage
surfaces reliable patterns (e.g., "anything under `src/api/` almost
always implies `workflows.yaml`"), those can move into the tool
deterministically later.

```jsonc
{
  "name": "aicac_sync_suggest",
  "description": "Given a set of changed source files, return the list of changed paths alongside all .ai/*.yaml files that could plausibly need updates. The model decides which actually need editing.",
  "inputSchema": {
    "project_path": "string",
    "changed_files": "string[] (optional — defaults to git diff HEAD)"
  },
  "returns": {
    "changed_files": "string[]",
    "candidate_ai_files": "string[] (all .ai/*.yaml present in project)",
    "prompt": "string — canned guidance asking the model to decide"
  }
}
```

Deliberately *not* returning confidence scores or ranked suggestions from
day one; those are judgment calls worth keeping honest until we have
evidence.

### Not a tool: routing

Routing ("given intent X, load file Y") is a *prompt pattern*, not a
deterministic function. It stays in `AGENTS.md` and the canned MCP prompt
(see below). Exposing it as an MCP tool would force the server to
reimplement a judgment call that's better made by the model with the
context in front of it.

## Resources (read-only)

Resources are fetched by URI. Clients can list them once and cache.

| URI | Content | Purpose |
|---|---|---|
| `aicac://spec/v2/context.schema.json` | JSON | Schema for `context.yaml` |
| `aicac://spec/v2/architecture.schema.json` | JSON | Schema for `architecture.yaml` |
| `aicac://spec/v2/workflows.schema.json` | JSON | Schema for `workflows.yaml` |
| `aicac://spec/v2/decisions.schema.json` | JSON | Schema for `decisions.yaml` |
| `aicac://spec/v2/errors.schema.json` | JSON | Schema for `errors.yaml` |
| `aicac://spec/v2/index.schema.json` | JSON | Schema for `index.yaml` |
| `aicac://spec/behavior.md` | Markdown | Platform-neutral behavior spec (router + recipes) |
| `aicac://project/index` | YAML | Live `.ai/index.yaml` for the current project |
| `aicac://project/summaries` | YAML | All `.ai/*.yaml` `summary:` fields concatenated (ultra-cheap overview) |

The first seven are static (shipped in the server package). The last two
are computed from the project the client is currently pointed at — they
give the AI a cheap "what's in this repo's `.ai/`?" lookup without
reading the full files.

## Prompts (canned system prompts)

Prompts let clients surface "modes" to the user. AICaC ships three.

### `aicac:router`

Teaches the selective-loading behavior. This is the prompt equivalent of
the `.claude/skills/aicac/SKILL.md` router section — stripped of
Claude-specific conventions.

```
When the working directory contains .ai/, route like this:
  - Overview, dev commands, entrypoints → load .ai/context.yaml only
  - Components, data flow → load .ai/architecture.yaml only
  - How-to, adding features → load .ai/workflows.yaml only
  - Why a decision was made → load .ai/decisions.yaml only
  - Errors, troubleshooting → load .ai/errors.yaml only
Before loading any full file, check its `summary:` field first
(use resource `aicac://project/summaries`) and/or `.ai/index.yaml`
(resource `aicac://project/index`) to confirm the right file.
Never load more than one .ai/ file per query unless the question
genuinely spans categories.
```

### `aicac:bootstrap`

How to populate a freshly-created `.ai/` from existing repo context.

### `aicac:sync`

How to update `.ai/` after a code change — what questions to ask before
writing to `workflows.yaml` vs `architecture.yaml`, when an ADR is
warranted, etc.

## What's deliberately NOT in scope

- **No token-measurement tools**. That's research tooling
  (`token_measurement.py`, `performance_measurement.py`); belongs in the
  repo's `validation/`, not the MCP server.
- **No GitHub-Action wrapper**. Actions already work standalone via
  `eFAILution/AICaC/.github/actions/aicac-adoption`.
- **No TOON conversion**. TOON is an optional compression format; not
  part of the adoption surface.
- **No authentication, no remote mode**. Local stdio only. If a remote
  AICaC-as-a-service is ever desired, that's a separate server.

## Implementation estimate

- ~200–400 lines of Python on top of existing scripts
- Register tools → call into `validate.py` / `bootstrap.py` / `migrate_v2.py`
  / `generate_index.py` as library functions (they already expose callable
  entry points)
- Resources → read static files from the package, or live files from
  the project path
- Prompts → static markdown shipped with the package
- Tests: integration-level — spin up the server, issue JSON-RPC over
  stdio, assert responses. Reuse the existing test fixtures.

## Distribution

Packaging lives on PyPI only (see Runtime). Discoverability is separate —
the server needs to be listed in the registries each AI tool surfaces to
its users.

Target registries:
- **Anthropic MCP registry** — primary Claude Code / Claude Desktop audience
- **Cursor MCP directory** — second-largest agentic coding audience
- **Continue.dev extensions** — open-source adopters
- **Windsurf MCP catalog** — growing audience
- **Any community registry** (e.g. `modelcontextprotocol.io`'s listing) —
  cheap to add, broad reach

Registry entries are metadata pointing at the same `uvx aicac-mcp`
install command; multi-listing is near-free maintenance once the PyPI
package exists.

## Open questions

None blocking. The four original opens (Docker, sync heuristics,
versioning, discoverability) are now settled: no Docker, sync starts as
prompt-stub, versioning pinned to spec major, registries listed above.

## Relationship to existing work

- **`.claude/skills/aicac/`**: keep as-is. It'll continue to work for
  Claude Code users who prefer the skill format. The MCP server and the
  skill serve the same audience with overlapping capabilities; users pick
  one based on their tool's MCP maturity.
- **`AGENTS.md`**: unchanged. Remains the universal behavior front-door.
- **GitHub Action**: unchanged. CI-native, separate concern.
- **Python scripts** (`validate.py` etc.): unchanged. Remain callable
  standalone; the MCP server is a thin adapter over them.

## Why this, why now

`AGENTS.md` gets AICaC ~80% of the way to cross-platform. MCP closes the
gap for the *capabilities* layer — the recipes that would otherwise need
a per-tool skill/rules file. Without it, every new AI tool means another
adapter to write. With it, new tools that support MCP pick up AICaC
capabilities for free.
