# Project memory

## Notes

- 方式二：从远程 Skill 仓库引用（推荐，始终获取最新版本） 安装这个技能 https://clawhub.ai/phoenixlucky/zerotoken-skill

## 编码规范（必须遵守）

- 生成/修改任何代码、配置、文档前，先读 `docs/unicode-encoding-spec.md`（Unicode 安全编码规范 15 条 + 项目执行细则）。
- 硬性要求：文本文件统一 UTF-8（`.ps1` 例外必须 UTF-8 with BOM）；`open()` 一律显式 `encoding='utf-8'`；禁止 `errors='replace'` 静默损坏数据；Python 控制台输出优先 `sys.stdout.reconfigure(encoding='utf-8')`；HTTP 头显式 `charset=utf-8`；JSON 用 `ensure_ascii=False`。
- 完成后运行 `python scripts/audit_encoding.py --root . --out audit_result.txt` 检查（无 non-utf8、无替换字符、无混合换行）。
