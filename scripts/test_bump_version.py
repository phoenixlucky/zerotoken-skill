"""Regression tests for bump_version (三处版本号联动).

Run: python scripts/test_bump_version.py
Covers:
- collect_versions: 三个锚点都能取到版本号
- apply_version: 三处都写入新版本，且不动其它内容
- gather: 一致 -> ok=True；任一漂移 -> ok=False
- 写入路径对锚点正则组数不敏感（v1.14.0 修的 IndexError 回归）
"""

import os
import tempfile

from bump_version import apply_version, collect_versions, gather
from safe_io import read_text, safe_write

PACKAGE = '''{
  "name": "demo",
  "version": "1.0.0",
  "files": [
    "SKILL.md"
  ]
}
'''

SKILL = '''---
name: demo
version: 1.0.0
metadata:
  platform: linux
---

# Demo
'''

README = '''<div align="center">

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
</div>

正文里也提到 1.0.0 这个数字，但不应被改写。
'''


def write_fixture(root, package=PACKAGE, skill=SKILL, readme=README):
    safe_write(os.path.join(root, 'package.json'), package)
    safe_write(os.path.join(root, 'SKILL.md'), skill)
    safe_write(os.path.join(root, 'README.md'), readme)


def main() -> None:
    with tempfile.TemporaryDirectory() as root:
        write_fixture(root)

        # ── collect_versions ──────────────────────────────
        versions = dict(collect_versions(root))
        assert versions == {
            'package.json': '1.0.0', 'SKILL.md': '1.0.0', 'README.md': '1.0.0',
        }, versions

        # ── gather: 一致 ──────────────────────────────────
        ok, values = gather(root)
        assert ok is True, values

        # ── apply_version: 三处都写，且不误改正文 ──────────
        changed = apply_version('2.3.4', root)
        assert set(changed) == {'package.json', 'SKILL.md', 'README.md'}, changed
        assert read_text(os.path.join(root, 'package.json')).count('2.3.4') == 1
        assert read_text(os.path.join(root, 'SKILL.md')).count('2.3.4') == 1
        readme = read_text(os.path.join(root, 'README.md'))
        assert 'version-2.3.4-blue.svg' in readme
        assert '正文里也提到 1.0.0' in readme, '正文里的版本号不应被改写'

        ok, values = gather(root)
        assert ok is True and set(values.values()) == {'2.3.4'}, values

        # 幂等：已是目标版本时不重复写入
        assert apply_version('2.3.4', root) == []

        # ── gather: 漂移 -> not ok ────────────────────────
        safe_write(os.path.join(root, 'README.md'),
                   readme.replace('version-2.3.4-blue.svg', 'version-2.3.3-blue.svg'))
        ok, values = gather(root)
        assert ok is False, values
        assert values['README.md'] == '2.3.3'

        # ── 锚点缺失 -> not ok（不抛异常）────────────────
        safe_write(os.path.join(root, 'SKILL.md'), '# 没有 frontmatter\n')
        ok, values = gather(root)
        assert ok is False and values['SKILL.md'] is None, values

        # ── SKILL.md 锚点只有两组时写入路径不崩 ─────────────
        write_fixture(root)
        apply_version('3.0.0', root)
        assert 'version: 3.0.0' in read_text(os.path.join(root, 'SKILL.md'))

    print('test_bump_version: all assertions passed')


if __name__ == '__main__':
    main()
