"""
verify_output.py — 验证结果输出工具（替代 print）

解决的问题：
- Python print() 在 Windows PowerShell 下因 GBK 编码报错
- AutoResearch verification 证据需要结构化输出
- 复杂验证结果需要同时写文件 + 打印摘要

用法：
    python scripts/verify_output.py <检查项名称> <out.txt> \\
        --pass "✓ 关键词A: 找到 5 处" \\
        --pass "✓ 关键词B: 找到 3 处" \\
        --fail "✗ 关键词C: 未找到"

输出文件格式（每行）：
    [PASS] ✓ 关键词A: 找到 5 处
    [PASS] ✓ 关键词B: 找到 3 处
    [FAIL] ✗ 关键词C: 未找到
    ---
    总计: 2 PASS, 1 FAIL
"""

import argparse
import os
import sys
from datetime import datetime
from typing import List, Tuple


# ── 安全打印（解决 #6: GBK 控制台 UnicodeEncodeError）──
# 统一实现见 safe_io.py（ensure_utf8_stdio / safe_print），此处仅复用。
from safe_io import ensure_utf8_stdio, safe_print

sp = safe_print  # 兼容本文件既有的调用名

ensure_utf8_stdio()


def write_verify_results(
    title: str,
    out_path: str,
    passes: List[str],
    fails: List[str],
    notes: str = "",
) -> str:
    """将验证结果写入文件并返回绝对路径。

    Args:
        title: 验证项名称
        out_path: 输出文件路径（建议 .txt）
        passes: 通过的检查项列表（推荐以 ✓ 开头）
        fails: 失败的检查项列表（推荐以 ✗ 开头）
        notes: 附加说明（可选）

    Returns:
        写入文件的绝对路径
    """
    lines: List[str] = []
    lines.append(f"验证: {title}")
    lines.append(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 50)

    for item in passes:
        lines.append(f"[PASS] {item}")

    for item in fails:
        lines.append(f"[FAIL] {item}")

    lines.append("-" * 50)
    total_pass = len(passes)
    total_fail = len(fails)
    lines.append(f"总计: {total_pass} PASS, {total_fail} FAIL")

    if notes:
        lines.append(f"说明: {notes}")

    if total_fail > 0:
        lines.append("状态: ❌ 验证未通过")
    else:
        lines.append("状态: ✅ 全部通过")

    content = "\n".join(lines) + "\n"

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

    abs_path = os.path.abspath(out_path)
    sp(f"结果已写入: {abs_path}")
    sp(f"  PASS: {total_pass}, FAIL: {total_fail}")
    sp(f"  用 read_file 查看: read_file(\"{abs_path}\")")

    return abs_path


def grep_check(
    file_path: str,
    pattern: str,
    expected_min: int = 1,
    label: str = "",
) -> Tuple[bool, str]:
    """检查文件中关键词出现次数，返回 (通过?, 描述)。

    这是纯 Python 实现，不依赖 grep 命令。
    """
    if not label:
        label = pattern

    try:
        # 安全读取：显式 UTF-8，失败时抛错而非静默替换
        with open(file_path, 'rb') as f:
            raw = f.read()
        if raw.startswith(b'\xef\xbb\xbf'):
            content = raw.decode('utf-8-sig')
        elif raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
            content = raw.decode('utf-16')
        else:
            content = raw.decode('utf-8')

        count = content.count(pattern)
        if count >= expected_min:
            return (True, f"'{pattern}': 找到 {count} 处 (期望 ≥{expected_min})")
        else:
            return (False, f"'{pattern}': 找到 {count} 处 (期望 ≥{expected_min})")

    except Exception as e:
        return (False, f"读取失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="验证结果输出工具"
    )
    parser.add_argument("title", help="验证名称")
    parser.add_argument("out_path", help="输出文件路径（.txt）")
    parser.add_argument("--pass", dest="passes", action="append",
                        default=[], help="通过的检查项")
    parser.add_argument("--fail", dest="fails", action="append",
                        default=[], help="失败的检查项")
    parser.add_argument("--notes", default="", help="附加说明")
    parser.add_argument("--grep", nargs=3, metavar=("FILE", "PATTERN", "MIN"),
                        help="文件关键词检查: <file> <pattern> <min_count>")

    args = parser.parse_args()

    passes: List[str] = args.passes[:]
    fails: List[str] = args.fails[:]

    # 可选的文件关键词检查
    if args.grep:
        file_path, pattern, min_str = args.grep
        try:
            min_count = int(min_str)
        except ValueError:
            min_count = 1
        ok, desc = grep_check(file_path, pattern, min_count)
        if ok:
            passes.append(desc)
        else:
            fails.append(desc)

    write_verify_results(args.title, args.out_path, passes, fails, args.notes)

    if fails:
        sys.exit(1)  # 有失败项时返回非零退出码


if __name__ == '__main__':
    main()
