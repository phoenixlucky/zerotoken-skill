"""
safe_io.py — 安全文件读写工具模块

解决的问题：
- 文件编码不一致（UTF-8 / UTF-16 / GB18030 / 含损坏字符）
- Python 控制台输出中文在 GBK 环境下失败
- PowerShell Add-Content / Set-Content 默认按 GBK 写入污染 UTF-8 文件

用法：
    from safe_io import safe_read, safe_write, safe_append, write_result

    content = safe_read("path/to/file.md")     # 自动检测编码；无法确定时抛错
    safe_write("path/to/file.md", content)     # 统一 UTF-8 无 BOM + LF
    safe_append("path/to/file.md", "追加内容")  # 替代 Add-Content
    write_result("验证通过", out_path="verify_result.txt")

编码检测策略（docs/unicode-encoding-spec.md 规范 6/13/14）：
    BOM（UTF-8/UTF-16LE/BE/UTF-32LE/BE）> UTF-8 严格验证 > GB18030 严格验证
    （GB18030 向下覆盖中文环境的 GBK/GB2312）。
    以上全部失败视为 unknown：strict 模式抛 UnknownEncodingError，
    绝不 errors='replace' 静默替换损坏字节。Big5/Shift_JIS 等其他编码
    属于「有明确需求才使用」的场景，应先用
    `python scripts/fix_encoding.py inspect <file>` 确认后显式指定。
"""

import os
import sys

__all__ = [
    "UnknownEncodingError",
    "sniff_encoding",
    "decode_bytes",
    "read_text",
    "safe_read",
    "safe_write",
    "safe_append",
    "write_result",
    "auto_encoding",
    "ensure_utf8_stdio",
    "safe_print",
]


class UnknownEncodingError(ValueError):
    """字节序列无法按已知编码（BOM/UTF-8/GB18030）解码时抛出。"""


# ── 编码安全的控制台输出 ──────────────────────────────────
# 解决 #6: Python 在 GBK 控制台下 print(中文/特殊符号) 报 UnicodeEncodeError
# 规范 2/15：不依赖系统默认字符集，优先显式把 stdio 切到 UTF-8，
# 而不是把中文替换成 '?'（显示层丢字）。
def ensure_utf8_stdio() -> None:
    """将 stdout/stderr 显式切换为 UTF-8（Python 3.7+）。

    Windows 中文系统默认控制台代码页为 GBK(936)，不切换时
    print(中文) 会抛 UnicodeEncodeError 或被替换成 '?'。
    切换到 UTF-8 后，配合 `chcp 65001`（或管道重定向）中文可完整显示。
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8')
        except (AttributeError, OSError, ValueError):
            # Python < 3.7 无 reconfigure，或流不支持重配置时保持原样
            pass


ensure_utf8_stdio()
_STDOUT_ENCODING = getattr(sys.stdout, 'encoding', 'utf-8') or 'utf-8'


def safe_print(*args, **kwargs) -> None:
    """安全打印，自动处理控制台编码不支持 Unicode 的问题。

    模块导入时已尝试把 stdout 切换到 UTF-8；在极少数仍无法
    编码的环境中，将无法编码的字符替换为 '?' 而不是崩溃。
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


# ── 编码检测与解码核心 ────────────────────────────────────

# 长 BOM 必须排在短 BOM 之前（FF FE 00 00 以 FF FE 开头）
_BOMS = (
    (b'\xef\xbb\xbf', 'utf-8-sig'),
    (b'\xff\xfe\x00\x00', 'utf-32-le'),
    (b'\x00\x00\xfe\xff', 'utf-32-be'),
    (b'\xff\xfe', 'utf-16-le'),
    (b'\xfe\xff', 'utf-16-be'),
)

# sniff 返回值 -> 实际解码用 codec：
# utf-16/utf-32 codec 自带 BOM 识别并剥离，避免开头残留 U+FEFF；
# utf-8-sig 剥离 BOM；utf-8/gb18030 无需转换。
_DECODE_CODECS = {
    'utf-16-le': 'utf-16',
    'utf-16-be': 'utf-16',
    'utf-32-le': 'utf-32',
    'utf-32-be': 'utf-32',
}


def sniff_encoding(raw: bytes) -> str:
    """探测字节流的编码，返回 codec 名称或 'unknown'（不抛错）。

    检测顺序（规范 6/14：显式声明 > BOM > 严格验证，绝不猜测）：
      1. BOM：utf-8-sig / utf-16-le / utf-16-be / utf-32-le / utf-32-be
      2. UTF-8 严格解码验证 -> 'utf-8'
      3. GB18030 严格解码验证 -> 'gb18030'（向下覆盖 GBK/GB2312）
      4. 其余 -> 'unknown'
    """
    for bom, name in _BOMS:
        if raw.startswith(bom):
            return name
    try:
        raw.decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError:
        pass
    try:
        raw.decode('gb18030')
        return 'gb18030'
    except UnicodeDecodeError:
        pass
    return 'unknown'


