"""整本专著 PDF 构建（pandoc + tectonic）。"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable
from urllib.parse import unquote

from .deps import ensure_toolchain_path
from .preprocess import preprocess_content, strip_frontmatter

LogFn = Callable[[str], None]

CHAPTER_NAMES = {
    '0.前言': '前言',
    '1.基础曲面展开方法': '第一章 基础曲面展开方法',
    '2.基础共形映射方法': '第二章 基础共形映射方法',
    '3.基于几何优化的方法': '第三章 基于几何优化的方法',
    '4.全局参数化方法': '第四章 全局参数化方法',
    '5.几何优化方法': '第五章 几何优化方法',
    '5.最优传输': '第五章 最优传输',
    '6.最优传输方法': '第六章 最优传输方法',
    '6.附录': '附录',
    '7.附录': '附录',
}


def packpdf_root() -> Path:
    return Path(__file__).resolve().parent.parent


def repo_root() -> Path:
    return packpdf_root().parent.parent


def default_posts_dir() -> Path:
    return repo_root() / '_posts' / '1.Parameterization'


def extract_all_image_urls(files: list[Path]) -> list[str]:
    urls: set[str] = set()
    for fp in files:
        text = fp.read_text('utf-8')
        text = re.sub(r'^---.*?\n---\n', '', text, flags=re.DOTALL, count=1)
        for m in re.finditer(r'!\[([^\]]*)\]\((https?://[^)]+)\)', text):
            urls.add(m.group(2))
    return sorted(urls)


def url_to_fname(url: str) -> str:
    path_part = url.rsplit('/', 1)[-1]
    fname = unquote(path_part)
    fname = re.sub(r'[^\w.\-]', '_', fname)
    if '.' not in fname[-6:]:
        fname += '.png'
    if len(fname) > 120:
        ext = fname.rsplit('.', 1)[-1] if '.' in fname else 'png'
        fname = hashlib.md5(url.encode()).hexdigest()[:12] + '.' + ext
    return fname


def download_image(url: str, local_path: Path) -> tuple[str, str | None, bool]:
    if local_path.exists() and local_path.stat().st_size > 100:
        return url, str(local_path), True
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            local_path.write_bytes(resp.read())
        return url, str(local_path), True
    except Exception as e:
        return url, None, False


def download_all_images(
    urls: list[str],
    img_dir: Path,
    *,
    max_workers: int = 8,
    on_log: LogFn | None = None,
) -> dict[str, str | None]:
    img_dir.mkdir(parents=True, exist_ok=True)
    tasks = [(url, (img_dir / url_to_fname(url)).resolve()) for url in urls]
    url_map: dict[str, str | None] = {}
    total = len(tasks)

    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    log(f'  共 {total} 张图片，并行下载 (workers={max_workers})...')
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(download_image, url, local): url for url, local in tasks}
        done = 0
        for f in as_completed(futures):
            done += 1
            url, local, ok = f.result()
            url_map[url] = local if ok else None
            if done % 50 == 0 or done == total:
                succeeded = sum(1 for v in url_map.values() if v is not None)
                log(f'  [{done}/{total}] 已下载，成功 {succeeded} 张')

    failed = total - sum(1 for v in url_map.values() if v is not None)
    log(f'  完成: {total - failed} 成功, {failed} 失败')
    return url_map


def collect_files(posts_dir: Path) -> list[Path]:
    files: list[Path] = []
    for root, _dirs, filenames in os.walk(posts_dir):
        for f in sorted(filenames):
            if f.endswith('.md') and '暂存' not in f and '问题' not in f:
                files.append(Path(root) / f)
    files.sort(key=lambda p: p.relative_to(posts_dir).parts)
    return files


def build_combined_md(
    posts_dir: Path,
    output_md: Path,
    url_map: dict[str, str | None] | None = None,
    *,
    on_log: LogFn | None = None,
) -> Path:
    files = collect_files(posts_dir)
    lines = [
        '---',
        'title: 参数化算法：从理论到实现',
        'author: "李雄国"',
        'documentclass: ctexart',
        'toc: true',
        'toc-depth: 2',
        'numbersections: true',
        'papersize: a4',
        'fontsize: 12pt',
        'linestretch: 1.5',
        'geometry: margin=2.5cm',
        '---',
        '',
    ]

    cur_dir: str | None = None
    for idx, fp in enumerate(files):
        rel = fp.relative_to(posts_dir)
        dk = rel.parts[0] if len(rel.parts) > 1 else ''
        raw = fp.read_text(encoding='utf-8')
        tm = re.search(r'title:\s*"([^"]*)"', raw)
        title = tm.group(1) if tm else rel.stem
        content = strip_frontmatter(raw)
        content = preprocess_content(content, url_map)

        if dk != cur_dir:
            cur_dir = dk
            label = CHAPTER_NAMES.get(dk, dk)
            lines.append(r'\newpage')
            lines.append(f'# {label}')

        lines.extend([f'## {title}', '', content, ''])

        msg = f'  [{idx + 1}/{len(files)}] {title}'
        if on_log:
            on_log(msg)
        else:
            print(msg)

    combined = '\n'.join(lines)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(combined, encoding='utf-8')
    return output_md


def run_pandoc_tectonic(md_file: Path, output: Path) -> None:
    ensure_toolchain_path()
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
        err = (result.stderr or result.stdout or '')[-2000:]
        raise RuntimeError(f'pandoc 失败 (exit {result.returncode}):\n{err}')


def build_monograph_pdf(
    *,
    posts_dir: Path | None = None,
    output: Path | None = None,
    work_dir: Path | None = None,
    include_images: bool = True,
    on_log: LogFn | None = None,
) -> Path:
    """构建整本专著 PDF，返回输出路径。"""
    root = packpdf_root()
    posts = posts_dir or default_posts_dir()
    work = work_dir or (root / 'build' / 'monograph')
    work.mkdir(parents=True, exist_ok=True)
    out = output or (repo_root() / '参数化算法专著.pdf')
    tmp_md = work / 'monograph_combined.md'
    img_dir = work / 'images'

    def log(msg: str) -> None:
        if on_log:
            on_log(msg)
        else:
            print(msg)

    files = collect_files(posts)
    url_map: dict[str, str | None] | None = None

    if include_images:
        log('步骤 0: 提取并下载图片...')
        urls = extract_all_image_urls(files)
        log(f'  发现 {len(urls)} 张远程图片')
        url_map = download_all_images(urls, img_dir, on_log=on_log)
    else:
        log('【无图片模式】跳过图片下载')

    log('步骤 1: 合并专著 Markdown...')
    build_combined_md(posts, tmp_md, url_map, on_log=on_log)
    log(f'  合并文件: {tmp_md}')

    log(f'步骤 2: pandoc + tectonic -> {out.name}')
    run_pandoc_tectonic(tmp_md, out)
    log(f'完成: {out} ({out.stat().st_size / 1024 / 1024:.1f} MB)')
    return out
