"""Regression tests for audit_encoding (编码合规审计).

Run: python scripts/test_audit_encoding.py
Covers:
- BOM 规则：.ps1 必须带 BOM，其余文本必须无 BOM
- 合规目录 -> 退出码 0；注入 BOM 违规 -> 退出码 1 且命中 [缺少BOM] / [意外BOM]
"""

import contextlib
import io
import json
import os
import sys
import tempfile

from audit_encoding import main
from safe_io import read_text, safe_write


def run_audit(root, out):
    old_argv = sys.argv
    sys.argv = ['audit_encoding.py', '--root', root, '--json', '--out', out]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return main()
    finally:
        sys.argv = old_argv


def run() -> None:
    with tempfile.TemporaryDirectory() as root:
        # 合规：.ps1 带 BOM，.md 无 BOM
        with open(os.path.join(root, 'ok.ps1'), 'wb') as f:
            f.write(b'\xef\xbb\xbf' + '写中文'.encode('utf-8'))
        safe_write(os.path.join(root, 'ok.md'), '中文内容\n')

        out = os.path.join(root, 'report.json')
        assert run_audit(root, out) == 0
        payload = json.loads(read_text(out))
        assert payload['ok'] is True, payload

        # 违规：.ps1 无 BOM，.md 带 BOM
        with open(os.path.join(root, 'bad.ps1'), 'wb') as f:
            f.write('no bom'.encode('utf-8'))
        with open(os.path.join(root, 'bad.md'), 'wb') as f:
            f.write(b'\xef\xbb\xbf' + '带BOM的md'.encode('utf-8'))

        assert run_audit(root, out) == 1
        payload = json.loads(read_text(out))
        joined = '\n'.join(payload['problems'])
        assert '[缺少BOM] bad.ps1' in joined, joined
        assert '[意外BOM] bad.md' in joined, joined

    print('test_audit_encoding: all assertions passed')


if __name__ == '__main__':
    run()
