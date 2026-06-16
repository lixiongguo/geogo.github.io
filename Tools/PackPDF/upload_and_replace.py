#!/usr/bin/env python3
"""
一键上传并替换：扫描 _posts/ 中所有本地图片 → 上传 OSS → 替换路径。

用法:
    python3 scripts/upload_and_replace.py          # 实际执行
    python3 scripts/upload_and_replace.py --dry    # 仅预览
"""

import re
import os
import sys
import time
import json
import urllib.parse
from pathlib import Path
from collections import defaultdict

try:
    import oss2
except ImportError:
    print("请先安装 oss2: pip install oss2")
    sys.exit(1)

# ========== 配置 ==========
AK = os.environ.get('OSS_ACCESS_KEY_ID', '')
SK = os.environ.get('OSS_ACCESS_KEY_SECRET', '')
if not AK or not SK:
    print("请设置环境变量 OSS_ACCESS_KEY_ID 和 OSS_ACCESS_KEY_SECRET")
    sys.exit(1)
OSS_BASE = "https://lgximgs.oss-cn-beijing.aliyuncs.com/images/"
ROOT = Path(__file__).resolve().parent.parent.parent
POSTS_DIR = ROOT / "_posts"
IMGS_DIR = ROOT / "imgs"

# ========== 正则 ==========
MD_IMG = re.compile(r'(!\[[^\]]*\])\(([^)]*imgs[/\\][^)]+)\)', re.IGNORECASE)
HTML_IMG = re.compile(r'(<img\s[^>]*src=["\'])([^"\']*imgs[/\\][^"\']+)(["\'][^>]*>)', re.IGNORECASE)
OSS_URL = re.compile(r'https?://lgximgs\.oss-cn-beijing\.aliyuncs\.com/images/', re.IGNORECASE)

CT = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
      '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml'}


def extract_filename(path_str):
    normalized = path_str.replace('\\', '/')
    idx = normalized.find('imgs/')
    if idx == -1:
        return None
    return normalized[idx + 5:].lstrip('/')


def is_local(path_str):
    s = path_str.strip()
    return not bool(OSS_URL.match(s) or s.startswith('http://') or s.startswith('https://'))


def collect_local_images():
    """扫描 _posts/ 下所有 md 文件，收集本地图片引用。"""
    images = {}  # filename -> [(file, old_path)]
    for md in sorted(POSTS_DIR.rglob('*.md')):
        content = md.read_text(encoding='utf-8')
        for pattern in [MD_IMG, HTML_IMG]:
            for m in pattern.finditer(content):
                path_str = m.group(2)
                if not is_local(path_str):
                    continue
                fn = extract_filename(path_str)
                if not fn:
                    continue
                images.setdefault(fn, []).append((md, path_str))
    return images


def upload_images(filenames):
    """上传图片到 OSS，跳过已存在的。返回成功上传的集合。"""
    auth = oss2.Auth(AK, SK)
    bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'lgximgs')
    uploaded = set()
    total = len(filenames)

    for i, fn in enumerate(filenames):
        lp = IMGS_DIR / fn
        if not lp.exists():
            print(f"[{i+1}/{total}] SKIP_MISS {fn}")
            continue

        # 检查 OSS 是否已有
        try:
            bucket.head_object('images/' + fn)
            print(f"[{i+1}/{total}] EXIST {fn}")
            uploaded.add(fn)
            continue
        except oss2.exceptions.NoSuchKey:
            pass

        ct = CT.get(lp.suffix.lower(), 'application/octet-stream')
        for attempt in range(4):
            try:
                bucket.put_object_from_file('images/' + fn, str(lp), headers={'Content-Type': ct})
                print(f"[{i+1}/{total}] OK {fn}")
                uploaded.add(fn)
                break
            except Exception as e:
                if attempt < 3:
                    time.sleep(2 ** attempt)
                else:
                    print(f"[{i+1}/{total}] FAIL {fn}: {e}")

        if (i + 1) % 20 == 0:
            time.sleep(0.5)

    return uploaded


def replace_in_file(filepath, replacements):
    """替换文件中指定路径为 OSS URL。"""
    content = filepath.read_text(encoding='utf-8')
    for old_path, fn in replacements:
        encoded = urllib.parse.quote(fn, safe='-_.~!$&\'()*+,;=@')
        new_url = OSS_BASE + encoded
        content = content.replace(old_path, new_url)
    filepath.write_text(content, encoding='utf-8')


def main():
    dry_run = '--dry' in sys.argv

    print("=" * 60)
    print("  扫描 _posts/ 中的本地图片引用...")
    print("=" * 60)

    images = collect_local_images()
    if not images:
        print("未发现需要处理的本地图片。")
        return

    print(f"发现 {len(images)} 张唯一本地图片，涉及 {sum(len(v) for v in images.values())} 处引用。\n")

    if dry_run:
        for fn, refs in sorted(images.items()):
            print(f"  {fn}:")
            for md, old_path in refs:
                print(f"    → {old_path}")
                new_url = OSS_BASE + urllib.parse.quote(fn, safe='-_.~!$&\'()*+,;=@')
                print(f"      {new_url}")
            print()
        print("--dry 模式，未实际修改。")
        return

    # 上传
    print("=" * 60)
    print("  上传图片到 OSS...")
    print("=" * 60)
    uploaded = upload_images(sorted(images.keys()))
    failed = [fn for fn in images if fn not in uploaded]

    if failed:
        print(f"\n⚠ 以下图片上传失败，将跳过替换：")
        for fn in failed:
            print(f"  - {fn}")

    # 替换
    print(f"\n{'=' * 60}")
    print(f"  替换 .md 文件中的路径...")
    print("=" * 60)

    replaced_count = 0
    for fn in sorted(uploaded):
        for md, old_path in images[fn]:
            replace_in_file(md, [(old_path, fn)])
            replaced_count += 1
            encoded = urllib.parse.quote(fn, safe='-_.~!$&\'()*+,;=@')
            print(f"  ✓ {md.relative_to(ROOT)}: {old_path} → {OSS_BASE}{encoded}")

    print(f"\n完成：上传 {len(uploaded)} 张，替换 {replaced_count} 处引用。")


if __name__ == '__main__':
    main()
