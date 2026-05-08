#!/usr/bin/env python3
"""
为曲面展开章节的文章添加章节分类
根据文件名中的章节编号（0-6）添加对应的分类
"""

import os
import re
from pathlib import Path

# 章节编号到章节名称的映射
CHAPTER_MAP = {
    '0': '前言',
    '1': '曲面展开介绍',
    '2': '共形映射方法',
    '3': '四边形网格化',
    '4': '计算共形几何',
    '5': '最优传输',
    '6': '附录'
}

def extract_chapter_number(filename):
    """从文件名中提取章节编号，例如：2016-03-06-1.曲面展开介绍-1.1 介绍.md → 1"""
    # 文件名格式: YYYY-MM-DD-X.章节名-...
    match = re.search(r'^\d{4}-\d{2}-\d{2}-(\d+)\.', filename)
    if match:
        return match.group(1)
    return None

def update_front_matter(filepath, chapter_num, chapter_name):
    """更新文章的 front matter，添加章节分类"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有 front matter
    if not content.startswith('---'):
        print(f"  跳过（无 front matter）: {filepath}")
        return False
    
    # 找到 front matter 的结束位置
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"  跳过（front matter 格式错误）: {filepath}")
        return False
    
    front_matter = parts[1]
    body = parts[2]
    
    # 检查是否已有章节分类
    category_pattern = re.compile(r'categories\s*:\s*(.+)', re.IGNORECASE)
    match = category_pattern.search(front_matter)
    
    new_category = f"曲面展开-{chapter_name}"
    
    if match:
        # 已有 categories，检查是否包含章节分类
        existing = match.group(1).strip()
        if '[' in existing:
            # 数组格式: categories: [Parameterization, xxx]
            if new_category in existing:
                print(f"  跳过（已存在分类: {new_category}）")
                return False
            # 添加新分类
            new_categories = existing.rstrip(']') + f', {new_category}]'
            front_matter = category_pattern.sub(f'categories: {new_categories}', front_matter)
        else:
            # 字符串格式: categories: Parameterization
            if new_category in existing:
                print(f"  跳过（已存在分类: {new_category}）")
                return False
            front_matter = category_pattern.sub(f'categories: [{existing}, {new_category}]', front_matter)
    else:
        # 没有 categories，添加
        front_matter = front_matter.rstrip() + f'\ncategories: ["Parameterization", "{new_category}"]'
    
    # 写回文件
    new_content = f"---{front_matter}---{body}"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✓ 已添加分类: {new_category}")
    return True

def main():
    # 目标目录
    target_dir = Path('/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/_posts/1.Parameterization/0.曲面展开')
    
    if not target_dir.exists():
        print(f"错误：目录不存在 {target_dir}")
        return
    
    print(f"处理目录: {target_dir}\n")
    
    # 遍历所有 markdown 文件
    md_files = sorted(target_dir.glob('*.md'))
    
    stats = {'success': 0, 'skip': 0, 'error': 0}
    
    for filepath in md_files:
        filename = filepath.name
        print(f"处理: {filename}")
        
        # 跳过暂存文件
        if filename == '暂存.md':
            print("  跳过（暂存文件）")
            stats['skip'] += 1
            continue
        
        # 提取章节编号
        chapter_num = extract_chapter_number(filename)
        if chapter_num is None:
            print(f"  跳过（无法提取章节编号）")
            stats['skip'] += 1
            continue
        
        # 获取章节名称
        chapter_name = CHAPTER_MAP.get(chapter_num, f'未知章节{chapter_num}')
        print(f"  章节: {chapter_num}. {chapter_name}")
        
        # 更新 front matter
        try:
            if update_front_matter(filepath, chapter_num, chapter_name):
                stats['success'] += 1
            else:
                stats['skip'] += 1
        except Exception as e:
            print(f"  错误: {e}")
            stats['error'] += 1
    
    print(f"\n{'='*60}")
    print(f"处理完成！")
    print(f"  成功: {stats['success']}")
    print(f"  跳过: {stats['skip']}")
    print(f"  错误: {stats['error']}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
