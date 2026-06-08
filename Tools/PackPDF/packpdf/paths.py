"""项目路径与子目录索引。"""

from __future__ import annotations

from pathlib import Path


PDF_OUTPUT_DIRNAME = 'PDF_output'


def pdf_output_dir(project_root: Path) -> Path:
    d = (project_root.resolve() / PDF_OUTPUT_DIRNAME)
    d.mkdir(parents=True, exist_ok=True)
    return d


def list_markdown_subdirs(project_root: Path) -> list[str]:
    """根目录下的一层子目录（含至少一个 .md 文件）。"""
    if not project_root.is_dir():
        return []
    names: list[str] = []
    for d in sorted(project_root.iterdir()):
        if d.is_dir() and any(d.glob('*.md')):
            names.append(d.name)
    return names


def subdir_path(project_root: Path, name: str) -> Path:
    return (project_root / name).resolve()


def default_pdf_path(project_root: Path, subdir_name: str) -> Path:
    safe = subdir_name.strip() or 'output'
    return pdf_output_dir(project_root) / f'{safe}.pdf'


def output_pdf_for_chapters(project_root: Path, chapter_names: list[str]) -> Path:
    pdf_output_dir(project_root)
    if len(chapter_names) == 1:
        return default_pdf_path(project_root, chapter_names[0])
    base = project_root.name.strip() or '合集'
    return project_root / PDF_OUTPUT_DIRNAME / f'{base}_合集.pdf'


def document_title_for_chapters(project_root: Path, chapter_names: list[str]) -> str:
    if len(chapter_names) == 1:
        return chapter_names[0]
    return project_root.name.strip() or '合集'
