#!/usr/bin/env python3
"""参数化专著 .md → PDF（pandoc + tectonic，LaTeX 数学渲染 + 图片）

用法：
    python3 build_monograph_pdf.py             # 含图片（会下载/缓存到 _pdf_images/）
    python3 build_monograph_pdf.py --no-img    # 不含图片，快速生成
"""
import os, re, subprocess, sys, hashlib, urllib.request, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts" / "1.Parameterization"
OUTPUT = ROOT / "参数化算法专著.pdf"
TMP = ROOT / "scripts" / "_monograph_combined.md"
IMG_DIR = ROOT / "scripts" / "_pdf_images"

# ═══════════════════════════════════════════════════════════════
# 图片下载
# ═══════════════════════════════════════════════════════════════

def extract_all_image_urls(files):
    """从所有 md 文件中提取远程图片 URL"""
    urls = set()
    for fp in files:
        text = fp.read_text('utf-8')
        text = re.sub(r'^---.*?\n---\n', '', text, flags=re.DOTALL, count=1)
        for m in re.finditer(r'!\[([^\]]*)\]\((https?://[^)]+)\)', text):
            urls.add(m.group(2))
    return sorted(urls)

def url_to_fname(url):
    """将 URL 映射为安全的本地文件名"""
    # 取 URL 路径最后一段
    path_part = url.rsplit('/', 1)[-1]
    # URL 解码
    from urllib.parse import unquote
    fname = unquote(path_part)
    # 特殊字符替换
    fname = re.sub(r'[^\w.\-]', '_', fname)
    # 补充扩展名
    if '.' not in fname[-6:]:
        fname += '.png'
    # 太长则哈希
    if len(fname) > 120:
        ext = fname.rsplit('.', 1)[-1] if '.' in fname else 'png'
        fname = hashlib.md5(url.encode()).hexdigest()[:12] + '.' + ext
    return fname

def download_image(url, local_path):
    """下载单张图片，返回 (url, local_path, success)"""
    if local_path.exists() and local_path.stat().st_size > 100:
        return (url, str(local_path), True)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        local_path.write_bytes(data)
        return (url, str(local_path), True)
    except Exception as e:
        print(f"  ⚠ 下载失败: {url} — {e}")
        return (url, None, False)

def download_all_images(urls, max_workers=8):
    """并行下载所有图片，返回 url→本地路径 映射"""
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    
    tasks = []
    for url in urls:
        local_path = (IMG_DIR / url_to_fname(url)).resolve()
        tasks.append((url, local_path))
    
    url_map = {}
    total = len(tasks)
    done = 0
    print(f"  共 {total} 张图片，并行下载 (workers={max_workers})...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {}
        for url, local_path in tasks:
            f = pool.submit(download_image, url, local_path)
            futures[f] = url
        
        for f in as_completed(futures):
            done += 1
            url, local, ok = f.result()
            url_map[url] = local if ok else None
            if done % 50 == 0 or done == total:
                succeeded = sum(1 for v in url_map.values() if v is not None)
                print(f"  [{done}/{total}] 已下载，成功 {succeeded} 张")
    
    succeeded = sum(1 for v in url_map.values() if v is not None)
    failed = total - succeeded
    print(f"  完成: {succeeded} 成功, {failed} 失败")
    return url_map

# ═══════════════════════════════════════════════════════════════
# 数学公式预处理
# ═══════════════════════════════════════════════════════════════

CJK_RANGE = r'\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\u3400-\u4dbf'
CJK_CONT_RE = re.compile(f'[{CJK_RANGE}，。；：！？、（）【】《》""''…—]+')

def wrap_chinese_in_math(math_body):
    """将数学表达式中的中文片段用 \\text{...} 包裹"""
    result = []
    i = 0
    while i < len(math_body):
        if math_body[i:].startswith(r'\text{') or math_body[i:].startswith(r'\mbox{'):
            brace_start = math_body.index('{', i) + 1
            depth = 1
            j = brace_start
            while j < len(math_body) and depth > 0:
                if math_body[j] == '{': depth += 1
                elif math_body[j] == '}': depth -= 1
                j += 1
            result.append(math_body[i:j])
            i = j
            continue
        
        if math_body[i] == '\\':
            j = i + 1
            if j < len(math_body) and math_body[j] in r'{}$%&_^~# ':
                result.append(math_body[i:j+1])
                i = j + 1
                continue
            while j < len(math_body) and math_body[j].isalpha():
                j += 1
            if j < len(math_body) and math_body[j] == '{':
                depth = 1
                j += 1
                while j < len(math_body) and depth > 0:
                    if math_body[j] == '{': depth += 1
                    elif math_body[j] == '}': depth -= 1
                    j += 1
            result.append(math_body[i:j])
            i = j
            continue
        
        m = CJK_CONT_RE.match(math_body, i)
        if m:
            result.append(r'\text{' + m.group(0) + '}')
            i = m.end()
            continue
        
        result.append(math_body[i])
        i += 1
    
    return ''.join(result)

def preprocess_math(text):
    """预处理所有数学环境中的中文"""
    # 1. \[...\]
    def fix_display_math(m):
        body = m.group(1)
        body = wrap_chinese_in_math(body)
        return r'\[' + body + r'\]'
    text = re.sub(r'\\\[(.+?)\\\]', fix_display_math, text, flags=re.DOTALL)
    
    # 2. $$...$$ (去空行，包裹中文)
    def fix_display_dollar(m):
        body = m.group(1)
        body = re.sub(r'\n\s*\n', '\n', body)
        body = wrap_chinese_in_math(body)
        return '$$' + body + '$$'
    text = re.sub(r'\$\$(.+?)\$\$', fix_display_dollar, text, flags=re.DOTALL)
    
    # 3. $...$ 行内数学
    def fix_inline_math(m):
        body = m.group(1)
        if r'\begin{cases}' in body or '\\begin{cases}' in body:
            body = wrap_chinese_in_math(body)
            return '\n$$' + body + '$$\n'
        body = wrap_chinese_in_math(body)
        return '$' + body + '$'
    text = re.sub(r'(?<!\$)\$(?!\$)((?:[^$]|\\\$)+?)\$(?!\$)', fix_inline_math, text)
    
    return text

def strip_frontmatter(text):
    text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text, flags=re.DOTALL, count=1)
    text = text.replace('{% raw %}', '').replace('{% endraw %}', '')
    return text

