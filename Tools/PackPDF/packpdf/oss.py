"""阿里云 OSS 图床：扫描、上传、替换 Markdown 中的本地图片路径。"""

from __future__ import annotations

import re
import time
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

try:
    import oss2
except ImportError:
    oss2 = None  # type: ignore

from packpdf.paths import subdir_path

LogFn = Callable[[str, str], None]  # (message, level: info|warn|error)

OSS_ENDPOINT = 'https://oss-cn-beijing.aliyuncs.com'
OSS_BUCKET = 'lgximgs'
OSS_BASE = 'https://lgximgs.oss-cn-beijing.aliyuncs.com/images/'

MD_IMG = re.compile(r'(!\[[^\]]*\])\(([^)]*imgs[/\\][^)]+)\)', re.IGNORECASE)
HTML_IMG = re.compile(r'(<img\s[^>]*src=["\'])([^"\']*imgs[/\\][^"\']+)(["\'][^>]*>)', re.IGNORECASE)
OSS_URL = re.compile(r'https?://lgximgs\.oss-cn-beijing\.aliyuncs\.com/images/', re.IGNORECASE)

CT = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml',
}


def _log(on_log: LogFn | None, msg: str, level: str = 'info') -> None:
    if on_log:
        on_log(msg, level)
    else:
        print(msg)


def extract_filename(path_str: str) -> str | None:
    normalized = path_str.replace('\\', '/')
    idx = normalized.find('imgs/')
    if idx == -1:
        return None
    return normalized[idx + 5:].lstrip('/')


def is_local(path_str: str) -> bool:
    s = path_str.strip()
    return not bool(OSS_URL.match(s) or s.startswith('http://') or s.startswith('https://'))


def resolve_imgs_dir(from_root: Path, imgs_subdir: str = 'imgs') -> Path:
    """从项目根向上查找 imgs/ 目录（通常在仓库根目录）。"""
    root = from_root.resolve()
    for base in (root, *root.parents):
        candidate = base / imgs_subdir
        if candidate.is_dir():
            return candidate
    return root / imgs_subdir


def _scan_md_file(md: Path, images: dict[str, list[tuple[Path, str]]]) -> None:
    content = md.read_text(encoding='utf-8')
    for pattern in (MD_IMG, HTML_IMG):
        for m in pattern.finditer(content):
            path_str = m.group(2)
            if not is_local(path_str):
                continue
            fn = extract_filename(path_str)
            if not fn:
                continue
            images.setdefault(fn, []).append((md, path_str))


def collect_local_images(posts_dir: Path) -> dict[str, list[tuple[Path, str]]]:
    images: dict[str, list[tuple[Path, str]]] = {}
    if not posts_dir.is_dir():
        return images
    for md in sorted(posts_dir.rglob('*.md')):
        _scan_md_file(md, images)
    return images


def collect_local_images_in_dirs(dirs: list[Path]) -> dict[str, list[tuple[Path, str]]]:
    """扫描指定目录（章节）下 .md 中的本地 imgs/ 引用。"""
    images: dict[str, list[tuple[Path, str]]] = {}
    for posts_dir in dirs:
        if not posts_dir.is_dir():
            continue
        for md in sorted(posts_dir.rglob('*.md')):
            _scan_md_file(md, images)
    return images


@dataclass
class OssScanResult:
    chapter_names: list[str]
    chapter_dirs: list[Path]
    images: dict[str, list[tuple[Path, str]]]
    imgs_dir: Path

    @property
    def unique(self) -> int:
        return len(self.images)

    @property
    def refs(self) -> int:
        return sum(len(v) for v in self.images.values())

    @property
    def missing(self) -> list[str]:
        return [fn for fn in self.images if not (self.imgs_dir / fn).exists()]

    def refs_by_document(self) -> list[tuple[Path, list[tuple[str, str]]]]:
        """按文档分组：(md_path, [(filename, url_path), ...])。"""
        grouped: dict[Path, list[tuple[str, str]]] = {}
        for fn, refs in self.images.items():
            for md, path_str in refs:
                grouped.setdefault(md, []).append((fn, path_str))
        return sorted(grouped.items(), key=lambda item: str(item[0]))


def scan_pack_chapters(
    project_root: Path,
    chapter_names: list[str],
    *,
    imgs_subdir: str = 'imgs',
) -> OssScanResult:
    """扫描待打包章节中的本地图片 URL 引用。"""
    chapter_dirs = [subdir_path(project_root, name) for name in chapter_names]
    imgs_dir = resolve_imgs_dir(project_root, imgs_subdir)
    images = collect_local_images_in_dirs(chapter_dirs)
    return OssScanResult(
        chapter_names=list(chapter_names),
        chapter_dirs=chapter_dirs,
        images=images,
        imgs_dir=imgs_dir,
    )


@dataclass
class OssUploadResult:
    success: bool
    uploaded: int = 0
    replaced: int = 0
    skipped_missing: int = 0
    failed: list[str] = field(default_factory=list)
    error: str = ''


