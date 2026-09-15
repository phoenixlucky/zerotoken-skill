# F 模式参考：Windows / PowerShell 环境适配

> **触发**：`python scripts/detect_env.py` 报告 `os.name == "windows"` 且推荐 shell 为 PowerShell。
> 自动启用，**无需用户请求**，也不要求任务涉及中文。
> 系统参数（OS 版本、控制台代码页、中文支持、PowerShell 发行版、Git quotepath）在探测时
> 存入 `.zerotoken/environment.json`（7 天有效期），后续所有命令选择以保存的参数为准。
>
> **不适用**：macOS / Linux → 见 `SKILL.md` 的 G 模式，不要套用本文的规避规则。

## 先决定：用编辑工具还是 Python 脚本

| 情形 | 做法 |
|---|---|
| 纯 ASCII 内容、单处改动、文件本身是 UTF-8 | `edit_file` 直接改（B 模式默认路径） |
| 内容含中文 / emoji / 特殊符号（`+`、反引号、`\r\n`） | `write_file` 写 `.py` 脚本，再 `python "script.py"` |
| 同一文件需要多处改动（≥2 处） | 一个 Python 脚本一次完成，或用 `scripts/batch_edit.py` |
| 批量编码转换 / GBK 污染修复 | `scripts/fix_encoding.py` / `scripts/detect_gbk_contamination.py` |
| 命令参数本身含中文 | 写 `.py` 脚本执行，**不要**在命令行内联中文 |

判定理由：PowerShell 命令行是编码 + 转义的双重雷区（见陷阱 1 / 8 / 11），
而 Python 脚本的「写入脚本文件」和「执行脚本」两条路径都受 UTF-8 控制。

## 已知陷阱与解决方案（15 条）

