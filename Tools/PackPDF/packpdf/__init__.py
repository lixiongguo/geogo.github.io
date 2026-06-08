"""PackPDF — 将 Markdown 文章目录合并打包为 PDF。"""

from .core import MergeResult, merge_chapters_to_pdf, merge_to_pdf
from .deps import check_deps, ensure_toolchain_path
from .monograph import build_monograph_pdf

__all__ = [
    'MergeResult',
    'merge_to_pdf',
    'merge_chapters_to_pdf',
    'check_deps',
    'ensure_toolchain_path',
    'build_monograph_pdf',
]
