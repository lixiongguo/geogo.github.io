#!/usr/bin/env python3
"""检查 _posts/ 中 {% post_url %} 引用是否断裂（CLI）。"""

from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from packpdf.post_check import check_directory, check_file


def main() -> int:
    if len(sys.argv) < 2:
        print('用法:')
        print('  python check_posts.py <file.md>        # 检查单文件')
        print('  python check_posts.py --all <dir>      # 检查整个目录')
        return 1

    if sys.argv[1] == '--all':
        root = sys.argv[2] if len(sys.argv) > 2 else '.'
        result = check_directory(root)
        for fr in result.files:
            if fr.ok:
                continue
            print(f'\n[断裂] {fr.path}: {len(fr.broken)} 处')
            for i, br in enumerate(fr.broken, 1):
                ref = br.ref
                print(f'  第{ref.line}行: post_url "{ref.slug}"')
                if br.suggestion:
                    print(f'             建议 → {br.suggestion}')
        print(f"\n{'=' * 60}")
        print(f'总计: {result.files_with_issues}/{result.total_files} 文件有断裂引用, 共 {result.total_broken} 处')
        return 1 if result.total_broken > 0 else 0

    broken = check_file(sys.argv[1])
    if broken:
        print(f'[断裂] {sys.argv[1]}: 发现 {len(broken)} 处')
        for i, br in enumerate(broken, 1):
            ref = br.ref
            print(f'  第{ref.line}行: post_url "{ref.slug}"')
            if br.suggestion:
                print(f'             建议 → {br.suggestion}')
        return 1
    print(f'[通过] {sys.argv[1]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