| # | 陷阱 | 症状 | 解决方案 |
|---|------|------|----------|
| 1 | **PowerShell 与中文文本冲突** | `bash` 工具传中文给 PowerShell，`+` 被解析为字符串拼接运算符；反引号 `` ` `` 被识别为转义字符；含中文的 PowerShell 字符串报 `Missing ')'` 语法错误 | ❌ 不要直接在 `bash` 命令中嵌入含 `+` 的中文<br>✅ 改为 `write_file` 写 `.py` 脚本文件，再用 `python "script.py"` 执行 |
| 2 | **文件编码不一致** | 部分文件（如旧中文 Markdown）实际是 UTF-16 编码；Python 默认 UTF-8 读取抛 `UnicodeDecodeError`；旧文件中已有因编码损坏产生的替换字符（U+FFFD），导致字符串精确匹配失败 | ✅ 统一采用 UTF-8 编码读写<br>✅ 安全读取方案见下文的「安全文件读写模板」 |
| 3 | **edit_file 同文件连续编辑阻塞**（宿主行为，与系统无关） | 同一文件的多处修改，第一次 `edit_file` 后第二次被拒，错误：`fresh read required — was already modified earlier this turn` | ✅ 对同一文件的多处修改，一次性用 Python 脚本完成<br>✅ 或用宿主提供的多编辑工具一次传入多个替换（≤5 个以内）<br>✅ 维护一个更新脚本，执行后统一验证 |
| 4 | **Git 中文文件名转义显示** | `git diff --stat` 显示 `\xxx\xxx` 编码序列，无法直接阅读中文文件名 | ✅ 先执行 `git config core.quotepath false` |
| 5 | **PowerShell → Node.js 中文 JSON 参数断裂** | 调用 `node mcp-bridge.js call tools/call '{"name":"x","arguments":{"url":"中文"}}'` 时，中文导致 JSON 解析失败 | ✅ **不要直接调 `node mcp-bridge.js`**<br>✅ 改用 Python 包装脚本（本地 MCP 桥自带 `mcp_call.py`），其内部已用 `json.dumps()` 正确序列化 |
| 6 | **宿主 verification 死循环**（宿主行为，与系统无关） | 验证证据已提供多次（git diff、文件检查、关键词检查），但系统始终不接受；`stale_count` 持续累积 | ✅ 见 [`tool-mapping.md`](tool-mapping.md) 的「宿主 verification 循环」 |
| 7 | **Python 控制台输出中文失败** | Python 的 `print()` 在 PowerShell 控制台下因 GBK 编码报错：`UnicodeEncodeError: 'gbk' codec can't encode character` | ✅ 不直接 `print()`，写入 `.txt` 文件后用 `read_file` 查看<br>✅ 使用 `with open(out_path, 'w', encoding='utf-8') as f: f.write(result)` |
| 8 | **PowerShell 中 `\r\n` 转义** | PowerShell 脚本中 `` `r`n `` 的反引号被解释为换行转义符，导致语法错误 | ✅ 不在 PowerShell 中拼接含换行的多语言文本<br>✅ 改用 Python 的 `\n` 处理换行 |
| 9 | **PowerShell Add-Content 使用 GBK 编码污染 UTF-8 文件** | 用 `Add-Content` 向 UTF-8 文件追加中文后，新内容变为乱码（GBK 字节被误读为 UTF-8，出现 U+FFFD 替换字符），文件末尾出现 `0x81` 等无效 UTF-8 字节<br>根因：PowerShell 的 `Add-Content` 默认使用系统区域编码（Windows 中文版为 GBK）写入 | ❌ **禁止直接使用 PowerShell Add-Content 追加含中文的内容**<br>✅ 使用 Python 安全追加：`open('file.md', 'a', encoding='utf-8').write('内容')`<br>✅ 或用 `safe_io.py` 的 `safe_append()` 函数<br>✅ 已污染的文件用 `detect_gbk_contamination.py` 检测修复 |
| 10 | **PowerShell `&&` 链式操作不兼容** | PowerShell 不支持 bash 风格的 `&&` 运算符，`cmd1 && cmd2` 报语法错误 | ✅ 用 `;` 无条件链式<br>✅ 用 `if ($?) { ... }` 做条件链式 |
| 11 | **内联 `python -c` 中文 SyntaxError** | `python -c "含中文的代码"` 在 PowerShell 下因编码问题导致 SyntaxError | ❌ 不要用 `python -c` 传入含中文的代码<br>✅ 改为 `write_file` 写 `.py` 脚本执行 |
| 12 | **终端显示层中文乱码（文件内容正确）** | PowerShell 终端显示中文为乱码/问号，但文件内容实际正确（GBK 终端显示 UTF-8 编码文件） | ✅ 用文件大小/行数验证<br>✅ 用 `chcp 65001` 切换终端到 UTF-8 |
| 13 | **PowerShell 读取附件时中文乱码显示** | 用 `Get-Content` / `type` 读取附件（用户上传的 .md/.txt/.csv 等）时中文显示为乱码（如 `鐗堟湰鍙?1.9.1`），但用 `read_file` 或编辑器打开内容正常<br>根因：Windows PowerShell 5.1 的 `Get-Content` 默认按 ANSI 代码页（中文系统为 GBK/936）解码无 BOM 的 UTF-8 文件，属**显示层**问题，文件本身未损坏<br>⚠️ 若把"显示乱码"误判为"文件被污染"并盲目转码重写，反而会造成真正的污染 | ✅ **优先用 `read_file` 工具读取附件**（按 UTF-8 解码，显示正确）<br>✅ 必须在 PowerShell 中读时显式指定编码：`Get-Content -Encoding UTF8 附件.md`（PS 7+ 默认 UTF-8；5.1 必须加 `-Encoding UTF8`）<br>✅ 附件本身是 GBK/UTF-16 等非 UTF-8 编码时，用 `safe_io.read_text()` 自动检测（UTF-8 BOM / UTF-16 BOM / GB18030）<br>✅ 先确认附件真实编码再处理；显示乱码≠文件损坏，禁止据此盲目转码 |
| 14 | **PowerShell 写入命令默认编码不统一（写方向污染）** | PS 5.1 下 `Set-Content` / `Add-Content` 默认按 GBK 写出：纯汉字变成 GBK 字节（追加进 UTF-8 文件即污染），emoji 等字符**静默写成 `?` 丢字**；`Out-File` / `>` 重定向默认 UTF-16 LE（带 BOM）；`-Encoding UTF8` 写出的又是 UTF-8 **带 BOM**（部分工具解析异常）<br>已实测：同一 emoji 字符串经 `Set-Content` 默认写出为字节 `3F`（问号） | ✅ PowerShell 中写 UTF-8 文本统一用 .NET API：`[IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))`（无 BOM；Append 用 `WriteAllText(..., $text, $enc)` 前先读原内容，或直接用 Python）<br>✅ 跨脚本/含中文的写入一律走 Python：`safe_io.safe_write()` / `safe_append()`（UTF-8 无 BOM + LF）<br>✅ 万不得已必须用 `Set-Content -Encoding UTF8` 时，知晓会带 BOM；禁止用其默认编码写任何非 ASCII 内容 |
| 15 | **`Add-Content -Encoding UTF8` 追加不补换行导致粘连 + 带 BOM** | 即使显式指定 `-Encoding UTF8`，`Add-Content` 追加到不以换行结尾的文件时**不自动补换行**，两段内容直接粘连成一行（实测：`base` + 追加 → `base## 标题 ...`）；且写出的内容带 UTF-8 BOM | ✅ 追加操作改用 `safe_io.safe_append()`：自动补换行、UTF-8 无 BOM<br>✅ 纯 PowerShell 方案需自行判断末尾换行再拼接，复杂且易错，不建议<br>✅ 追加后发现首段粘连，检查是否由本陷阱导致，不要误判为内容错误 |

