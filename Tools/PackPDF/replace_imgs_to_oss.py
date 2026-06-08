#!/usr/bin/env python3
"""
将 _posts/ 下所有 .md 文件中本地路径引用的图片替换为阿里云 OSS URL。
支持 dry-run 模式（预览不写入）和实际执行模式。

引用模式：
  1. 相对路径：../../../imgs/xxx.png 或 ../imgs/xxx.png
  2. Mac 绝对路径：/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs/xxx.png
  3. Windows 绝对路径：C:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/imgs/xxx.png
  4. 其他盘 Windows 路径：D:/MyDocs/geogo.github.io/imgs/xxx.png
  5. 混合路径：/Users/lgxgeogo/Desktop/.../../../../imgs/xxx.png
  6. <img> 标签中的本地路径

已跳过：
  - 已是 OSS URL 的：https://lgximgs.oss-cn-beijing.aliyuncs.com/images/xxx.png
  - 其他 http/https 远程链接

用法：
  python replace_imgs_to_oss.py --dry-run    # 预览模式，不修改文件
  python replace_imgs_to_oss.py              # 实际执行替换
"""

import os
import re
import sys
import json
import urllib.parse
from pathlib import Path
from collections import defaultdict

# ========== 配置 ==========
OSS_BASE = "https://lgximgs.oss-cn-beijing.aliyuncs.com/images/"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMGS_DIR = PROJECT_ROOT / "imgs"
OUTPUT_MANIFEST = PROJECT_ROOT / "scripts" / "oss_upload_manifest.txt"

# ========== 正则表达式 ==========
# Markdown 图片：![alt](path)
# 匹配不以 http 开头的路径，且包含 imgs/ 的引用
MD_IMG_PATTERN = re.compile(
    r'(!\[[^\]]*\])\(([^)]*imgs[/\\][^)]+)\)',
    re.IGNORECASE
)

# HTML <img> 标签：src 属性包含本地路径
HTML_IMG_PATTERN = re.compile(
    r'(<img\s[^>]*src=["\'])([^"\']*imgs[/\\][^"\']+)(["\'][^>]*>)',
    re.IGNORECASE
)

# 已是 OSS URL 的模式
OSS_URL_PATTERN = re.compile(r'https?://lgximgs\.oss-cn-beijing\.aliyuncs\.com/images/', re.IGNORECASE)


def extract_image_filename(path_str):
    """从路径中提取 imgs/ 之后的文件名部分。
    
    Examples:
        ../../../imgs/image-xxx.png → image-xxx.png
        /Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs/image-xxx.png → image-xxx.png
        C:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/imgs/image-xxx.png → image-xxx.png
        /Users/lgxgeogo/Desktop/.../../../../imgs/xxx.png → xxx.png
    """
    # 统一用正斜杠
    normalized = path_str.replace('\\', '/')
    
    # 找到 imgs/ 的位置
    idx = normalized.find('imgs/')
    if idx == -1:
        return None
    
    # 取 imgs/ 之后的部分
    filename = normalized[idx + 5:]  # len('imgs/') = 5
    return filename


def is_local_path(path_str):
    """判断路径是否是需要替换的本地路径（非 OSS URL、非其他远程链接）"""
    stripped = path_str.strip()
    # 已经是 OSS URL
    if OSS_URL_PATTERN.match(stripped):
        return False
    # 其他远程链接
    if stripped.startswith('http://') or stripped.startswith('https://'):
        return False
    # 包含 imgs/ 的本地路径
    if 'imgs/' in stripped or 'imgs\\' in stripped:
        return True
    return False


def replace_markdown_images(content, filepath, dry_run=True):
    """替换 Markdown 格式的图片引用。
    
    Returns: (new_content, list_of_replacements)
    """
    replacements = []
    
    def replacer(match):
        alt_text = match.group(1)  # ![alt]
        path_str = match.group(2)  # path
        
        if not is_local_path(path_str):
            return match.group(0)
        
        filename = extract_image_filename(path_str)
        if filename is None:
            return match.group(0)
        
        # URL 编码文件名中的特殊字符（空格、中文等）
        # 但保留 / 和基本 ASCII 字符
        encoded_filename = urllib.parse.quote(filename, safe='-_.~!$&\'()*+,;=@')
        new_url = OSS_BASE + encoded_filename
        
        replacements.append({
            'file': str(filepath.relative_to(PROJECT_ROOT)),
            'old': path_str,
            'new': new_url,
            'filename': filename,
        })
        
        return f'{alt_text}({new_url})'
    
    new_content = MD_IMG_PATTERN.sub(replacer, content)
    return new_content, replacements


def replace_html_images(content, filepath, dry_run=True):
    """替换 HTML <img> 标签中的本地图片路径。
    
    Returns: (new_content, list_of_replacements)
    """
    replacements = []
    
    def replacer(match):
        prefix = match.group(1)   # <img src="
        path_str = match.group(2) # path
        suffix = match.group(3)   # " ...>
        
        if not is_local_path(path_str):
            return match.group(0)
        
        filename = extract_image_filename(path_str)
        if filename is None:
            return match.group(0)
        
        encoded_filename = urllib.parse.quote(filename, safe='-_.~!$&\'()*+,;=@')
        new_url = OSS_BASE + encoded_filename
        
        replacements.append({
            'file': str(filepath.relative_to(PROJECT_ROOT)),
            'old': path_str,
            'new': new_url,
            'filename': filename,
        })
        
        return f'{prefix}{new_url}{suffix}'
    
    new_content = HTML_IMG_PATTERN.sub(replacer, content)
    return new_content, replacements


