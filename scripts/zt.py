"""zt.py — ZeroToken 统一命令入口

把 scripts/ 下的工具收敛成一条命令，参数**原样透传**给对应脚本
（因此 zt.py 不需要重复定义任何参数，也就不会与子脚本漂移）：

    python scripts/zt.py <命令> [原脚本参数...]

常用：
    python scripts/zt.py check                一键校验（回归测试 + 编码审计 + 文档一致性 + 版本联动）
    python scripts/zt.py env                  识别系统参数（写 .zerotoken/environment.json）
    python scripts/zt.py audit --json         文档一致性审计（JSON 供 AI / CI 解析）
    python scripts/zt.py encoding --json      编码合规审计
    python scripts/zt.py version 1.14.0       版本号三处联动（空参=只校验）

设计约束：
- 子进程用 sys.executable + 绝对脚本路径 + 参数列表（不经 shell），
  cwd 固定为仓库根 —— 从任何目录调用都能工作，也绕开 PowerShell 引号 / GBK 问题。
- 不带参数、`help`、`-h` 都打印命令表；未知命令打印命令表并返回 2。
- 原脚本仍可独立调用：zt.py 只是转发。
"""

import json
import os
import subprocess
import sys
import tempfile

from safe_io import ensure_utf8_stdio, safe_print, safe_write

ensure_utf8_stdio()

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO_ROOT, 'scripts')

# 命令 -> (目标脚本, 一句话说明, 示例)
COMMANDS = {
    'env': ('detect_env.py',
            '识别系统参数（OS/Shell/控制台编码/中文支持/PS 版本）并保存 7 天缓存',
            ('python scripts/zt.py env', 'python scripts/zt.py env --force')),
    'audit': ('audit_skill.py',
              '文档一致性审计：体积/链接/计数/脚本引用/异体字',
              ('python scripts/zt.py audit',
               'python scripts/zt.py audit --json --out audit_skill.json')),
    'encoding': ('audit_encoding.py',
                 '编码合规审计：UTF-8 / 替换字符 / 混合换行',
                 ('python scripts/zt.py encoding',
                  'python scripts/zt.py encoding --json')),
    'version': ('bump_version.py',
                '版本号三处联动（package.json / SKILL.md / README）：空参=校验，带版本号=写入',
                ('python scripts/zt.py version',
                 'python scripts/zt.py version 1.14.0')),
    'gbk': ('detect_gbk_contamination.py',
            'GBK 污染检测与修复（scan / inspect / fix）',
            ('python scripts/zt.py gbk scan .',
             'python scripts/zt.py gbk fix . --backup --preview')),
    'convert': ('fix_encoding.py',
                '批量编码转换（scan / preview / convert / check-replacement）',
                ('python scripts/zt.py convert scan .',
                 'python scripts/zt.py convert convert . --backup')),
    'edit': ('batch_edit.py',
             '同一文件多处替换（宿主编辑工具阻塞时的备用路径）',
             ('python scripts/zt.py edit notes.md replacements.json',)),
    'verify': ('verify_output.py',
               '验证结果写入 .txt（避免终端中文乱码，供 read_file 读取）',
               ('python scripts/zt.py verify "检查项" out.txt --pass "✓ 通过"',)),
}

# check 的步骤：(说明, 脚本, 参数)
CHECK_STEPS = (
    ('回归测试：safe_io 编码检测', 'test_safe_io.py', ()),
    ('回归测试：detect_env 环境探测', 'test_detect_env.py', ()),
    ('回归测试：bump_version 版本联动', 'test_bump_version.py', ()),
    ('编码合规审计', 'audit_encoding.py', None),   # None -> 运行时注入临时 --out
    ('文档一致性审计', 'audit_skill.py', ()),
    ('版本号三处联动', 'bump_version.py', ('--check',)),
)

OUTPUT_LIMIT = 4000