## 脚本工具（`scripts/` 目录）

**统一入口（推荐）：** `python scripts/zt.py <命令>` —— `zt.py help` 列出全部命令，
`zt.py check` 一键跑完全部校验（回归测试 / 编码审计 / 文档一致性 / 版本联动）；
参数原样透传，命令示例见 `zt.py help`。下表脚本均可独立调用（zt.py 只是转发）。

仓库自带一系列 Python 脚本，开箱即用，覆盖 F 模式的常见操作：

| 脚本 | 解决问题 | 用法示例 |
|------|----------|----------|
| `detect_env.py` | 环境识别：探测 OS / Shell / 控制台编码 / 中文支持 / PowerShell 版本并保存系统参数 | `python scripts/detect_env.py --force`（结果存 `.zerotoken/environment.json`，7 天有效期） |
| `safe_io.py` | #2 编码不一致（UTF-8 BOM / UTF-16/32 BOM / GB18030） / #7 无法 print 中文 / #9 安全追加替代 Add-Content（自动补换行） / #13 附件乱码读取（自动检测编码） / #14 写方向编码统一（safe_write 无 BOM + LF） | `from safe_io import read_text, safe_write, safe_append, write_result`（编码无法确定时显式抛 `UnknownEncodingError`，不静默替换） |
| `detect_gbk_contamination.py` | #9 检测修复 GBK 编码污染 | `python scripts/detect_gbk_contamination.py scan .` / `python scripts/detect_gbk_contamination.py fix . --backup` |
| `batch_edit.py` | #3 edit_file 连续编辑阻塞 | `python scripts/batch_edit.py file.json replacements.json` |
| `fix_encoding.py` | #2 批量编码转换 | `python scripts/fix_encoding.py scan .` / `python scripts/fix_encoding.py convert . --backup` |
| `verify_output.py` | #7 控制台输出 / 验证结果落文件 | `python scripts/verify_output.py "检查项" out.txt --pass "✓ 通过"` |
| `init_env.ps1` | #4 Git 配置 / 环境初始化 | 在新会话中 `. ./scripts/init_env.ps1` |

