#!/usr/bin/env python3
"""检查 markdown 文件中的公式编辑规范问题"""
import re, sys
from pathlib import Path

def check_file(filepath):
    text = Path(filepath).read_text('utf-8')
    issues = []
    lines = text.split('\n')

    # 1. $ 与中文紧邻 (排除 $$)
    for m in re.finditer(r'[\u4e00-\u9fff]\$[^\$]|\$[^\$][\u4e00-\u9fff]', text):
        ln = text[:m.start()].count('\n') + 1
        issues.append(f"  L{ln}: $ 前后缺少空格")

    # 2. $...$ 含中文 (不含已经在 \text{...} 中的)
    for m in re.finditer(r'(?<!\$)\$(?!\$)((?:(?!\$).)+?)\$(?!\$)', text):
        body = m.group(1)
        body_no_text = re.sub(r'\\text\{[^}]*\}', '', body)
        if re.search(r'[\u4e00-\u9fff]', body_no_text):
            ln = text[:m.start()].count('\n') + 1
            issues.append(f"  L{ln}: 行内公式含中文 (应移到外部或用 \\text{{...}})")

    # 3. $ 内的 \begin{cases}
    for m in re.finditer(r'(?<!\$)\$(?!\$)(.+?)\\begin\{cases\}(.+?)\$(?!\$)', text, re.DOTALL):
        ln = text[:m.start()].count('\n') + 1
        issues.append(f"  L{ln}: \\begin{{cases}} 在行内公式中 (应改为 $$ 块)")

    # 4. $$ 块有空行
    for m in re.finditer(r'\$\$(.+?)\$\$', text, re.DOTALL):
        body = m.group(1)
        if '\n\n' in body:
            ln = text[:m.start()].count('\n') + 1
            issues.append(f"  L{ln}: $$ 块内存在空行")

    # 5. \sub 裸用
    for m in re.finditer(r'\\sub(?![a-zA-Z])', text):
        s = m.group()
        if not s.startswith(('\\subsection', '\\substack', '\\subset', '\\subseteq')):
            ln = text[:m.start()].count('\n') + 1
            issues.append(f"  L{ln}: \\sub 非标准命令 (请用 \\subset)")

    # 6. 双重包裹 \(\$)
    for m in re.finditer(r'\\\(\$[^$]*\$\\\)', text):
        ln = text[:m.start()].count('\n') + 1
        issues.append(f"  L{ln}: \\(\\) 与 $ 双重包裹 (二选一即可)")

    # 7. $$ 不成对
    dollar_count = 0
    in_block = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('$$') and len(stripped) > 2:
            # $$ ... $$ on same line
            pass
        elif stripped == '$$':
            in_block = not in_block
    if in_block:
        issues.append(f"  EOF: $$ 未配对")

    return issues

if __name__ == '__main__':
    import glob
    if len(sys.argv) < 2:
        print("用法: python check_math.py <file.md> 或 python check_math.py --all <dir>")
        sys.exit(1)

    if sys.argv[1] == '--all':
        root = sys.argv[2] if len(sys.argv) > 2 else '.'
        files = glob.glob(f'{root}/**/*.md', recursive=True)
        total_issues = 0
        files_with_issues = 0
        for f in sorted(files):
            issues = check_file(f)
            if issues:
                files_with_issues += 1
                total_issues += len(issues)
                print(f"\n📋 {f}: {len(issues)} 个问题")
                for issue in issues:
                    print(issue)
        print(f"\n{'='*60}")
        print(f"总计: {files_with_issues}/{len(files)} 个文件有问题, 共 {total_issues} 处")
    else:
        issues = check_file(sys.argv[1])
        if issues:
            print(f"📋 {sys.argv[1]}: 发现 {len(issues)} 个问题")
            for i in issues:
                print(i)
        else:
            print(f"✅ {sys.argv[1]}: 通过检查")
