"""将指定目录下的 .md 文章合并生成单个 PDF（需要 pandoc + xelatex）"""
import os, re, sys, subprocess, tempfile, shutil, urllib.request, hashlib

_dl_cache = {}

def _download(url, dl_dir):
    if url in _dl_cache: return _dl_cache[url]
    try:
        ext = os.path.splitext(url.split('?')[0])[1] or '.png'
        fname = hashlib.md5(url.encode()).hexdigest()[:12] + ext
        local = os.path.join(dl_dir, fname)
        if not os.path.exists(local): urllib.request.urlretrieve(url, local)

        # 检测 GIF 并转换为 PNG（xelatex 不支持 GIF）
        with open(local, 'rb') as f: header = f.read(6)
        if header[:3] == b'GIF':
            try:
                from PIL import Image
                img = Image.open(local)
                png_local = os.path.splitext(local)[0] + '.png'
                img.save(png_local, 'PNG')
                if png_local != local:
                    os.remove(local)
                local = png_local
                print(f'  [转换] GIF→PNG: {os.path.basename(local)}')
            except ImportError:
                print(f'  [跳过] PIL 未安装，无法转换 GIF')
                _dl_cache[url] = ''
                return ''

        _dl_cache[url] = local
        return local
    except: _dl_cache[url] = ''; return ''

def check_deps():
    for cmd in ['pandoc', 'xelatex']:
        if not shutil.which(cmd): print(f'[错误] 未找到 {cmd}'); return False
    return True

CJK_RE = re.compile(r'([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+)')

def _has_cjk(s):
    return bool(CJK_RE.search(s))

def _wrap_cjk(s):
    return CJK_RE.sub(lambda m: r'\text{' + m.group(1) + '}', s)

# ============== Markdown 级别预处理 ==============
def _preprocess_md(text, base_dir, dl_dir):
    """在 Markdown 层面做所有预处理"""
    # 0. 清理
    text = text.replace('{% raw %}', '').replace('{% endraw %}', '').replace('<!--more-->', '')
    text = re.sub(r'<img[^>]*/?>', '', text)

    # 1. 图片：HTTP 下载、本地保留
    def _resolve_img(m):
        alt, path = m.group(1), m.group(2)
        if path.startswith('http'):
            local = _download(path, dl_dir)
            return f'![{alt}]({local})' if local and os.path.exists(local) else ''
        for c in [
            os.path.normpath(os.path.join(base_dir, path)),
            os.path.normpath(os.path.join(base_dir, '..', '..', '..', path.replace('\\', '/'))),
        ]:
            if os.path.exists(c): return f'![{alt}]({c})'
        return ''
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', _resolve_img, text)

    # 2. 数学模式 CJK → \text{} + \begin{cases} 块转 $$...$$
    #    先处理：如果 $...$ 内包含 \begin{cases}，则转为 $$...$$
    def _upgrade_cases_inline(m):
        full = m.group(0)
        inner = m.group(1)
        if '\\begin{cases}' in inner or '\\begin{array}' in inner:
            return '$$' + inner + '$$'
        return full
    text = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', _upgrade_cases_inline, text)

    # $$...$$ 块：CJK → \text{}
    def _fix_math_block(m):
        inner = m.group(1)
        return '$$' + _wrap_cjk(inner) + '$$' if _has_cjk(inner) else m.group(0)
    text = re.sub(r'\$\$(.+?)\$\$', _fix_math_block, text, flags=re.DOTALL)

    # $...$ 内联（不含 $$ 且不含 cases/array）：CJK → \text{}
    def _fix_inline_math(m):
        inner = m.group(1)
        return '$' + _wrap_cjk(inner) + '$' if _has_cjk(inner) else m.group(0)
    text = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', _fix_inline_math, text)

    return text

# ============== LaTeX 级别后处理 ==============
def _fix_latex(tex):
    """修复 pandoc 生成的 LaTeX 中的问题"""

    # 1. pandoc 转义 $ → \$，恢复为真正的数学模式分隔符
    #    pattern: \$ ... \$ (跨行，通常包含数学内容)
    tex = tex.replace(r'\textdollar', r'\$')
    # 只替换成对出现的 \$（后面跟着空白行然后数学内容）
    tex = re.sub(r'\\\$\s*\n\s*\n(\s*\\begin\{cases\})', r'$\n\n\1', tex)
    tex = re.sub(r'(\\end\{cases\})\s*\n\s*\n\s*\\\$', r'\1\n\n$', tex)
    # 如果 cases 已经被 $$ 包裹，移除残留的 \$
    tex = re.sub(r'\\\$\s*\n\s*\n\s*\$\$', r'$$\n\n$$', tex)

    # 2. 图片路径 normalize
    tex = re.sub(r'([a-zA-Z]:[^\s{}]+\.\./[^\s{}]+)', lambda m: os.path.normpath(m.group(1)), tex)

    # 3. \begin{figure}[htbp] → [H] + 添加 float 包
    tex = tex.replace(r'\begin{figure}[htbp]', r'\begin{figure}[H]')
    if r'\usepackage{float}' not in tex:
        # 在 graphicx 之后插入 float
        tex = tex.replace(r'\usepackage{graphicx}',
                          r'\usepackage{graphicx}' + '\n' + r'\usepackage{float}')

    # 4. 容忍长行
    if r'\sloppy' not in tex:
        tex = tex.replace(r'\begin{document}', r'\sloppy' + '\n' + r'\begin{document}')

    return tex

