# 工具名映射与宿主专属行为

> 本 skill 描述的是**能力**，不是某个宿主的工具名。
> 下表把本文档与 `SKILL.md` 中用到的能力映射到具体宿主工具；
> 只调用当前宿主**实际提供**的等价工具，不要臆造名字。

## 能力 → 工具名

| 能力 | Reasonix | 其他宿主常见名 |
|---|---|---|
| 文本搜索（定位行） | `grep` | `search_content` / ripgrep / `grep` |
| 文件枚举 | `glob` / `ls` | `directory_tree` / `find` / `list_dir` |
| 局部读取 | `read_file`（`offset` + `limit`） | `read_file` / `open_file` |
| 写入 / 编辑 | `write_file` / `edit_file` | `apply_patch` / `str_replace_editor` |
| 同文件多处编辑 | `scripts/batch_edit.py`（宿主若提供 `multi_edit` 可优先用） | `multi_edit` |
| 待办清单 | `todo_write` | `complete_step` / `update_plan` |
| 跨文件探索 / 影响面 | `explore`（只读子代理） | `codegraph_context` / `codegraph_trace` / Task |
| 结构化提问 | `ask` | `ask_user` |
| 编译 / 类型检查 | `lsp_diagnostics` | `diagnostics` |
| 网页抓取 | `web_fetch`（宿主提供时） | `fetch` / `browse` |

> 代码图类工具（`codegraph_*`）若宿主提供，在 E 模式下优先于 `explore`——
> 它给出的是调用链而非搜索命中。没有这类工具时，用 `explore` + `grep` 组合替代。

## 宿主 verification 循环

部分宿主（如带 AutoResearch 签收机制的宿主）会出现：验证证据已提供多次
（git diff、文件检查、关键词检查），系统仍不接受，`stale_count` 持续累积。

✅ 使用宿主提供的签收工具（如 `complete_step`，`kind: "verification"`）推进任务，
而不是仅靠 `<autoresearch-evidence>` 之类的文本块。
✅ 签收证据的 `command` 字段必须与会话历史中的命令文本**完全一致**，否则被视为无效。
✅ 宿主不提供签收工具时忽略本节——它是宿主行为，不是 Windows / 编码问题。

## plan / todo 注册行为

某些宿主的 plan 模式会把**每层 bullet 列表项**注册为独立待办项，且必须严格线性签收。
规避方式：

✅ 每个 phase 只写 1 行顶层步骤（共 2-5 个），细节写在说明文字中而非子 bullet。

```text
✅ 正确：
1. safe_io.py 新增 safe_append 函数 — 用 open('a', encoding='utf-8') 替代 Add-Content

❌ 错误（会生成 10+ 待办项）：
1. safe_io.py 新增 safe_append
   - 实现函数
   - 更新文档字符串
   - 导出 __all__
```

若已陷入子步骤阻塞：优先用宿主的步骤调整机制（如 `complete_step({ step_index: N })`
跳过中间项）直接签收当前卡住的项。

**签收证据类型规则（宿主提供签收工具时）**

- 工具写入的文件（`write_file` / `edit_file`）→ `files` 证据
- 脚本写入的文件（如 Python 执行产物）→ `manual` 证据
- `verification` 证据的 `command` 必须与会话历史中的命令文本完全一致
- 每次工具调用只签一个步骤，按顺序推进（部分宿主限制：每轮只允许一个成功签收）
