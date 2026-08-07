<#
.SYNOPSIS
    Windows/PowerShell + 中文环境初始化脚本
.DESCRIPTION
    配置当前仓库的 Git 设置（仅本地，不修改全局配置），避免中文文本处理中的常见陷阱。
    在每个新的 PowerShell 会话中运行一次。
.EXAMPLE
    . .\scripts\init_env.ps1    # 点引用（dot-source）加载到当前会话
#>

function Write-Step {
    param([string]$Label, [string]$Status, [string]$Detail = "")
    $icon = if ($Status -eq "OK") { "✓" } elseif ($Status -eq "WARN") { "⚠" } else { "✗" }
    $detailStr = if ($Detail) { " — $Detail" } else { "" }
    Write-Host "  $icon $Label$detailStr" -ForegroundColor $(if ($Status -eq "OK") { "Green" } elseif ($Status -eq "WARN") { "Yellow" } else { "Red" })
}

Write-Host "`n=== ZeroToken Windows/PowerShell 环境初始化 ===" -ForegroundColor Cyan
Write-Host ""

# 1. Git quotepath（仅本地仓库，不修改全局设置）
Write-Host "[1/4] Git 配置" -ForegroundColor Cyan
try {
    git config core.quotepath false
    Write-Step "core.quotepath false (local)" "OK"
} catch {
    Write-Step "core.quotepath false" "WARN" "设置失败，git diff 中文文件名将显示为转义序列"
}
Write-Host "注意：quotepath 仅在当前仓库生效，不修改全局 Git 配置。" -ForegroundColor Yellow

# 2. Python 编码检查
Write-Host "[2/4] Python 环境" -ForegroundColor Cyan
try {
    $pyVersion = python --version
    Write-Step "Python 可用" "OK" $pyVersion
} catch {
    Write-Step "Python" "FAIL" "未找到 python 命令，脚本工具无法使用"
}

# 3. 检查替换字符
Write-Host "[3/4] 编码健康状况" -ForegroundColor Cyan
try {
    python scripts/fix_encoding.py check-replacement . --ext .md,.yaml,.json 2>$null
    Write-Step "替换字符检查" "OK"
} catch {
    Write-Step "替换字符检查" "WARN" "需手动运行: python scripts/fix_encoding.py check-replacement ."
}

# 4. 提示可用工具
Write-Host "[4/4] 可用脚本工具" -ForegroundColor Cyan
Write-Host "  • python scripts/safe_io.py          — 安全文件读写（含 safe_append 替代 Add-Content）" -ForegroundColor Gray
Write-Host "  • python scripts/detect_gbk_contamination.py — 检测修复 GBK 编码污染" -ForegroundColor Gray
Write-Host "  • python scripts/batch_edit.py       — 一次性多编辑（解决 edit_file 阻塞）" -ForegroundColor Gray
Write-Host "  • python scripts/fix_encoding.py     — 批量编码转换" -ForegroundColor Gray
Write-Host "  • python scripts/verify_output.py    — 验证结果输出到文件（替代 print）" -ForegroundColor Gray
Write-Host ""

Write-Host "初始化完成。按 ZeroToken F 模式工作流操作。" -ForegroundColor Green
