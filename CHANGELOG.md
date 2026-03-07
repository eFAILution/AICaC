# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



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
