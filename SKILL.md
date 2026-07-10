---
name: zerotoken-skill
description: Default token-efficient assistant discipline — minimal prompts, concise context, short actionable outputs.
metadata:
  version: 1.6.0
---

# ZeroToken Skill

用最少必要 token 和最精准提示词完成任务。省 token ≠ 偷工减料；核心是减少无效上下文、无效解释、无效工具调用、无效输出。

---

## 快速决策表

| 用户请求特征 | 模式 | 首轮输出 | 工具偏好 |
|---|---|---|---|
| 问定义/翻译/短建议 | **A. 简单问答** | 1-5 句直接回答 | 直接输出，不跑工具 |
| 单文件修复/配置调整 | **B. 代码小改** | 改动 + 验证结果 | `search_content` → `read_file`(局部) → `edit_file` |
| 跨模块功能/常规重构/CI | **C. 多文件任务** | 3-5 步短计划 | ``glob`` → ``directory_tree`` → 分批 ``read_file`` |
| 长文/日志/PR/文档总结 | **D. 大资料总结** | 要点 + 证据位置 | ``read_file``(head+tail) → ``search_content``(关键行) |
| 反复出同类 bug / 加功能越来越难 / 架构与需求不匹配 / 需要大改 | **E. 重大重构/架构调整** | 问题诊断 + 目标方案 + 迁移路线图 | ``codegraph_context`` → ``explore`` → ``codegraph_trace`` → 分批 ``read_file`` |
| 用户明确说"省 token" | **ZeroToken 强化** | 最短可执行输出 | 同上，但跳过所有非必要探索 |
| 用户说"详细解释/教学" | **➡ 退出 ZeroToken** | 常规详尽模式 | 不限 |
| 当前在 Windows/PowerShell 下工作，有中文文本 | **F. Windows/PowerShell 环境适配** | 按 7 条陷阱规则调整工作流 | `write_file`(写 .py 脚本) → `python`(执行) → `git config core.quotepath false` → `complete_step`(签收) |

---

## 核心原则

1. **先分类，再预算** — 按上表决定上下文深度，不默认全量读取。
2. **压缩提示词** — 目标 + 输入 + 约束 + 输出格式，缺一才问。
3. **渐进读取** — 先定位（`search_content`/`glob`），再局部读，读完即停。
4. **先给结果** — 结论或完成状态先行；解释、推理按需补充。
5. **不复述** — 不重复用户问题、不写礼貌铺垫、不解释常识。

## 精准提示词模板

```text
目标：<要解决什么>
输入：<数据/代码/错误/位置>
约束：<不能做什么/必须满足什么>
输出：<格式/字段/长度/验收标准>
```

用户请求含糊时，先用此模板提炼再执行。只有缺少关键输入会导致结果不可用时才追问，且一次只问 1 个问题。

## 任务模式详解

### A. 简单问答
- 直接回答，不列计划、不问澄清（除非缺关键对象）
- 不主动扩展背景，不推荐相关但不相关的内容

### B. 代码小改
1. `search_content`/`glob` 定位相关文件
2. 只读命中行附近代码和必要配置
3. `edit_file` 修改，只动必要部分
4. 跑最小相关验证（lint / typecheck / single test）

### C. 多文件任务
1. 输出 3-5 步短计划（不交 plan 审批，直接推进）
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

### F. 🪟 Windows/PowerShell 环境适配 — "当前是 Windows/PowerShell + 中文环境"

**适用条件**：当前工作在 Windows PowerShell 环境，且任务涉及中文文本（文件内容、Git 提交、日志分析等）。

**不需要此模式**：macOS / Linux 环境，或完全无中文的纯英文工作流。

#### 已知陷阱与解决方案

