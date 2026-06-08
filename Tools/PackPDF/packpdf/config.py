"""PackPDF 配置读写。"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field


def _config_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, 'config.json')


def default_project_root() -> str:
    """Tools/PackPDF -> 仓库根目录。"""
    return os.path.normpath(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', '..')
    )


@dataclass
class AppConfig:
    project_root: str = ''
    last_markdown_subdir: str = ''
    selected_chapters: list[str] = field(default_factory=list)
    single_chapter: bool = True
    check_dir: str = ''
    posts_subdir: str = '_posts'
    imgs_subdir: str = 'imgs'
    oss_access_key_id: str = ''
    oss_access_key_secret: str = ''
    remember_oss_keys: bool = False
    extra_path: list[str] = field(default_factory=list)
    window_geometry: str = '820x720'
    # 兼容旧版 config，加载后忽略
    input_dir: str = ''
    output_pdf: str = ''
    title: str = ''


def load_config() -> AppConfig:
    path = _config_path()
    cfg = AppConfig()
    if not cfg.project_root:
        cfg.project_root = default_project_root()
    if not cfg.check_dir:
        cfg.check_dir = os.path.join(cfg.project_root, '_posts')
    if not os.path.exists(path):
        return cfg
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        for key, value in data.items():
            if hasattr(cfg, key):
                setattr(cfg, key, value)
        if not cfg.project_root:
            cfg.project_root = default_project_root()
        if not cfg.check_dir:
            cfg.check_dir = os.path.join(cfg.project_root, '_posts')
        return cfg
    except Exception:
        return cfg


def save_config(cfg: AppConfig) -> None:
    data = asdict(cfg)
    if not cfg.remember_oss_keys:
        data['oss_access_key_id'] = ''
        data['oss_access_key_secret'] = ''
    path = _config_path()
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
