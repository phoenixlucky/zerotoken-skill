# Changelog

All notable changes to this project will be documented in this file.

## [1.16.0] - 2026-09-20

### Added
- `scripts/audit_skill.py` 新增第 10/11 项检查：站内 Markdown 锚点有效性
  （近似 github-slugger 规则还原锚点，兼容 emoji 标题）、每个非测试脚本
  必须在文档中被引用（`scripts/test_*.py` 豁免，防新增脚本漏改清单）。
- `scripts/test_zt.py` 回归测试（测试自动发现、路由退出码、help 输出）。
- `package.json` 补 `repository` / `homepage` / `bugs` 元数据。

### Fixed
- README 指向 `SKILL.md` 的 4 个锚点失效：片段带了 emoji，而 GitHub 生成锚点时会
  剥离 emoji（`#⚔️-ai-…` 实际应为 `#-ai-…`）；现由 audit_skill 锚点检查长期兜住。

### Changed
- README 深度瘦身（19304 B -> 10632 B，-45%）：新增目录；合并重复的安装方式；
  把「场景详解 A-G」「尉缭子十原则全文」「搜索 / 编码 / 提示词 / 强化模式」等
  `SKILL.md` / `references/` 的副本改为摘要 + 入口（消除双份事实源）；
  平台小节由 6 张卡片改为一张表；新增 CI 状态徽章；
  修正「五种主流 Agent 工具」与 6 个小节的口径。
- `assets/zerotoken-banner.webp` 重压为 720x1080 / q72：582 KB -> 165 KB（-72%）。

## [1.15.0] - 2026-09-20

### Added
- `scripts/audit_skill.py` 新增第 9 项检查：CHANGELOG.md 顶部版本必须等于
  `package.json` 版本（版本号隐性第 4 处锚点，此前无机器校验）。
- 回归测试 `scripts/test_audit_skill.py` / `scripts/test_audit_encoding.py`
  （合规 fixture 通过 + 注入缺陷命中），回归测试 3 -> 5 个。
- `.editorconfig`：charset / eol / final-newline 的编辑器侧约束，与 `.gitattributes`
  及编码规范一致；`.ps1` 标注 `utf-8-bom`。
- `package.json` 增 `scripts.check`（等价 `python scripts/zt.py check`）。

### Fixed
- `scripts/audit_encoding.py` 纳入 BOM 规则校验：`.ps1` 必须 UTF-8 with BOM，
  其余文本必须无 BOM（此前只统计不判违规）。
- `scripts/audit_encoding.py` 改走 `safe_io`（`ensure_utf8_stdio` / `safe_print` /
  `safe_write`），消除「工具不守自身编码规范」的漂移。

### Changed
- `SKILL.md` 常驻体积预算 12KB -> 14KB（`audit_skill.py` 的 `SKILL_SIZE_BUDGET`），
  并同步 `AGENTS.md` / `README.md` 口径；实占 12194 B，此前仅余 94 B。
- `AGENTS.md` 修正「所有命令支持 `--json`」的表述：实际仅
  `check / audit / encoding / version` 支持，其余命令为文本输出。
- `scripts/zt.py` 的 `check` 步骤改为自动发现 `scripts/test_*.py`，新增测试无需手改入口。

## [1.14.0] - 2026-09-15

### Added
- `scripts/bump_version.py` — 版本号三处联动的校验与写入（`package.json` /
  SKILL.md frontmatter / README badge）。`--check` 供 CI 与发布前使用，
  终结 v1.13.2 记录的「三处联动只能人工核对」漏改问题。
- `scripts/audit_skill.py` — 文档一致性审计（8 项）：版本三处一致、SKILL.md 体积预算、
  Markdown 相对链接存在性、核心原则条数（SKILL.md vs README）、`scripts/*.py` 引用存在性、
  F 模式陷阱条数与文案声明一致、核心文档不得出现宿主专属工具名、
  非规范 CJK 字符（康熙部首 / 兼容表意文字）。
