# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2026-04-27

### Added
- Added about description and topic tags to GitHub repository.
- Added LICENSE file (MIT) to complete open source compliance.

## [1.1.0] - 2026-04-27

### Added
- Added LICENSE file (MIT) to complete open source compliance.
- Added quick decision table mapping user request patterns → task mode → output format → tool preference.
- Added "精准提示词模板" (precise prompt template) with compact goal/input/constraints/output format.
- Added "ZeroToken 强化模式" section for explicit token-saving requests.
- Added "何时不使用 ZeroToken" guard section.

### Changed
- Restructured SKILL.md: decision table at top, then core principles (5 from 8), then task modes with concrete tool mappings.
- Tightened all sections—removed redundancy across core principles, task modes, and output rules.
- Updated agents/openai.yaml default_prompt to match new decision-table-first flow.

## [1.0.3] - 2026-04-27

### Changed
- Expanded package keywords for prompt engineering, context optimization, token budgeting, and agent workflow discovery.

## [1.0.2] - 2026-04-27

### Added
- Added guidance for crafting the shortest precise prompt needed to solve the user's problem.
- Added prompt framing rules for goal, input, constraints, output format, and acceptance criteria.

## [1.0.1] - 2026-04-27

### Changed
- Changed the skill trigger guidance so ZeroToken is the default working discipline for suitable tasks.
- Documented exceptions for exhaustive explanation, teaching-style expansion, brainstorming, and broad exploration.

## [1.0.0] - 2026-04-27

### Added
- Added the initial `SKILL.md` with ZeroToken working discipline for token-efficient task execution.
- Added `agents/openai.yaml` with a host-facing ZeroToken prompt preset.
- Added minimal publishing files: `package.json`, `README.md`, and `CHANGELOG.md`.
