"""Load cpp/wasm_packages.yaml manifest."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
MANIFEST_PATH = REPO_ROOT / "cpp" / "wasm_packages.yaml"
OUTPUT_DIR = REPO_ROOT / "assets" / "wasm"
BUILD_SCRIPT = REPO_ROOT / "cpp" / "build_wasm.ps1"


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    path = path or MANIFEST_PATH
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def resolve_sources(manifest: dict[str, Any], pkg: dict[str, Any]) -> list[str]:
    groups = manifest.get("source_groups") or {}
    out: list[str] = []
    for item in pkg.get("sources") or []:
        if isinstance(item, dict) and "group" in item:
            out.extend(groups.get(item["group"], []))
        elif isinstance(item, str):
            out.append(item)
    return out
