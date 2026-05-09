#!/usr/bin/env python3
"""参数化专著 .md → PDF（matplotlib 渲染数学公式 + 缓存）"""
import os, re, io, hashlib
from pathlib import Path
from markdown import markdown
from weasyprint import HTML
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts" / "1.Parameterization"
OUTPUT = ROOT / "参数化算法专著.pdf"
CACHE_DIR = ROOT / "scripts" / ".math_cache"
CACHE_DIR.mkdir(exist_ok=True)

# 全局重用单个 figure
_fig = None

def _get_fig():
    global _fig
    if _fig is None:
        _fig = plt.figure(figsize=(0.01, 0.01))
    return _fig

def render_svg(latex, display=False):
    """渲染单个 LaTeX 公式 → SVG 字符串（带缓存）"""
    key = hashlib.md5(f"{latex}|{display}".encode()).hexdigest()
    cf = CACHE_DIR / f"{key}.svg"
    if cf.exists():
        return cf.read_text()
    
    try:
        fig = _get_fig()
        fig.clf()
        fs = 13 if display else 11
        
        # 先测尺寸
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        t = ax.text(0, 0.5, f"${latex}$", fontsize=fs, va='center')
        fig.canvas.draw()
        bb = t.get_window_extent()
        fig.clf()
        
        w, h = bb.width / 100, bb.height / 100
        margin = 0.05
        dpi_out = 120
        
        fig2 = plt.figure(figsize=(w + margin, h + margin), dpi=dpi_out)
        ax2 = fig2.add_axes([0, 0, 1, 1])
        ax2.axis('off')
        ax2.text(0.5, 0.5, f"${latex}$", fontsize=fs, va='center', ha='center',
                 transform=ax2.transAxes)
        
        buf = io.BytesIO()
        fig2.savefig(buf, format='svg', bbox_inches='tight', pad_inches=0.02,
                     transparent=True)
        plt.close(fig2)
        
        svg = buf.getvalue().decode()
        m = re.search(r'<svg.*?</svg>', svg, re.DOTALL)
        result = m.group(0) if m else f'<i>${latex}$</i>'
        cf.write_text(result)
        return result
    except:
        return f'<span style="font-family:serif;font-style:italic">${latex}$</span>'

def process_math(md_text):
    """替换 $...$ 和 $$...$$ 为 SVG"""
    # 保护代码块
    codes = []
    def save_code(m):
        codes.append(m.group(0))
        return f'%%CODEBLOCK{len(codes)-1}%%'
    md_text = re.sub(r'```.*?```', save_code, md_text, flags=re.DOTALL)
    
    # 行间公式 $$...$$
    def repl_block(m):
        svg = render_svg(m.group(1).strip(), display=True)
        if svg.startswith('<svg'):
            return f'<div style="text-align:center;margin:10pt 0;">{svg}</div>'
        return f'<p style="text-align:center;">${m.group(1).strip()}$</p>'
    
    md_text = re.sub(r'\$\$\s*(.+?)\s*\$\$', repl_block, md_text, flags=re.DOTALL)
    
    # 行内公式 $...$
    def repl_inline(m):
        svg = render_svg(m.group(1).strip(), display=False)
        if svg.startswith('<svg'):
            return f'<span style="display:inline-block;vertical-align:middle;">{svg}</span>'
        return f'<span class="math-inline">\\( {m.group(1).strip()} \\)</span>'
    
    md_text = re.sub(r'(?<!\\)\$([^\$]+?)(?<!\\)\$', repl_inline, md_text)
    
    # 恢复代码块
    for i, code in enumerate(codes):
        md_text = md_text.replace(f'%%CODEBLOCK{i}%%', code)
    
    return md_text

def strip_frontmatter(text):
    text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text, flags=re.DOTALL, count=1)
    return text.replace('{% raw %}', '').replace('{% endraw %}', '')

def collect_files():
    files = []
    for root, dirs, filenames in os.walk(POSTS_DIR):
        for f in sorted(filenames):
            if f.endswith('.md') and '暂存' not in f and '问题' not in f:
                files.append(Path(root) / f)
    files.sort(key=lambda p: p.relative_to(POSTS_DIR).parts)
    return files

