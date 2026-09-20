<div align="center">

# ⚡ ZeroToken Skill

**让 Agent 用最少的 token 做最准的事**

> ⚔️ **先谋后动，军无二令 —— 省 token 是效率，尉缭子是秩序。**
>
> 💬 **用不完，根本用不完，妈妈再也不用担心我缺 token 了。**

[![Version](https://img.shields.io/badge/version-1.17.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/author-phoenixlucky-orange.svg)]()
[![CI](https://github.com/phoenixlucky/zerotoken-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/phoenixlucky/zerotoken-skill/actions/workflows/ci.yml)

</div>

> **ZeroToken Skill** 是一套为 AI Agent 设计的**提示词纪律规范**——在不降低回答准确性的前提下，压缩无效上下文、无效解释、无效工具调用和无效输出。
>
> 它解决的核心问题是：Agent 在任务中经常过度读取、过度思考、过度输出，导致一次对话消耗成千上万不必要的 token。本 Skill 通过一套可执行的**模式决策表 + 行为约束 + 工具链策略**，让 Agent 在每一个任务环节都有明确的"省 token 行为准则"。
>
> 🎯 **目标：** 用最精准的提示，做最少的往返，产最精炼的结果。
>
> ✅ **适用于：** Reasonix / Codex CLI / OpenCode / Hermes / Cline 等主流 Agent 工具。一次学习，全平台受益。

<div align="center">

<img src="assets/zerotoken-banner.webp" alt="ZeroToken Skill 概览" width="480">

</div>

---

## 目录

- [安装](#-安装)
- [能力一览](#-能力一览)
- [任务模式速查](#-任务模式速查)
- [平台集成](#-平台集成)
- [文档地图](#-文档地图)
- [延伸阅读](#-延伸阅读)
- [核心原则（一句话版）](#-核心原则一句话版)
- [Agent 预设](#-agent-预设)
- [The King Skills](#-the-king-skills)

---

## 🔌 安装

| 方式 | 操作 |
|------|------|
| **AI 助手安装（推荐）** | 直接对助手说：`安装这个技能 https://github.com/phoenixlucky/zerotoken-skill`（或 ClawHub 源 `https://clawhub.ai/phoenixlucky/zerotoken-skill`） |
| **远程 Skill 仓库引用** | `install-source --source https://github.com/phoenixlucky/zerotoken-skill`（或 `--source https://clawhub.ai/phoenixlucky/zerotoken-skill`） |
| **手动载入** | 克隆仓库，将本目录作为 Skill 载入，入口为 [`SKILL.md`](SKILL.md) |

> 📦 分发双端：GitHub（源码）+ ClawHub（发布包）。详见 [`references/publishing-clawhub.md`](references/publishing-clawhub.md)（仅维护者）。

---

## 📋 能力一览

根据请求特征与系统环境，ZeroToken Skill 自动匹配**七种任务模式**。每种模式都有专属的**工具链**、**输出格式**和 **token 预算策略**：

| 模式 | 一句话概括 | Token 成本 |
|------|-----------|:----------:|
| **A. 💬 简单问答** | 直接回答，不跑工具 | 🔵 极低 |
| **B. 🔧 代码小改** | 定位 → 读 → 精准改 → 最小验证 | 🟢 低 |
| **C. 📦 多文件任务** | 短计划 → 分批加载 → 按步推进 | 🟡 中 |
| **D. 📚 大资料总结** | 要点 + 证据位置，不逐段复述 | 🟠 中高 |
| **E. 🏗️ 重大架构调整** | 诊断根因 → 确认方案 → 增量迁移 | 🔴 高（但可控） |
| **F. 🖥️ Windows/PowerShell 环境适配** | 系统参数自动识别保存 + 15 条陷阱规则 + 脚本工具，Windows 系统自动启用 | 🟢 低 |
| **G. 🐧 POSIX 标准工作流** | Linux/macOS 自动启用：sh/bash 工具链，不套用 PowerShell 规则 | 🔵 极低 |

> 平台环境由 `python scripts/detect_env.py` 自动识别（`SKILL.md` 中的 F/G 模式），无需用户声明语言或平台。

---

## 🧩 任务模式速查

| 模式 | 典型信号 | 行为要点 | 不做什么 |
|------|---------|---------|---------|
| **A. 简单问答** | 定义查询、翻译、短建议 | 从已加载上下文/内置知识提取，1-3 句直接回答 | ❌ 不搜索代码库 ❌ 不加客套话 |
| **B. 代码小改** | 单文件 bug、配置调整、重命名 | grep 定位 → 只读命中行附近 → 精准改 → 最小验证 | ❌ 不写长计划 ❌ 不重构无关代码 |
| **C. 多文件任务** | 新增功能、常规重构、接口变更 | 3-5 步短计划，一次加载 2-3 个文件，改一批验一批 | ❌ 不一次性加载所有文件 ❌ 不超 5 步 |
| **D. 大资料总结** | 长文档、日志、PR 差异 | 只标记关键信息，输出「要点 + 证据位置」 | ❌ 不逐段复述 ❌ 不加无关评语 |
| **E. 重大架构调整** | 反复同类 bug、架构不匹配 | **唯一必须先确认方案再执行**：诊断根因 → 2-3 方案 → 增量迁移 | ❌ 不跳过影响面评估 ❌ 不做不可逆大改 |
| **F. Windows/PowerShell** | `detect_env.py` 报 Windows | 按保存的系统参数选 PowerShell，含特殊符号/中文的写入走 Python 脚本 | ❌ 不在 Windows 用 bash ❌ 不用 `Add-Content` 写中文 |
| **G. POSIX** | `detect_env.py` 报 Linux/macOS | sh/bash（macOS 默认 zsh），不套用 F 模式规则 | ❌ 不套用 PowerShell 规避规则 |

> 完整行为定义、工具链与输出模板见 [`SKILL.md`](SKILL.md)；E 模式迁移手册见 [`references/refactor-playbook.md`](references/refactor-playbook.md)。

---

## 💻 平台集成

| 宿主 | 强化方向 |
|------|---------|
| **⚡ Reasonix** | 原生 Skill 引擎、请求特征自动匹配模式、按模式限制工具调用范围 |
| **🤖 Codex CLI** | 提示词纪律、先搜索后局部读取、只返回结果+验证+注意 |
| **🦾 Cline** | A-G 决策表约束读取深度、停止条件明确、结论先行输出 |
| **🔧 OpenCode** | 行为可预期、避免全目录 glob、短计划分批执行、减少无效往返 |
| **🧠 Hermes** | 降低每次 instruct 的 token 消耗、无装饰输出、system prompt 一次性注入 |
| **🌐 openclaw（ClawHub）** | Skill 分发与版本托管，同一套规范跨平台复用 |

---

## 📖 文档地图

**文档分层：** `SKILL.md` 是常驻核心（决策表 + 原则 + 输出格式，≤14KB）；细节按需读取
`references/` 下的参考文档——这样加载时不为当前任务用不到的内容付 token。

**`SKILL.md`（常驻核心）**

- 📐 **快速决策表** — 按请求类型匹配模式与工具链
- 🧭 **核心原则（8 条）** — 先分类再预算、压缩提示词、渐进读取、先给结果、不复述、plan 只写顶层步骤、设置停止条件、先识别环境再选 Shell
- ⚔️ **AI 编程总纲（尉缭子十原则）** — 权限边界、单一指令、责任明确、执行一致
- 📝 **精准提示词模板** — 目标 → 输入 → 约束 → 输出 → 预算
- 🔄 **任务模式要点 (A-G)** — 每种模式的首轮行为
- ⚡ **ZeroToken 强化模式 & 退出条件** / 🛡️ **质量底线**

**`references/`（按需读取）**

| 文档 | 内容 |
|---|---|
| [`windows-powershell.md`](references/windows-powershell.md) | F 模式：15 条已知陷阱 + 脚本工具表 + 推荐工作流 + 安全读写模板 |
| [`refactor-playbook.md`](references/refactor-playbook.md) | E 模式：根因诊断 → 影响面 → 方案确认 → 增量迁移 → 收尾 |
| [`search.md`](references/search.md) | 搜索资料规范：仅用已注册工具、显式授权桥、数据外发提示、禁用行为 |
| [`tool-mapping.md`](references/tool-mapping.md) | 工具名跨宿主映射、宿主 verification 循环、plan/todo 注册行为 |
| [`publishing-clawhub.md`](references/publishing-clawhub.md) | 维护者手册：C1-C6 发布陷阱 + 固定发布时序 |

**其他目录**

- 📜 **`docs/unicode-encoding-spec.md`** — Unicode 安全编码规范 15 条 + 项目执行细则
- 🛠️ **`scripts/` 工具集** — `zt.py`（统一入口：`zt.py help` / `zt.py check`）, `detect_env.py`, `safe_io.py`, `detect_gbk_contamination.py`, `batch_edit.py`, `fix_encoding.py`, `verify_output.py`, `audit_encoding.py`, `audit_skill.py`, `bump_version.py`, `init_env.ps1`

---

## 📚 延伸阅读

以下内容在 `SKILL.md` / `references/` / `docs/` 有完整定义，此处只给入口，避免双份事实源：

- 📝 **精准提示词模板** — [SKILL.md「精准提示词模板」](SKILL.md#-精准提示词模板)
- ⚔️ **AI 编程总纲（尉缭子十原则）** — 完整十原则与 System Prompt 总纲见 [SKILL.md「AI 编程总纲」](SKILL.md#-ai-编程总纲尉缭子十原则)
- ⚡ **ZeroToken 强化模式** — 更激进的压缩规则见 [SKILL.md「ZeroToken 强化模式」](SKILL.md#-zerotoken-强化模式)
- 🚫 **何时退出 ZeroToken** — 教学/头脑风暴/深度研究自动切详尽模式，见 [SKILL.md「何时不使用 ZeroToken」](SKILL.md#-何时不使用-zerotoken)
- 🔍 **搜索资料规范** — 已注册工具优先、抓取工具兜底，见 [`references/search.md`](references/search.md)
- 📜 **Unicode 安全编码规范** — 文本统一 UTF-8（`.ps1` 例外带 BOM），见 [`docs/unicode-encoding-spec.md`](docs/unicode-encoding-spec.md)

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
| 8 | **先识别环境，再选 Shell** | 命令行任务先跑 `detect_env.py` 保存系统参数，再按平台选 PowerShell / POSIX shell |

---

## 🤖 Agent 预设

针对 OpenAI 兼容接口（含 Codex、OpenCode、Hermes 等）的预设配置位于 [`agents/openai.yaml`](agents/openai.yaml)，可直接导入使用。

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
