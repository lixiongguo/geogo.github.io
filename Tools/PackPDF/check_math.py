#!/usr/bin/env python3
"""Markdown 公式规范检查（CLI）。"""
from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from packpdf.math_check import check_directory, check_file, get_check_rules


def main() -> int:
    if len(sys.argv) < 2:
        print('用法:')
        print('  python check_math.py --rules          # 列出检查依据')
        print('  python check_math.py <file.md>')
        print('  python check_math.py --all <dir>')
        return 1

    if sys.argv[1] == '--rules':
        for rule in get_check_rules():
            print(f'\n{rule.title}')
            print(f'  {rule.description}')
            print(f'  错误: {rule.wrong}')
            print(f'  正确: {rule.correct}')
        return 0

    if sys.argv[1] == '--all':
        root = sys.argv[2] if len(sys.argv) > 2 else '.'
        result = check_directory(root)
        for fr in result.files:
            print(f'\n[检查] {fr.path}: {len(fr.issues)} 个问题')
            for issue in fr.issues:
                print(f'  {issue.format_short()}')
        print(f"\n{'=' * 60}")
        print(f'总计: {result.files_with_issues}/{result.total_files} 个文件有问题, 共 {result.total_issues} 处')
        return 0

    issues = check_file(sys.argv[1])
    if issues:
        print(f'[检查] {sys.argv[1]}: 发现 {len(issues)} 个问题')
        for i in issues:
            print(f'  {i.format_short()}')
        return 1
    print(f'[通过] {sys.argv[1]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