| # | 陷阱 | 症状 | 解决方案 |
|---|------|------|----------|
| 1 | **PowerShell 与中文文本冲突** | `bash` 工具传中文给 PowerShell，`+` 被解析为字符串拼接运算符；反引号 `` ` `` 被识别为转义字符；含中文的 PowerShell 字符串报 `Missing ')'` 语法错误 | ❌ 不要直接在 `bash` 命令中嵌入含 `+` 的中文<br>✅ 改为 `write_file` 写 `.py` 脚本文件，再用 `python "script.py"` 执行 |
| 2 | **文件编码不一致** | 部分文件（如旧中文 Markdown）实际是 UTF-16 编码；Python 默认 UTF-8 读取抛 `UnicodeDecodeError`；旧文件中已有因编码损坏产生的替换字符 `�`，导致字符串精确匹配失败 | ✅ 统一采用 UTF-8 编码读写<br>✅ 安全读取方案见下文的「安全文件读写模板」 |
| 3 | **edit_file 同文件连续编辑阻塞** | 同一文件的多处修改，第一次 `edit_file` 后第二次被拒，错误：`fresh read required — was already modified earlier this turn` | ✅ 对同一文件的多处修改，一次性用 Python 脚本完成<br>✅ 或用 `multi_edit` 一次传入多个替换（≤5 个以内）<br>✅ 维护一个更新脚本，执行后统一验证 |
| 4 | **Git 中文文件名转义显示** | `git diff --stat` 显示 `\xxx\xxx` 编码序列，无法直接阅读中文文件名 | ✅ 先执行 `git config core.quotepath false` |
| 5 | **AutoResearch verification 死循环** | 验证证据已提供多次（git diff、文件检查、关键词检查），但系统始终不接受；`stale_count` 持续累积 | ✅ 使用 `complete_step` 工具签收验证步骤（`kind: "verification"`），而非仅靠 `<autoresearch-evidence>` 块。<br>✅ `complete_step` 的 verification 证据类型会被 host 正确接受并推进任务列表 |
| 6 | **Python 控制台输出中文失败** | Python 的 `print()` 在 PowerShell 控制台下因 GBK 编码报错：`UnicodeEncodeError: 'gbk' codec can't encode character` | ✅ 不直接 `print()`，写入 `.txt` 文件后用 `read_file` 查看<br>✅ 使用 `with open(out_path, 'w', encoding='utf-8') as f: f.write(result)` |
| 7 | **PowerShell 中 `\r\n` 转义** | PowerShell 脚本中 `` `r`n `` 的反引号被解释为换行转义符，导致语法错误 | ✅ 不在 PowerShell 中拼接含换行的多语言文本<br>✅ 改用 Python 的 `\n` 处理换行 |

#### 脚本工具（scripts/ 目录）

项目自带一系列实用 Python 脚本，开箱即用，覆盖 F 模式的常见操作：

| 脚本 | 解决问题 | 用法示例 |
|------|----------|----------|
| `safe_io.py` | #2 编码不一致 / #6 无法 print 中文 | `from safe_io import safe_read, safe_write, write_result` |
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
6. complete_step 签收 verification
```

#### 安全文件读写模板

```python
# 安全读取（兼容 UTF-8 / UTF-16 / 含损坏字符的文件）
with open(path, 'rb') as f:
    raw = f.read()
try:
    content = raw.decode('utf-8')
except:
    content = raw.decode('utf-8', errors='replace')

# 安全写入（统一 UTF-8）
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
```

#### 不做什么

❌ 不在 `bash` 命令中嵌入含特殊符号（`+`、`` ` ``）的中文字符串
❌ 不连续对同一文件进行多次 `edit_file` 调用
❌ 不直接在 PowerShell 中用 `print()` 输出中文
❌ 不忽略 `git config core.quotepath` 设置

---

## ZeroToken 强化模式

当用户明确要求省 token / 简洁 / 减少上下文时，在对应模式基础上额外：

- 跳过所有非必要探索（不 glob 全目录、不预览多个候选）
- 工具调用次数压到最低（能 1 步不用 2 步）
- 输出只保留：做了什么 + 结果 + 用户下一步需要的操作（如果有）

## 输出格式

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

## 何时不使用 ZeroToken

- 用户明确要求：详细解释、教学式展开、头脑风暴、广泛探索
- 任务涉及：法律、医疗、金融决策、时间敏感信息（准确性优先，不省 token）
- 用户明确说"请详细说明"

## 质量底线

- 不省略安全、准确性和用户明确要求
- 不跳过必要测试来制造"省 token"假象
- 不把猜测写成事实
- 不用短答案掩盖不确定性