def markdown_table_to_text(content):
    """将 markdown 表格转为纯文本代码块"""
    lines = content.split('\n')
    result = []
    in_table = False
    table_lines = []
    
    for i in range(len(lines)):
        line = lines[i]
        stripped = line.strip()
        is_table_line = bool(re.match(r'^\|.*\|$', stripped))
        is_separator = bool(re.match(r'^\|[\s\-:|]+\|$', stripped))
        prev_is_table = (i > 0 and bool(re.match(r'^\|.*\|$', lines[i-1].strip())))
        
        if is_table_line or (is_separator and prev_is_table):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
        else:
            if in_table:
                result.append(_render_table_as_text(table_lines))
                table_lines = []
                in_table = False
            result.append(line)
    
    if in_table and table_lines:
        result.append(_render_table_as_text(table_lines))
    
    return '\n'.join(result)

def _render_table_as_text(lines):
    data_lines = [l for l in lines if not re.match(r'^\|[\s\-:|]+\|$', l.strip())]
    if not data_lines:
        return ''
    text_lines = ['', '```text']
    for dl in data_lines:
        cells = [c.strip() for c in dl.strip().strip('|').split('|')]
        text_lines.append('  ' + ' | '.join(cells))
    text_lines.append('```')
    text_lines.append('')
    return '\n'.join(text_lines)

def preprocess_content(content, url_map=None):
    """综合预处理
    
    Args:
        content: markdown 文本
        url_map: {远程URL: 本地路径} 映射，为 None 则移除图片
    """
    # 图片处理
    if url_map is not None:
        def _replace_img(m):
            alt = m.group(1) or ''
            url = m.group(2)
            local = url_map.get(url)
            if local:
                return f'![{alt}]({local})'
            else:
                return f'[图: {alt}]'
        content = re.sub(r'!\[([^\]]*)\]\((https?://[^)]+)\)', _replace_img, content)
    else:
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'[图: \1]', content)
    
    # 移除不兼容 HTML
    content = re.sub(r'<details[^>]*>.*?</details>', '', content, flags=re.DOTALL)
    content = re.sub(r'<summary[^>]*>.*?</summary>', '', content, flags=re.DOTALL)
    content = re.sub(r'</?br\s*/?>', '\\\\', content)
    
    # markdown 表格 → 代码块
    content = markdown_table_to_text(content)
    
    # 破折号
    content = content.replace('------', '——')
    content = content.replace('-----', '——')
    
    # \sub → \subset
    content = re.sub(r'\\sub(?![a-zA-Z])', r'\\subset', content)
    
    # \($...$\) 双包裹修复
    content = re.sub(r'\\\(\$([^$]+?)\$\\\)', r'\\(\1\\)', content)
    content = re.sub(r'\$\\\(([^)]+?)\\\)\$', r'\\(\1\\)', content)
    
    # 去掉 $ 内部首尾空格
    def _strip_inner(m):
        body = m.group(1).strip()
        return '$' + body + '$'
    for _ in range(3):
        content = re.sub(r'(?<!\$)\$ ([^$]+?)\$(?!\$)', _strip_inner, content)
        content = re.sub(r'(?<!\$)\$([^$]+?) \$(?!\$)', _strip_inner, content)
    
    # 数学公式中文 → \text{}
    content = preprocess_math(content)
    
    # 为 $...$ 添加外部空格（避免 pandoc 列表环境 $ 转义）
    def _wrap(m):
        return ' $' + m.group(1) + '$ '
    content = re.sub(r'(?<!\$)\$([^\n$]+?)\$(?!\$)', _wrap, content)
    
    return content

