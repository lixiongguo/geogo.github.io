"""Markdown 字数统计。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_CJK_RE = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]')


def count_chinese(text: str) -> int:
    return len(_CJK_RE.findall(text))


@dataclass
class FileWordCount:
    path: str
    chars: int
    cjk: int

    def rel_path(self, root: str | Path) -> str:
        try:
            return str(Path(self.path).relative_to(Path(root).resolve()))
        except ValueError:
            return self.path


@dataclass
class WordCountResult:
    files: list[FileWordCount] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        return len(self.files)

    @property
    def total_chars(self) -> int:
        return sum(f.chars for f in self.files)

    @property
    def total_cjk(self) -> int:
        return sum(f.cjk for f in self.files)


def count_file(filepath: str | Path) -> FileWordCount:
    path = Path(filepath)
    text = path.read_text(encoding='utf-8')
    return FileWordCount(path=str(path.resolve()), chars=len(text), cjk=count_chinese(text))


def count_directory(root: str | Path, *, recursive: bool = True) -> WordCountResult:
    root = Path(root)
    pattern = '**/*.md' if recursive else '*.md'
    files = sorted(root.glob(pattern))
    return WordCountResult(files=[count_file(fp) for fp in files])


def count_paths(paths: list[str | Path]) -> WordCountResult:
    """递归统计多个章节目录下的 .md 文件。"""
    md_files: list[Path] = []
    for raw in paths:
        root = Path(raw)
        if root.is_dir():
            md_files.extend(root.rglob('*.md'))
    unique = sorted({fp.resolve() for fp in md_files})
    return WordCountResult(files=[count_file(fp) for fp in unique])
