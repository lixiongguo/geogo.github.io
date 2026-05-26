"""Resolve PyMongeAmpere build directory and prepend to sys.path.

Set PYMongeAmpere_BUILD to an absolute path to force a specific build tree.
Otherwise tries, in order:
  ../PyMongeAmpere-build/   (legacy layout next to reflector-master)
  ../ma_ot/PyMongeAmpere-build-wsl/  (WSL build from cpp/ma_ot/build_wsl.sh)
"""
from __future__ import print_function

import os
import sys


def ensure_pymonge_on_path():
    _here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(_here, ".."))
    candidates = []
    env = os.environ.get("PYMongeAmpere_BUILD")
    if env:
        candidates.append(os.path.abspath(env))
    candidates.extend(
        [
            os.path.normpath(os.path.join(root, "..", "PyMongeAmpere-build")),
            os.path.normpath(
                os.path.join(root, "..", "ma_ot", "PyMongeAmpere-build-wsl")
            ),
        ]
    )
    seen = set()
    for cand in candidates:
        if cand in seen or not os.path.isdir(cand):
            continue
        seen.add(cand)
        for p in (cand, os.path.join(cand, "lib")):
            if os.path.isdir(p) and p not in sys.path:
                sys.path.insert(0, p)
