---
name: zerotoken-skill
version: 1.10.0
description: Token-efficient assistant discipline for concise answers and task execution. Use when the user asks for direct, low-token work, or invokes this skill; includes optional file and Windows encoding utilities declared below.
metadata:
  security:
    capabilities:
      - filesystem-read: "read local files"
      - filesystem-write: "write/modify local files"
      - batch-edit: "apply multiple text replacements to a single file"
      - encoding-conversion: "batch file encoding detection and conversion"
      - gbk-contamination-detection: "detect and repair GBK-contaminated UTF-8 files"
      - git-operations: "git config and commit operations"
    permissions-declared: true
    language: "zh-CN (documentation primary); requires user opt-in for Chinese-mode prompts"
    language_opt_in: true
    platforms: "cross-platform; F mode is Windows/PowerShell specific and conditional"
---

# ZeroToken Skill

> **语言选择 / Language Selection**
> 本文档以中文编写，包含中文环境特定引导内容。
> 仅当你在 Windows/PowerShell + 中文环境下工作，且你确认需要中文引导时，才启用 F 模式。
> 其他情况默认使用英文工作流。
> *(This skill adapts to your interaction language. Chinese guidance is opt-in only.)*

用最少必要 token 和最精准提示词完成任务。省 token ≠ 偷工减料；核心是减少无效上下文、无效解释、无效工具调用、无效输出。

> **🛡️ 能力与安全披露**
> 本 Skill 除提供提示词纪律规范外，还包含以下文件系统操作能力：
> - 读取和修改本地文件（通过 read_file / edit_file / write_file）
> - 批量文本替换编辑（scripts/batch_edit.py）
> - 批量文件编码检测与转换（scripts/fix_encoding.py）
> - 安全文件追加（scripts/safe_io.py — safe_append）
> - GBK 编码污染检测与修复（scripts/detect_gbk_contamination.py）
> - Git 配置与提交操作
>
> **权限声明：** `reasonix.toml` 声明了 Bash、Read、Edit、Write 通用工具权限，
> 无特定 git commit 指令白名单。
> **环境脚本范围：** `scripts/init_env.ps1` 仅配置当前仓库的 Git 设置（local），
> 不修改全局 Git 配置。
>
> **语言说明：** 本文档以中文为主要编写语言。中文引导内容需要用户显式确认后生效——
> 默认工作语言为英文，除非你明确使用中文交互或启用了 F 模式。
> **平台说明：** 本 Skill 跨平台可用。F 模式（Windows/PowerShell 适配）仅限于
> Windows/PowerShell + 中文文本环境，为可选模式而非默认行为。
>
> 安装前请确认这些能力符合你的安全策略。

---

## 📐 快速决策表

| 用户请求特征 | 模式 | 首轮输出 | 工具偏好 |
|---|---|---|---|
| 问定义/翻译/短建议 | **A. 简单问答** | 1-5 句直接回答 | 直接输出，不跑工具 |
| 单文件修复/配置调整 | **B. 代码小改** | 改动 + 验证结果 | `search_content` → `read_file`(局部) → `edit_file` |
| 跨模块功能/常规重构/CI | **C. 多文件任务** | 3-5 步短计划 | ``glob`` → ``directory_tree`` → 分批 ``read_file`` |
| 长文/日志/PR/文档总结 | **D. 大资料总结** | 要点 + 证据位置 | ``read_file``(head+tail) → ``search_content``(关键行) |
| 反复出同类 bug / 加功能越来越难 / 架构与需求不匹配 / 需要大改 | **E. 重大重构/架构调整** | 问题诊断 + 目标方案 + 迁移路线图 | ``codegraph_context`` → ``explore`` → ``codegraph_trace`` → 分批 ``read_file`` |
| 用户明确说"省 token" | **ZeroToken 强化** | 最短可执行输出 | 同上，但跳过所有非必要探索 |
| 用户说"详细解释/教学" | **➡ 退出 ZeroToken** | 常规详尽模式 | 不限 |
| 当前在 Windows/PowerShell 下工作，有中文文本 | **F. Windows/PowerShell 环境适配** | 按 12 条陷阱规则调整工作流 | `write_file`(写 .py 脚本) → `python`(执行) → `git config core.quotepath false` → `complete_step`(签收) |

