# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



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
