"""Regression tests for detect_env (environment detection + persistence).

Run: python scripts/test_detect_env.py
Covers:
- recommended_shell per OS
- check_cjk_console: utf-8/cp65001/GBK/ASCII
- detect_environment structure on the current host
- save/load round-trip, staleness and corruption handling
"""

import json
import os
import tempfile
import time

from detect_env import (DEFAULT_ENV_PATH, MAX_AGE_SECONDS, build_report,
                        check_cjk_console, detect_environment,
                        is_fresh, load_environment, recommended_shell,
                        save_environment)

TEXT = "中文内容 emoji 🧭 end"


def main() -> None:
    # ── recommended_shell ──────────────────────────────
    assert recommended_shell("windows") == "powershell"
    assert recommended_shell("linux") == "bash"
    assert recommended_shell("darwin") == "zsh"
    assert recommended_shell("sunos") == "bash"  # 未知 POSIX 系统回退 bash

    # ── check_cjk_console ──────────────────────────────
    assert check_cjk_console("utf-8") is True
    assert check_cjk_console("cp65001") is True
    assert check_cjk_console("cp936") is True       # GBK：能显示中文
    assert check_cjk_console("gb18030") is True     # gb 前缀命中
    assert check_cjk_console("ascii") is False
    assert check_cjk_console("") is False           # 未知 → 不假设支持

    # ── detect_environment 结构完整性 ───────────────────
    env = detect_environment()
    os_name = env["os"]["name"]
    assert env["shell"]["recommended"] == recommended_shell(os_name)
    if os_name == "windows":
        assert env["powershell"], "Windows 上必须探测到 PowerShell 信息块"
        assert env["console"]["ansi_cp"] > 0
        assert isinstance(env["git"].get("quotepath"), str)
    else:
        assert env["powershell"] == {}
        assert isinstance(env["shell"]["bash_available"], bool)

    report_text = build_report(env)
    assert "Mode" in report_text
    if os_name == "windows":
        assert "POWERSHELL" in report_text
        assert "do NOT use bash" in report_text
        assert "Mode F active" in report_text
    else:
        assert "Mode G" in report_text or "POSIX" in report_text

    # ── 持久化：round-trip / 过期 / 损坏 ─────────────────
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "environment.json")

        saved_to = save_environment(env, out_path=path)
        assert saved_to == path
        with open(path, "rb") as f:
            raw = f.read()
        assert not raw.startswith(b"\xef\xbb\xbf"), "BOM must not be written"
        assert b"\r\n" not in raw, "LF only"
        data = json.loads(raw.decode("utf-8"))
        assert data["os"]["name"] == os_name
        assert data == json.loads(json.dumps(env, ensure_ascii=False)), \
            "saved JSON must round-trip the report as-is"

        loaded = load_environment(path)
        assert loaded == data, "load must return identical JSON"

        # 过期文件必须被拒绝
        stale = dict(data)
        old = time.localtime(time.time() - MAX_AGE_SECONDS - 60)
        stale["detected_at"] = time.strftime("%Y%m%dT%H%M%S%z", old)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(stale, f, ensure_ascii=False, indent=2)
        assert load_environment(path) is None, "stale file must be rejected"

        # 损坏文件必须被拒绝且给出可读错误
        with open(path, "w", encoding="utf-8") as f:
            f.write("{not-json")
        assert load_environment(path) is None, "corrupt file must be rejected"

        # 缓存复用路径：is_fresh 判断
        fresh_data = dict(data)
        assert is_fresh(fresh_data) is True
        fresh_data["detected_at"] = ""
        assert is_fresh(fresh_data) is False

    print("test_detect_env: all assertions passed")


if __name__ == "__main__":
    main()