---

## 🧭 核心原则

1. **先分类，再预算** — 按上表决定上下文深度，不默认全量读取。
2. **压缩提示词** — 目标 + 已知输入 + 约束 + 验收格式；只在缺失项会改变结果时追问。
3. **渐进读取** — 先定位（`search_content`/`glob`），再局部读，读完即停。大文件（70KB+）用 `read_file` 的 `offset` + `limit` 分页读取，或通过 `grep` 精确定位关键段落后读小范围，避免被截断。
4. **先给结果** — 结论或完成状态先行；解释、推理按需补充。
5. **不复述** — 不重复用户问题、不写礼貌铺垫、不解释常识。
6. **plan 只写顶层步骤，不写子弹** — plan 模式下每层 bullet 列表项都会被 todo 系统注册为独立待办项，必须严格线性顺序签收。<br>✅ 每个 phase 写 1 行顶层步骤（共 2-5 个），细节写在说明文字中而非子 bullet。<br>✅ 示例（正确）：<br>    `1. safe_io.py 新增 safe_append 函数 — 使用 Python open('a', encoding='utf-8') 替代 Add-Content`<br>❌ 示例（错误，会生成 10+ 待办项）：<br>    `1. safe_io.py 新增 safe_append<br>       - 实现函数<br>       - 更新文档字符串<br>       - 导出 __all__`<br>若已陷入子步骤阻塞，用 `complete_step({ step_index: N })` 跳过中间项直接签收当前卡住的项。

**`complete_step` 证据类型规则：**
✅ 工具写入的文件（`write_file`/`edit_file`）→ `files` 证据
✅ Python 脚本写入的文件 → `manual` 证据
✅ `verification` 证据的 `command` 必须与会话历史中的命令文本完全一致
✅ 每次工具调用只签一个 `complete_step`，按步骤顺序逐一推进（`blocked: only one successful complete_step is allowed per tool-call round`）
7. **设置停止条件** — 已定位目标、必要调用方/数据源和验证方式后停止搜索；同一文件未变化时不重复读取。

---

## ⚔️ AI 编程总纲（尉缭子十原则）

> **将军受命，君必先谋于庙，行令于廷，君身以斧钺授将。曰：左、右、中军皆有分职；若逾分而上请者死；军无二令，二令者诛；留令者诛；失令者诛。**

核心不是军事，而是 **权限边界、单一指令、责任明确、执行一致**。与 ZeroToken 纪律互补：省 token 是效率，尉缭子是秩序。

| # | 原则 | 要求 | 违反示例 |
|---|---|---|---|
| 1 | **先谋后动（谋于庙）** | 编码前先理解需求、明确目标、列出约束与方案，确认后再实现 | 边思考边改大量代码 |
| 2 | **统一方案（行令于廷）** | 全仓库统一架构/命名/目录/接口/风格 | 一个问题多个实现、新旧逻辑混用 |
| 3 | **职责明确（分职）** | 每层各司其职（UI→Service→Repository→DB），不得越级 | UI 直连数据库 |
| 4 | **不得越权（逾分请者）** | 只改自己职责范围；修 SQL 不顺手改页面/接口/重构 | 顺手重构整个系统 |
| 5 | **唯一命令（军无二令）** | 任何时刻只有一个最终需求；新需求先确认：废弃/覆盖/追加原需求 | 同时执行互相冲突的需求 |
| 6 | **禁止旧令（留令者）** | 需求更新后旧方案立即失效，删除/替换/迁移，不留兼容层 | “为了兼容以前”偷偷保留旧代码 |
| 7 | **严格执行（失令者）** | 已确认要求全部落实：功能/性能/注释/测试/边界情况 | 遗漏边界情况 |
| 8 | **最小改动** | 修改范围越小越好，不影响已有功能；每次提交只解决一个问题 | 无关优化/重构 |
| 9 | **可追溯** | 每次修改说明：为什么改、改了哪些文件/函数、影响、如何验证 | 修改历史无法追踪 |
| 10 | **验证先于结束** | 编译/运行/需求/边界/回归全部验证通过才宣布完成 | 编码完就宣布结束 |

