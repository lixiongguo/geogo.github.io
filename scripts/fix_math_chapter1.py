#!/usr/bin/env python3
"""修复第一章 markdown 文件的公式规范问题，正确处理 $$ 块边界"""
import re, sys, glob
from pathlib import Path

def fix_file(filepath: str) -> bool:
    text = Path(filepath).read_text('utf-8')
    original = text

    # 将文本分成 $$...$$ 块和非 $$ 块
    segments = re.split(r'(\$\$.+?\$\$)', text, flags=re.DOTALL)

    for i, seg in enumerate(segments):
        if seg.startswith('$$') and seg.endswith('$$'):
            # $$ 块内：规则 4 (删除空行)、规则 6 (\sub → \subset)
            body = seg[2:-2]
            # 删除块内空行
            body = re.sub(r'\n\s*\n', '\n', body)
            # \sub → \subset（排除 \subsection, \substack, \subset, \subseteq）
            body = re.sub(r'\\sub(?=\s|\{|\[)(?!section|stack|set)', r'\\subset', body)
            segments[i] = '$$' + body + '$$'
        else:
            # 非 $$ 块：规则 1 ($ 与中文间加空格)
            # 中文后紧跟 $（非 $$ 开头）
            seg = re.sub(r'([\u4e00-\u9fff])\$(?!\$)', r'\1 $', seg)
            # $ 后紧跟中文（非 $$ 开头）
            seg = re.sub(r'(?<!\$)\$(?!\$)([\u4e00-\u9fff])', r'$ \1', seg)
            segments[i] = seg

    text = ''.join(segments)
    if text != original:
        Path(filepath).write_text(text, 'utf-8')
        return True
    return False

if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else '_posts/1.Parameterization/1.基础曲面展开方法'
    files = sorted(glob.glob(f'{root}/*.md'))
    fixed_count = 0
    for f in files:
        if fix_file(f):
            print(f"✅ 已修复: {f}")
            fixed_count += 1
        else:
            print(f"⏭️ 无变化: {f}")
    print(f"\n共修复 {fixed_count}/{len(files)} 个文件")
