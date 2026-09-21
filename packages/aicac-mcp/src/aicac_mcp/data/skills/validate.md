# Validate recipe — check AICaC compliance

## One-liner

```bash
python3 .github/actions/aicac-adoption/scripts/validate.py .
```

Exits non-zero on blocking errors; prints compliance level on success.

## What the validator checks (in order)

1. **Required files present.** `.ai/context.yaml` must exist.
2. **JSON Schema conformance** per file against
   `spec/v2/*.schema.json`. Catches missing required fields, wrong types,
   `project.type` outside the enum, v1.x-only fields.
3. **Cross-references.** `workflows.*.touches_components`,
   `decisions.*.affects_components`, `components.*.depends_on`, and
   `decisions.*.superseded_by` must resolve to ids that exist.
4. **Content quality.** Files where >50% of non-comment lines are TODO
   placeholders are excluded from the compliance count (with a warning).

## Common failures and fixes

| Error                                          | Fix                                    |
|------------------------------------------------|----------------------------------------|
| `project.type` not in enum                     | Use one of the canonical values or `other` + `type_detail` |
| `description` minLength 10                     | Write a real one-line description      |
| `version` doesn't match `^(1|2)\.[0-9]+(\.[0-9]+)?$` | Use `'2.0'`                    |
| XREF: workflow references unknown component    | Fix typo or add the component to `architecture.yaml` |
| DEPRECATION: list form for decisions           | Run `migrate_v2.py`                    |
| DEPRECATION: `common_commands`                 | Rename to `common_tasks`               |
| schema validation skipped (no jsonschema)      | `pip install jsonschema`               |

## Strict mode

```bash
python3 .github/actions/aicac-adoption/scripts/validate.py . --strict
```

Treats deprecation warnings as errors. Use in CI before committing to a
v3.0 migration.

## JSON output (for tooling)

```bash
python3 .github/actions/aicac-adoption/scripts/validate.py . --json > compliance.json
```

## When to run

- Before committing any change to `.ai/`
- In CI on every PR touching `.ai/**`
- As the final step of the bootstrap or sync recipes