def decode_bytes(raw: bytes, source: str = '<bytes>') -> str:
    """按 sniff_encoding 的结果解码字节流。

    unknown 时抛 UnknownEncodingError（含前 32 字节 hex 与排查指引），
    绝不 errors='replace' 静默替换（规范 14：不确定时不猜测）。

    注：带 BOM 的 UTF-16/UTF-32 统一交给 'utf-16'/'utf-32' codec 解码，
    由其识别并剥离 BOM，避免文本开头残留 U+FEFF。
    """
    enc = sniff_encoding(raw)
    if enc == 'unknown':
        raise UnknownEncodingError(
            f"无法确定编码（非 UTF-8/UTF-16(BOM)/GB18030）: {source}\n"
            f"前 32 字节: {raw[:32].hex(' ')}\n"
            f"请先运行 `python scripts/fix_encoding.py inspect \"{source}\"` "
            "确认原编码后再处理，禁止盲目转换。"
        )
    return raw.decode(_DECODE_CODECS.get(enc, enc))


def read_text(path: str, *, strict: bool = True) -> str:
    """安全读取文本文件（二进制读入后按检测结果显式解码）。

    自动识别：UTF-8（含 BOM）/ UTF-16 / UTF-32（含 BOM）/ GB18030。

    Args:
        path: 文件路径
        strict: True（默认）= 无法确定编码时抛 UnknownEncodingError；
                False = 仅限查看/诊断场景，以 U+FFFD 替换无法解码的字节，
                **返回结果禁止回写文件**。

    Returns:
        解码后的文本
    """
    with open(path, 'rb') as f:
        raw = f.read()
    if strict:
        return decode_bytes(raw, path)
    try:
        return decode_bytes(raw, path)
    except UnknownEncodingError:
        return raw.decode('utf-8', errors='replace')


# 向后兼容别名（v1.10 及以前的公开名称）
safe_read = read_text


def safe_write(path: str, content: str) -> None:
    """安全写入文件，统一 UTF-8 编码（不含 BOM），行尾统一 LF。"""
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def _file_ends_with_newline(path: str) -> bool:
    """检查文件最后一个字节是否为 LF（用于追加前的粘连防护）。"""
    with open(path, 'rb') as f:
        f.seek(-1, os.SEEK_END)
        return f.read(1) == b'\n'


def safe_append(path: str, content: str) -> str:
    """安全追加内容到文件，统一使用 UTF-8 编码。

    专为替代 PowerShell Add-Content 设计。Add-Content 在 Windows 中文版下
    默认使用 GBK 编码写入（emoji 等字符还会被静默写成 '?'），
    与文件原有的 UTF-8 编码混合导致乱码；
    即使显式 `-Encoding UTF8` 也会写入 BOM、且追加到不以换行结尾的
    文件时不自动补换行导致内容粘连。

    始终使用 Python open(path, 'a', encoding='utf-8', newline='\n')，确保编码一致。

    Args:
        path: 文件路径（父目录不存在时自动创建）
        content: 要追加的内容（会自动在末尾加换行）

    Returns:
        写入文件的绝对路径

    Example:
        safe_append("笔记.md", "## 新的章节")
        # 等价于 PowerShell 的 Add-Content -Path 笔记.md -Value "## 新的章节"
        # 但使用 UTF-8 无 BOM、自动补换行
    """
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    # Add-Content 每次追加都自带换行；本函数对齐该语义：
    # 文件已存在且不以 \n 结尾时先补一个换行，避免段间内容粘连。
    needs_leading_newline = (
        os.path.exists(path) and os.path.getsize(path) > 0
        and not _file_ends_with_newline(path)
    )
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        if needs_leading_newline:
            f.write('\n')
        f.write(content)
        if not content.endswith('\n'):
            f.write('\n')

    abs_path = os.path.abspath(path)
    safe_print(f"已追加到: {abs_path}")
    return abs_path


def write_result(result: str, out_path: str = "verify_result.txt",
                 append: bool = False) -> str:
    """将结果写入文本文件，避免 print() 在 GBK 环境下报错。

    返回写入的绝对路径，供 read_file 工具读取。
    """
    mode = 'a' if append else 'w'
    with open(out_path, mode, encoding='utf-8', newline='\n') as f:
        f.write(result)
        if not result.endswith('\n'):
            f.write('\n')

    abs_path = os.path.abspath(out_path)
    safe_print(f"结果已写入: {abs_path}  <- 用 read_file 查看")
    return abs_path


def auto_encoding(path: str) -> str:
    """读取文件内容；无法确定编码或读取失败时返回 ''（调用方据此跳过）。

    与 read_text 的区别：不抛异常，适合批处理中跳过坏文件。
    注意返回 '' 无法区分「空文件」和「坏文件」，
    需要区分时请用 read_text 并捕获 UnknownEncodingError。
    """
    try:
        return read_text(path)
    except (UnknownEncodingError, OSError):
        return ""