- `.github/workflows/ci.yml` — 最小 CI：两个回归测试 + 编码审计 + 文档一致性 + 版本联动。
- `AGENTS.md` 补项目结构、校验命令、发布指针（原先只有编码规范与一条安装笔记）。

### Fixed
- SKILL.md 中的异体字：用 Kangxi 部首 U+2F0C 冒充「文」，视觉相同但码位不同，
  搜索与精确匹配会静默失败。同类问题现由 `audit_skill.py` 长期兜住。
- README 核心原则表长期只有 7 条：v1.12.0 新增的 #8「先识别环境，再选 Shell」未同步，
  现由 `audit_skill.py` 强制两边条数一致。
- **`bump_version.py` 写入路径崩溃**：`apply_version()` 依赖正则的第 3 组拼接文本，
  而 SKILL.md 的锚点只有 2 组 → `python scripts/bump_version.py <版本号>` 抛
  `IndexError: no such group`，且此时 `package.json` 已被改写、另外两处未改（半写入状态）。
  改为基于第 2 组的 `match.span()` 替换，对组数变化免疫；补 `test_bump_version.py` 兜住。
  （该路径自引入起只被 `--check` 覆盖过，写入分支从未被测 —— 教训：CLI 的写入分支必须有测试。）
- `audit_encoding.py` / `bump_version.py` 统一返回退出码：发现问题返回 1
  （此前 `audit_encoding.py` 恒返回 0，CI 会把编码违规当成功放行）。

### Changed
- 文档统一以 zt.py 为主入口：`README.md`（F 模式段 + 文档地图）、
  `references/windows-powershell.md`（脚本工具段）、`AGENTS.md`（校验命令）、
  `references/publishing-clawhub.md`（发布时序 7 步 → 4 步，校验收敛为一条 `zt.py check`）、
  `.github/workflows/ci.yml`（5 个 step → 1 个）。
- `bump_version.py` 的 `check()` 重构为 `gather()`（返回结构化结果，CLI 与 JSON 共用）。
- `audit_encoding.py` 的 `--out` 默认值改为 `None`（默认行为仍是写 `audit_result.txt`；
  JSON 模式不落盘，除非显式 `--out`），避免 CI / `zt.py check` 污染工作区。
- `SKILL.md` description 补中文触发词（「省 token / 简洁点 / 直接给结果 / 少废话 / 别解释」），
  提高宿主自动加载命中率；新增一行工具入口指引（体积仍在 12KB 预算内）。

### Tests
- 新增负向探针验证：对仓库副本注入 8 类缺陷（版本漂移、坏链接、缺脚本引用、
  原则条数不一致、陷阱条数漂移、宿主专属工具名、异体字），`audit_skill.py` 全部命中。

## [1.13.2] - 2026-08-28

### Fixed
- **README 顶部版本徽章漏更新**：停在 `version-1.11.0`（v1.12.0 起 bump 只改
  `package.json` + `SKILL.md` frontmatter，README badge 未同步）。
  已更新为 `version-1.13.2`。
- 教训固化：**版本号 bump 是三处联动**（`package.json` / `SKILL.md` frontmatter /
  `README.md` 顶部 shield badge），发布节奏中应统一核对。

## [1.13.1] - 2026-08-28

### Changed
- **README.md 平台集成指南更新**（补发到 ClawHub 发布包）：
  - 方式一标注「（推荐，AI助手安装）」
  - 方式二、方式三补充 GitHub 源安装命令
    （`install-source --source https://github.com/phoenixlucky/zerotoken-skill` /
    「安装这个技能 https://github.com/phoenixlucky/zerotoken-skill」），
    与 ClawHub 源并列
- 教训固化：**发布包内的 README 以发布时工作区文件为准**——GitHub 提交 ≠
  ClawHub 包同步，README 等文档后续改动需新发版本（docs-only 可 bump patch）

## [1.13.0] - 2026-08-28