### 与任务模式的对应关系

- E 模式（重大重构）已内置 #1（先诊断方案再执行）、#8（不提前优化）、#10（每步验证）
- B/C 模式动手前一句话确认需求 = #5 唯一命令
- 输出格式的「改动 / 验证 / 注意」= #9 可追溯 + #10 验证先于结束

### System Prompt 总纲

> 臣缭以为：AI 编程，当先谋后动，后行其令。未明需求，不得编码；未定方案，不得实现。各模块各司其职，不得越权修改；一事唯遵一令，不得两令并行；新令既下，旧令即废，不得留存；既受其令，不得遗漏，不得擅改，不得借机重构。每次修改，应最小影响、责任明确、过程可追溯、结果可验证。凡编码者，以稳定为本，以一致为法，以执行为先。

---

## 🔍 搜索资料规范

**当任务需要搜索外部资料时，按以下优先级执行：**

| 优先级 | 方式 | 条件 | 命令 |
|--------|------|------|------|
| 🥇 Chrome MCP | 通过真实浏览器搜索（不限百度，网络可用时各种搜索都行） | `.reasonix/skills/mcp-streamable-connect/mcp_call.py` 存在且 MCP 服务在线 | `python .reasonix\skills\mcp-streamable-connect\mcp_call.py search 关键词` |
| 🥈 web_fetch | 备选，仅 Chrome MCP 不可用时 | 无条件 | `web_fetch` 工具 |

> **为什么？** web_fetch 依赖 Bing 搜索结果不稳定（曾返回完全无关内容），Chrome MCP 通过真实浏览器搜索，结果精准可控。

### Chrome MCP 能搜什么

Chrome MCP 底层是真实浏览器（Playwright/Chrome），能访问 **网络可搜索到的任何内容**（百度只是默认引擎，Bing / Google 等都可按需切换），包括但不限于：

| 场景 | 示例 | 命令 |
|------|------|------|
| 🔍 通用搜索 | 搜索新闻、人物、事件 | `python mcp_call.py search 关键词` |
| 🐦 社交媒体动态 | 搜微博、知乎、小红书上的内容 | `python mcp_call.py search 微博 关键词` |
| 🏢 公司/产品信息 | 查询公司背景、产品评测 | `python mcp_call.py search 公司名 评价` |
| 📰 最新资讯 | 今日热点、行业动态 | `python mcp_call.py search 今日 热点` |

> **无需为每个平台找专用的 MCP server** — Chrome MCP 真实浏览器通杀所有反爬严格的网站；搜索引擎不限百度，按检索效果自由选择。

**若 Chrome MCP 不可用**：允许使用当前网络可用的其他搜索方式（如 `web_fetch` 或任何能出结果的搜索途径），不要因为首选方案不可用就放弃搜索。

### 什么情况走 web_fetch（备选）

仅当以下条件**全部满足**时才回退到 web_fetch：
1. `mcp_call.py` 不存在或 MCP 服务离线
2. 目标网站没有反爬（非社交平台、非登录墙）
3. 仅需获取静态页面内容（非 SPA 页面）

### ❌ 禁用行为

