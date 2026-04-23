# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## [0.4.0](https://github.com/eFAILution/AICaC/compare/0.3.0...0.4.0) (2026-04-23)

### Features

* **action:** v2-aware, three-channel adoption aligned ([9beb2a7](https://github.com/eFAILution/AICaC/commit/9beb2a7b948f2d6421f7db7cb8dcbb34235bdd32))
* Claude Code skill, router AGENTS.md, honest empirical framing ([8d9fa20](https://github.com/eFAILution/AICaC/commit/8d9fa201294968f5c10c00ee2d76651173ada3a4))
* **spec:** v2.0 canonical shapes + JSON Schemas + schema-driven validator ([1bf4aa7](https://github.com/eFAILution/AICaC/commit/1bf4aa7badea53b7730c4c41c8e0c09b9834f7af))

### Bug Fixes

* **ai:** drop timestamp from generated .ai/index.yaml ([10b61d5](https://github.com/eFAILution/AICaC/commit/10b61d5d0fff550c16b8278cf6fc491d35da35f6))
* **ci:** pass GITHUB_TOKEN to gitleaks-action ([ac7647b](https://github.com/eFAILution/AICaC/commit/ac7647b42af42fd7e2bdfa7fe463fa8ff311221f))
* **deps:** pin Pillow, tqdm, zipp to clear OSV advisories ([1a27be1](https://github.com/eFAILution/AICaC/commit/1a27be148f411cfb3f11a5c8ef21b9700a935bcb))

### Maintenance

* **ai:** regenerate .ai/index.yaml ([6cea525](https://github.com/eFAILution/AICaC/commit/6cea525dc596242eec0d44726da8ba2821d5afb2))
* **ai:** regenerate .ai/index.yaml ([eee1f12](https://github.com/eFAILution/AICaC/commit/eee1f128e5a7506e08f0a1ee396133230e30d655))
* **ai:** regenerate .ai/index.yaml ([6157307](https://github.com/eFAILution/AICaC/commit/6157307217401d804d328c276d0acc56aceb0106))
* gitignore validation/real-world-projects/ scratch ([dc6e27e](https://github.com/eFAILution/AICaC/commit/dc6e27ed9e60cb09503c880960d020cd236ae9fb))
* **security:** argus config, lint/bandit configs, npm update ([e56543b](https://github.com/eFAILution/AICaC/commit/e56543b5a16ac381438fe52fa5605dffae746e09))

### Documentation

* **readme:** concrete install paths for the Claude Code skill ([0c21c6c](https://github.com/eFAILution/AICaC/commit/0c21c6cc9ebb3f645d70260e472599b739ec4ed8))
* reframe MCP design after production-MCP guidance ([2c45958](https://github.com/eFAILution/AICaC/commit/2c459585b9518e918ef591bd5639c734a70cca46))
* **results:** live Claude pilot (n=12) — AICaC_SELECTIVE 100% vs AGENTS 50% ([59495a3](https://github.com/eFAILution/AICaC/commit/59495a34525a88ed005a8967935d803dffa1c95c))
* **validation:** in-harness v2.0 eval protocol (deferred) ([c911d14](https://github.com/eFAILution/AICaC/commit/c911d14f8220fc6cd2c9c722ad89f3403a09aee6))
* **validation:** MCP server design sketch (deferred implementation) ([ef466e4](https://github.com/eFAILution/AICaC/commit/ef466e430427ef71ca2269e4ff00a0c43d1c6d44))

### Code Refactoring

* **ai:** migrate .ai/ + sample to v2.0 canonical shape ([6c86d3e](https://github.com/eFAILution/AICaC/commit/6c86d3e5c9359cd64588db23a8ae29a767fac46a))

### Tests

* **toon:** update yaml_to_toon tests for v2.0 canonical shape ([6ad6114](https://github.com/eFAILution/AICaC/commit/6ad6114d239066ae7838208705aae23c55f21a62))

### Continuous Integration

* block Claude attribution and session URLs from ever landing ([6d0435c](https://github.com/eFAILution/AICaC/commit/6d0435c4a59a52fa0e7e75f2c9ddfba55e3b72cb))
* install jsonschema for unit tests ([f2c9254](https://github.com/eFAILution/AICaC/commit/f2c92546c37df771ced613928ac6d20ec4c87267))

## [0.3.0](https://github.com/eFAILution/AICaC/compare/0.2.0...0.3.0) (2026-03-07)

### Features

* **action:** add rebase/retry checkbox and restrict migration to default branch ([f78e02c](https://github.com/eFAILution/AICaC/commit/f78e02c7f42f70d50608dc0c5a76665070904d7a))
* regenerate TOON files from updated YAML sources ([0b37fb6](https://github.com/eFAILution/AICaC/commit/0b37fb68e8863c78eedb2557b9f4c29a8b0b3478))

### Bug Fixes

* **action:** handle existing migration branch and skip if PR exists ([8a525b0](https://github.com/eFAILution/AICaC/commit/8a525b0d90e4f63df2b135ba86ba31c10ec034c2))
* **action:** use force-push fallback instead of branch deletion ([8faf906](https://github.com/eFAILution/AICaC/commit/8faf90647b7f0e0fc5e2ce0c71978529de96b51a))
* **ai:** escape nested quotes in errors.yaml ([10f6b26](https://github.com/eFAILution/AICaC/commit/10f6b26f0229722230e9a4d8418a0128de9182ef))
* **ci:** fix yamllint YAML syntax and add actionlint ([2790bdb](https://github.com/eFAILution/AICaC/commit/2790bdb24540ebe1d2e0da730d005a1eb4f0e7f0))
* **ci:** resolve actionlint errors and add git identity for migration ([92b3a6a](https://github.com/eFAILution/AICaC/commit/92b3a6a05f6f86f6f8e6c88dc25b6abd39fe5357))

### Continuous Integration

* **lint:** add yamllint to validate-aicac pipeline ([f2c505f](https://github.com/eFAILution/AICaC/commit/f2c505fddc95f5e1cfd467bbf0f39642cc760a4b))

## [0.2.0](https://github.com/eFAILution/AICaC/compare/0.1.1...0.2.0) (2026-03-07)

### Features

* **action:** add TOON generation and issue-based migration workflow ([4a976a7](https://github.com/eFAILution/AICaC/commit/4a976a7439a0f4c304c8b097afccff68492a8984))
* **action:** enable suggest-toon by default ([ed54b0e](https://github.com/eFAILution/AICaC/commit/ed54b0e100cca2f94131072cc8507af8c344ceae))
* **validation:** integrate TOON encoding as benchmark format ([becd122](https://github.com/eFAILution/AICaC/commit/becd1224d6745122fa3b88b3f39e188a90a35d93)), closes [#3](https://github.com/eFAILution/AICaC/issues/3)

### Bug Fixes

* **action:** add issues:write permission and ensure migration label exists ([f120b9c](https://github.com/eFAILution/AICaC/commit/f120b9c2e52f6a858be92d29e6e853fd03ad9034))
* **ci:** accept common_commands in validator and override pytest addopts ([7f110bb](https://github.com/eFAILution/AICaC/commit/7f110bb431acc71d8c82959dcb14a980ff6c4f11))
* **ci:** checkout PR branch ref to fix release-it dry run ([3bd0dd6](https://github.com/eFAILution/AICaC/commit/3bd0dd68f4f3a96a2a584dfe340eb5280ef7b32e))
* **ci:** fix unit test and integration test failures ([3c5943a](https://github.com/eFAILution/AICaC/commit/3c5943a822b82e7dfee347167acc9d45067ef0f3))

### Continuous Integration

* **action:** add unit tests and integration tests to PR validation ([55d8164](https://github.com/eFAILution/AICaC/commit/55d81643aa6ccf6c6b3e3c73852011b13a51da13))

## [0.1.1](https://github.com/eFAILution/AICaC/compare/v0.1.0...0.1.1) (2026-02-11)

### Bug Fixes

* **validate.py:** handle missing contexts and report to user ([f701ec6](https://github.com/eFAILution/AICaC/commit/f701ec67b3385c0558432f5650f198785407d386))

### Maintenance

* fix release-it dry run errors ([53067e0](https://github.com/eFAILution/AICaC/commit/53067e0ad57a1f2ca8b7d17759b0255f923b58ac))

### Continuous Integration

* add release-it config and workflow ([cfc0226](https://github.com/eFAILution/AICaC/commit/cfc0226916b02a042bc909998d9859bb1544bd4b))
