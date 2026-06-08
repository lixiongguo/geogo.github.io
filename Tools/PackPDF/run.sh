#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "[错误] 未找到 Python"
  exit 1
fi

if [[ -x .venv/bin/python ]]; then
  PY=.venv/bin/python
fi

"$PY" -m pip install -q -r requirements.txt 2>/dev/null || true
exec "$PY" app.py
