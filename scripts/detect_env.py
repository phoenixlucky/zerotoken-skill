"""detect_env — 运行时环境探测与持久化（ZeroToken F/G 模式基础设施）。

用途：
    在任何涉及命令行执行的任务开始时，先运行本模块获取当前系统的
    OS / Shell / 编码 / 中文支持能力，并把结果持久化到
    ``.zerotoken/environment.json``，供后续命令选择参考。

设计原则（对齐 docs/unicode-encoding-spec.md）：
- Windows 系统优先使用 PowerShell，明确排除 bash；
  Linux/macOS 使用 sh/bash；macOS 默认 zsh（兼容 sh/bash）。
- 不猜测、不依赖默认值：所有结论来自显式探测。
- 输出与持久化统一 UTF-8（ensure_ascii=False），控制台输出经 safe_print。

用法：
    命令行： python scripts/detect_env.py [--force] [--out PATH]
    库调用： from detect_env import detect_environment, load_environment
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from safe_io import ensure_utf8_stdio, safe_print

__all__ = [
    "DEFAULT_ENV_PATH",
    "MAX_AGE_SECONDS",
    "UnknownEncodingError",
    "build_report",
    "check_cjk_console",
    "check_powershell",
    "detect_environment",
    "is_fresh",
    "load_environment",
    "main",
    "recommended_shell",
]

# 探测结果默认存放位置（仓库根目录 .zerotoken/ 下）
DEFAULT_ENV_PATH = os.path.join(".zerotoken", "environment.json")
# 结果有效期：超过后建议重新探测（系统更新、终端切换会使结果过期）
MAX_AGE_SECONDS = 7 * 24 * 3600


def recommended_shell(os_name: str) -> str:
    """按操作系统给出推荐 shell。Windows → PowerShell，Linux/macOS → sh/bash/zsh。"""
    if os_name == "windows":
        return "powershell"
    if os_name == "darwin":
        return "zsh"
    return "bash"


def check_powershell() -> Dict[str, Any]:
    """探测 PowerShell 可用性、版本与发行版（Desktop=5.1 / Core=7+）。"""
    info: Dict[str, Any] = {"available": False}
    exe = shutil.which("powershell") or shutil.which("pwsh")
    if not exe:
        return info
    info["available"] = True
    info["executable"] = exe
    name = Path(exe).name.lower()
    info["edition"] = "powershell-core" if name.startswith("pwsh") else "windows-powershell"
    try:
        completed = subprocess.run(
            [exe, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        if completed.returncode == 0 and completed.stdout:
            version = completed.stdout.strip().splitlines()[-1].strip()
            if version:
                info["version"] = version
                major = int(version.split(".")[0])
                # PS 5.1 (Desktop) 与 PS 7+ (Core) 的编码默认行为差异巨大，
                # 直接决定写文件是否需要显式 -Encoding / WriteAllText。
                info["generation"] = "core" if major >= 6 else "desktop"
    except (OSError, subprocess.TimeoutExpired):
        pass
    return info


def check_cjk_console(stdout_encoding: str) -> bool:
    """判断当前控制台能否直接输出中文（无需 chcp 65001 / 文件中转）。

    规则：
    - cp936/gbk/gb18030/big5 等中文代码页 → 能显示中文（但 emoji 可能丢字）
    - cp65001/utf-8 → 完全支持
    - ascii / 其他单字节代码页 → 不支持，需走文件验证路径
    """
    normalized = stdout_encoding.lower().replace("-", "")
    if normalized in {"utf8", "cp65001"}:
        return True
    if re.fullmatch(r"cp(936|950|95[0-4])", normalized) or normalized.startswith("gb"):
        return True
    return False


def detect_environment(force: bool = False) -> Dict[str, Any]:
    """收集当前系统参数并返回结构化报告（不落盘）。"""
    os_name = platform.system().lower()
    stdout_enc = (getattr(sys.stdout, "encoding", None) or "").lower()
    preferred_enc = (sys.getfilesystemencoding() or "").lower()
    fs_encoding = sys.getfilesystemencoding()
    cjk_ok = check_cjk_console(stdout_enc)

    env: Dict[str, Any] = {
        "schema": 1,
        # 机器解析用（is_fresh 依赖此格式）；detected_at_iso 为人类可读副本
        "detected_at": time.strftime("%Y%m%dT%H%M%S%z"),
        "detected_at_iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "os": {
            "name": os_name,                       # windows / linux / darwin
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python_platform": sys.platform,
        },
        "shell": {
            "recommended": recommended_shell(os_name),
            "comspec": os.environ.get("COMSPEC"),
            "posix": os.name == "posix",
            "bash_available": None,                # 非 POSIX 下不探测，保持 None
        },
        "console": {
            "stdout_encoding": stdout_enc,
            "preferred_encoding": preferred_enc,
            "filesystem_encoding": (fs_encoding or "").lower(),
            "utf8_mode": bool(sys.flags.utf8_mode),
            "ansi_cp": None,
            "oem_cp": None,
            "cjk_capable": cjk_ok,
            "cjk_note": (
                "UTF-8 console; CJK output OK"
                if cjk_ok and stdout_enc in {"utf-8", "cp65001"}
                else "CJK codepage; CJK visible, emoji may degrade"
                if cjk_ok
                else "non-CJK console; verify via files, not terminal display"
            ),
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "git": {},
        "powershell": {},
    }

    # ── Windows 特有：ANSI/OEM 代码页 + Git quotepath + PowerShell ──
    if os_name == "windows":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            env["console"]["ansi_cp"] = kernel32.GetACP()
            env["console"]["oem_cp"] = kernel32.GetOEMCP()
        except Exception:  # noqa: BLE001 — 探测失败不影响主流程
            pass

        try:
            git_quotepath = subprocess.run(
                ["git", "config", "--get", "core.quotepath"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
            env["git"]["quotepath"] = (
                git_quotepath.stdout.strip() if git_quotepath.returncode == 0 else "(unset)"
            )
        except (OSError, subprocess.TimeoutExpired):
            env["git"]["quotepath"] = "unknown"

        env["powershell"] = check_powershell()

    # ── POSIX：确认 bash 是否真实存在 ──
    elif os.name == "posix":
        env["shell"]["bash_available"] = shutil.which("bash") is not None

    return env


# ── 持久化：保存 / 加载 / 过期检查 ────────────────────────────────


def is_fresh(data: Optional[Dict[str, Any]], max_age: int = MAX_AGE_SECONDS) -> bool:
    """判断已保存的探测结果是否仍然有效（未过期且结构完整）。"""
    if not isinstance(data, dict):
        return False
    raw_ts = data.get("detected_at")
    if not isinstance(raw_ts, str) or len(raw_ts) < 15:
        return False
    try:
        ts = time.mktime(time.strptime(raw_ts[:15], "%Y%m%dT%H%M%S"))
    except ValueError:
        return False
    return (time.time() - ts) < max_age


def save_environment(report: Optional[Dict[str, Any]] = None,
                     out_path: str = DEFAULT_ENV_PATH) -> str:
    """把探测报告写入 JSON（UTF-8 无 BOM + LF + ensure_ascii=False）。"""
    if report is None:
        report = detect_environment()
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return str(path)


def load_environment(path: str = DEFAULT_ENV_PATH,
                     *, force_refresh: bool = False,
                     max_age: int = MAX_AGE_SECONDS) -> Any:
    """读取已保存的环境信息；不存在或过期时返回 None。

    Args:
        path: environment.json 路径。
        force_refresh: True 时直接返回 None（强制上层重新探测）。
        max_age: 有效期秒数，默认 7 天。
    """
    if force_refresh:
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[detect_env] {path} 不存在，请先运行: python scripts/detect_env.py",
              file=sys.stderr)
        return None
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(f"[detect_env] {path} 已损坏或非 UTF-8，请用 --force 重新生成",
              file=sys.stderr)
        return None
    if not is_fresh(data, max_age):
        print(f"[detect_env] {path} 已过期（>{max_age // 86400} 天），请重新探测",
              file=sys.stderr)
        return None
    return data


# ── 报告渲染 ─────────────────────────────────────────────────────


def build_report(env: Dict[str, Any], source_path: str = DEFAULT_ENV_PATH) -> str:
    """把探测结果渲染为面向 agent 的行动建议文本（纯 ASCII 标记）。"""
    lines: list[str] = []
    os_info = env["os"]
    console = env["console"]
    ps_info = env.get("powershell") or {}
    git_info = env.get("git") or {}

    lines.append("=== ZeroToken Environment Detection ===")
    lines.append("")
    lines.append("[System]")
    lines.append(f"os                  : {os_info['name']} {os_info['release']} ({os_info['machine']})")
    py = env.get("python", {})
    lines.append(f"python              : {py.get('version', '?')} ({py.get('executable', '?')})")
    lines.append("")
    lines.append("[Shell]")
    lines.append(f"recommended shell   : {env['shell']['recommended'].upper()}")

    if os_info["name"] == "windows":
        lines.append("rule                : Windows uses PowerShell; do NOT use bash")
    else:
        bash_flag = "yes" if env["shell"].get("bash_available") else "no"
        lines.append(f"bash available      : {bash_flag}")
    lines.append("")

    lines.append("[Console Encoding]")
    lines.append(f"stdout encoding     : {console['stdout_encoding'] or '(unknown)'}")
    if os_info["name"] == "windows":
        lines.append(f"ANSI codepage       : {console['ansi_cp']}")
        lines.append(f"OEM codepage        : {console['oem_cp']}")
    cjk_state = "yes" if console["cjk_capable"] else "NO"
    lines.append(f"CJK console         : {cjk_state} ({console['cjk_note']})")
    lines.append("")

    if os_info["name"] == "windows" and ps_info:
        lines.append("[PowerShell]")
        lines.append(f"available           : {ps_info.get('available', False)}")
        lines.append(f"edition             : {ps_info.get('edition', '?')}"
                     f" v{ps_info.get('version', '?')}")
        gen = ps_info.get("generation")
        warn = ""
        if gen == "desktop":
            warn = ("  <- PS 5.1: Set-Content/Add-Content default to GBK;"
                    " write via Python safe_io")
        lines.append(f"generation          : {gen}{warn}")
        lines.append("")

    if os_info["name"] == "windows" and git_info:
        lines.append("[Git]")
        qp = git_info.get("quotepath")
        hint = ""
        if qp in ("(unset)", "true", None, "unknown"):
            hint = "  <- run: git config core.quotepath false (local)"
        lines.append(f"core.quotepath      : {qp}{hint}")
        lines.append("")

    lines.append("[Saved Report]")
    lines.append(f"path                 : {source_path}")
    age_hint = f"{MAX_AGE_SECONDS // 86400} days"
    lines.append(f"validity             : <= {age_hint}; rerun when stale")
    lines.append("")
    lines.append("[Recommended Workflow]")
    if os_info["name"] == "windows":
        lines.append("1. Use the saved system parameters above for every command choice.")
        lines.append("2. Prefer PowerShell syntax; never use bash on Windows.")
        lines.append("3. Write/edit files with Chinese via scripts/safe_io.py"
                     " (safe_write / safe_append).")
        if not console["cjk_capable"]:
            lines.append("4. Console cannot show CJK: verify content by reading"
                         " files, not terminal output.")
        else:
            lines.append("4. Console shows CJK, but still prefer file-based"
                         " verification for accuracy.")
        if ps_info.get("generation") == "desktop":
            lines.append("5. PS 5.1 detected: no Set-Content/Add-Content/Out-File"
                         " for non-ASCII content.")
        if git_info.get("quotepath") in ("(unset)", "true", None, "unknown"):
            lines.append("6. Run: git config core.quotepath false")
    else:
        lines.append("1. Use the saved system parameters above for every command choice.")
        lines.append("2. Use POSIX shell syntax (sh/bash); PowerShell rules do NOT apply.")
        if not console["cjk_capable"]:
            lines.append("3. Non-CJK locale: verify CJK content via files"
                         " (cat may mojibake under non-UTF8 locales).")
        lines.append("3. Standard ZeroToken workflow applies.")

    lines.append("")
    lines.append("[Mode]")
    if os_info["name"] == "windows":
        lines.append("Detected: Windows/PowerShell -> Mode F active (auto-enabled,"
                     " no Chinese text required).")
    else:
        lines.append("Detected: POSIX system -> Mode G (POSIX): standard workflow,"
                     " sh/bash allowed.")
    return "\n".join(lines)


def main(argv: Optional[list] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    force = False
    out_path = DEFAULT_ENV_PATH
    it = iter(argv)
    for arg in it:
        if arg == "--force":
            force = True
        elif arg == "--out":
            try:
                out_path = next(it)
            except StopIteration:
                safe_print("[detect_env] --out requires a value")
                return 2
    ensure_utf8_stdio()

    if not force and is_fresh(_peek_saved(out_path)):
        env = _peek_saved(out_path)
        source = out_path
    else:
        env = detect_environment()
        source = save_environment(env, out_path)
    safe_print(build_report(env, source_path=source))
    return 0


def _peek_saved(path: str) -> Any:
    """静默读取已保存报告（无则 None），供 main 判断缓存复用。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            import json as _json

            return _json.load(f)
    except Exception:  # noqa: BLE001 — 缓存不可用时一律重新探测
        return None


if __name__ == "__main__":
    raise SystemExit(main())
