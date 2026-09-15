"""audit_skill.py — 文档一致性审计（防止文档漂移）

检查项：
1. 版本号三处一致（package.json / SKILL.md / README.md，复用 bump_version 的锚点）
2. SKILL.md 体积预算 —— 常驻核心超出预算即违背自身的「渐进读取」原则
3. Markdown 相对链接目标存在（SKILL.md / README.md / references/*.md / docs/*.md）
4. SKILL.md 核心原则条数 == README 核心原则表行数
5. 文档里引用的 scripts/*.py、scripts/*.ps1 均存在
6. F 模式陷阱表实际条数 == 文案中声明的「N 条陷阱」
7. SKILL.md / README.md 不出现宿主专属工具名（应只出现在 references/ 下）
8. 非规范 CJK 字符（康熙部首 / CJK 部首补充 / 兼容表意文字，视觉相同但码位不同，
   会导致搜索与精确匹配静默失败）

用法：
    python scripts/audit_skill.py [--root .] [--out audit_skill_result.txt]
退出码：0 无问题；1 发现问题。
"""

import argparse
import json
import os
import re
import sys

from bump_version import collect_versions
from safe_io import ensure_utf8_stdio, read_text, safe_print, safe_write

ensure_utf8_stdio()

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SKILL.md 常驻预算（字节）。超出说明细节又该外移到 references/。
SKILL_SIZE_BUDGET = 12 * 1024

CORE_DOCS = ('SKILL.md', 'README.md')
EXTRA_DOCS = ('CHANGELOG.md',)
MD_DIRS = ('references', 'docs')

# 宿主专属工具名：本仓库主体文档不应出现（细节归 references/tool-mapping.md）
HOST_SPECIFIC_TOKENS = (
    'search_content', 'directory_tree',
    'codegraph_context', 'codegraph_trace',
    'complete_step', 'multi_edit', 'autoresearch-evidence',
)

# 视觉相同、码位不同的 CJK 区间
WEIRD_CJK_RANGES = (
    (0x2E80, 0x2EFF, 'CJK 部首补充'),
    (0x2F00, 0x2FDF, '康熙部首'),
    (0xF900, 0xFAFF, 'CJK 兼容表意文字'),
    (0x2F800, 0x2FA1F, 'CJK 兼容表意文字补充'),
)

LINK_RE = re.compile(r'\[[^\]]*\]\(([^)\s]+)\)')
SCRIPT_REF_RE = re.compile(r'scripts/([A-Za-z0-9_]+\.(?:py|ps1))')
TRAP_COUNT_CLAIM_RE = re.compile(r'(\d+) 条(?:已知)?陷阱')
TRAP_TABLE_HEADING_RE = re.compile(r'^## 已知陷阱与解决方案（(\d+) 条）\s*$', re.M)
TRAP_ROW_RE = re.compile(r'^\|\s*(\d+)\s*\|', re.M)
PRINCIPLE_ITEM_RE = re.compile(r'^\d+\.\s+\*\*', re.M)
PRINCIPLE_ROW_RE = re.compile(r'^\|\s*\d+\s*\|', re.M)


def md_files(root: str):
    """收集需要审计的 Markdown 文件（相对路径，供报告使用）。"""
    found = []
    for rel in CORE_DOCS + EXTRA_DOCS:
        if os.path.exists(os.path.join(root, rel)):
            found.append(rel)
    for sub in MD_DIRS:
        directory = os.path.join(root, sub)
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            if name.lower().endswith('.md'):
                found.append(f'{sub}/{name}')
    return found


def extract_section(text: str, heading: str) -> str:
    """截取从 heading 行到下一个二级标题或分隔线之间的正文（找不到则返回 ''）。"""
    match = re.search(rf'^{re.escape(heading)}\s*$', text, re.M)
    if not match:
        return ''
    rest = text[match.end():]
    end = re.search(r'^(?:## |---\s*$)', rest, re.M)
    return rest[:end.start()] if end else rest


def find_weird_cjk(text: str):
    """返回 [（行号, 码位, 区间名）]，用于定位异体字。"""
    hits = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for ch in line:
            code = ord(ch)
            for low, high, name in WEIRD_CJK_RANGES:
                if low <= code <= high:
                    hits.append((lineno, code, name))
                    break
    return hits


def is_external_link(target: str) -> bool:
    return (target.startswith(('http://', 'https://', 'mailto:', '#'))
            or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) is not None)


