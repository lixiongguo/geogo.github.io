#!/usr/bin/env bash
# Build WASM packages via conformal-parameterization/wasm/Makefile
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MAKE_DIR="$SCRIPT_DIR/conformal-parameterization/wasm"
MANIFEST="$SCRIPT_DIR/wasm_packages.yaml"

TARGET="${1:-page}"

resolve_make_target() {
  local name="$1"
  case "$name" in
    page|page-all) echo "build-page-all" ;;
    all) echo "build-all" ;;
    *)
      if command -v python3 >/dev/null 2>&1; then
        python3 - "$name" "$MANIFEST" <<'PY'
import sys, yaml
from pathlib import Path
name, path = sys.argv[1], Path(sys.argv[2])
data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
pkg = (data.get("packages") or {}).get(name) or {}
print(pkg.get("make_target", ""))
PY
      else
        echo ""
      fi
      ;;
  esac
}

MAKE_TARGET="$(resolve_make_target "$TARGET")"
if [[ -z "$MAKE_TARGET" ]]; then
  echo "Unknown target: $TARGET" >&2
  exit 1
fi

if ! command -v em++ >/dev/null 2>&1; then
  if [[ -f "$REPO_ROOT/cpp/emsdk/emsdk_env.sh" ]]; then
    # shellcheck disable=SC1091
    source "$REPO_ROOT/cpp/emsdk/emsdk_env.sh"
  fi
fi

echo "[build_wasm.sh] make -C $MAKE_DIR $MAKE_TARGET"
make -C "$MAKE_DIR" "$MAKE_TARGET"
