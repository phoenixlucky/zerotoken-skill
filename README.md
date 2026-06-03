# ZeroToken Skill

**Version:** 1.3.0 &nbsp;|&nbsp; **License:** GPL-3.0 &nbsp;|&nbsp; **Author:** phoenixlucky

`ZeroToken Skill` 是一个默认约束 Agent 以**最少必要 token** 和**最精准提示词**完成任务的技能。减少无效上下文、无效解释、无效工具调用、无效输出——同时在准确性不下降的前提下压缩过程成本。

---

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
- 四种任务模式详解（简单问答 / 代码小改 / 多文件任务 / 大资料总结）
- ZeroToken 强化模式与退出条件
- 质量底线

详细内容请直接阅读 [`SKILL.md`](SKILL.md)。

## Agent 预设

针对 OpenAI 兼容接口的预设配置位于 [`agents/openai.yaml`](agents/openai.yaml)。

## 标签

`zerotoken` `token-efficient` `prompt-engineering` `context-optimization` `agent-discipline` `ai-workflow` `token-budget` `concise-output`
