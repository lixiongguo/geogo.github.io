@echo off
setlocal
cd /d "%~dp0"

REM 常见 Pandoc / MiKTeX 路径（若已在 PATH 中可忽略）
set "PATH=C:\Program Files\Pandoc;C:\Program Files\MiKTeX\miktex\bin\x64;%PATH%"

python --version >nul 2>&1
if errorlevel 1 (
  echo [错误] 未找到 Python，请先安装 Python 3.9+
  pause
  exit /b 1
)

if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

"%PY%" -m pip install -q -r requirements.txt 2>nul
"%PY%" app.py
endlocal
