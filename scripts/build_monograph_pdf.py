#!/usr/bin/env python3
"""将参数化专著所有 .md 文件合并转换为 PDF"""
import os, re, sys
from pathlib import Path
from markdown import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts" / "1.Parameterization"
OUTPUT = ROOT / "参数化算法专著.pdf"

# 章节排序：按文件夹 + 文件名日期
def sort_key(filepath):
    parts = filepath.relative_to(POSTS_DIR).parts
    return parts  # 自然按目录/文件名排序

def strip_frontmatter(text):
    """移除 Jekyll frontmatter 和 Liquid raw/endraw 标签"""
    # 移除 --- ... --- frontmatter
    text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text, flags=re.DOTALL, count=1)
    # 移除 {% raw %} / {% endraw %}
    text = text.replace('{% raw %}', '').replace('{% endraw %}', '')
    return text

def collect_files():
    """收集所有 .md 文件，按章节排序"""
    files = []
    for root, dirs, filenames in os.walk(POSTS_DIR):
        for f in sorted(filenames):
            if f.endswith('.md'):
                files.append(Path(root) / f)
    # 按路径部分排序（保证 0.前言 → 1.基础 → 2.共形 → ...）
    files.sort(key=lambda p: p.relative_to(POSTS_DIR).parts)
    return files

def build_html():
    """构建完整 HTML"""
    files = collect_files()
    
    # CSS 样式（中文排版）
    css = """
    <style>
      @page { size: A4; margin: 2cm 2.2cm; }
      body { font-family: "PingFang SC", "STSong", "Songti SC", serif; font-size: 12pt; line-height: 1.8; color: #222; }
      h1 { font-size: 20pt; text-align: center; margin: 40pt 0 20pt; page-break-before: always; }
      h2 { font-size: 16pt; margin: 28pt 0 12pt; border-bottom: 1px solid #ccc; padding-bottom: 4pt; }
      h3 { font-size: 13pt; margin: 20pt 0 8pt; }
      p { margin: 6pt 0; text-indent: 2em; }
      p.no-indent { text-indent: 0; }
      img { max-width: 100%; height: auto; margin: 10pt auto; display: block; }
      blockquote { margin: 10pt 20pt; padding: 8pt 16pt; border-left: 3px solid #4a90d9; background: #f5f7fa; font-style: italic; color: #555; }
      blockquote p { text-indent: 0; }
      pre { background: #f4f4f4; padding: 10pt; border-radius: 4pt; font-size: 9pt; font-family: "SF Mono", "Menlo", monospace; overflow-x: auto; margin: 8pt 0; }
      code { font-family: "SF Mono", "Menlo", monospace; font-size: 9.5pt; background: #f0f0f0; padding: 1pt 4pt; border-radius: 2pt; }
      pre code { background: none; padding: 0; }
      table { border-collapse: collapse; margin: 12pt auto; font-size: 10pt; }
      table th, table td { border: 1px solid #ccc; padding: 5pt 10pt; }
      table th { background: #eee; }
      .math { font-family: "STIX Two Math", "Cambria Math", serif; font-style: italic; }
      .chapter-title { font-size: 22pt; text-align: center; margin: 80pt 0 30pt; page-break-before: always; }
      .toc-item { margin: 3pt 0; text-indent: 0; }
      .toc-h2 { font-weight: bold; margin-top: 8pt; }
    </style>
    """
    
    # 构建目录和正文
    chapters_html = []
    toc_items = []
    chapter_num = 0
    
    # 按目录分组
    current_dir = None
    chapter_sections = []
    dir_names = {
        "0.前言": "前言",
        "1.基础曲面展开方法": "第一章 基础曲面展开方法",
        "2.基础共形映射方法": "第二章 基础共形映射方法",
        "3.基于几何优化的方法": "第三章 基于几何优化的方法",
        "4.计算共形几何": "第四章 计算共形几何",
        "5.最优传输": "第五章 最优传输",
        "6.附录": "附录",
    }
    
    for filepath in files:
        rel = filepath.relative_to(POSTS_DIR)
        parts = rel.parts
        dir_key = parts[0] if len(parts) > 1 else ""
        
        with open(filepath, 'r', encoding='utf-8') as f:
            raw = f.read()
        
        # 提取 title
        title_match = re.search(r'title:\s*"([^"]*)"', raw)
        title = title_match.group(1) if title_match else rel.stem
        
        content = strip_frontmatter(raw)
        
        # 检查是否有新章节
        if dir_key != current_dir:
            current_dir = dir_key
            chapter_num += 1
            dir_label = dir_names.get(dir_key, dir_key)
            chapters_html.append(f'<h1 class="chapter-title">{dir_label}</h1>')
            toc_items.append(f'<p class="toc-item toc-h2">{chapter_num}. {dir_label}</p>')
        
        # 转换 Markdown → HTML（启用扩展）
        try:
            html_body = markdown(content, extensions=['tables', 'fenced_code', 'codehilite', 'nl2br'])
        except:
            html_body = markdown(content)
        
        section_html = f"""
        <h2>{title}</h2>
        {html_body}
        """
        chapters_html.append(section_html)
        toc_items.append(f'<p class="toc-item">&nbsp;&nbsp;{title}</p>')
    
    # 组装完整 HTML
    toc_html = '\n'.join(toc_items)
    body_html = '\n'.join(chapters_html)
    
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>参数化算法专著</title>
{css}
</head>
<body>
<h1>参数化算法：从理论到实现</h1>
<p style="text-align:center;margin-bottom:30pt;">
<em>——三角网格曲面展开、共形映射、四边形网格化与最优传输</em>
</p>

<h2>目录</h2>
{toc_html}

<div style="page-break-before: always;"></div>

{body_html}

</body>
</html>"""
    return full_html

def main():
    print(f"正在生成专著 HTML...")
    html = build_html()
    
    # 写入临时 HTML
    temp_html = ROOT / "scripts" / "_monograph_temp.html"
    temp_html.write_text(html, encoding='utf-8')
    print(f"HTML 已生成: {temp_html} ({len(html):,} 字符)")
    
    # 转换为 PDF
    print(f"正在渲染 PDF → {OUTPUT.name} ...")
    HTML(string=html).write_pdf(str(OUTPUT))
    
    # 清理临时文件
    temp_html.unlink(missing_ok=True)
    
    size_mb = OUTPUT.stat().st_size / 1024 / 1024
    print(f"\n✅ 完成！PDF 已保存至: {OUTPUT}")
    print(f"   文件大小: {size_mb:.1f} MB")

if __name__ == '__main__':
    main()
