"""检查 _posts/ 中 {% post_url ... %} 引用是否存在。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PostRef:
    """单个 post_url 引用。"""
    slug: str       # 引用中的文件名 stem，如 "2017-09-01-向量场的平行移动"
    file: Path      # 引用所在文件的路径
    line: int       # 所在行号
    raw: str        # 原始匹配文本


@dataclass
class BrokenRef:
    """一个断裂的引用。"""
    ref: PostRef
    suggestion: str = ""  # 可能的正确文件名


@dataclass
class FileCheckResult:
    """单个文件的检查结果。"""
    path: str
    broken: list[BrokenRef] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.broken) == 0


@dataclass
class PostCheckResult:
    """全局 post_url 检查结果。"""
    files: list[FileCheckResult] = field(default_factory=list)

    @property
    def files_with_issues(self) -> int:
        return sum(1 for f in self.files if not f.ok)

    @property
    def total_files(self) -> int:
        return len(self.files)

    @property
    def total_broken(self) -> int:
        return sum(len(f.broken) for f in self.files)


# 匹配 {% post_url 2017-09-01-向量场的平行移动 %}
_POST_URL_RE = re.compile(r'\{%-?\s*post_url\s+([^\s%]+).*?%\}')

# 匹配文件名 → 提取 stem（日期前缀 + 标题）
# e.g. "2017-09-01-向量场的联络与拓扑.md" → "2017-09-01-向量场的联络与拓扑"
_FILE_STEM_RE = re.compile(r'^(\d{4}-\d{2}-\d{2}-.+?)\.(?:md|markdown|html)$')


def _find_post_file(slug: str, posts_dir: Path) -> Path | None:
    """在 posts_dir 下递归查找匹配 slug 的文件。"""
    slug_norm = slug.strip()
    candidates = list(posts_dir.rglob(f"{slug_norm}.md"))
    if candidates:
        return candidates[0]
    candidates = list(posts_dir.rglob(f"{slug_norm}.markdown"))
    if candidates:
        return candidates[0]
    # 模糊匹配：slug 作为文件 stem 的一部分
    for f in posts_dir.rglob("*.md"):
        if f.stem == slug_norm:
            return f
    return None


def _collect_all_stems(posts_dir: Path) -> set[str]:
    """收集 posts_dir 下所有 .md 文件的 stem。"""
    stems: set[str] = set()
    for f in posts_dir.rglob("*.md"):
        stems.add(f.stem)
    for f in posts_dir.rglob("*.markdown"):
        stems.add(f.stem)
    return stems


def _suggest_stem(slug: str, all_stems: set[str]) -> str:
    """对断裂的引用给出建议：查找共享日期前缀或标题相近的文件。"""
    # 提取日期部分
    date_match = re.match(r'^(\d{4}-\d{2}-\d{2})', slug)
    date_prefix = date_match.group(1) if date_match else ""
    # 提取标题关键词
    slug_title = slug[11:] if len(slug) > 11 else slug  # 去掉日期前缀

    best = ""
    best_score = 0
    for stem in all_stems:
        score = 0
        if date_prefix and stem.startswith(date_prefix):
            score += 100
        # 简单子串匹配
        for ch in slug_title:
            if ch in stem:
                score += 1
        if score > best_score:
            best_score = score
            best = stem

    if best_score > len(slug_title) * 0.3:
        return best
    return ""


def check_file(filepath: str | Path) -> list[BrokenRef]:
    """检查单个文件中的 post_url 引用。"""
    fp = Path(filepath)
    posts_dir = fp.parent
    # 向上查找 _posts 根目录
    while posts_dir.name != "_posts" and posts_dir.parent != posts_dir:
        posts_dir = posts_dir.parent
    if posts_dir.name != "_posts":
        # 如果不在 _posts 下，用 filepath 的 parent 作为搜索根
        posts_dir = fp.parent

    all_stems = _collect_all_stems(posts_dir)
    broken: list[BrokenRef] = []

    with open(fp, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            for m in _POST_URL_RE.finditer(line):
                slug = m.group(1).strip()
                found = _find_post_file(slug, posts_dir)
                if found is None:
                    suggestion = _suggest_stem(slug, all_stems)
                    broken.append(BrokenRef(
                        ref=PostRef(slug=slug, file=fp, line=lineno, raw=m.group(0)),
                        suggestion=suggestion,
                    ))

    return broken


def check_directory(root: str | Path, *, recursive: bool = True) -> PostCheckResult:
    """检查目录下所有 .md 文件的 post_url 引用。"""
    rp = Path(root)
    if not rp.is_dir():
        raise ValueError(f"不是目录: {root}")

    files: list[FileCheckResult] = []
    glob = rp.rglob("*.md") if recursive else rp.glob("*.md")

    for fp in sorted(glob):
        broken = check_file(fp)
        files.append(FileCheckResult(path=str(fp), broken=broken))

    return PostCheckResult(files=files)
