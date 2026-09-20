---
name: aicac
description: Use when the working directory contains a `.ai/` directory, or when the user asks to adopt AICaC (AI Context as Code), validate `.ai/` compliance, populate `.ai/` files, answer questions using AICaC structured context, or keep `.ai/` in sync after code changes. Routes queries to the single relevant `.ai/*.yaml` file (context/architecture/workflows/decisions/errors) using `AGENTS.md` + `.ai/index.yaml` rather than loading all documentation.
---

# AICaC Skill (Grok Bot / Cursor)

**This is the Grok Bot / Cursor entrypoint for the AICaC skill.**

The shared skill content is in `../../skills/aicac/` (or `skills/aicac/` if
you're in a project that adopted this skill). Read the shared SKILL.md first,
then use the recipes in that directory.

For convenience, the recipes are also available here as symlinks:

- **Bootstrap `.ai/` in a new project** → [`bootstrap.md`](bootstrap.md)
- **Validate `.ai/` compliance** → [`validate.md`](validate.md)
- **Answer a question using the router** → [`router.md`](router.md)
- **Keep `.ai/` in sync after a code change** → [`sync.md`](sync.md)
- **Migrate v1.x → v2.0** → [`migrate.md`](migrate.md)

See [`../../skills/aicac/SKILL.md`](../../skills/aicac/SKILL.md) for the full
skill documentation.