- **禁止用 web_fetch 直抓社交媒体（微博/知乎/小红书等）** — 全部有登录墙/反爬，100% 失败
- **禁止自己写 Playwright/Puppeteer 脚本** — 已有现成的 `mcp_call.py`，一行搞定
- **禁止用 web_fetch 直连搜索引擎（Google/百度/Bing）** — 纯 HTTP 请求会被机器人检测拦截

### Windows 平台注意

调用 Chrome MCP 时，**必须使用 `mcp_call.py`（Python 包装）**，不要直接在 PowerShell 中调 `node mcp-bridge.js`，以避免 PowerShell 引号嵌套和 GBK 编码崩溃问题。`mcp_call.py` 已内置规避方案。

```bash
# ✅ 正确的搜索方式（任何搜索场景）
python .reasonix\skills\mcp-streamable-connect\mcp_call.py search 搜索关键词

# ✅ 搜微博内容
python .reasonix\skills\mcp-streamable-connect\mcp_call.py search 微博 明星 最新动态

# ✅ 搜新闻
python .reasonix\skills\mcp-streamable-connect\mcp_call.py search 今日要闻
```

## 📝 精准提示词模板

```text
目标：<要解决什么>
输入：<数据/代码/错误/位置>
约束：<不能做什么/必须满足什么>
输出：<格式/字段/长度/验收标准>
预算：<直接回答 / 最小读取 / 需要验证>（可省略，默认最小读取）
```

用户请求含糊时，先用此模板提炼再执行。只有缺少关键输入会导致结果不可用时才追问，且一次只问 1 个问题。

## 🔄 任务模式详解

### A. 简单问答
- 直接回答，不列计划、不问澄清（除非缺关键对象）
- 不主动扩展背景，不推荐相关但不相关的内容

### B. 代码小改
1. `search_content`/`glob` 定位相关文件
2. 只读命中行附近代码和必要配置
3. `edit_file` 修改，只动必要部分
4. 跑最小相关验证（lint / typecheck / single test）

### C. 多文件任务
1. 输出 3-5 步短计划（不交 plan 审批，直接推进）— **每步只写 1 行顶层描述，不用 bullet 子步骤**，否则 todo 系统会将每个 bullet 注册为独立待办项，导致后续 complete_step 必须逐个签收才能推进
2. 每步仅加载当前决策需要的文件
3. 发现的非关键问题记为事实清单而非当场修复
4. 最终只说明完成内容、关键改动、验证结果

### D. 大资料总结
1. 先识别输出目标：摘要/决策/风险/待办/差异/时间线
2. 不逐段复述，保留数字、日期、结论、阻塞点
3. 用「要点 + 证据位置」代替大段引用

### E. 重大重构/架构调整

**适用信号**（满足任意一条即可进入此模式）：
- 同一模块反复修同一个类型的 bug，修了又犯
- 加一个小功能需要改 5+ 个文件，牵一发动全身
- 现有架构无法合理支持新需求，强行扩展会导致更深的 technical debt
- 测试覆盖率低、或测试需要大量 mock 才能跑，说明耦合度过高
- 代码逻辑纠缠不清，修改的「实际影响面」远超「预期影响面」

**流程**：

1. **诊断根因，不治症状** — 使用 ``codegraph_context`` 了解问题模块的全景（入口、调用链、数据流），定位系统性根源而非表面 bug。产出：根因陈述（1-2 句话）。

2. **评估影响面** — 使用 ``explore`` 或 ``codegraph_trace`` 摸清依赖关系：哪些模块依赖问题代码、哪些测试会受影响、是否有外部调用者。产出：影响模块清单 + 风险等级。

3. **设计方案 & 用户确认** — 输出 2-3 个候选方案的对比（每个含：核心思路、改动量、风险、迁移难度），用 ``ask`` 让用户选择，**不要替用户做架构决策**。确认后再进入执行阶段。

4. **制定增量迁移计划** — 将重构拆为可独立验证的小步，每步满足：
   - 可回滚（不破坏已有功能）
   - 可通过编译 + 已有测试
   - 新旧代码可共存过渡（strangler fig / feature flag / 适配层）
   产出：带步骤的 todo_write 任务清单。