def audit(root: str):
    """执行全部检查，返回（报告行列表, 问题列表）。"""
    problems = []
    notes = []
    docs = md_files(root)
    texts = {rel: read_text(os.path.join(root, rel)) for rel in docs}

    # 1. 版本三处一致
    versions = collect_versions(root)
    values = {v for _, v in versions if v}
    if len(values) == 1 and all(v for _, v in versions):
        notes.append(f'版本一致: {values.pop()}（package.json / SKILL.md / README.md）')
    else:
        rendered = ', '.join(f'{rel}={v or "<未找到>"}' for rel, v in versions)
        problems.append(f'[版本不一致] {rendered}')

    # 2. SKILL.md 体积预算
    skill_path = os.path.join(root, 'SKILL.md')
    size = os.path.getsize(skill_path)
    if size > SKILL_SIZE_BUDGET:
        problems.append(
            f'[体积超预算] SKILL.md {size} B > {SKILL_SIZE_BUDGET} B'
            '（细节应外移到 references/）')
    else:
        notes.append(f'SKILL.md 体积: {size} B / 预算 {SKILL_SIZE_BUDGET} B')

    # 3. 相对链接目标存在
    for rel in docs:
        base = os.path.dirname(os.path.join(root, rel))
        for target in LINK_RE.findall(texts[rel]):
            if is_external_link(target):
                continue
            path = os.path.normpath(os.path.join(base, target.split('#')[0]))
            if not os.path.exists(path):
                problems.append(f'[链接失效] {rel} -> {target}')

    # 4. 核心原则条数一致
    skill_items = len(PRINCIPLE_ITEM_RE.findall(
        extract_section(texts['SKILL.md'], '## 🧭 核心原则')))
    readme_rows = len(PRINCIPLE_ROW_RE.findall(
        extract_section(texts['README.md'], '## 🔑 核心原则（一句话版）')))
    if skill_items != readme_rows:
        problems.append(
            f'[原则条数不一致] SKILL.md={skill_items} 条，README.md={readme_rows} 行')
    else:
        notes.append(f'核心原则条数一致: {skill_items}')

    # 5. scripts/ 引用存在
    for rel in docs:
        for name in set(SCRIPT_REF_RE.findall(texts[rel])):
            if not os.path.exists(os.path.join(root, 'scripts', name)):
                problems.append(f'[脚本引用不存在] {rel} -> scripts/{name}')

    # 6. 陷阱表条数与文案声明一致
    trap_doc = 'references/windows-powershell.md'
    if trap_doc in texts:
        trap_text = texts[trap_doc]
        heading = TRAP_TABLE_HEADING_RE.search(trap_text)
        declared = int(heading.group(1)) if heading else None
        section = extract_section(trap_text, f'## 已知陷阱与解决方案（{declared} 条）'
                                  if declared else '## 已知陷阱与解决方案')
        actual = len(TRAP_ROW_RE.findall(section))
        if declared != actual:
            problems.append(
                f'[陷阱条数不一致] {trap_doc} 标题声明 {declared} 条，表内实为 {actual} 条')
        for rel in CORE_DOCS:
            for claim in set(TRAP_COUNT_CLAIM_RE.findall(texts[rel])):
                if int(claim) != actual:
                    problems.append(
                        f'[陷阱条数不一致] {rel} 文案写 {claim} 条，'
                        f'实际 {actual} 条（见 {trap_doc}）')
        if declared == actual:
            notes.append(f'F 模式陷阱条数一致: {actual}')

    # 7. 宿主专属工具名不应出现在核心文档
    for rel in CORE_DOCS:
        for token in HOST_SPECIFIC_TOKENS:
            if token in texts[rel]:
                problems.append(
                    f'[宿主专属工具名] {rel} 含 {token}'
                    '（应移入 references/tool-mapping.md）')

    # 8. 非规范 CJK 字符
    for rel in docs:
        for lineno, code, name in find_weird_cjk(texts[rel]):
            problems.append(
                f'[异体字] {rel}:{lineno} U+{code:04X} ({name}) — 视觉相同但码位不同，'
                '搜索/匹配会静默失败')

    return notes, problems


def main() -> int:
    parser = argparse.ArgumentParser(description='Skill 文档一致性审计')
    parser.add_argument('--root', default=REPO_ROOT)
    parser.add_argument('--out', default=None,
                        help='可选：把报告写入该文件（UTF-8）')
    parser.add_argument('--json', action='store_true',
                        help='输出 JSON（供 AI / CI 解析；中文按 Unicode 原样输出）')
    args = parser.parse_args()

    notes, problems = audit(args.root)
    ok = not problems

    if args.json:
        payload = json.dumps({
            'ok': ok,
            'root': os.path.abspath(args.root),
            'notes': notes,
            'problems': problems,
        }, ensure_ascii=False, indent=2)
        if args.out:
            safe_write(args.out, payload + '\n')
            safe_print(f'JSON 报告已写入: {os.path.abspath(args.out)}')
        else:
            safe_print(payload)
        return 0 if ok else 1

    lines = ['=' * 60, 'Skill 文档一致性审计', f'仓库根目录: {os.path.abspath(args.root)}',
             '=' * 60]
    lines.extend(f'  {n}' for n in notes)
    lines.append('')
    if problems:
        lines.append(f'发现问题 {len(problems)} 项:')
        lines.extend(f'  {p}' for p in problems)
    else:
        lines.append('未发现问题。')

    report = '\n'.join(lines) + '\n'
    for line in lines:
        safe_print(line)
    if args.out:
        safe_write(args.out, report)
        safe_print(f'报告已写入: {os.path.abspath(args.out)}')

    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
