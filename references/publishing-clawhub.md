# ClawHub 发布（skill 分发与同步）

> 本文是**维护者手册**——使用者无需阅读。
> 项目通过 ClawHub 分发：<https://clawhub.ai/phoenixlucky/zerotoken-skill>。
> 以下规则来自实测发布过程，发布任何版本时必须遵守。

## 关键事实

- ❗ **ClawHub 不是 Git 端点** — 仓库远程 `clawhub` 只是发布页地址，
  `git fetch/push clawhub` 必然 404（`repository not found`）。**发布必须走 clawhub CLI**，
  不能指望 git push。
- 发布 CLI 由 pnpm 全局安装：`%LOCALAPPDATA%\pnpm\clawhub.CMD`
  （PowerShell `PATH` 未包含 pnpm 目录时直接调 `clawhub` 会「无法识别」，需用全路径）。
- 登录状态用 `clawhub whoami` 验证（应输出 `phoenixlucky`）。
- 新版本提交后 ClawHub 会跑**安全扫描**（异步、分钟级），**提交成功 ≠ 立即可见**。
- 发布包内容以**发布时的工作区文件**为准：GitHub 提交 ≠ ClawHub 包同步。
  打包范围由 `package.json` 的 `files` 字段声明（改目录结构时必须同步核对）。

## 发布陷阱表（C 系，与 F 模式 #1-15 区分）

| # | 陷阱 | 症状 | 解决方案 |
|---|------|------|----------|
| C1 | **PowerShell `curl` 是别名** | `curl -s -o NUL https://...` 报「缺少参数 SessionVariable」 | PS 里 `curl` = `Invoke-WebRequest`（参数不兼容）；探测网络/API 一律用 **`curl.exe`** |
| C2 | **`clawhub publish` 相对路径解析错误** | `publish .` 报 `Error: SKILL.md required` | CLI 默认 `--dir skills`（相对 workdir），相对路径找不到根目录 SKILL.md；✅ 传**绝对路径** |
| C3 | **发布命令长时零输出** | 前台发布跑 2 分钟无输出被超时终止，ClawHub 无变化 | 上传 registry 需 5-6 分钟且**全程零输出**（易误判卡死）；✅ 用后台运行（`run_in_background`）+ 轮询等待 |
| C4 | **安全扫描异步** | 发布提交成功（`Update submitted ... pending security scans before it becomes public`）但 registry/页面仍是旧版本号 | 平台规则：扫描通过才公开；✅ 用 `clawhub inspect phoenixlucky/zerotoken-skill --json` 或页面 `og:image` 复查，看到新版本号即已公开 |
| C5 | **发布前工作区有未提交改动** | 工作区脏时发布，未提交改动**已随包上传 ClawHub** 但 GitHub 缺失，两端分叉 | ✅ 发布前先 `git status` 确认干净（或先提交）再发布；发布后复查 `git status` |
| C6 | **带 source 参数触发上传 ticket 失效** | `publish ... --source-repo ... --source-commit <sha>` 报 `Skill upload ticket is missing, used, or expired`（连续重试 + 等冷却无效） | 实测：**去掉 `--source-repo` / `--source-commit` 重试即成功**；source 元数据可发布后通过页面/GitHub 关联，不影响打包内容 |

## 推荐发布时序（每次发布固定流程）

```text
0. git status 确认工作区干净；git log 记录待发布版本号
1. 一键校验：python scripts/zt.py check
   （回归测试 + 编码审计 + 文档一致性 + 版本号三处联动；与 CI 同一条命令）
2. git push origin main（GitHub 先行）
3. clawhub publish <仓库绝对路径> --slug zerotoken-skill --owner phoenixlucky \
     --version <新版本> --changelog "<变更摘要>" --no-input
   —— 先加 --dry-run 预览（应输出 Would publish <slug>@<version>），
      确认无误后移除 --dry-run 再次执行，并放后台运行（陷阱 C3）
4. clawhub inspect phoenixlucky/zerotoken-skill 复查公开状态（异步，陷阱 C4）
```

> 版本号用 `python scripts/zt.py version <x.y.z>` 写入三处；`zt.py check` 与 CI 跑同一套校验。
