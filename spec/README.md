# AICaC Specification

Machine-readable JSON Schemas for the `.ai/` directory convention, versioned by spec level.

## Layout

```
spec/
├── v1/   # v1.x shapes — accepted for backward compatibility
└── v2/   # v2.0 canonical shapes — dict-keyed, schema-validated
```

## Versions

### v2.0 (current canonical)

Canonical shape for every multi-entry file is a **dict keyed by stable id**:

| File                | Canonical key                       |
|---------------------|-------------------------------------|
| `context.yaml`      | single doc (no keyed list)          |
| `architecture.yaml` | `components.<component_id>`         |
| `workflows.yaml`    | `workflows.<workflow_id>`           |
| `decisions.yaml`    | `decisions.<adr_id>` (e.g. ADR-001) |
| `errors.yaml`       | `errors.<error_id>`                 |
| `index.yaml` (opt.) | auto-generated routing index        |

Rationale: direct lookup by id is token-cheap, stable refs survive reorderings,
merge conflicts stay local to one entry, and cross-references (e.g.
`workflow.touches_components: [api, db]`) can be validated.

### v1.x (legacy)

v1.x permitted list forms (`components: [- name: api, ...]`,
`decisions: [- id: ADR-001, ...]`). The v2.0 validator accepts both and warns
when it sees the list form.

## Migration from v1.x → v2.0

The validator emits `DEPRECATION` warnings when it sees v1.x shapes. To migrate,
run the migration helper:

```bash
python .github/actions/aicac-adoption/scripts/migrate_v2.py .
```

Concretely, migration is mechanical:

```yaml
# v1.x
components:
  - name: api
    purpose: "HTTP handlers"
    depends_on: [services]

# v2.0
components:
  api:
    purpose: "HTTP handlers"
    depends_on: [services]
```

## Schema validation

```bash
pip install jsonschema pyyaml
python .github/actions/aicac-adoption/scripts/validate.py .
```

Validator checks, in order:
1. Required files present
2. JSON Schema conformance per file
3. Cross-reference integrity (components referenced by workflows/decisions must exist)
4. Content-quality heuristics (no all-TODO files, minimum populated entries)

## New in v2.0

- **`summary` fields** — an optional one-line summary per file enables routers
  (and the auto-generated `index.yaml`) to pick the right file without loading
  everything.
- **`index.yaml`** — auto-generated, token-cheap. Lists ids available in each
  file plus a routing table. Regenerate with the adoption action.
- **`touches_components` / `affects_components` / `external_dependencies`** —
  cross-reference fields enforced by the validator.
- **Enumerated `project.type`** — closed set (`rest-api`, `cli`, `library`, …)
  with `other` escape.

## Backward compatibility

v2.0 validator accepts v1.x files and warns. Bootstrap generates v2.0 by
default. `common_commands` remains accepted as an alias for `common_tasks` with
deprecation warning; it will be removed in v3.0.
