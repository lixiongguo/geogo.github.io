#!/usr/bin/env python3
"""统计指定文件夹下所有 .md 文章的字数。"""
from __future__ import annotations

import os
import re
import sys


def count_chinese(text: str) -> int:
    return len(re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', text))


def count_files(folder: str, ext: str = '.md') -> None:
    folder = os.path.abspath(folder)
    files = sorted(f for f in os.listdir(folder) if f.endswith(ext))
    if not files:
        print(f'未找到 {ext} 文件')
        return

    print(f'{"#":>3}  {"文件名":<45} {"总字符":>8} {"中文":>8}')
    print('-' * 68)
    total_all = total_cjk = 0
    for i, f in enumerate(files, 1):
        path = os.path.join(folder, f)
        with open(path, 'r', encoding='utf-8') as fh:
            text = fh.read()
        total = len(text)
        cjk = count_chinese(text)
        total_all += total
        total_cjk += cjk
        print(f'{i:>3}  {f:<45} {total:>8} {cjk:>8}')
    print('-' * 68)
    print(f'  {"合计":<45} {total_all:>8} {total_cjk:>8}')


def main() -> int:
    if len(sys.argv) < 2:
        print('用法: python count_words.py <文件夹路径>')
        return 1
    count_files(sys.argv[1])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