### Added
- **ClawHub 发布规范**（source: v1.12.0 实测发布过程）：
  - SKILL.md 新增「📤 ClawHub 发布」章节：关键事实 + 发布陷阱表（C1-C5）+
    固定发布时序
  - **C1**：PowerShell `curl` 是 `Invoke-WebRequest` 别名（参数不兼容），网络探测一律用 `curl.exe`
  - **C2**：`clawhub publish` 相对路径解析错误（默认 `--dir skills` 找不到根目录 SKILL.md），
    必须传绝对路径，且先 `--dry-run` 预览
  - **C3**：发布命令上传 registry 需 5-6 分钟且全程零输出，前台运行会被超时终止，
    必须后台运行 + 轮询等待
  - **C4**：ClawHub 安全扫描异步——提交成功（`pending security scans`）≠ 公开，
    registry 仍是旧版本号，用 `clawhub inspect` 复查
  - **C5**：发布前工作区必须干净（未提交改动会随包上传 ClawHub 但 GitHub 缺失，
    两端分叉），发布前后各查一次 `git status`
  - 关键事实澄清：ClawHub 不是 Git 端点（`git fetch/push clawhub` 404），
    发布必须走 clawhub CLI（pnpm 全局安装于 `%LOCALAPPDATA%\pnpm\clawhub.CMD`，用全路径调用）
- README.md「📖 核心文档」索引新增 ClawHub 发布条目

## [1.12.0] - 2026-08-25

### Added
- **环境识别与系统参数持久化**：新增 `scripts/detect_env.py` — 任何涉及命令行执行的
  任务开始时先探测当前系统参数并保存到 `.zerotoken/environment.json`（7 天有效期）：
  OS 名称/版本、推荐 Shell（Windows→PowerShell，Linux→bash，macOS→zsh）、
  控制台编码（stdout encoding + Windows ANSI/OEM 代码页）、
  **中文字符支持判定**（`console.cjk_capable`）、PowerShell 可用性/版本/发行版
  （5.1 Desktop 与 7+ Core 编码行为不同）、Git `core.quotepath` 现状
- 新增 G 模式（POSIX 标准工作流）：detect_env.py 识别到 Linux/macOS 时自动启用，
  使用 sh/bash/zsh 工具链，明确不套用 F 模式的 PowerShell 规避规则
- 核心原则新增 #8「先识别环境，再选 Shell」：命令行任务第一步先获取并保存系统参数，
  之后所有命令按已保存参数选择 Shell——**Windows 一律 PowerShell，禁用 bash**
- `init_env.ps1` 新增 [0.5] 系统参数识别段：输出 PowerShell 版本/发行版、ANSI 代码页、
  中文字符支持判定，并联动 `detect_env.py` 输出完整探测报告
- `docs/unicode-encoding-spec.md` 新增「Shell 选择规则」章节：先探测系统参数再选 Shell，
  中文支持能力以 `console.cjk_capable` 为准
- 回归测试 `scripts/test_detect_env.py`：recommended_shell 分支、CJK 判定矩阵、
  结构完整性、持久化 round-trip / 过期拒绝 / 损坏拒绝

### Changed
- **F 模式触发条件放宽**：由「Windows/PowerShell + 中文文本且用户确认」改为
  「detect_env.py 识别到 Windows 系统即自动启用」，中文支持内置于环境识别结果，
  不再要求任务涉及中文