# ============== 主逻辑 ==============
def merge_to_pdf(folder, output_pdf, title='合集', single_chapter=False):
    if not check_deps(): sys.exit(1)

    folder = os.path.abspath(folder)
    files = sorted([f for f in os.listdir(folder) if f.endswith('.md') and f != '目录.md'])
    if single_chapter:
        files = [f for f in files if not re.match(r'^0\.', f)]
    if not files: print('未找到 .md 文件'); sys.exit(1)

    # 工作目录（normpath 解决 .. 问题）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    work_dir = os.path.normpath(os.path.join(script_dir, '..', 'build_pdf'))
    os.makedirs(work_dir, exist_ok=True)
    dl_dir = os.path.normpath(os.path.join(work_dir, 'images'))
    os.makedirs(dl_dir, exist_ok=True)

    # ====== 合并 MD ======
    merged = f'# {title}\n\n' if single_chapter else ''
    ch = 0
    for f in files:
        ch += 1
        path = os.path.join(folder, f)
        with open(path, 'r', encoding='utf-8') as fh: text = fh.read()
        m = re.search(r'^title:\s*[\"\']?(.+?)[\"\']?\s*$', text, re.M)
        tt = m.group(1) if m else os.path.splitext(f)[0]
        text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text, count=1, flags=re.DOTALL)
        text = _preprocess_md(text, folder, dl_dir)
        if single_chapter:
            merged += f'\n\n{text}\n'
        else:
            merged += f'\n\n# 第{ch}章  {tt}\n\n{text}\n'

    md_path = os.path.join(work_dir, 'merged.md')
    with open(md_path, 'w', encoding='utf-8') as fh: fh.write(merged)
    print(f'合并: {ch} 章, {len(merged)} chars')

    # ====== pandoc → LaTeX ======
    tex_path = os.path.join(work_dir, 'merged.tex')
    r = subprocess.run([
        'pandoc', md_path, '-o', tex_path,
        '--standalone', '--toc', '--toc-depth=1',
        '-f', 'markdown+tex_math_dollars+raw_tex',
        '-V', 'mainfont=SimSun',
        '-V', f'title={title}',
        '-V', 'CJKmainfont=SimSun',
        '-V', 'geometry=margin=2.5cm',
    ], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print(f'[错误] pandoc→tex:\n{r.stderr[-500:]}'); return

    # ====== 修复 LaTeX ======
    with open(tex_path, 'r', encoding='utf-8') as fh: tex = fh.read()
    tex = _fix_latex(tex)
    with open(tex_path, 'w', encoding='utf-8') as fh: fh.write(tex)

    print(f'LaTeX: {len(tex)} chars')

    # ====== xelatex 编译 ×2 ======
    output_pdf = os.path.abspath(output_pdf)
    for i in range(2):
        print(f'xelatex pass {i+1}...')
        subprocess.run(
            ['xelatex', '-interaction=nonstopmode',
             '-output-directory', work_dir, 'merged.tex'],
            capture_output=True, cwd=work_dir, timeout=300,
            encoding='utf-8', errors='replace')

    pdf_src = os.path.join(work_dir, 'merged.pdf')
    if os.path.exists(pdf_src) and os.path.getsize(pdf_src) > 10000:
        with open(pdf_src, 'rb') as f: content = f.read()
        if content.rfind(b'%%EOF') > 0 and content.rfind(b'startxref') > 0:
            shutil.copy(pdf_src, output_pdf)
            sz = os.path.getsize(output_pdf) / 1024
            # 用 PyPDF2 获取页数（PDF 1.5+ 使用压缩对象流，需解析）
            try:
                from PyPDF2 import PdfReader
                pages = len(PdfReader(output_pdf).pages)
            except Exception:
                pages = '?'
            print(f'已生成: {output_pdf} ({sz:.1f} KB, {pages} 页)')
            _dl_cache.clear()
            return

    # ====== 失败分析 ======
    print(f'[失败] PDF 不完整')
    log_path = os.path.join(work_dir, 'merged.log')
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8', errors='replace') as fh: log = fh.read()
        errs = re.findall(r'^!.*', log, re.MULTILINE)
        print(f'xelatex 错误 ({len(errs)}):')
        for e in errs[:20]: print(f'  {e.strip()}')
    print(f'\n文件保留在: {work_dir}')
    _dl_cache.clear()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: python merge_pdf.py <md文件夹> <输出pdf路径> [标题] [--single-chapter]')
        sys.exit(1)
    flags = [a for a in sys.argv[3:] if a.startswith('--')]
    args = [a for a in sys.argv[1:3]] + [a for a in sys.argv[3:] if not a.startswith('--')]
    title = args[2] if len(args) > 2 else '合集'
    single = '--single-chapter' in flags
    merge_to_pdf(args[0], args[1], title, single_chapter=single)
