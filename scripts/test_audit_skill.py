"""Regression tests for audit_skill (文档一致性审计).

Run: python scripts/test_audit_skill.py
Covers:
- 合规的最小 fixture -> audit() 无 problems
- CHANGELOG 顶部版本与 package.json 漂移 -> 命中 [CHANGELOG 版本不一致]
- 站内锚点指向不存在的标题 -> 命中 [锚点失效]
- 未文档化的非测试脚本 -> 命中 [脚本未文档化]（test_*.py 豁免）
"""

import os
import tempfile

from audit_skill import audit
from safe_io import safe_write

PACKAGE = '''{
  "name": "demo",
  "version": "1.0.0"
}
'''

SKILL = '''---
name: demo
version: 1.0.0
---

# Demo

## 🧭 核心原则

1. **先分类，再预算** — demo

## 📝 精准提示词模板

目标 / 输入 / 约束 / 输出 / 预算。
'''

README = '''[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()

[安装锚点](#-安装) · [提示词模板](SKILL.md#-精准提示词模板) · 工具见 `scripts/demo.py`

## 🔌 安装

demo

## 🔑 核心原则（一句话版）

| # | 原则 | 含义 |
|:-:|------|------|
| 1 | **先分类** | demo |
'''

CHANGELOG = '''# Changelog

## [1.0.0] - 2026-01-01

- init
'''

TRAPS = '''# F 模式参考

## 已知陷阱与解决方案（0 条）

| # | 陷阱 | 症状 | 解决方案 |
|---|------|------|----------|
'''


def write_fixture(root, changelog=CHANGELOG, readme=README, extra_scripts=()):
    safe_write(os.path.join(root, 'package.json'), PACKAGE)
    safe_write(os.path.join(root, 'SKILL.md'), SKILL)
    safe_write(os.path.join(root, 'README.md'), readme)
    safe_write(os.path.join(root, 'CHANGELOG.md'), changelog)
    safe_write(os.path.join(root, 'references', 'windows-powershell.md'), TRAPS)
    safe_write(os.path.join(root, 'scripts', 'demo.py'), '# demo\n')
    for name in extra_scripts:
        safe_write(os.path.join(root, 'scripts', name), '# extra\n')


def run() -> None:
    with tempfile.TemporaryDirectory() as root:
        write_fixture(root, extra_scripts=('test_demo.py',))

        # ── 合规 fixture -> 无问题（test_*.py 不要求文档化）──
        notes, problems = audit(root)
        assert problems == [], problems
        assert any(n.startswith('CHANGELOG 版本一致: 1.0.0') for n in notes), notes
        assert '站内锚点全部有效' in notes, notes

        # ── CHANGELOG 漂移 -> 命中 ─────────────────────────
        write_fixture(root, changelog=CHANGELOG.replace('[1.0.0]', '[9.9.9]'))
        _, problems = audit(root)
        assert any('CHANGELOG 版本不一致' in p for p in problems), problems

        # ── 锚点失效 -> 命中 ───────────────────────────────
        broken = README.replace('(#-安装)', '(#-不存在的标题)')
        write_fixture(root, readme=broken)
        _, problems = audit(root)
        assert any('锚点失效' in p for p in problems), problems

        # ── 脚本未文档化 -> 命中 ───────────────────────────
        write_fixture(root, extra_scripts=('other.py',))
        _, problems = audit(root)
        assert any('脚本未文档化' in p for p in problems), problems

    print('test_audit_skill: all assertions passed')


if __name__ == '__main__':
    run()
