"""将指定目录下的 .md 文章合并生成单个 PDF（需要 pandoc + xelatex）"""
import os, re, sys, subprocess, tempfile, shutil, urllib.request, hashlib

# 全局缓存：{url: local_path}
_dl_cache = {}

def _download(url, dl_dir):
    """下载 HTTP 图片到 dl_dir，返回本地路径；失败返回空"""
    if url in _dl_cache:
        return _dl_cache[url]
    try:
        ext = os.path.splitext(url.split('?')[0])[1] or '.png'
        fname = hashlib.md5(url.encode()).hexdigest()[:12] + ext
        local = os.path.join(dl_dir, fname)
        if not os.path.exists(local):
            urllib.request.urlretrieve(url, local)
        _dl_cache[url] = local
        return local
    except Exception:
        _dl_cache[url] = ''
        return ''

def check_deps():
    for cmd in ['pandoc', 'xelatex']:
        if not shutil.which(cmd):
            print(f'[错误] 未找到 {cmd}')
            print('  pandoc: https://pandoc.org/installing.html')
            print('  xelatex: 安装 MiKTeX 或 TeX Live')
            return False
    return True

def _resolve_image(alt, path, base_dir, dl_dir):
    """解析图片路径，HTTP 则下载到 dl_dir，本地存在则保留，否则返回空"""
    if path.startswith('http'):
        local = _download(path, dl_dir)
        return f'![{alt}]({local})' if local else ''
    for c in [
        os.path.normpath(os.path.join(base_dir, path)),
        os.path.normpath(os.path.join(base_dir, '..', '..', '..', path.replace('\\', '/'))),
    ]:
        if os.path.exists(c):
            return f'![{alt}]({c})'
    return ''


def _fix_images(text, base_dir, dl_dir):
    """移除 <img> 标签，![]() 处理：HTTP 下载、本地保存、不存在剔除"""
    text = re.sub(r'<img[^>]*/?>', '', text)
    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', lambda m: _resolve_image(m.group(1), m.group(2), base_dir, dl_dir), text)


def merge_to_pdf(folder, output_pdf, title='合集'):
    if not check_deps():
        sys.exit(1)

    folder = os.path.abspath(folder)
    files = sorted([f for f in os.listdir(folder) if f.endswith('.md')])
    if not files:
        print('未找到 .md 文件')
        sys.exit(1)

    # 临时目录（图片下载 + LaTeX 编译共用）
    tmpdir = tempfile.mkdtemp()
    dl_dir = os.path.join(tmpdir, 'images')
    os.makedirs(dl_dir, exist_ok=True)

    # 合并
    merged = ''
    chapter = 0
    for f in files:
        path = os.path.join(folder, f)
        with open(path, 'r', encoding='utf-8') as fh:
            text = fh.read()
        chapter += 1
        m = re.search(r'^title:\s*[\"\']?(.+?)[\"\']?\s*$', text, re.M)
        title_txt = m.group(1) if m else os.path.splitext(f)[0]
        text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text, count=1, flags=re.DOTALL)
        text = text.replace('{% raw %}', '').replace('{% endraw %}', '')
        text = text.replace('<!--more-->', '')
        text = _fix_images(text, folder, dl_dir)
        merged += f'\n\n# 第{chapter}章  {title_txt}\n\n{text}\n'

    # 步骤1: markdown -> latex
    md_path = os.path.join(tmpdir, 'merged.md')
    tex_path = os.path.join(tmpdir, 'merged.tex')
    with open(md_path, 'w', encoding='utf-8') as fh:
        fh.write(merged)

    print(f'正在生成 LaTeX ({chapter} 篇文章)...')
    r = subprocess.run([
        'pandoc', md_path, '-o', tex_path,
        '--standalone',
        '--toc', '--toc-depth=1',
        '-f', 'markdown+tex_math_dollars+raw_tex',
        '-V', 'mainfont=SimSun',
        '-V', f'title={title}',
        '-V', 'CJKmainfont=SimSun',
        '-V', 'geometry=margin=2.5cm',
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(f'[错误] Markdown->LaTeX:\n{r.stderr[-500:]}')
        shutil.rmtree(tmpdir, ignore_errors=True)
        return

    # 修复 LaTeX: $$ 块内中文包 \text{}
    with open(tex_path, 'r', encoding='utf-8') as fh:
        tex = fh.read()
    tex = re.sub(
        r'\$\$(.+?)\$\$',
        lambda m: '$$' + re.sub(
            r'([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+)',
            lambda c: r'\text{' + c.group(1) + '}', m.group(1)
        ) + '$$',
        tex, flags=re.DOTALL
    )
    with open(tex_path, 'w', encoding='utf-8') as fh:
        fh.write(tex)

    # 步骤2: xelatex 编译 (两次以生成目录)
    output_pdf = os.path.abspath(output_pdf)
    print('正在编译 PDF...')
    for i in range(2):
        r2 = subprocess.run(
            ['xelatex', '-interaction=nonstopmode', '-output-directory', tmpdir, tex_path],
            capture_output=True, cwd=tmpdir,
            encoding='utf-8', errors='replace'
        )

    pdf_src = os.path.join(tmpdir, 'merged.pdf')
    if os.path.exists(pdf_src) and os.path.getsize(pdf_src) > 100:
        shutil.copy(pdf_src, output_pdf)
        print(f'已生成: {output_pdf}')
    else:
        # 输出 xelatex 日志以供排查
        log_path = os.path.join(tmpdir, 'merged.log')
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8', errors='replace') as fh:
                log = fh.read()
            # 找第一个错误
            for m in re.finditer(r'^!.*', log, re.M):
                print(f'  {m.group().strip()}')
        print(f'[错误] xelatex 编译失败，请检查模板')
    shutil.rmtree(tmpdir, ignore_errors=True)
    _dl_cache.clear()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: python merge_pdf.py <md文件夹> <输出pdf路径> [标题]')
        sys.exit(1)
    merge_to_pdf(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '合集')
