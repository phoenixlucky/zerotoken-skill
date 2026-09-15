"""bump_version.py — 版本号三处联动校验与写入

背景：版本号散落在三个文件里，历史上多次漏改（v1.12.0 起 bump 只改
package.json + SKILL.md frontmatter，README 顶部 badge 停在 1.11.0，直到
v1.13.2 才被发现）。本脚本把「三处联动」变成一条命令。

三处锚点：
    1. package.json          "version": "x.y.z"
    2. SKILL.md frontmatter  version: x.y.z
    3. README.md             badge/version-x.y.z-blue.svg

用法：
    python scripts/bump_version.py --check      # 只校验（CI / 发布前），不一致退出码 1
    python scripts/bump_version.py 1.14.0       # 写入三处并复查
"""

import argparse
import json
import os
import re
import sys

from safe_io import ensure_utf8_stdio, read_text, safe_print, safe_write

ensure_utf8_stdio()

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (相对路径, 匹配「前缀 + 版本号 + 后缀」的正则，第 2 组必须是版本号)
TARGETS = (
    ('package.json', re.compile(r'("version"\s*:\s*")([^"]+)(")')),
    ('SKILL.md', re.compile(r'^(version:\s*)([^\s]+)\s*$', re.M)),
    ('README.md', re.compile(r'(badge/version-)([0-9][^-\s]*)(-blue\.svg)')),
)

VERSION_RE = re.compile(r'^\d+\.\d+\.\d+$')


def collect_versions(root: str = REPO_ROOT):
    """返回 [(相对路径, 版本号或 None)]；锚点缺失时版本号为 None。"""
    found = []
    for rel, pattern in TARGETS:
        text = read_text(os.path.join(root, rel))
        match = pattern.search(text)
        found.append((rel, match.group(2) if match else None))
    return found


def apply_version(version: str, root: str = REPO_ROOT):
    """把三处锚点写成 version，返回实际被修改的相对路径列表。

    替换基于第 2 组（版本号）的 span，而不是拼接各组文本 ——
    这样正则的组数变化不会让写入路径静默崩溃（v1.14.0 修）。
    """
    changed = []
    for rel, pattern in TARGETS:
        path = os.path.join(root, rel)
        text = read_text(path)
        match = pattern.search(text)
        if not match or match.group(2) == version:
            continue
        start, end = match.span(2)
        safe_write(path, text[:start] + version + text[end:])
        changed.append(rel)
    return changed


def gather(root: str = REPO_ROOT):
    """返回 (三处是否都存在且一致, {相对路径: 版本号或 None})。"""
    values = dict(collect_versions(root))
    version_set = set(values.values())
    ok = None not in version_set and len(version_set) == 1
    return ok, values


def main() -> int:
    parser = argparse.ArgumentParser(
        description='版本号三处联动（package.json / SKILL.md / README.md）')
    parser.add_argument('version', nargs='?',
                        help='新版本号（如 1.14.0）；省略则只校验')
    parser.add_argument('--check', action='store_true',
                        help='只校验不写入（即使同时给了版本号）')
    parser.add_argument('--json', action='store_true',
                        help='输出 JSON（供 AI / CI 解析）')
    parser.add_argument('--out', default=None,
                        help='把 JSON 报告写入该文件（UTF-8，AI 用 read_file 读）')
    parser.add_argument('--root', default=REPO_ROOT,
                        help='仓库根目录（默认取脚本上级目录）')
    args = parser.parse_args()

    updated = []
    if args.version and not args.check:
        if not VERSION_RE.match(args.version):
            safe_print(f'非法版本号: {args.version!r}（应为 x.y.z）')
            return 2
        updated = apply_version(args.version, args.root)
        if not args.json:
            for rel in updated:
                safe_print(f'已更新: {rel} -> {args.version}')

    ok, values = gather(args.root)

    if args.json:
        payload = json.dumps({'ok': ok, 'updated': updated, 'values': values},
                             ensure_ascii=False, indent=2)
        if args.out:
            safe_write(args.out, payload + '\n')
            safe_print(f'JSON 报告已写入: {os.path.abspath(args.out)}')
        else:
            safe_print(payload)
        return 0 if ok else 1

    if ok:
        safe_print(f'版本一致: {values["package.json"]} '
                   '(package.json / SKILL.md / README.md)')
        return 0

    safe_print('版本不一致:')
    for rel, value in values.items():
        safe_print(f'  {rel:<14} {value if value else "<未找到>"}')
    safe_print('修复: python scripts/bump_version.py <版本号>')
    return 1


if __name__ == '__main__':
    sys.exit(main())
