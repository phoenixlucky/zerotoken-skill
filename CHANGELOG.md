# Changelog

All notable changes to this project will be documented in this file.

## [1.7.3] - 2026-07-?? (unreleased)

### Added
- 适配 browser-localmcp-skills：新增 mcp_call.py Python 包装脚本，彻底规避 Windows PowerShell 引号嵌套和 GBK 编码崩溃问题
- SKILL.md 新增「搜索资料指南」章节，明确 Chrome MCP 优先搜索策略
- SKILL.md 全量示例迁移至 mcp_call.py，消除 Windows 平台调用屏障

### Fixed
- 规避「Bing 搜索返回无关结果」问题，强制优先走 Chrome MCP（百度搜索）

## [1.7.2] - 2026-07-22

### Fixed
- 重新发布 v1.7.2 以修复 ClawHub 版本列表未更新的问题（前版 publish 成功但未写入数据库）
- 内容与 v1.7.0 一致

## [1.7.1] - 2026-07-22

### Fixed
- 重新发布以刷新 ClawHub 页面展示版本（技术性 bump，内容与 v1.7.0 一致）

## [1.7.0] - 2026-07-21

### Security
- **Tp4 (MCP Tool Poisoning)** — 重写 SKILL.md `description` frontmatter，从纯"token-efficient discipline"扩展为同时声明文件系统工具能力的透明描述。
- **Language Policy Opt-in** — 添加 `language_opt_in: true` metadata；H1 下方新增语言选择提示，明确中文引导为 opt-in；`agents/openai.yaml` 的 `default_prompt` 添加 opt-in 前缀。
- 新增 `language_opt_in` metadata 字段至 SKILL.md frontmatter，供主机/审计工具检测。

### Added
- `agents/openai.yaml` 的 `short_description` 改为英文描述 + opt-in 说明。
- `scripts/safe_io.py`: 新增 `safe_append(path, content)` 函数 — 使用 Python `open(path, 'a', encoding='utf-8')` 替代 PowerShell `Add-Content`，防止 GBK 编码污染 UTF-8 文件
- `scripts/detect_gbk_contamination.py`: 新增检测和修复 UTF-8 文件中 GBK 编码污染的独立脚本（三种模式：`scan` 扫描目录检测污染文件、`inspect` 详细查看污染位置和字节上下文、`fix` 智能修复污染并支持 `--backup` 备份和 `--preview` 预览）
- SKILL.md F 模式：新增陷阱 #8（PowerShell Add-Content GBK 编码污染），脚本工具表新增 `detect_gbk_contamination.py` 条目并更新 `safe_io.py` 条目，安全文件读写模板增加安全追加示例，"不做什么"清单增加 Add-Content 禁令
- `scripts/init_env.ps1`: 脚本工具提示中加入 `detect_gbk_contamination.py` 条目并更新 `safe_io.py` 描述

## [1.6.2] - 2026-07-10

### Security
- Removed hardcoded git commit permission from `reasonix.toml` — replaced with generic tool permissions (Bash, Read, Edit, Write) to eliminate appearance of hidden repository-modifying intent.
- Changed `scripts/init_env.ps1` Git quotepath from `--global` to local scope (removed `--global` flag); removed unnecessary `core.autocrlf` setting.
- Updated SKILL.md security disclosure to explicitly address `reasonix.toml` permission declarations and `init_env.ps1` local-only scope.

## [1.6.1] - 2026-07-10

### Security
- Added `security` metadata to SKILL.md frontmatter — explicitly declares all file system capabilities (read/write, batch-edit, encoding-conversion, git-operations) so users and hosts can review before installation.
- Added "🛡️ 能力与安全披露" (Capabilities & Security Disclosure) section to SKILL.md — transparently documents what the skill can do beyond prompting guidance.
- Clarified F mode (Windows/PowerShell) is conditional and optional, not default behavior — macOS/Linux users and English-only workflows do not need it.
- Added language disclosure: documentation is primarily in Chinese but the skill adapts to the user's interaction language.
- Fixed `scripts/fix_encoding.py` docstring: changed "默认创建 .bak 备份" to "需要 --backup 参数才会创建 .bak 备份" to match actual implementation behavior.

## [1.6.0] - 2026-07-10

### Added
- Added `scripts/` directory with 4 Python utility scripts + 1 PowerShell init script:
  - `scripts/safe_io.py` — safe file read/write module (handles UTF-8/UTF-16, write-to-file instead of print)
  - `scripts/fix_encoding.py` — batch file encoding detection and conversion to UTF-8 (4 modes: scan/preview/convert/check-replacement)
  - `scripts/verify_output.py` — verification result output to .txt file (replaces print to avoid GBK error)
  - `scripts/batch_edit.py` — apply multiple replacements to one file atomically (solves edit_file consecutive edit blocking)
  - `scripts/init_env.ps1` — Windows PowerShell environment init (git config, Python check, encoding health)
- Added `.gitattributes` — proper line ending configuration for all file types
- Updated SKILL.md F mode: references scripts/ tools in decision table and recommended workflow; adds "脚本工具" reference table

## [1.5.0] - 2026-07-10

### Added
- Added **F. Windows/PowerShell 环境适配** task mode to SKILL.md for handling Windows PowerShell + Chinese text environment pitfalls — includes 7 known trap solutions, recommended workflow, safe file I/O template, and "what not to do" checklist.

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
