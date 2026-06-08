#!/usr/bin/env python3
"""批量修复 markdown 文件的常见公式规范问题。"""
from __future__ import annotations

import glob
import re
import sys
from pathlib import Path


def fix_file(filepath: str | Path) -> bool:
    text = Path(filepath).read_text('utf-8')
    original = text
    segments = re.split(r'(\$\$.+?\$\$)', text, flags=re.DOTALL)

    for i, seg in enumerate(segments):
        if seg.startswith('$$') and seg.endswith('$$'):
            body = seg[2:-2]
            body = re.sub(r'\n\s*\n', '\n', body)
            body = re.sub(r'\\sub(?=\s|\{|\[)(?!section|stack|set)', r'\\subset', body)
            segments[i] = '$$' + body + '$$'
        else:
            seg = re.sub(r'([\u4e00-\u9fff])\$(?!\$)', r'\1 $', seg)
            seg = re.sub(r'(?<!\$)\$(?!\$)([\u4e00-\u9fff])', r'$ \1', seg)
            segments[i] = seg

    text = ''.join(segments)
    if text != original:
        Path(filepath).write_text(text, 'utf-8')
        return True
    return False


def main() -> int:
    if len(sys.argv) < 2:
        print('用法: python fix_math.py <目录路径>')
        return 1

    root = sys.argv[1]
    files = sorted(glob.glob(f'{root}/*.md'))
    if not files:
        print(f'未找到 .md 文件: {root}')
        return 1

    fixed = 0
    for f in files:
        if fix_file(f):
            print(f'[已修复] {f}')
            fixed += 1
        else:
            print(f'[无变化] {f}')
    print(f'\n共修复 {fixed}/{len(files)} 个文件')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
