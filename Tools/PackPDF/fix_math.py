#!/usr/bin/env python3
"""批量修复 markdown 文件的常见公式规范问题。"""
from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from packpdf.math_fix import fix_directory, fix_file


def main() -> int:
    if len(sys.argv) < 2:
        print('用法: python fix_math.py <目录路径>')
        return 1

    root = Path(sys.argv[1])
    if root.is_file():
        ok, changes = fix_file(root)
        if ok:
            print(f'[已修复] {root}')
            for c in changes:
                print(f'  - {c}')
        else:
            print(f'[无变化] {root}')
        return 0

    result = fix_directory(root, recursive=False)
    for path, changes in result.details:
        print(f'[已修复] {path}')
        for c in changes:
            print(f'  - {c}')
    for _ in range(result.unchanged_files):
        pass
    print(f'\n共修复 {result.fixed_files}/{result.scanned} 个文件')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
