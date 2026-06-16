"""Package model and overlap analysis."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from manifest_loader import OUTPUT_DIR, load_manifest, resolve_sources


@dataclass
class PackageInfo:
    name: str
    kind: str
    export_name: str
    make_target: str
    methods: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    wasm_size: int | None = None
    js_size: int | None = None
    built: bool = False
    pages: list[tuple[str, str]] = field(default_factory=list)  # (page, load mode)


def _file_size(path: Path) -> int | None:
    return path.stat().st_size if path.exists() else None


def build_package_model(manifest: dict[str, Any] | None = None) -> list[PackageInfo]:
    manifest = manifest or load_manifest()
    packages_cfg = manifest.get("packages") or {}
    pages_cfg = manifest.get("pages") or {}

    page_refs: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for page, cfg in pages_cfg.items():
        for ref in cfg.get("packages") or []:
            page_refs[ref["name"]].append((page, ref.get("load", "eager")))

    result: list[PackageInfo] = []
    for name, cfg in packages_cfg.items():
        wasm = OUTPUT_DIR / f"{name}.wasm"
        js = OUTPUT_DIR / f"{name}.js"
        info = PackageInfo(
            name=name,
            kind=cfg.get("kind", "compat"),
            export_name=cfg.get("export_name", name),
            make_target=cfg.get("make_target", ""),
            methods=list(cfg.get("methods") or []),
            exports=list(cfg.get("exports") or []),
            sources=resolve_sources(manifest, cfg),
            wasm_size=_file_size(wasm),
            js_size=_file_size(js),
            built=wasm.exists() and js.exists(),
            pages=page_refs.get(name, []),
        )
        result.append(info)
    return result


def source_overlap(packages: list[PackageInfo]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for pkg in packages:
        for src in pkg.sources:
            index[src].append(pkg.name)
    return {src: names for src, names in index.items() if len(names) > 1}
