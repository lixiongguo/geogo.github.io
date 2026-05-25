#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OVERLAY="$ROOT/_ddg-overlay"
TARGET="$ROOT/ddg-exercises-js"

if [[ ! -d "$TARGET/projects" ]]; then
  echo "ddg-exercises-js submodule not initialized; run: git submodule update --init ddg-exercises-js"
  exit 1
fi

cp -f "$OVERLAY/projects/index.html" "$TARGET/projects/index.html"
cp -f "$OVERLAY/projects/project-nav.js" "$TARGET/projects/project-nav.js"
cp -f "$OVERLAY/style/main.css" "$TARGET/style/main.css"

NAV_MARK='id="project-nav-wrap"'
NAV_HTML=$'	<div id="project-nav-wrap" data-current="PROJECT_ID"></div>\n\t<script src="../project-nav.js"></script>\n'

for dir in "$TARGET/projects"/*/; do
  index="$dir/index.html"
  [[ -f "$index" ]] || continue
  if grep -q "$NAV_MARK" "$index"; then
    continue
  fi
  project_id="$(basename "$dir")"
  snippet="${NAV_HTML//PROJECT_ID/$project_id}"
  # shellcheck disable=SC2016
  python3 - "$index" "$snippet" <<'PY'
import sys
path, snippet = sys.argv[1], sys.argv[2]
text = open(path, encoding="utf-8").read()
needle = "<body>"
if needle not in text:
    sys.exit(f"no <body> in {path}")
open(path, "w", encoding="utf-8").write(text.replace(needle, needle + "\n" + snippet, 1))
PY
  echo "patched $project_id"
done

echo "DDG overlay applied."
