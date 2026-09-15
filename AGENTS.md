# Project memory

## 项目结构

- `SKILL.md` — **常驻核心**（快速决策表 / 核心原则 / 输出格式 / 质量底线）。
  体积预算 ≤12KB，超出即说明细节该外移到 `references/`。
- `references/` — **按需读取**的细节：`windows-powershell.md`（F 模式 15 条陷阱）、
  `refactor-playbook.md`（E 模式）、`search.md`、`tool-mapping.md`、`publishing-clawhub.md`。
- `scripts/` — 编码与一致性工具；`safe_io.py` 是其余脚本的公共依赖（`ensure_utf8_stdio` / `safe_print`）。
- `docs/unicode-encoding-spec.md` — 编码规范的本仓库执行细则。
- 分发：GitHub + ClawHub 双端；打包范围由 `package.json` 的 `files` 字段声明。

## 校验命令（改完必跑，与 `.github/workflows/ci.yml` 一致）

```powershell
python scripts/zt.py check        # 一键：回归测试 + 编码审计 + 文档一致性 + 版本联动
```

排查时单步跑（入口一览见 `python scripts/zt.py help`）：

```powershell
python scripts/zt.py env          # 识别系统参数（写 .zerotoken/environment.json）
python scripts/zt.py audit        # 文档一致性：体积/链接/计数/脚本引用/异体字
python scripts/zt.py encoding     # 编码合规：UTF-8/替换字符/混合换行
python scripts/zt.py version      # 版本号三处联动（带版本号=写入）
```

> 所有命令支持 `--json [--out 文件]`，供 AI / CI 解析；`scripts/` 下的原脚本仍可独立调用。

## 发布（仅维护者）

- 版本号一律用 `python scripts/zt.py version <x.y.z>` 写入三处，不要手改单点。
- 发布时序、C1-C6 陷阱与 ClawHub CLI 用法见 `references/publishing-clawhub.md`；
  **ClawHub 不是 Git 端点**，`git push` 发不出去。

## Notes

- 方式二：从远程 Skill 仓库引用（推荐，始终获取最新版本） 安装这个技能 https://clawhub.ai/phoenixlucky/zerotoken-skill

## 编码规范（必须遵守）

- 生成/修改任何代码、配置、文档前，先读 `docs/unicode-encoding-spec.md`（Unicode 安全编码规范 15 条 + 项目执行细则）。
- 硬性要求：文本文件统一 UTF-8（`.ps1` 例外必须 UTF-8 with BOM）；`open()` 一律显式 `encoding='utf-8'`；禁止 `errors='replace'` 静默损坏数据；Python 控制台输出优先 `sys.stdout.reconfigure(encoding='utf-8')`（本仓库统一走 `safe_io.safe_print`）；HTTP 头显式 `charset=utf-8`；JSON 用 `ensure_ascii=False`。
- 完成后运行 `python scripts/audit_encoding.py --root . --out audit_result.txt` 检查（无 non-utf8、无替换字符、无混合换行）。