def build_html():
    files = collect_files()
    
    css = """<style>
@page{size:A4;margin:2.2cm 2.5cm}
body{font-family:"PingFang SC","STSong","Songti SC",serif;font-size:12pt;line-height:1.9;color:#222}
h1{font-size:21pt;text-align:center;margin:50pt 0 24pt;page-break-before:always}
h2{font-size:16pt;margin:30pt 0 14pt;border-bottom:1px solid #ddd;padding-bottom:5pt}
h3{font-size:13pt;margin:22pt 0 10pt}
h4{font-size:11.5pt;margin:16pt 0 8pt}
p{margin:7pt 0;text-indent:2em}
blockquote{margin:10pt 24pt;padding:8pt 18pt;border-left:3px solid #4a90d9;background:#f5f7fa}
blockquote p{text-indent:0}
pre{background:#f4f4f4;padding:12pt;border-radius:4pt;font-size:9pt;font-family:"SF Mono","Menlo",monospace;overflow-x:auto;margin:10pt 0;line-height:1.5}
code{font-family:"SF Mono","Menlo",monospace;font-size:9.5pt;background:#f0f0f0;padding:1pt 4pt;border-radius:2pt}
pre code{background:none;padding:0}
table{border-collapse:collapse;margin:14pt auto;font-size:10pt}
table th,td{border:1px solid #ccc;padding:6pt 12pt}
table th{background:#eee}
.math-inline{font-family:"Times New Roman","STIX Two Math",serif;font-style:italic;font-size:11pt;color:#333}
.chapter-title{font-size:23pt;text-align:center;margin:90pt 0 35pt;page-break-before:always}
.toc-item{margin:3pt 0;text-indent:0}
.toc-h2{font-weight:bold;margin-top:10pt}
img{max-width:95%;height:auto;margin:12pt auto;display:block}
strong{color:#333}
</style>"""
    
    chapters, toc = [], []
    cur_dir, ch = None, 0
    dn = {"0.前言":"前言","1.基础曲面展开方法":"第一章 基础曲面展开方法",
          "2.基础共形映射方法":"第二章 基础共形映射方法",
          "3.基于几何优化的方法":"第三章 基于几何优化的方法",
          "4.计算共形几何":"第四章 计算共形几何",
          "5.最优传输":"第五章 最优传输","6.附录":"附录"}
    
    for idx, fp in enumerate(files):
        rel = fp.relative_to(POSTS_DIR)
        dk = rel.parts[0] if len(rel.parts) > 1 else ""
        raw = fp.read_text(encoding='utf-8')
        tm = re.search(r'title:\s*"([^"]*)"', raw)
        title = tm.group(1) if tm else rel.stem
        content = strip_frontmatter(raw)
        content = process_math(content)
        
        if dk != cur_dir:
            cur_dir = dk; ch += 1
            label = dn.get(dk, dk)
            chapters.append(f'<h1 class="chapter-title">{label}</h1>')
            toc.append(f'<p class="toc-item toc-h2">{ch}. {label}</p>')
        
        body = markdown(content, extensions=['tables', 'fenced_code', 'nl2br'])
        chapters.append(f'<h2>{title}</h2>\n{body}')
        toc.append(f'<p class="toc-item">&nbsp;&nbsp;{title}</p>')
        print(f"  [{idx+1}/{len(files)}] {title}")
    
    return f"""<!DOCTYPE html><html lang="zh-CN">
<head><meta charset="utf-8"><title>参数化算法专著</title>{css}</head>
<body>
<h1>参数化算法：从理论到实现</h1>
<p style="text-align:center;margin-bottom:30pt;text-indent:0"><em>——三角网格曲面展开、共形映射、四边形网格化与最优传输</em></p>
<h2>目录</h2>
{''.join(toc)}
<div style="page-break-before:always"></div>
{''.join(chapters)}
</body></html>"""

def main():
    print("生成专著（公式 SVG 渲染 + 缓存）...")
    html = build_html()
    print(f"渲染 PDF → {OUTPUT.name} ...")
    HTML(string=html).write_pdf(str(OUTPUT))
    print(f"✅ {OUTPUT}  ({OUTPUT.stat().st_size/1024/1024:.1f} MB)")

if __name__ == '__main__':
    main()
