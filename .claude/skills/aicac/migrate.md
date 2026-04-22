# Migrate recipe — v1.x → v2.0

## What changed in v2.0

| v1.x shape                                 | v2.0 canonical                          |
|--------------------------------------------|-----------------------------------------|
| `components: [- name: api, ...]`           | `components: {api: {...}}`              |
| `decisions: [- id: ADR-001, ...]`          | `decisions: {ADR-001: {...}}`           |
| `error_patterns: [- pattern: X, ...]`      | `errors: {SLUG: {symptom: X, ...}}`     |
| `common_commands: {...}`                   | `common_tasks: {...}`                   |
| `version: "1.0"` / `"1.1"`                 | `version: "2.0"`                        |
| (implicit)                                 | new `summary:` field per file           |
| (implicit)                                 | cross-ref fields: `touches_components`, `affects_components`, `depends_on`, `superseded_by` |
| `project.type` free-form                   | `project.type` enum + `other` escape    |

## Automated migration

```bash
python3 .github/actions/aicac-adoption/scripts/migrate_v2.py . --dry-run
python3 .github/actions/aicac-adoption/scripts/migrate_v2.py .
python3 .github/actions/aicac-adoption/scripts/validate.py .
```

This handles the structural rewrites. You still need to hand-add:
- `summary:` fields (one sentence per file)
- cross-reference fields (`touches_components`, `affects_components`, etc.)
  where they make sense
- canonical `project.type` (if the old value was something like `node-app`
  or `python-app` — map to `web-app`/`library`/`cli` per the enum)

## Backward compatibility

v2.0 validator accepts v1.x list-form files with a DEPRECATION warning.
Projects can migrate incrementally. The warning becomes a hard error in v3.0
(no timeline yet).

## Verifying round-trip

```bash
# Before
python3 .github/actions/aicac-adoption/scripts/validate.py . 2>&1 | grep -i deprecation

# After
python3 .github/actions/aicac-adoption/scripts/validate.py . --strict
```

No deprecation warnings, `--strict` passes → migration complete.
