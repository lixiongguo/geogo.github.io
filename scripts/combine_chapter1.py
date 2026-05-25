#!/usr/bin/env python3
"""合并第一章所有文章并去除 Jekyll front matter，输出为单一 markdown"""
import sys, glob
from pathlib import Path

def strip_front_matter(text: str) -> str:
    """去除 Jekyll YAML front matter (---...---)"""
    if text.startswith('---'):
        idx = text.find('---', 3)
        if idx != -1:
            return text[idx + 3:].lstrip('\n')
    return text

def combine_files(root_dir: str, output_path: str):
    files = sorted(glob.glob(f'{root_dir}/*.md'))
    
    header = """---
title: "曲面展开 — 第一章：基础曲面展开方法"
author: "李雄国"
lang: zh-CN
mainfont: PingFang SC
documentclass: ctexart
toc: true
numbersections: false
---

"""
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(header)
        for f in files:
            text = Path(f).read_text('utf-8')
            text = strip_front_matter(text)
            out.write(text)
            out.write('\n\n')
    
    print(f"✅ 已合并 {len(files)} 篇文章 → {output_path}")

if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else '_posts/1.Parameterization/1.基础曲面展开方法'
    output = sys.argv[2] if len(sys.argv) > 2 else '/tmp/chapter1_combined.md'
    combine_files(root, output)
