#!/usr/bin/env python3
"""PackPDF 命令行入口。"""

from __future__ import annotations

import argparse
import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from packpdf.core import merge_to_pdf
from packpdf.deps import check_deps, format_deps_report


def main() -> int:
    parser = argparse.ArgumentParser(description='将 Markdown 目录合并打包为 PDF')
    parser.add_argument('folder', nargs='?', help='包含 .md 文件的目录')
    parser.add_argument('output', nargs='?', help='输出 PDF 路径')
    parser.add_argument('title', nargs='?', default='合集', help='文档标题')
    parser.add_argument('--single-chapter', action='store_true', help='单章模式')
    parser.add_argument('--check-deps', action='store_true', help='仅检测依赖')
    args = parser.parse_args()

    if args.check_deps or not args.folder:
        print(format_deps_report(check_deps()))
        if not args.folder:
            parser.print_help()
            return 0 if args.check_deps else 1

    if not args.output:
        parser.error('需要指定输出 PDF 路径')

    result = merge_to_pdf(
        args.folder,
        args.output,
        args.title,
        single_chapter=args.single_chapter,
    )
    if not result.success:
        print(result.error, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
