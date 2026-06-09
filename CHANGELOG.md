# Changelog

All notable changes to this project will be documented in this file.

## [1.4.0] - 2026-04-27

### Added
- Added **E. 重大重构/架构调整** task mode to SKILL.md for handling systemic bugs, architecture mismatches, and large-scale refactoring — includes 5 trigger signals, 6-step flow (diagnosis → impact assessment → user-confirmed design → incremental migration → verified execution → cleanup), and dedicated output format.

## [1.3.0] - 2026-04-27

### Changed
- Deduplicated README.md by removing content replicated from SKILL.md; README now serves as a slim landing page.
- Trimmed package.json keywords from 24 to 7 (removed synonyms and sub-variants).
- Shortened SKILL.md frontmatter description for clarity.
- Relicensed from MIT to GPL-3.0 (copyleft license for stronger openness).

### Fixed
- Removed duplicate "Added LICENSE" entry from [1.1.0] in CHANGELOG.md — LICENSE was first added in v1.2.0.

## [1.2.0] - 2026-04-27

### Added
- Added about description and topic tags to GitHub repository.
- Added LICENSE file (MIT) to complete open source compliance.

## [1.1.0] - 2026-04-27

### Added
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
