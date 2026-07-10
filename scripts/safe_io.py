"""
safe_io.py — 安全文件读写工具模块

解决的问题：
- 文件编码不一致（UTF-8 / UTF-16 / 含损坏字符）
- Python 控制台输出中文在 GBK 环境下失败

用法：
    from safe_io import safe_read, safe_write, write_result

    content = safe_read("path/to/file.md")
    safe_write("path/to/file.md", content)
    write_result("验证通过", out_path="verify_result.txt")
"""

import os
import sys
from typing import Optional


# ── 编码安全的控制台输出 ──────────────────────────────────
# 解决 #6: Python 在 GBK 控制台下 print(中文/特殊符号) 报 UnicodedEncodeError
_STDOUT_ENCODING = getattr(sys.stdout, 'encoding', 'utf-8') or 'utf-8'


def safe_print(*args, **kwargs) -> None:
    """安全打印，自动处理控制台编码不支持 Unicode 的问题。

    在 GBK 控制台下，会将无法编码的字符替换为 '?' 而不是崩溃。
    永远不会有 UnicodeEncodeError。
    """
    try:
        # 先尝试正常 print
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # 兜底：对每个参数做编码安全处理
        safe_args = []
        for a in args:
            if isinstance(a, str):
                safe_args.append(a.encode(
                    _STDOUT_ENCODING, errors='replace').decode(
                    _STDOUT_ENCODING, errors='replace'))
            else:
                safe_args.append(str(a))
        print(*safe_args, **kwargs)


def safe_read(path: str) -> str:
    """安全读取文件，兼容 UTF-8 / UTF-16 / 含损坏字符的文件。

    自动检测 BOM（UTF-16 LE/BE），回退到 UTF-8 带 errors=replace。
    """
    with open(path, 'rb') as f:
        raw = f.read()

    # 检测 BOM
    if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
        # UTF-16 LE / BE
        try:
            return raw.decode('utf-16')
        except:
            pass

    # UTF-8（容忍损坏字符）
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        return raw.decode('utf-8', errors='replace')


def safe_write(path: str, content: str) -> None:
    """安全写入文件，统一 UTF-8 编码（不含 BOM）。"""
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def write_result(result: str, out_path: str = "verify_result.txt",
                 append: bool = False) -> str:
    """将结果写入文本文件，避免 print() 在 GBK 环境下报错。

    返回写入的绝对路径，供 read_file 工具读取。
    """
    mode = 'a' if append else 'w'
    with open(out_path, mode, encoding='utf-8') as f:
        f.write(result)
        if not result.endswith('\n'):
            f.write('\n')

    abs_path = os.path.abspath(out_path)
    safe_print(f"结果已写入: {abs_path}  <- 用 read_file 查看")
    return abs_path


def auto_encoding(path: str) -> str:
    """自动判断文件编码并读取。与 safe_read 相同但返回 None 时不会崩溃。

    用于批量脚本需要跳过无法处理的文件时。
    """
    try:
        return safe_read(path)
    except Exception:
        return ""