def run_script(script, args, capture=False):
    """运行 scripts/<script>，返回 (退出码, 捕获输出)。

    capture=True 时把 stdout/stderr 收进内存（供 JSON 报告携带失败原因）；
    解码用 backslashreplace —— 不静默丢字节，也无法编码的字节以转义形式保留。
    """
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, script), *args]
    if not capture:
        try:
            return subprocess.run(cmd, cwd=REPO_ROOT).returncode, ''
        except OSError as exc:
            safe_print(f'[zt] 无法执行 {script}: {exc}')
            return 3, ''

    try:
        proc = subprocess.run(cmd, cwd=REPO_ROOT, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
    except OSError as exc:
        return 3, f'无法执行 {script}: {exc}'
    output = (proc.stdout or b'').decode('utf-8', errors='backslashreplace')
    return proc.returncode, output


def write_or_print_json(payload, out_path):
    """JSON 打到 stdout，或（--out）写 UTF-8 文件供 read_file 读取。"""
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if out_path:
        safe_write(out_path, text + '\n')
        safe_print(f'JSON 报告已写入: {os.path.abspath(out_path)}')
    else:
        safe_print(text)


def parse_json_out(argv):
    """拆出 --json / --out（其余参数原样返回）。"""
    json_mode, out_path, rest = False, None, []
    it = iter(argv)
    for arg in it:
        if arg == '--json':
            json_mode = True
        elif arg == '--out':
            try:
                out_path = next(it)
            except StopIteration:
                return None, None, None      # 缺值 -> 调用方报错
        else:
            rest.append(arg)
    return json_mode, out_path, rest


def run_check(argv) -> int:
    json_mode, out_path, rest = parse_json_out(argv)
    if json_mode is None:
        safe_print('[zt] --out 需要一个文件路径')
        return 2
    if rest:
        safe_print(f'[zt] check 不认识的参数: {" ".join(rest)}'
                   '（支持 --json / --out <文件>）')
        return 2

    total = len(CHECK_STEPS)
    ok = True
    steps = []
    with tempfile.TemporaryDirectory(prefix='zt-check-') as tmp:
        for index, (name, script, extra) in enumerate(CHECK_STEPS, start=1):
            args = list(extra) if extra is not None else [
                '--root', '.', '--out', os.path.join(tmp, 'audit_result.txt')]
            if not json_mode:
                safe_print(f'[{index}/{total}] {name} ...')
            code, output = run_script(script, args, capture=json_mode)
            step = {'name': name, 'script': script, 'exit': code}
            if code != 0:
                ok = False
                if json_mode:
                    step['output'] = output[-OUTPUT_LIMIT:]
                    if output:
                        safe_print(f'[{index}/{total}] {name} 输出:\n{output}')
                else:
                    safe_print(f'[{index}/{total}] {name} -> 失败（退出码 {code}）')
                steps.append(step)
                break
            if not json_mode:
                safe_print(f'[{index}/{total}] {name} -> OK')
            steps.append(step)

    if json_mode:
        write_or_print_json({'ok': ok, 'repo': REPO_ROOT, 'steps': steps}, out_path)
    elif ok:
        safe_print(f'全部通过（{total} 步）。')
    else:
        safe_print(f'失败步骤: {steps[-1]["name"]} —— 见上方输出。')
    return 0 if ok else 1


def run_init() -> int:
    safe_print('PowerShell 会话初始化（点引用无法由 Python 转发，请手动执行）：')
    safe_print('    . ./scripts/init_env.ps1')
    safe_print('（PowerShell 在 .zerotoken/environment.json 中探测到，POSIX 系统无需此步）')
    return 0


def build_help() -> str:
    lines = [
        'zt.py — ZeroToken 统一命令入口',
        '',
        '用法: python scripts/zt.py <命令> [参数...]',
        '',
        '常用:',
        '  check [--json] [--out 文件]  一键校验：回归测试 + 编码审计 + 文档一致性 + 版本联动',
        '  env [--force]                识别系统参数（写 .zerotoken/environment.json，7 天缓存）',
        '  audit [--json]               文档一致性审计（体积 / 链接 / 计数 / 脚本引用 / 异体字）',
        '  encoding [--json]            编码合规审计（UTF-8 / 替换字符 / 混合换行）',
        '  version [x.y.z]              版本号三处联动：空参=校验，带版本号=写入',
        '',
        '按需:',
        '  gbk scan|inspect|fix [路径]      GBK 污染检测 / 修复',
        '  convert scan|preview|convert [目录]  批量编码转换',
        '  edit <文件> <替换.json>          同一文件多处替换',
        '  verify "<检查项>" <out.txt>      验证结果写入 .txt',
        '  init                            打印 PowerShell 初始化命令',
        '',
        '参数原样透传给 scripts/<脚本>；看子命令帮助：python scripts/zt.py audit --help',
        '机器可读输出：python scripts/zt.py check --json --out zt.json',
    ]
    return '\n'.join(lines)


def main() -> int:
    argv = sys.argv[1:]
    if not argv or argv[0] in ('help', '-h', '--help'):
        safe_print(build_help())
        return 0

    name, rest = argv[0], argv[1:]

    if name == 'check':
        return run_check(rest)
    if name == 'init':
        return run_init()

    spec = COMMANDS.get(name)
    if spec is None:
        safe_print(f'[zt] 未知命令: {name}\n')
        safe_print(build_help())
        return 2

    return run_script(spec[0], rest)[0]


if __name__ == '__main__':
    sys.exit(main())
