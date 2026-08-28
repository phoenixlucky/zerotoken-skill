<div align="center">

# ⚡ ZeroToken Skill

**让 Agent 用最少的 token 做最准的事**

> ⚔️ **将军受命，君必先谋于庙，行令于廷，君身以斧钺授将。曰：左、右、中军皆有分职；若逾分而上请者死；军无二令，二令者诛；留令者诛；失令者诛。**
>
> 💬 **用不完，根本用不完，妈妈再也不用担心我缺 token 了。**

[![Version](https://img.shields.io/badge/version-1.13.2-blue.svg)]()
[![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/author-phoenixlucky-orange.svg)]()
</div>

> **ZeroToken Skill** 是一套为 AI Agent 设计的**提示词纪律规范**——在不降低回答准确性的前提下，压缩无效上下文、无效解释、无效工具调用和无效输出，从而大幅降低 token 消耗和响应延迟。
>
> 它解决的核心问题是：Agent 在任务中经常过度读取、过度思考、过度输出，导致一次对话消耗成千上万不必要的 token。ZeroToken Skill 通过一套可执行的**模式决策表 + 行为约束 + 工具链策略**，让 Agent 在每一个任务环节都有明确的"省 token 行为准则"。
>
> 🎯 **目标：** 用最精准的提示，做最少的往返，产最精炼的结果。
>
> ✅ **适用于：** Reasonix / Codex CLI / OpenCode / Hermes / Cline 等主流 Agent 工具。一次学习，全平台受益。

<div align="center">

<img src="assets/zerotoken-banner.webp" alt="ZeroToken Skill 概览" width="480">

</div>

---

## 🔌 平台集成指南

### 方式一（推荐，AI助手安装）
```text
请依次阅读并安装以下 Skill。

- **ZeroToken Skill** — phoenixlucky，Token 高效约束：最少 token 和精准提示完成任务，减少无效输出
- 地址：https://github.com/phoenixlucky/zerotoken-skill

请根据上面每个 Skill 的「安装指令」完成安装。
```

### 方式二：从远程 Skill 仓库引用

```
install-source --source https://github.com/phoenixlucky/zerotoken-skill
```

或者

```text
install-source --source https://clawhub.ai/phoenixlucky/zerotoken-skill
```

### 方式三 （AI助手安装）
```text
安装这个技能  https://github.com/phoenixlucky/zerotoken-skill
```

或者

```text
安装这个技能  https://clawhub.ai/phoenixlucky/zerotoken-skill
```

以下是 ZeroToken Skill 对五种主流 Agent 工具的具体强化方向。

---

### ⚡ Reasonix

| 强化维度 | 说明 |
|---------|------|
| **🧠 原生 Skill 引擎** | Reasonix 的 Skill 机制原生支持本规范，载入即用，无需额外配置 |
| **🎯 自动模式匹配** | 根据请求特征与系统环境自动选择任务模式之一（A-G），无需手动指定 |
| **🔧 工具链优化** | 按模式限制工具调用范围（简单问答不调工具、多文件任务分批加载） |
| **📄 输出规范** | 结论先行、不复述、要点+位置 等输出模板内嵌为默认行为 |
| **💰 Token 预算策略** | 按模式自动分配上下文深度：简单问答极低预算，重大重构允许高消耗 |

---

### 🤖 Codex CLI

| 强化维度 | 说明 |
|---------|------|
| **📏 提示词纪律** | 消除冗长的 Agent 开场白、过渡语和客套话，直入主题 |
| **🎣 工具调用策略** | 先搜索定位再局部读取，避免扫描全项目；能 1 步不用 2 步 |
| **✂️ 输出精简** | 只返回结果+验证+注意，不添加无关分析和总结评语 |
| **🧮 上下文预算意识** | 先判断请求类型再决定投入多少上下文，不默认全量读取 |

---

### 🔧 OpenCode

| 强化维度 | 说明 |
|---------|------|
| **🎯 行为可预测性** | 请求类型公开匹配对应模式，Agent 行为一致可预期 |
| **🚫 避免过度探索** | 不 glob 全目录、不预览多个候选、不扫描无关文件 |
| **📋 输出结构一致** | 结论先行格式，开发者一眼看到结果无需翻找 |
| **⚡ 减少无效往返** | 短计划（3-5 步）+ 分批执行，首轮就给出可操作的输出 |

---

### 🧠 Hermes

| 强化维度 | 说明 |
|---------|------|
| **💬 指令响应效率** | 降低每次 instruct 调用的 token 消耗，响应更快 |
| **🔇 无装饰输出** | 直接给结果，无问候、无过渡、无"如果你还需要帮助" |
| **🧩 行为可配置** | 通过 system prompt 一次性注入完整决策表和行为规范 |
| **📉 上下文压缩** | 能用 1 句话表达的不用 3 句，保留全部准确性 |

---

### 🌐 openclaw（ClawHub）

| 强化维度 | 说明 |
|---------|------|
| **📦 Skill 分发** | 一次编写，多平台加载，openclaw 作为官方发布中心 |
| **🔖 版本管理** | openclaw 托管最新 `SKILL.md`，所有用户统一更新路径 |
| **🔄 跨平台复用** | 同一套规范同时服务 Reasonix / Codex / Hermes 等不同工具 |
| **📐 标准化规范** | Skill 格式本身即是 ZeroToken 理念的实践——用最少的描述传达最完整的规则 |

---

## 📋 能力一览

根据你的请求特征与系统环境，ZeroToken Skill 自动匹配七种任务模式。每种模式都有专属的**工具链**、**输出格式**和 **token 预算策略**：

| 模式 | 一句话概括 | Token 成本 |
|------|-----------|:----------:|
| **A. 💬 简单问答** | 直接回答，不跑工具 | 🔵 极低 |
| **B. 🔧 代码小改** | 定位 → 读 → 精准改 → 最小验证 | 🟢 低 |
| **C. 📦 多文件任务** | 短计划 → 分批加载 → 按步推进 | 🟡 中 |
| **D. 📚 大资料总结** | 要点 + 证据位置，不逐段复述 | 🟠 中高 |
| **E. 🏗️ 重大架构调整** | 诊断根因 → 确认方案 → 增量迁移 | 🔴 高（但可控） |
| **F. 🖥️ Windows/PowerShell 环境适配** | 系统参数自动识别保存 + 15 条陷阱规则 + 脚本工具，Windows 系统自动启用 | 🟢 低 |
| **G. 🐧 POSIX 标准工作流** | Linux/macOS 自动启用：sh/bash 工具链，不套用 PowerShell 规则 | 🔵 极低 |

---

## 🎭 场景详解

### A. 💬 简单问答 — "直接告诉我答案"

**适用场景：** 定义查询、翻译、短建议、快速事实确认。

**典型信号：**
```
"什么是 RESTful API？"
"把这段翻译成英文"
"Go 和 Rust 在并发模型上有什么不同？"
```

**行为表现：**
```
🏷️ 识别 → "简单问答，无需工具"
   🔍 定位 → 从已加载上下文或内置知识提取
      💡 输出 → 1-3 句精炼回答，无冗余开场白
```

**不做什么：** ❌ 不搜索代码库 ❌ 不调用外部工具 ❌ 不加"好的，我来回答..."这类客套话

---

### B. 🔧 代码小改 — "这里有个小问题，改一下"

**适用场景：** 单文件 bug 修复、配置项调整、变量重命名、简单样式修改。

**典型信号：**
```
"这个按钮颜色不对，改成蓝色"
"login 函数有个空指针异常"
"把超时时间从 30s 改成 60s"
```

**行为表现：**
```
🏷️ 识别 → "单文件局部修改"
   🔍 定位 → 快速 grep / LSP 跳到目标行
      🔧 修改 → 精准编辑，不扫描无关文件
         ✅ 验证 → 最小化验证（语法检查 / 单测）
```

**不做什么：** ❌ 不写长篇计划 ❌ 不重构无关代码 ❌ 不扫描整个项目

---

### C. 📦 多文件任务 — "跨模块，有计划地推进"

**适用场景：** 新增功能、常规重构、跨文件修改、接口变更。

**典型信号：**
```
"给用户模块添加导出 CSV 功能"
"把日志系统从 zap 迁移到 slog"
"重构 auth 中间件，支持多租户"
```

**行为表现：**
```
🏷️ 识别 → "跨文件任务，需要计划"
   📋 计划 → 3-5 步短计划，标注文件清单
      📂 分批 → 一次只加载 2-3 个相关文件
         ⚡ 执行 → 改一批 → 验证 → 下一批
```

**不做什么：** ❌ 不一次性加载所有文件 ❌ 不做过度设计 ❌ 不写超过 5 步的详细计划

---

### D. 📚 大资料总结 — "太长了，说重点"

**适用场景：** 长文档分析、日志审查、PR 差异审查、大型配置审计。

**典型信号：**
```
"总结这个 5000 行的日志中的关键错误"
"review 这个 PR，只说有问题的部分"
"这个设计文档太长了，提取架构决策"
```

**行为表现：**
```
🏷️ 识别 → "资料总结，压缩输出"
   🔍 提取 → 逐段扫描，只标记关键信息
      📊 输出 → 要点列表 + 证据位置
         ❌ 省略 → 不逐段复述，不加评语
```

**不做什么：** ❌ 不逐段翻译/复述 ❌ 不输出"这部分看起来没问题" ❌ 不添加无关分析

---

### E. 🏗️ 重大架构调整 — "要大改，先确认方案"

**适用场景：** 反复出 bug 的系统、架构不匹配、数据库迁移、大规模重构。

**典型信号：**
```
"这个支付模块太乱了，每次加功能都出 bug"
"把单体应用拆成微服务"
"ORM 性能太差，换成原生 SQL"
```

**行为表现：**
```
🏷️ 识别 → "重大变更，需要谨慎"
   🩺 诊断 → 深入分析根因（非表面问题）
      🤝 确认 → 向用户呈现 2-3 种方案+推荐
         ✅ 认可 → 用户确认后再动手
            📈 增量 → 分步迁移，每步可验证/可回滚
```

**核心区别：** 这是唯一**必须先确认方案**再执行的模式。其他所有模式都是"识别即执行"。

---

### F. 🖥️ Windows/PowerShell 环境适配 — "detect_env.py 识别到 Windows 系统"

> **自动启用：** `python scripts/detect_env.py` 探测到 Windows 系统即进入此模式，
> 不要求任务涉及中文。系统参数（OS / Shell / 控制台编码 / 中文支持 / PowerShell 版本）
> 探测后保存到 `.zerotoken/environment.json`（7 天有效期），后续命令选择以保存的参数为准。

**适用场景：** Windows 系统下的命令执行、文件读写、Git 操作、脚本执行、编码处理。

**典型信号：**
```
detect_env.py 报告 os.name == "windows"
"这个中文文件打开是乱码"
"git diff 显示 \\xxx 而不是中文文件名"
"PowerShell 里中文报语法错误"
"文件被 GBK 污染了，修复一下"
```

**行为表现：**
```
🏷️ 识别 → detect_env.py 探测 Windows 系统，自动启用 F 模式
   📋 检查 → 系统参数已保存；15 条已知陷阱匹配当前症状
      🛠️ 解决 → PowerShell 命令 + 对应脚本工具或安全模板处理
         📝 输出 → 修复结果 + 验证确认
```

**不做什么：** ❌ 不在 Windows 上使用 bash（一律 PowerShell）❌ 不在 bash 命令中直接嵌入含 `+` 的中文 ❌ 不使用 `Add-Content` 追加中文 ❌ 不用 PS 5.1 的 `Set-Content` / `Out-File` 默认编码写非 ASCII 内容 ❌ 不直接在 PowerShell 中 `print()` 中文 ❌ 不忽略编码问题强行操作

**内置工具包（`scripts/`）：** `detect_env.py`(环境识别+系统参数保存)、`safe_io.py`（编码自动检测 + 安全读写/追加，unknown 显式抛错）、`detect_gbk_contamination.py`（检测修复 GBK 污染）、`batch_edit.py`（批量编辑）、`fix_encoding.py`（编码转换）、`verify_output.py`（验证输出）、`init_env.ps1`（环境初始化）

---

### G. 🐧 POSIX 标准工作流 — "detect_env.py 识别到 Linux/macOS"

**适用场景：** Linux / macOS 系统下的常规任务。

**行为表现：**
```
🏷️ 识别 → detect_env.py 探测 POSIX 系统，自动启用 G 模式
   🐚 Shell → sh/bash（macOS 默认 zsh），禁用 PowerShell 语法
      ⚙️ 执行 → 标准 ZeroToken 工作流，文件编码仍统一 UTF-8
```

**不做什么：** ❌ 不套用 F 模式的 PowerShell 规避规则（GBK 污染、Add-Content 等与 POSIX 无关）

---

## ⚔️ AI 编程总纲（尉缭子十原则）

> **将军受命，君必先谋于庙，行令于廷，君身以斧钺授将。曰：左、右、中军皆有分职；若逾分而上请者死；军无二令，二令者诛；留令者诛；失令者诛。**

核心不是军事，而是 **权限边界、单一指令、责任明确、执行一致**。与 ZeroToken 纪律互补：**省 token 是效率，尉缭子是秩序**。

完整十原则（含违反示例）、与任务模式的对应关系及 System Prompt 总纲见 [SKILL.md「⚔️ AI 编程总纲（尉缭子十原则）」](SKILL.md#⚔️-ai-编程总纲尉缭子十原则)。

---

## 🔍 搜索资料规范

**当任务需要搜索外部资料时，按以下优先级执行：**

| 优先级 | 方式 | 条件 |
|--------|------|------|
| 🥇 **Chrome MCP** | 真实浏览器搜索（不限百度） | `mcp_call.py` 存在且服务在线 |
| 🥈 **web_fetch** | 备选 | 仅当 Chrome MCP 不可用 |

> Chrome MCP 真实浏览器可通杀微博/知乎/小红书等反爬严格的平台；若 Chrome MCP 不可用，允许使用当前网络可用的其他搜索方式。

完整规则（禁用行为、Windows 调用注意、搜索命令示例）见 [SKILL.md「🔍 搜索资料规范」](SKILL.md#🔍-搜索资料规范)。

---

## 📝 精准提示词模板

用「目标 / 输入 / 约束 / 输出 / 预算」五要素压缩提示词；请求含糊时先用模板提炼再执行，只有缺少关键输入会导致结果不可用才追问，且一次只问 1 个问题。模板全文见 [SKILL.md「📝 精准提示词模板」](SKILL.md#📝-精准提示词模板)。

---

## 📜 Unicode 安全编码规范

全项目硬性编码规范，详见 **[`docs/unicode-encoding-spec.md`](docs/unicode-encoding-spec.md)**（15 条硬性规定 + 项目执行细则）：

- 🔤 文本文件统一 **UTF-8**（`.ps1` 例外，必须 UTF-8 with BOM）
- 📖 `open()` 一律显式 `encoding='utf-8'`，写模式加 `newline='\n'` 防 CRLF 污染
- 🚫 禁止 `errors='replace'` 静默损坏数据；非 UTF-8/UTF-16/GB18030 文件显式抛错
- 🖥️ Python 控制台输出优先 `sys.stdout.reconfigure(encoding='utf-8')`
- 🌐 HTTP 头显式 `charset=utf-8`；JSON 用 `ensure_ascii=False`
- 🧪 完成后运行 `python scripts/audit_encoding.py --root . --out audit_result.txt` 全项目审计（检测非 UTF-8 / 替换字符 / 混合换行）

---

## ✨ ZeroToken 强化模式

当用户明确要求"省 token"时，叠加更激进的压缩规则（零问候、最大压缩输出、省略冗余、准确性不妥协），触发词如"省点 token""简洁点""直接给结果"。完整规则见 [SKILL.md「⚡ ZeroToken 强化模式」](SKILL.md#⚡-zerotoken-强化模式)。

---

## 🚫 退出条件

教学/学习、头脑风暴、深度研究、用户要求详细等场景自动**退出 ZeroToken 模式**，切换为**详尽模式**。完整规则见 [SKILL.md「🚫 何时不使用 ZeroToken」](SKILL.md#🚫-何时不使用-zerotoken)。

---

## 📖 核心文档

所有详细规范定义在 **[`SKILL.md`](SKILL.md)**，配套脚本工具在 **`scripts/`** 目录：

- 📐 **快速决策表** — 按请求类型匹配模式与工具链
- 🧭 **核心原则** — 先分类再预算、压缩提示词、渐进读取、先给结果、不复述、设置停止条件
- ⚔️ **AI 编程总纲（尉缭子十原则）** — 权限边界、单一指令、责任明确、执行一致，附 System Prompt 总纲
- 📝 **精准提示词模板** — 目标 → 输入 → 约束 → 输出 → 预算
- 🔍 **搜索资料规范** — Chrome MCP 优先，web_fetch 备选
- 📜 **Unicode 安全编码规范** — 全项目编码硬性规定，见 `docs/unicode-encoding-spec.md`
- 🔄 **七种任务模式详解 (A-G)** — 每种模式的完整行为规范
- 🖥️ **F. Windows/PowerShell 环境适配** — 15 条已知陷阱与解决方案，Windows 系统自动启用
- 🐧 **G. POSIX 标准工作流** — Linux/macOS 自动启用，sh/bash 工具链
- 📤 **ClawHub 发布** — C1-C5 发布陷阱 + 固定发布时序（CLI 非 git push、后台运行、异步扫描）
- 🛠️ **scripts/ 工具集** — `detect_env.py`, `safe_io.py`, `detect_gbk_contamination.py`, `batch_edit.py`, `fix_encoding.py`, `verify_output.py`, `audit_encoding.py`, `init_env.ps1`
- ⚡ **ZeroToken 强化模式 & 退出条件**
- 🛡️ **质量底线** — 压缩不降质的硬性要求

---


## 🤖 Agent 预设

针对 OpenAI 兼容接口（含 Codex、OpenCode、Hermes 等）的预设配置位于 [`agents/openai.yaml`](agents/openai.yaml)，可直接导入使用。

---

## 🔑 核心原则（一句话版）

| # | 原则 | 含义 |
|:-:|------|------|
| 1 | **先分类，再预算** | 接到请求先确定模式，再分配 token |
| 2 | **压缩提示词** | 用最短的精确描述代替长段落 |
| 3 | **渐进读取** | 按需读取，不看完整文件 |
| 4 | **先给结果** | 结论先行，细节随后 |
| 5 | **不复述** | 不重复用户已说的内容 |
| 6 | **plan 只写顶层步骤** | 避免 bullet 子步骤被 todo 系统注册为独立待办项 |
| 7 | **设置停止条件** | 已定位目标、必要调用方和验证方式后即停止搜索，不重复读取未变化的文件 |

---

## 👑 The King Skills

[**The King Skills**](https://phoenixlucky.github.io/theKingSkills/) 是一个 AI Agent Skill 索引网站，收集热门且好用的 AI Agent Skill，指导各种 AI Agent 快速一键安装配置。

- 🌐 **网站地址：** https://phoenixlucky.github.io/theKingSkills/
- 📂 **覆盖范围：** 10 大分类，持续收录优质 Skill
- 🚀 **目标：** 让用户像安装 App 一样安装 AI Agent Skill

---

<div align="center">

**⚡ 少即是多 — Less is More**

</div>
