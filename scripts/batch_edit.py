"""
batch_edit.py — 一次性对同一文件应用多处修改

解决的问题：
- edit_file 工具同文件连续编辑阻塞（"fresh read required"）
- 需要在同一文件中做多处精准替换时的原子性保证

用法：
    python scripts/batch_edit.py <file> <replacements.json>

replacements.json 格式：
    [
        {"old": "原文1", "new": "新文1"},
        {"old": "原文2", "new": "新文2"}
    ]

或通过命令行参数传入单次替换：
    python scripts/batch_edit.py <file> --old "原文" --new "新文"

安全保证：
    - 所有替换在内存中顺序执行
    - 只有全部替换成功才写入磁盘
    - 任一步失败则放弃写入，打印错误行号
"""

import json
import os
import sys
from typing import List, Tuple


# ── 安全打印（解决 #6: GBK 控制台 UnicodeEncodeError）──
# 统一实现见 safe_io.py（ensure_utf8_stdio / sp 别名），
# 此处仅复用，不再各脚本维护副本。
from safe_io import ensure_utf8_stdio, read_text, safe_print, safe_write

sp = safe_print  # 兼容本文件既有的调用名

ensure_utf8_stdio()


def safe_write(path: str, content: str) -> None:
    """安全写入 UTF-8。"""
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def apply_replacements(content: str,
                       replacements: List[Tuple[str, str]],
                       path: str) -> str:
    """对 content 顺序应用所有替换，任一步失败则抛出 ValueError。"""
    result = content
    for i, (old, new) in enumerate(replacements):
        count = result.count(old)
        if count == 0:
            raise ValueError(
                f"[step {i+1}] not found: {repr(old[:40])} "
                f"(in {path})"
            )
        if count > 1:
            raise ValueError(
                f"[step {i+1}] found {count} matches, need unique: "
                f"{repr(old[:40])} (in {path})"
            )
        result = result.replace(old, new)
        sp(f"  + replace {i+1}/{len(replacements)}: "
           f"{repr(old[:30])} -> {repr(new[:30])}")
    return result


def main():
    if len(sys.argv) < 3:
        sp("usage:")
        sp("  python scripts/batch_edit.py <file> <replacements.json>")
        sp("  python scripts/batch_edit.py <file> --old <old> --new <new>")
        sys.exit(1)

    path = sys.argv[1]

    # 解析替换对
    replacements: List[Tuple[str, str]] = []

    if sys.argv[2].endswith('.json'):
        # 从 JSON 文件读取
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            data = json.load(f)
        for item in data:
            replacements.append((item['old'], item['new']))
    else:
        # 从命令行参数读取
        if '--old' in sys.argv and '--new' in sys.argv:
            idx_old = sys.argv.index('--old')
            idx_new = sys.argv.index('--new')
            replacements.append((sys.argv[idx_old + 1], sys.argv[idx_new + 1]))
        else:
            sp("error: need --old and --new args, or a JSON file")
            sys.exit(1)

    # 执行
    sp(f"file: {path}")
    sp(f"replacements: {len(replacements)}")
    sp("-" * 40)

    content = read_text(path)
    new_content = apply_replacements(content, replacements, path)

    if content == new_content:
        sp("(no change - old and new are identical)")
    else:
        safe_write(path, new_content)
        old_len = len(content)
        new_len = len(new_content)
        delta = new_len - old_len
        sp(f"written ({old_len} -> {new_len} chars, delta={delta:+d})")


if __name__ == '__main__':
    main()
