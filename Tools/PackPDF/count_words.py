#!/usr/bin/env python3
"""统计指定文件夹下所有 .md 文章的字数。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from packpdf.word_count import count_directory  # noqa: E402


def count_files(folder: str) -> None:
    result = count_directory(folder, recursive=False)
    if not result.files:
        print('未找到 .md 文件')
        return

    print(f'{"#":>3}  {"文件名":<45} {"总字符":>8} {"中文":>8}')
    print('-' * 68)
    for i, fr in enumerate(result.files, 1):
        name = Path(fr.path).name
        print(f'{i:>3}  {name:<45} {fr.chars:>8} {fr.cjk:>8}')
    print('-' * 68)
    print(f'  {"合计":<45} {result.total_chars:>8} {result.total_cjk:>8}')


def main() -> int:
    if len(sys.argv) < 2:
        print('用法: python count_words.py <文件夹路径>')
        return 1
    count_files(sys.argv[1])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