def process_file(filepath, dry_run=True):
    """处理单个 .md 文件。
    
    Returns: (was_modified, list_of_replacements)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 先替换 Markdown 格式
    new_content, md_replacements = replace_markdown_images(content, filepath, dry_run)
    
    # 再替换 HTML 格式
    new_content, html_replacements = replace_html_images(new_content, filepath, dry_run)
    
    all_replacements = md_replacements + html_replacements
    
    if not all_replacements:
        return False, []
    
    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    return True, all_replacements


def main():
    dry_run = '--dry-run' in sys.argv or '--dry' in sys.argv
    
    if dry_run:
        print("=" * 70)
        print("  DRY-RUN 模式：仅预览替换，不修改任何文件")
        print("=" * 70)
    else:
        print("=" * 70)
        print("  实际执行模式：将修改 .md 文件中的图片路径")
        print("  按 Ctrl+C 取消，5 秒后开始...")
        print("=" * 70)
        try:
            import time
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n已取消。")
            return
    
    # 遍历所有 .md 文件
    md_files = sorted(POSTS_DIR.rglob('*.md'))
    
    all_replacements = []
    modified_files = []
    skipped_files = []
    
    for filepath in md_files:
        try:
            was_modified, replacements = process_file(filepath, dry_run)
            if was_modified:
                modified_files.append(filepath)
                all_replacements.extend(replacements)
            else:
                skipped_files.append(filepath)
        except Exception as e:
            print(f"  ✗ 错误处理 {filepath}: {e}")
    
    # ========== 统计与输出 ==========
    print(f"\n{'=' * 70}")
    print(f"  处理完成！")
    print(f"{'=' * 70}")
    print(f"  总文件数: {len(md_files)}")
    print(f"  有替换的文件: {len(modified_files)}")
    print(f"  无需替换的文件: {len(skipped_files)}")
    print(f"  总替换次数: {len(all_replacements)}")
    
    # 去重统计需要上传的唯一图片
    unique_images = set()
    for r in all_replacements:
        unique_images.add(r['filename'])
    
    print(f"  涉及唯一图片数: {len(unique_images)}")
    
    # 输出每个文件的替换详情
    if all_replacements:
        print(f"\n{'─' * 70}")
        print("  替换详情：")
        print(f"{'─' * 70}")
        
        # 按文件分组
        by_file = defaultdict(list)
        for r in all_replacements:
            by_file[r['file']].append(r)
        
        for filepath_str, reps in sorted(by_file.items()):
            print(f"\n  📄 {filepath_str} ({len(reps)} 处)")
            for r in reps:
                print(f"     {r['old']}")
                print(f"     → {r['new']}")
    
    # 生成上传清单
    if unique_images:
        print(f"\n{'─' * 70}")
        print(f"  需要上传到 OSS 的唯一图片清单（共 {len(unique_images)} 张）：")
        print(f"  保存至: {OUTPUT_MANIFEST}")
        print(f"{'─' * 70}")
        
        with open(OUTPUT_MANIFEST, 'w', encoding='utf-8') as f:
            for img_name in sorted(unique_images):
                f.write(img_name + '\n')
        
        # 验证本地 imgs/ 目录中有多少图片实际存在
        existing_count = 0
        missing_count = 0
        missing_list = []
        for img_name in sorted(unique_images):
            local_path = IMGS_DIR / img_name
            if local_path.exists():
                existing_count += 1
            else:
                missing_count += 1
                missing_list.append(img_name)
        
        print(f"  本地存在: {existing_count} 张")
        print(f"  本地缺失: {missing_count} 张")
        
        if missing_list:
            print(f"\n  ⚠ 以下图片在本地 imgs/ 中未找到：")
            for img in missing_list[:20]:
                print(f"    - {img}")
            if len(missing_list) > 20:
                print(f"    ... 还有 {len(missing_list) - 20} 张")
        
        # 输出 ossutil 批量上传命令
        print(f"\n{'─' * 70}")
        print(f"  OSS 上传命令（使用 ossutil）：")
        print(f"{'─' * 70}")
        print(f"""
  # 方法1：批量上传整个 imgs/ 目录到 OSS
  ossutil sync {IMGS_DIR} oss://lgximgs/images/ -f --include "*.png" --include "*.jpg" --include "*.jpeg" --include "*.gif" --include "*.webp"

  # 方法2：仅上传清单中的图片（推荐，避免上传无用图片）
  # 需先安装 ossutil：https://help.aliyun.com/document_detail/120075.html
  # 然后执行以下 PowerShell 命令：
  
  $images = Get-Content "{OUTPUT_MANIFEST}"
  foreach ($img in $images) {{
      $localPath = "{IMGS_DIR}\\$img"
      if (Test-Path $localPath) {{
          ossutil cp $localPath oss://lgximgs/images/$img -f
      }} else {{
          Write-Host "SKIP (not found): $img"
      }}
  }}
  
  # 方法3：使用 Python + oss2 SDK 上传（更灵活）
  # pip install oss2
  # 然后运行: python scripts/upload_to_oss.py
""")
    
    # 保存完整替换日志为 JSON
    log_path = PROJECT_ROOT / "scripts" / "oss_replace_log.json"
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump({
            'dry_run': dry_run,
            'total_files': len(md_files),
            'modified_files': len(modified_files),
            'total_replacements': len(all_replacements),
            'unique_images': len(unique_images),
            'replacements': all_replacements,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"  完整替换日志: {log_path}")
    print(f"  上传清单文件: {OUTPUT_MANIFEST}")
    
    if dry_run:
        print(f"\n  ⚠ 这是 DRY-RUN 模式，文件未被修改。")
        print(f"  要实际执行替换，请运行: python {Path(__file__).name}")


if __name__ == '__main__':
    main()