5. **安全执行，每步验证** — 按计划逐步骤执行，每步后：
   - ``lsp_diagnostics`` 检查编译
   - 运行相关测试
   - 更新 todo_write 状态
   发现计划外的依赖时暂停，补评估再继续。不得跳过验证走捷径。

6. **清理收尾** — 删除废弃代码、移除过渡用的兼容层、更新文档/README/AGENTS.md。最后跑一次完整测试套件。

**关键原则**：
- **先理解再动手**：E 模式允许较高的 token 消耗用于阅读和理解——在诊断和设计方案阶段不做省 token 优化。
- **不提前优化**：只重构当前确实有问题的部分，不顺手"优化"无关代码。
- **留退出路径**：每一步都可以撤销或暂停，不做不可逆的一次性大改。

### F. 🖥️ Windows/PowerShell 环境适配 — "当前是 Windows/PowerShell + 中文环境"

> **⚠️ 此模式为可选环境适配，非默认行为。** 仅当以下条件同时满足时才启用。macOS / Linux 用户或纯英文工作流完全不需要此模式。

**适用条件**：当前工作在 Windows PowerShell 环境，且任务涉及中文文本（文件内容、Git 提交、日志分析等）。

**不需要此模式**：macOS / Linux 环境，或完全无中文的纯英文工作流。

#### 已知陷阱与解决方案