def upload_and_replace(
    project_root: Path,
    *,
    access_key_id: str,
    access_key_secret: str,
    posts_subdir: str = '_posts',
    imgs_subdir: str = 'imgs',
    dry_run: bool = False,
    on_log: LogFn | None = None,
) -> OssUploadResult:
    if oss2 is None:
        return OssUploadResult(success=False, error='未安装 oss2，请运行: pip install oss2')

    if not access_key_id or not access_key_secret:
        return OssUploadResult(success=False, error='请填写 OSS AccessKey ID 和 Secret（或设置环境变量）')

    posts_dir = project_root / posts_subdir
    if not posts_dir.is_dir():
        return OssUploadResult(success=False, error=f'文章目录不存在: {posts_dir}')

    imgs_dir = resolve_imgs_dir(project_root, imgs_subdir)

    _log(on_log, f'扫描 {posts_dir} 中的本地图片引用...', 'info')
    images = collect_local_images(posts_dir)
    if not images:
        _log(on_log, '未发现需要处理的本地图片。', 'info')
        return OssUploadResult(success=True)

    ref_count = sum(len(v) for v in images.values())
    _log(on_log, f'发现 {len(images)} 张唯一图片，共 {ref_count} 处引用。', 'info')

    if dry_run:
        for fn, refs in sorted(images.items()):
            _log(on_log, f'  {fn} ({len(refs)} 处引用)', 'info')
            for md, old_path in refs:
                new_url = OSS_BASE + urllib.parse.quote(fn, safe='-_.~!$&\'()*+,;=@')
                _log(on_log, f'    {md.name}: {old_path}', 'info')
                _log(on_log, f'      -> {new_url}', 'warn')
        _log(on_log, '[预览模式] 未上传、未修改文件。', 'warn')
        return OssUploadResult(success=True)

    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET)
    uploaded: set[str] = set()
    skipped_missing = 0
    failed: list[str] = []
    total = len(images)

    _log(on_log, '开始上传到 OSS...', 'info')
    for i, fn in enumerate(sorted(images.keys())):
        lp = imgs_dir / fn
        if not lp.exists():
            _log(on_log, f'[{i + 1}/{total}] SKIP_MISS {fn}', 'warn')
            skipped_missing += 1
            continue

        try:
            bucket.head_object('images/' + fn)
            _log(on_log, f'[{i + 1}/{total}] EXIST {fn}', 'info')
            uploaded.add(fn)
            continue
        except oss2.exceptions.NoSuchKey:
            pass
        except Exception as e:
            _log(on_log, f'[{i + 1}/{total}] HEAD_FAIL {fn}: {e}', 'warn')

        ct = CT.get(lp.suffix.lower(), 'application/octet-stream')
        ok = False
        for attempt in range(4):
            try:
                bucket.put_object_from_file('images/' + fn, str(lp), headers={'Content-Type': ct})
                _log(on_log, f'[{i + 1}/{total}] OK {fn}', 'info')
                uploaded.add(fn)
                ok = True
                break
            except Exception as e:
                if attempt < 3:
                    time.sleep(2 ** attempt)
                else:
                    _log(on_log, f'[{i + 1}/{total}] FAIL {fn}: {e}', 'error')
                    failed.append(fn)
        if (i + 1) % 20 == 0:
            time.sleep(0.5)

    if failed:
        _log(on_log, f'上传失败 {len(failed)} 张，将跳过这些文件的替换。', 'error')

    _log(on_log, '替换 Markdown 中的图片路径...', 'info')
    replaced = 0
    for fn in sorted(uploaded):
        encoded = urllib.parse.quote(fn, safe='-_.~!$&\'()*+,;=@')
        new_url = OSS_BASE + encoded
        for md, old_path in images[fn]:
            content = md.read_text(encoding='utf-8')
            if old_path not in content:
                continue
            content = content.replace(old_path, new_url)
            md.write_text(content, encoding='utf-8')
            replaced += 1
            rel = md.relative_to(project_root) if md.is_relative_to(project_root) else md
            _log(on_log, f'  OK {rel}: {fn}', 'info')

    _log(
        on_log,
        f'完成：上传/已存在 {len(uploaded)} 张，替换 {replaced} 处，缺失 {skipped_missing} 张，失败 {len(failed)} 张。',
        'info' if not failed else 'warn',
    )
    return OssUploadResult(
        success=len(failed) == 0,
        uploaded=len(uploaded),
        replaced=replaced,
        skipped_missing=skipped_missing,
        failed=failed,
    )


def scan_summary(project_root: Path, posts_subdir: str = '_posts', imgs_subdir: str = 'imgs') -> dict:
    posts_dir = project_root / posts_subdir
    imgs_dir = resolve_imgs_dir(project_root, imgs_subdir)
    images = collect_local_images(posts_dir) if posts_dir.is_dir() else {}
    missing = [fn for fn in images if not (imgs_dir / fn).exists()]
    return {
        'unique': len(images),
        'refs': sum(len(v) for v in images.values()),
        'missing': missing,
    }
