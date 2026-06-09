# ZeroToken Skill

**Version:** 1.4.0 &nbsp;|&nbsp; **License:** GPL-3.0 &nbsp;|&nbsp; **Author:** phoenixlucky

`ZeroToken Skill` 是一个默认约束 Agent 以**最少必要 token** 和**最精准提示词**完成任务的技能。减少无效上下文、无效解释、无效工具调用、无效输出——同时在准确性不下降的前提下压缩过程成本。

> **在线地址：** [clawhub.ai/phoenixlucky/zerotoken-skill](https://clawhub.ai/phoenixlucky/zerotoken-skill)

---

## 功能简介

根据用户请求特征，自动匹配五种任务模式，每种模式有专属的工具链、输出格式和 token 预算策略：

| 模式 | 适用场景 | 核心思路 |
|---|---|---|
| **A. 简单问答** | 定义、翻译、短建议 | 直接回答，不跑工具 |
| **B. 代码小改** | 单文件修复、配置调整 | 定位 → 局部读 → 精准改 → 最小验证 |
| **C. 多文件任务** | 跨模块功能、常规重构 | 短计划 → 分批加载 → 按步推进 |
| **D. 大资料总结** | 长文、日志、PR、文档 | 要点 + 证据位置，不逐段复述 |
| **E. 重大重构/架构调整** | 反复出 bug、架构不匹配、需要大改 | 诊断根因 → 用户确认方案 → 增量迁移 → 逐歩验证 |

此外还提供 **ZeroToken 强化模式**（用户明确省 token 时进一步压缩）和明确的**退出条件**（教学、头脑风暴等场景自动切换为详尽模式）。

## 快速开始

1. 克隆仓库：
   ```bash
   git clone https://github.com/phoenixlucky/zerotoken-skill.git
   ```
2. 在 Reasonix 或兼容 Agent 中载入 `SKILL.md` 作为 Skill 即可使用：

   ```
   /zerotoken-skill
   ```

## 核心文档

所有规范定义位于 **[`SKILL.md`](SKILL.md)**，包括：

- 快速决策表（按请求类型匹配模式与工具链）
- 核心原则（先分类再预算、压缩提示词、渐进读取、先给结果、不复述）
- 精准提示词模板（目标 → 输入 → 约束 → 输出）
- 五种任务模式详解（简单问答 / 代码小改 / 多文件任务 / 大资料总结 / 重大重构与架构调整）
- ZeroToken 强化模式与退出条件
- 质量底线

详细内容请直接阅读 [`SKILL.md`](SKILL.md)。

## Agent 预设

针对 OpenAI 兼容接口的预设配置位于 [`agents/openai.yaml`](agents/openai.yaml)。

## 标签

`zerotoken` `token-efficient` `prompt-engineering` `context-optimization` `agent-discipline` `ai-workflow` `token-budget` `concise-output`
