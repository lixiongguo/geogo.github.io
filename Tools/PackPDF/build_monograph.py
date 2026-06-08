#!/usr/bin/env python3
"""整本专著 .md -> PDF（pandoc + tectonic）

用法:
    python build_monograph.py              # 含图片
    python build_monograph.py --no-img     # 无图片，快速生成
    python build_monograph.py -o out.pdf   # 指定输出路径
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from packpdf.monograph import build_monograph_pdf, default_posts_dir, repo_root


def main() -> int:
    parser = argparse.ArgumentParser(description='构建参数化算法整本专著 PDF')
    parser.add_argument('--no-img', action='store_true', help='不含图片，快速生成')
    parser.add_argument('-o', '--output', help='输出 PDF 路径')
    parser.add_argument('--posts-dir', help='文章根目录（默认 _posts/1.Parameterization）')
    args = parser.parse_args()

    posts = Path(args.posts_dir) if args.posts_dir else default_posts_dir()
    output = Path(args.output) if args.output else repo_root() / '参数化算法专著.pdf'

    if not posts.is_dir():
        print(f'[错误] 目录不存在: {posts}', file=sys.stderr)
        return 1

    try:
        build_monograph_pdf(
            posts_dir=posts,
            output=output,
            include_images=not args.no_img,
        )
        return 0
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