- SKILL.md / README.md：F 模式描述同步改写为自动识别；模式计数更新为七种（A-G）；
  清除全部 ```` ```bash ```` 代码块标记（Windows 环境下不再展示 bash 用法）
- 工具清单补齐：SKILL.md 脚本表与 README.md 工具集列表均加入 `detect_env.py`

### Fixed
- `detect_env.py` 时间戳格式与过期解析不一致的 bug（`detected_at` 统一为
  紧凑格式供 `is_fresh()` 解析，另附人类可读的 `detected_at_iso`）
- `init_env.ps1` 变量 `$psEdition` 与 PS 只读自动变量 `$PSEdition` 冲突
  （PS 变量名大小写不敏感），更名为 `$psEditionName`

## [1.11.0] - 2026-08-14

### Added
- 新增陷阱 #14：PS 5.1 写方向编码不统一 — `Set-Content`/`Add-Content` 默认按 GBK
  写出（纯汉字→GBK 字节污染 UTF-8 文件；emoji 等字符**静默写成 `?` 丢字**，
  字节级实测为 `3F`），`Out-File` / `>` 默认 UTF-16 LE，显式 `-Encoding UTF8`
  又带 BOM。修复方案：PowerShell 内写 UTF-8 统一用
  `[IO.File]::WriteAllText($path, $text, [Text.UTF8Encoding]::new($false))`；
  含中文/emoji 的写入一律走 Python `safe_io.safe_write()` / `safe_append()`
- 新增陷阱 #15：`Add-Content -Encoding UTF8` 追加到不以换行结尾的文件时**不补换行**
  导致内容粘连（实测 `base` + 追加标题 → 粘连成一行），且带 BOM。
  修复方案：统一改用 `safe_io.safe_append()`（自动补换行、UTF-8 无 BOM）
- `docs/unicode-encoding-spec.md` 新增「文件写入编码矩阵（PS 5.1 实测）」：
  Set-Content / Add-Content / Out-File / WriteAllText 四种方式的默认与显式行为对照
- `scripts/init_env.ps1` 新增第 0 步：把当前会话 `[Console]::OutputEncoding` /
  `$OutputEncoding` 切到 UTF-8（仅当前会话生效，不改系统全局设置），
  缓解终端显示层中文乱码

### Changed
- `scripts/safe_io.py` 重构：新增 `sniff_encoding()`（BOM→UTF-8→GB18030 单一检测核心）
  与 `decode_bytes()`；编码无法确定时显式抛 `UnknownEncodingError`，
  **移除 `errors='replace'` 静默损坏兜底**（对齐 docs 规范「禁止静默替换」；
  `strict=False` 仅限查看场景且禁止回写）。`safe_read` 保留为兼容别名，
  UTF-16/32 解码统一交由对应 codec 剥离 BOM（避免开头残留 U+FEFF）
- `scripts/safe_io.py` `safe_append()` 修复段间粘连：目标文件存在且不以换行结尾时
  先补换行再追加，对齐 Add-Content「每次追加自带换行」语义
- 五个脚本的重复 `_ensure_utf8_stdio` + `sp` 副本统一收敛到
  `safe_io.ensure_utf8_stdio` / `safe_print`（batch_edit / verify_output /
  fix_encoding / detect_gbk_contamination 仅 import 复用）；
  `batch_edit.py` 删除行为分裂的本地 `safe_read`，改用统一的 `read_text`
- 同步更新 `SKILL.md`（陷阱表 13→15 条、模式速查、不做什么、工具表）、
  `README.md`（计数引用与 F 模式描述）

### Tests
- `scripts/test_safe_io.py` 扩充为完整回归：sniff 全分支、BOM 剥离无 U+FEFF、
  unknown 抛错、strict/非 strict、safe_write/safe_append 无 BOM+LF+补换行、
  write_result 往返

## [1.10.1] - 2026-08-13

### Changed
- 版本号 1.10.0 → 1.10.1

### Added
- 新增陷阱 #13：PowerShell 读取附件时中文乱码显示（Get-Content 默认按 ANSI/GBK 解码
  UTF-8 无 BOM 文件），属显示层问题、文件未损坏。修复方案：优先用 `read_file` 工具
  读取附件；必须在 PowerShell 中读时显式 `Get-Content -Encoding UTF8`；非 UTF-8 附件
  用 `safe_io.safe_read()` 自动检测编码；禁止把显示乱码误判为文件污染而盲目转码
- 同步更新 `SKILL.md`（陷阱表、模式速查表、不做什么）、`README.md`（3 处引用）、
  `docs/unicode-encoding-spec.md`（读取附件/文件编码细则）

## [1.10.0] - 2026-08-10

### Changed
- 版本号 1.9.1 → 1.10.0
- 文档排版与结构规范化：修复 `SKILL.md` 未闭合代码块（「精准提示词模板」标题此前被吞进代码块）；`SKILL.md` 顶层章节标题统一 emoji 前缀（与 README 一致）；`README.md` 与 `SKILL.md` 重复的 5 个章节（尉缭子十原则、搜索资料规范、精准提示词模板、ZeroToken 强化模式、退出条件）精简为摘要 + 锚点链接，单一信息源；修复 `docs/unicode-encoding-spec.md` 死链引用
- 搜索资料规范放宽：Chrome MCP 搜索引擎**不限百度**（百度只是默认，网络可用时 Bing / Google / 知乎等按检索效果自由选择）；Chrome MCP 不可用时允许使用当前网络可用的其他搜索方式（含 `web_fetch`），不再因首选方案不可用而放弃搜索。同步更新 `README.md`、`SKILL.md`
- 落地「Unicode 安全编码规范」（新增 `docs/unicode-encoding-spec.md`，15 条硬性规定 + 项目执行细则；AGENTS.md 增加编码规范约束）
- 所有 Python 脚本：控制台输出优先 `sys.stdout.reconfigure(encoding='utf-8')`（Python 3.7+），不再把中文替换成 `?`；写模式 `open()` 显式 `newline='\n'`，避免 Windows 文本模式把 LF 写成 CRLF
- `scripts/batch_edit.py` / `scripts/verify_output.py`：去除 `errors='replace'` 静默损坏，非 UTF-8/UTF-16/GB18030 文件显式抛错提示先检查原编码
- `scripts/init_env.ps1` 转为 UTF-8 with BOM（Windows PowerShell 5.1 解析中文必需）；清理未使用变量
- `.reasonix/skills/mcp-streamable-connect/mcp-bridge.js`：HTTP `Content-Type` 显式声明 `charset=utf-8`
- SKILL.md「安全文件读写模板」更新（写/追加显式 `newline='\n'`），替换字符示例改为文字描述（U+FFFD）

### Added
- 新增 `scripts/audit_encoding.py` 全项目编码审计工具（UTF-8 / BOM / 替换字符 / 混合换行检测）

## [1.9.1] - 2026-08-08

### Changed
- 版本号 1.9.0 → 1.9.1

## [1.9.0] - 2026-08-07

### Added
- SKILL.md 核心原则之后新增「AI 编程总纲（尉缭子十原则）」章节 — 以《尉缭子》兵法治编程纪律：先谋后动、统一方案、职责明确、不得越权、唯一命令、禁止旧令、严格执行、最小改动、可追溯、验证先于结束
- 十原则以「原则 + 要求 + 违反示例」表格精炼呈现，并给出与 B/C/E 任务模式的对应关系及可直接用作 System Prompt 的总纲引文
- 核心理念：省 token 是效率（ZeroToken），尉缭子是秩序（权限边界、单一指令、责任明确、执行一致）

## [1.8.2] - 2026-07-24

### Added
- 新增陷阱 #10-#12：PowerShell `&&` 不兼容、内联 `python -c` SyntaxError、终端显示层中文乱码
- 核心原则第3条补充大文件分页读取规则
- 核心原则第6条补充 `complete_step` 证据类型规则（files/manual/verification 用法 + 单步签收）
- 「不做什么」新增 3 条禁用规则

## [1.8.1] - 2026-07-24

### Added
- 增强搜索规范：新增「Chrome MCP 能搜什么」场景表，消除 AI 不知道 Chrome MCP 能搜微博/新闻等的问题
- 新增「禁用行为」三项硬约束：禁 web_fetch 直抓社交平台、禁自写 playwright 脚本、禁 web_fetch 直连搜索引擎

## [1.8.0] - 2026-07-?? (unreleased)

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