# ═══════════════════════════════════════════════════════════════
# 合并与编译
# ═══════════════════════════════════════════════════════════════

def collect_files():
    files = []
    for root, dirs, filenames in os.walk(POSTS_DIR):
        for f in sorted(filenames):
            if f.endswith('.md') and '暂存' not in f and '问题' not in f:
                files.append(Path(root) / f)
    files.sort(key=lambda p: p.relative_to(POSTS_DIR).parts)
    return files

def build_combined_md(url_map=None):
    files = collect_files()
    
    dn = {
        "0.前言": "前言",
        "1.基础曲面展开方法": "第一章 基础曲面展开方法",
        "2.基础共形映射方法": "第二章 基础共形映射方法",
        "3.基于几何优化的方法": "第三章 基于几何优化的方法",
        "4.全局参数化方法": "第四章 全局参数化方法",
        "5.最优传输": "第五章 最优传输",
        "6.附录": "附录",
    }
    
    lines = [
        "---",
        "title: 参数化算法：从理论到实现",
        'author: "李雄国"',
        "documentclass: ctexart",
        "toc: true",
        "toc-depth: 2",
        "numbersections: true",
        "papersize: a4",
        "fontsize: 12pt",
        "linestretch: 1.5",
        "geometry: margin=2.5cm",
        "---",
        "",
    ]
    
    cur_dir = None
    for idx, fp in enumerate(files):
        rel = fp.relative_to(POSTS_DIR)
        dk = rel.parts[0] if len(rel.parts) > 1 else ""
        raw = fp.read_text(encoding='utf-8')
        tm = re.search(r'title:\s*"([^"]*)"', raw)
        title = tm.group(1) if tm else rel.stem
        content = strip_frontmatter(raw)
        content = preprocess_content(content, url_map)
        
        if dk != cur_dir:
            cur_dir = dk
            label = dn.get(dk, dk)
            lines.append(f"\\newpage")
            lines.append(f"# {label}")
        
        lines.append(f"## {title}")
        lines.append("")
        lines.append(content)
        lines.append("")
        
        print(f"  [{idx+1}/{len(files)}] {title}")
    
    combined = '\n'.join(lines)
    TMP.write_text(combined, encoding='utf-8')
    print(f"合并 Markdown: {TMP} ({len(combined):,} 字符)")
    return TMP

def run_pandoc(md_file, output):
    """运行 pandoc + tectonic"""
    cmd = [
        'pandoc', str(md_file),
        '--pdf-engine=tectonic',
        '--from=markdown+tex_math_dollars+tex_math_single_backslash+raw_tex',
        '-V', 'colorlinks=true',
        '-V', 'linkcolor=blue',
        '-o', str(output),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        print("\npandoc stderr (末尾 2000 字):")
        print(result.stderr[-2000:])
        raise RuntimeError(f"pandoc 失败 (exit {result.returncode})")
    return True

def main():
    no_img = '--no-img' in sys.argv
    
    if no_img:
        print("【模式: 无图片版】仅文字与公式\n")
        url_map = None
    else:
        print("【模式: 完整版】含图片（首次需下载，后续从缓存读取）\n")
    
    # 第一步：合并 markdown（先生成无图版收集 URL，或先下载再合并）
    files = collect_files()
    
    if not no_img:
        print("步骤 0: 提取并下载图片...")
        all_urls = extract_all_image_urls(files)
        print(f"  发现 {len(all_urls)} 张远程图片")
        url_map = download_all_images(all_urls)
    else:
        url_map = None
    
    print("\n步骤 1: 合并专著 Markdown（预处理公式 + 替换图片路径）...")
    md_file = build_combined_md(url_map)
    
    print(f"\n步骤 2: pandoc + tectonic 渲染 PDF → {OUTPUT.name} ...")
    run_pandoc(md_file, OUTPUT)
    
    size_mb = OUTPUT.stat().st_size / 1024 / 1024
    print(f"\n✅ {OUTPUT}  ({size_mb:.1f} MB)")

if __name__ == '__main__':
    main()