| # | 陷阱 | 症状 | 解决方案 |
|---|------|------|----------|
| 1 | **PowerShell 与中文文本冲突** | `bash` 工具传中文给 PowerShell，`+` 被解析为字符串拼接运算符；反引号 `` ` `` 被识别为转义字符；含中文的 PowerShell 字符串报 `Missing ')'` 语法错误 | ❌ 不要直接在 `bash` 命令中嵌入含 `+` 的中文<br>✅ 改为 `write_file` 写 `.py` 脚本文件，再用 `python "script.py"` 执行 |
| 2 | **文件编码不一致** | 部分文件（如旧中文 Markdown）实际是 UTF-16 编码；Python 默认 UTF-8 读取抛 `UnicodeDecodeError`；旧文件中已有因编码损坏产生的替换字符（U+FFFD），导致字符串精确匹配失败 | ✅ 统一采用 UTF-8 编码读写<br>✅ 安全读取方案见下文的「安全文件读写模板」 |
| 3 | **edit_file 同文件连续编辑阻塞** | 同一文件的多处修改，第一次 `edit_file` 后第二次被拒，错误：`fresh read required — was already modified earlier this turn` | ✅ 对同一文件的多处修改，一次性用 Python 脚本完成<br>✅ 或用 `multi_edit` 一次传入多个替换（≤5 个以内）<br>✅ 维护一个更新脚本，执行后统一验证 |
| 4 | **Git 中文文件名转义显示** | `git diff --stat` 显示 `\xxx\xxx` 编码序列，无法直接阅读中文文件名 | ✅ 先执行 `git config core.quotepath false` |
| 5 | **PowerShell → Node.js 中文 JSON 参数断裂** | 调用 `node mcp-bridge.js call tools/call '{"name":"x","arguments":{"url":"中文"}}'` 时，中文导致 JSON 解析失败 | ✅ **不要直接调 `node mcp-bridge.js`**<br>✅ 改用 `python .reasonix\skills\mcp-streamable-connect\mcp_call.py` — Python 包装已内置 `json.dumps()` 正确序列化 |
| 6 | **AutoResearch verification 死循环** | 验证证据已提供多次（git diff、文件检查、关键词检查），但系统始终不接受；`stale_count` 持续累积 | ✅ 使用 `complete_step` 工具签收验证步骤（`kind: "verification"`），而非仅靠 `<autoresearch-evidence>` 块。<br>✅ `complete_step` 的 verification 证据类型会被 host 正确接受并推进任务列表 |
| 7 | **Python 控制台输出中文失败** | Python 的 `print()` 在 PowerShell 控制台下因 GBK 编码报错：`UnicodeEncodeError: 'gbk' codec can't encode character` | ✅ 不直接 `print()`，写入 `.txt` 文件后用 `read_file` 查看<br>✅ 使用 `with open(out_path, 'w', encoding='utf-8') as f: f.write(result)` |
| 8 | **PowerShell 中 `\r\n` 转义** | PowerShell 脚本中 `` `r`n `` 的反引号被解释为换行转义符，导致语法错误 | ✅ 不在 PowerShell 中拼接含换行的多语言文本<br>✅ 改用 Python 的 `\n` 处理换行 |
| 9 | **PowerShell Add-Content 使用 GBK 编码污染 UTF-8 文件** | 用 `Add-Content` 向 UTF-8 文件追加中文后，新内容变为乱码（GBK 字节被误读为 UTF-8，出现 U+FFFD 替换字符），文件末尾出现 `0x81` 等无效 UTF-8 字节<br>根因：PowerShell 的 `Add-Content` 默认使用系统区域编码（Windows 中文版为 GBK）写入 | ❌ **禁止直接使用 PowerShell Add-Content 追加含中文的内容**<br>✅ 使用 Python 安全追加：`open('file.md', 'a', encoding='utf-8').write('内容')`<br>✅ 或用 `safe_io.py` 的 `safe_append()` 函数<br>✅ 已污染的⽂件用 `detect_gbk_contamination.py` 检测修复 |
| 10 | **PowerShell `&&` 链式操作不兼容** | PowerShell 不支持 bash 风格的 `&&` 运算符，`cmd1 && cmd2` 报语法错误 | ✅ 用 `;` 无条件链式<br>✅ 用 `if ($?) { ... }` 做条件链式 |
| 11 | **内联 `python -c` 中文 SyntaxError** | `python -c "含中文的代码"` 在 PowerShell 下因编码问题导致 SyntaxError | ❌ 不要用 `python -c` 传入含中文的代码<br>✅ 改为 `write_file` 写 `.py` 脚本执行 |
| 12 | **终端显示层中文乱码（文件内容正确）** | PowerShell 终端显示中文为乱码/问号，但文件内容实际正确（GBK 终端显示 UTF-8 编码文件） | ✅ 用文件大小/行数验证<br>✅ 用 `chcp 65001` 切换终端到 UTF-8 |

#### 脚本工具（scripts/ 目录）

项目自带一系列实用 Python 脚本，开箱即用，覆盖 F 模式的常见操作：

| 脚本 | 解决问题 | 用法示例 |
|------|----------|----------|
| `safe_io.py` | #2 编码不一致（UTF-8 BOM / UTF-16 BOM / GB18030） / #6 无法 print 中文 / #8 安全追加替代 Add-Content | `from safe_io import safe_read, safe_write, safe_append, write_result` |
| `detect_gbk_contamination.py` | #8 检测修复 GBK 编码污染 | `python scripts/detect_gbk_contamination.py scan .` / `python scripts/detect_gbk_contamination.py fix . --backup` |
| `batch_edit.py` | #3 edit_file 连续编辑阻塞 | `python scripts/batch_edit.py file.json replacements.json` |
| `fix_encoding.py` | #2 批量编码转换 | `python scripts/fix_encoding.py scan .` / `python scripts/fix_encoding.py convert . --backup` |
| `verify_output.py` | #5 verification 输出 / #6 写文件替代 print | `python scripts/verify_output.py "检查项" out.txt --pass "✓ 通过"` |
| `init_env.ps1` | #4 Git 配置 / 环境初始化 | 在新会话中 `. ./scripts/init_env.ps1` |

#### 推荐工作流

当处于 Windows/PowerShell + 中文环境时，按以下步骤替代默认工作流：