## 推荐工作流

当 `detect_env.py` 识别到 Windows 系统时，按以下步骤替代默认工作流：

```text
0. （首次）python scripts/detect_env.py 探测系统参数并保存
   （.zerotoken/environment.json，7 天有效；之后每次会话自动复用）
1. 判断改动类型（见上文「先决定：用编辑工具还是 Python 脚本」）
2. 需要脚本时：write_file 写 Python 更新脚本（.py）
3. python "script.py" 执行（避免 PowerShell + edit_file 的所有问题）
4. git diff --stat 验证文件变更
5. 用 verify_output.py 输出验证结果到 .txt 文件
6. read_file 读取验证结果
7. 签收/收尾（宿主若提供 complete_step 等签收工具，见 references/tool-mapping.md）
```

## 安全文件读写模板

优先直接调用 `safe_io`（`read_text` / `safe_write` / `safe_append`）；
需要内联时使用等价写法：

```python
# 安全读取（UTF-8 / UTF-8 BOM / UTF-16 / GB18030 自动检测）
with open(path, 'rb') as f:
    raw = f.read()

from safe_io import decode_bytes      # 无法确定编码时显式抛错
content = decode_bytes(raw, path)

# 安全写入（统一 UTF-8，行尾 LF；newline='\n' 防止 Windows 文本模式写成 CRLF）
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

# 安全追加（替代 Add-Content，避免 GBK 污染；newline='\n' 同上）
with open(path, 'a', encoding='utf-8', newline='\n') as f:
    f.write(content)
    if not content.endswith('\n'):
        f.write('\n')
```

## 不做什么

❌ 不在 `bash` 命令中嵌入含特殊符号（`+`、`` ` ``）的中文字符串
❌ 不连续对同一文件进行多次 `edit_file` 调用
❌ 不直接在 PowerShell 中用 `print()` 输出中文
❌ 不忽略 `git config core.quotepath` 设置
❌ **不使用 PowerShell 的 `Add-Content` 追加含中文的内容** — 改用 Python `open(path, 'a', encoding='utf-8')` 或 `safe_io.safe_append()`
❌ **不在 PowerShell 中直接调用 `node mcp-bridge.js` 传递中文 JSON 参数** — 改用 Python 包装脚本
❌ **不用 `web_fetch` 直抓社交媒体（微博/知乎/小红书等）** — 100% 被登录墙或反爬拦截
❌ **不自己写 Playwright/Puppeteer 脚本**（已有现成 MCP 桥，见 [`search.md`](search.md)）
❌ **不使用 `python -c` 内联含中文的代码** — 改用 `write_file` + `python "script.py"` 两步法
❌ **不使用 `&&` 链式命令** — PowerShell 不支持，改用 `;` 或 `if ($?) { ... }`
❌ **不依赖终端输出验证中文内容** — 用文件内容验证替代
❌ **不用 `Get-Content` 直接查看含中文的附件** — 5.1 默认按 GBK 解码会显示乱码，改用 `read_file` 工具或 `Get-Content -Encoding UTF8`；显示乱码≠文件损坏，禁止据此盲目转码
❌ **不在 PS 5.1 中用 `Set-Content` / `Add-Content` / `Out-File` 的默认编码写任何非 ASCII 内容** — 默认 GBK 会污染 UTF-8 文件、emoji 静默变 `?`；写方向统一走 Python `safe_io.safe_write()` / `safe_append()`，或 .NET `[IO.File]::WriteAllText($path, $text, [Text.UTF8Encoding]::new($false))`
❌ **不依赖 `Add-Content -Encoding UTF8` 做追加** — 仍会带 BOM 且目标不以换行结尾时不补换行导致内容粘连；统一用 `safe_io.safe_append()`
