#!/usr/bin/env python3
"""
将曲面展开章节的文章分类从中文改为英文
并更新 sidebar.html 的映射
"""

import os
import re
from pathlib import Path

# 中文分类名到英文分类名的映射
CHINESE_TO_ENGLISH = {
    '曲面展开-前言': 'Parameterization-Preface',
    '曲面展开-曲面展开介绍': 'Parameterization-Intro',
    '曲面展开-共形映射方法': 'Parameterization-ConformalMapping',
    '曲面展开-四边形网格化': 'Parameterization-QuadRemeshing',
    '曲面展开-计算共形几何': 'Parameterization-ComputationalConformalGeometry',
    '曲面展开-最优传输': 'Parameterization-OptimalTransport',
    '曲面展开-附录': 'Parameterization-Appendix'
}

# 英文分类名到中文显示名的映射（用于 sidebar）
ENGLISH_TO_CHINESE_DISPLAY = {
    'Parameterization-Preface': '前言',
    'Parameterization-Intro': '曲面展开介绍',
    'Parameterization-ConformalMapping': '共形映射方法',
    'Parameterization-QuadRemeshing': '四边形网格化',
    'Parameterization-ComputationalConformalGeometry': '计算共形几何',
    'Parameterization-OptimalTransport': '最优传输',
    'Parameterization-Appendix': '附录'
}

def update_post_categories(target_dir):
    """更新文章的分类从中文改为英文"""
    if not target_dir.exists():
        print(f"错误：目录不存在 {target_dir}")
        return
    
    print(f"处理目录: {target_dir}\n")
    
    md_files = sorted(target_dir.glob('*.md'))
    
    stats = {'success': 0, 'skip': 0, 'error': 0}
    
    for filepath in md_files:
        filename = filepath.name
        print(f"处理: {filename}")
        
        # 跳过暂存文件和无 front matter 的文件
        if filename == '暂存.md':
            print("  跳过（暂存文件）")
            stats['skip'] += 1
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有 front matter
        if not content.startswith('---'):
            print("  跳过（无 front matter）")
            stats['skip'] += 1
            continue
        
        # 找到 front matter 的结束位置
        parts = content.split('---', 2)
        if len(parts) < 3:
            print("  跳过（front matter 格式错误）")
            stats['skip'] += 1
            continue
        
        front_matter = parts[1]
        body = parts[2]
        
        # 检查是否有 categories
        category_pattern = re.compile(r'categories\s*:\s*(.+)', re.IGNORECASE)
        match = category_pattern.search(front_matter)
        
        if not match:
            print("  跳过（无 categories）")
            stats['skip'] += 1
            continue
        
        categories_str = match.group(1).strip()
        
        # 解析 categories（可能是数组格式或字符串格式）
        updated = False
        new_categories = []
        
        # 尝试解析为数组
        if categories_str.startswith('[') and categories_str.endswith(']'):
            # 数组格式: ["Parameterization", "曲面展开-前言"]
            cats = [c.strip().strip('"').strip("'") for c in categories_str.strip('[]').split(',')]
            for cat in cats:
                if cat in CHINESE_TO_ENGLISH:
                    new_categories.append(CHINESE_TO_ENGLISH[cat])
                    updated = True
                else:
                    new_categories.append(cat)
        else:
            # 字符串格式或单个值
            if categories_str in CHINESE_TO_ENGLISH:
                new_categories = [CHINESE_TO_ENGLISH[categories_str]]
                updated = True
            else:
                print(f"  跳过（无需更新: {categories_str}）")
                stats['skip'] += 1
                continue
        
        if updated:
            # 写回文件
            new_categories_str = '[' + ', '.join([f'"{c}"' for c in new_categories]) + ']'
            new_front_matter = category_pattern.sub(f'categories: {new_categories_str}', front_matter)
            new_content = f"---{new_front_matter}---{body}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✓ 已更新分类: {new_categories}")
            stats['success'] += 1
        else:
            print(f"  跳过（无需更新）")
            stats['skip'] += 1
    
    print(f"\n{'='*60}")
    print(f"处理完成！")
    print(f"  成功: {stats['success']}")
    print(f"  跳过: {stats['skip']}")
    print(f"  错误: {stats['error']}")
    print(f"{'='*60}")
    
    return ENGLISH_TO_CHINESE_DISPLAY

def update_sidebar_mapping(sidebar_path, mapping):
    """更新 sidebar.html，添加英文分类到中文显示的映射"""
    with open(sidebar_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到第一个 case 语句的位置（Parameterization 部分）
    # 在 {% case cat_name %} 后面添加新章节的分类映射
    
    # 构建新的 when 语句
    new_when_cases = []
    for eng_cat, chinese_display in mapping.items():
        new_when_cases.append(f"		  {{% when '{eng_cat}' %}}{{% assign cat_display = '{chinese_display}' %}}")
    
    # 在第一个 case 块的 {% else %} 前插入新的 when 语句
    # 找到第一个 case 块的 else
    pattern = r'({% when \'MeshDeform\' %}{% assign cat_display = \'网格变形\' %}.*?)({% else %}{% assign cat_display = cat_name %})'
    
    replacement = r'\1' + '\n'.join(new_when_cases) + r'\n    \3'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(sidebar_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("\n✓ 已更新 sidebar.html 的分类映射")
    else:
        print("\n! sidebar.html 更新失败，请手动更新")

def main():
    # 目标目录
    target_dir = Path('/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/_posts/1.Parameterization/0.曲面展开')
    
    # 更新文章分类
    mapping = update_post_categories(target_dir)
    
    # 更新 sidebar
    sidebar_path = Path('/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/_includes/sidebar.html')
    if sidebar_path.exists():
        update_sidebar_mapping(sidebar_path, mapping)
    
    print("\n" + "="*60)
    print("映射关系：")
    for eng, chn in mapping.items():
        print(f"  {eng} → {chn}")
    print("="*60)

if __name__ == '__main__':
    main()
