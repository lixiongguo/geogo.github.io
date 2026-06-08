"""检测 pandoc / xelatex 等外部依赖，并补全 PATH。"""

from __future__ import annotations

import os
import platform
import shutil
from dataclasses import dataclass
from typing import Iterable


@dataclass
class ToolStatus:
    name: str
    found: bool
    path: str | None = None


def _candidate_dirs() -> list[str]:
    system = platform.system()
    dirs: list[str] = []

    if system == 'Windows':
        dirs.extend([
            r'C:\Program Files\Pandoc',
            r'C:\Program Files (x86)\Pandoc',
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Pandoc'),
            r'C:\Program Files\MiKTeX\miktex\bin\x64',
            r'C:\Program Files (x86)\MiKTeX\miktex\bin\x64',
            r'C:\texlive\2025\bin\windows',
            r'C:\texlive\2024\bin\windows',
            r'C:\texlive\2023\bin\windows',
        ])
    elif system == 'Darwin':
        dirs.extend([
            '/opt/homebrew/bin',
            '/usr/local/bin',
            '/Library/TeX/texbin',
        ])
    else:
        dirs.extend([
            '/usr/bin',
            '/usr/local/bin',
            '/snap/bin',
        ])

    extra = os.environ.get('PACKPDF_EXTRA_PATH', '')
    if extra:
        dirs.extend(p.strip() for p in extra.split(os.pathsep) if p.strip())
    return [d for d in dirs if d and os.path.isdir(d)]


def ensure_toolchain_path(extra_dirs: Iterable[str] | None = None) -> list[str]:
    """将常见安装目录 prepend 到 PATH，返回实际追加的目录。"""
    added: list[str] = []
    path_parts = os.environ.get('PATH', '').split(os.pathsep)
    seen = {p.lower() for p in path_parts if p}

    for d in list(_candidate_dirs()) + list(extra_dirs or []):
        norm = os.path.normpath(d)
        key = norm.lower()
        if key not in seen:
            path_parts.insert(0, norm)
            seen.add(key)
            added.append(norm)

    os.environ['PATH'] = os.pathsep.join(path_parts)
    return added


def _which(cmd: str) -> str | None:
    return shutil.which(cmd)


def check_deps(extra_dirs: Iterable[str] | None = None) -> dict[str, ToolStatus]:
    ensure_toolchain_path(extra_dirs)
    result: dict[str, ToolStatus] = {}
    for cmd in ('pandoc', 'xelatex'):
        path = _which(cmd)
        result[cmd] = ToolStatus(name=cmd, found=path is not None, path=path)
    return result


def deps_ok(extra_dirs: Iterable[str] | None = None) -> bool:
    return all(s.found for s in check_deps(extra_dirs).values())


def format_deps_summary(status: dict[str, ToolStatus]) -> str:
    """单行依赖状态摘要。"""
    parts: list[str] = []
    for s in status.values():
        if s.found:
            parts.append(f'{s.name}: OK')
        else:
            parts.append(f'{s.name}: 缺失')
    return '  |  '.join(parts)


def format_deps_report(status: dict[str, ToolStatus]) -> str:
    lines = ['依赖检测:']
    for s in status.values():
        if s.found:
            lines.append(f'  [OK] {s.name}: {s.path}')
        else:
            lines.append(f'  [缺失] {s.name}: 未找到（请安装 Pandoc 与 MiKTeX/TeX Live）')
    return '\n'.join(lines)
