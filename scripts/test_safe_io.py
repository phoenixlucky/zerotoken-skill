"""Regression tests for safe_io encoding detection and fallbacks.

Run: python scripts/test_safe_io.py
Covers the v1.11.0 refactor contract:
- sniff_encoding: BOM / utf-8 / gb18030 / unknown
- decode_bytes: unknown raises UnknownEncodingError (no silent replace)
- read_text strict vs non-strict
- safe_write / safe_append: UTF-8 no BOM, LF, append newline fix-up
- write_result round-trip
"""

import os
import tempfile

from safe_io import (UnknownEncodingError, decode_bytes, read_text,
                     safe_append, safe_read, safe_write, sniff_encoding,
                     write_result)

TEXT = "中文内容 emoji 🧭 end"


def expect_raises(exc_type, fn):
    try:
        fn()
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__} was not raised")


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        # ── sniff_encoding ────────────────────────────────
        assert sniff_encoding(TEXT.encode("utf-8")) == "utf-8"
        assert sniff_encoding(b"\xef\xbb\xbf" + TEXT.encode("utf-8")) == "utf-8-sig"
        assert sniff_encoding(b"\xff\xfe" + TEXT.encode("utf-16-le")) == "utf-16-le"
        assert sniff_encoding(b"\xfe\xff" + TEXT.encode("utf-16-be")) == "utf-16-be"
        assert sniff_encoding(b"\xff\xfe\x00\x00" + TEXT.encode("utf-32-le")) == "utf-32-le"
        assert sniff_encoding(TEXT.encode("gb18030")) == "gb18030"
        assert sniff_encoding(b"\x81\x40\xff\xff") == "unknown"

        # ── decode_bytes: BOM stripped, no U+FEFF residue ─
        for name, raw in {
            "utf-16 codec": TEXT.encode("utf-16"),                      # 自带 LE BOM
            "utf-16 le+bom": b"\xff\xfe" + TEXT.encode("utf-16-le"),
            "utf-16 be+bom": b"\xfe\xff" + TEXT.encode("utf-16-be"),
            "utf-32 codec": TEXT.encode("utf-32"),                      # 自带 LE BOM
            "utf-32 le+bom": b"\xff\xfe\x00\x00" + TEXT.encode("utf-32-le"),
        }.items():
            assert decode_bytes(raw) == TEXT, f"BOM residue for {name}"
        assert decode_bytes(TEXT.encode("utf-8")) == TEXT
        assert decode_bytes(TEXT.encode("gb18030")) == TEXT
        expect_raises(UnknownEncodingError,
                      lambda: decode_bytes(b"\x81\x40\xff\xff"))

        # ── files: utf-8 / BOM / gb18030 / broken ─────────
        u8 = os.path.join(directory, "u8.txt")
        bom = os.path.join(directory, "bom.txt")
        gb = os.path.join(directory, "gb.txt")
        bad = os.path.join(directory, "bad.bin")
        with open(u8, "wb") as f:
            f.write(TEXT.encode("utf-8"))
        with open(bom, "wb") as f:
            f.write(b"\xef\xbb\xbf" + TEXT.encode("utf-8"))
        with open(gb, "wb") as f:
            f.write(TEXT.encode("gb18030"))
        with open(bad, "wb") as f:
            f.write(b"\x81\x40\xff\xff")

        for p in (u8, bom, gb):
            assert read_text(p) == TEXT, p
            assert safe_read(p) == TEXT, p  # backward-compatible alias
        expect_raises(UnknownEncodingError, lambda: read_text(bad))
        # non-strict: view-only mode may replace, but must never equal garbage-free TEXT
        assert isinstance(read_text(bad, strict=False), str)

        # ── safe_write / safe_append: no BOM, LF ──────────
        out = os.path.join(directory, "out.md")
        safe_write(out, "第一行")
        safe_append(out, "第二行")
        with open(out, "rb") as f:
            data = f.read()
        assert not data.startswith(b"\xef\xbb\xbf"), "BOM must not be written"
        assert b"\r\n" not in data, "LF only"
        assert data.decode("utf-8") == "第一行\n第二行\n", \
            "append must add missing newline between segments"

        # ── write_result round-trip ───────────────────────
        res = os.path.join(directory, "res.txt")
        path = write_result("PASS ✓ 中文", out_path=res)
        assert os.path.isabs(path)
        assert read_text(res) == "PASS ✓ 中文\n"

    print("test_safe_io: all assertions passed")


if __name__ == "__main__":
    main()