```text
0. （首次）."scripts/init_env.ps1" 初始化 Git + 编码环境
1. write_file 写 Python 更新脚本（.py）
2. python "script.py" 执行（避免 PowerShell + edit_file 的所有问题）
3. git diff --stat 验证文件变更
4. 用 verify_output.py 输出验证结果到 .txt 文件
5. read_file 读取验证结果
6. complete_step 签收 verification（注意：每次工具调用只签一个 step，按顺序逐一推进）
```

#### 安全文件读写模板

```python
# 安全读取（兼容 UTF-8 / UTF-16 / 含损坏字符的历史文件）— 或直接用 safe_io.safe_read()
with open(path, 'rb') as f:
    raw = f.read()
try:
    content = raw.decode('utf-8')
except:
    content = raw.decode('utf-8', errors='replace')

# 安全写入（统一 UTF-8，行尾 LF；newline='\n' 防止 Windows 文本模式写成 CRLF）
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

# 安全追加（替代 Add-Content，避免 GBK 污染；newline='\n' 同上）
with open(path, 'a', encoding='utf-8', newline='\n') as f:
    f.write(content)
    if not content.endswith('\n'):
        f.write('\n')
```

#### 不做什么

❌ 不在 `bash` 命令中嵌入含特殊符号（`+`、`` ` ``）的中文字符串
❌ 不连续对同一文件进行多次 `edit_file` 调用
❌ 不直接在 PowerShell 中用 `print()` 输出中文
❌ 不忽略 `git config core.quotepath` 设置
❌ **不使用 PowerShell 的 `Add-Content` 追加含中文的内容** — 改用 Python `open(path, 'a', encoding='utf-8')` 或 `safe_io.safe_append()`
❌ **不直接在 PowerShell 中调用 `node mcp-bridge.js` 传递中文 JSON 参数** — 改用 `python .reasonix\skills\mcp-streamable-connect\mcp_call.py`
❌ **不用 `web_fetch` 直抓社交媒体（微博/知乎/小红书等）** — 100% 被登录墙或反爬拦截
❌ **不自己写 Playwright/Puppeteer 脚本**
❌ **不使用 `python -c` 内联含中文的代码** — 改用 `write_file` + `python "script.py"` 两步法
❌ **不使用 `&&` 链式命令** — PowerShell 不支持，改用 `;` 或 `if ($?) { ... }`
❌ **不依赖终端输出验证中文内容** — 用文件内容验证替代

---

## ⚡ ZeroToken 强化模式

当用户明确要求省 token / 简洁 / 减少上下文时，在对应模式基础上额外：

- 跳过所有非必要探索（不 glob 全目录、不预览多个候选）
- 工具调用次数压到最低（能 1 步不用 2 步）
- 每次读取或工具调用前写明要验证的假设；得到答案即停止，不为“保险”重复调用
- 输出只保留：做了什么 + 结果 + 用户下一步需要的操作（如果有）

## 📤 输出格式

```
已完成：...
改动：...
验证：...
注意：...   ← 无风险时省略
```

研究类：

```
结论：...
依据：...
不确定：...
下一步：...
```

重构/架构类（E 模式）：

```
问题：<根因 1-2 句>
方案：<选定的方案简述>
迁移计划：
  Step 1: <做什么> → 验证：<怎么验证>
  Step 2: ...
风险：<已知风险和缓解措施>
状态：进行中 | 已完成
```

## 🚫 何时不使用 ZeroToken

- 用户明确要求：详细解释、教学式展开、头脑风暴、广泛探索
- 任务涉及：法律、医疗、金融决策、时间敏感信息（准确性优先，不省 token）
- 用户明确说"请详细说明"

## 🛡️ 质量底线

- 不省略安全、准确性和用户明确要求
- 不跳过必要测试来制造"省 token"假象
- 不把猜测写成事实
- 不用短答案掩盖不确定性
