"""Regression tests for zt.py (统一命令入口的路由)。

Run: python scripts/test_zt.py
Covers:
- discover_tests / CHECK_STEPS：自动发现 scripts/test_*.py 并接线
- build_help：包含命令表关键字
- main 路由：help/-h 返回 0；未知命令返回 2
"""

import contextlib
import io
import os
import sys

import zt


def run_argv(argv):
    old = sys.argv
    sys.argv = argv
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return zt.main()
    finally:
        sys.argv = old


def run() -> None:
    # ── 测试自动发现 ─────────────────────────────────────
    discovered = zt.discover_tests()
    list_names = [name for _, name, _ in discovered]
    names = set(list_names)
    assert 'test_safe_io.py' in names, names
    assert 'test_zt.py' in names, names
    assert list_names == sorted(list_names), '发现的测试应按文件名排序'
    for _, name, args in discovered:
        assert args == ()
        assert os.path.exists(os.path.join(zt.SCRIPTS_DIR, name)), name

    # ── CHECK_STEPS：测试在前，审计/版本在后 ──────────────
    step_scripts = [script for _, script, _ in zt.CHECK_STEPS]
    assert 'audit_encoding.py' in step_scripts
    assert 'audit_skill.py' in step_scripts
    assert step_scripts[-1] == 'bump_version.py'
    assert step_scripts.index('audit_encoding.py') > len(discovered) - 1

    # ── build_help ──────────────────────────────────────
    help_text = zt.build_help()
    assert 'zt.py' in help_text and 'check' in help_text and 'version' in help_text

    # ── main 路由 ───────────────────────────────────────
    assert run_argv(['zt.py', 'help']) == 0
    assert run_argv(['zt.py', '-h']) == 0
    assert run_argv(['zt.py', '不存在的命令']) == 2
    assert run_argv(['zt.py']) == 0

    print('test_zt: all assertions passed')


if __name__ == '__main__':
    run()
