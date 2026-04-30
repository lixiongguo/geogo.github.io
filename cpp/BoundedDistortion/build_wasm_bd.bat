@echo off
REM build_wasm_bd.bat — 编译 Bounded Distortion LSCM 为 WebAssembly
REM 输出:    ../../assets/wasm/bd_lscm_solver.js / .wasm

echo ============================================
echo   BD-LSCM WASM Build
echo   Bounded Distortion + LSCM via Eigen
echo ============================================

REM ── 激活 Emscripten 环境 ────────────────────
call "%~dp0..\emsdk\emsdk_env.bat"

REM ── 检查 emcc ────────────────────────────────
where emcc >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] emcc 未找到
    pause
    exit /b 1
)
echo [OK] emcc 编译器就绪

REM ── 路径 (相对于 BoundedDistortion 目录) ──────
set SRC_DIR=%~dp0
set EIGEN_DIR=%SRC_DIR%..\conformal-parameterization\deps\Eigen
set BD_DIR=%SRC_DIR%.
set OUT_DIR=%SRC_DIR%..\..\assets\wasm

if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo.
echo [编译] wasm_bd_lscm.cpp  ->  bd_lscm_solver.js

cd /d "%SRC_DIR%"

emcc ^
    wasm_bd_lscm.cpp ^
    -I"%EIGEN_DIR%\.." ^
    -I"%BD_DIR%" ^
    -s MODULARIZE=1 ^
    -s EXPORT_NAME="BDLSCMSolver" ^
    -s "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','setValue','getValue']" ^
    -s "EXPORTED_FUNCTIONS=['_malloc','_free','_solve_bd_lscm','_get_bd_uv_result','_get_bd_uv_result_size','_get_bd_last_time_ms','_bd_dispose']" ^
    -s ALLOW_MEMORY_GROWTH=1 ^
    -s WASM=1 ^
    -s FILESYSTEM=0 ^
    -std=c++17 ^
    -O2 ^
    -o "%OUT_DIR%\bd_lscm_solver.js"

if %ERRORLEVEL% NEQ 0 (
    echo [失败] 编译出错
    exit /b 1
)

echo.
if exist "%OUT_DIR%\bd_lscm_solver.js"  echo [OK] %OUT_DIR%\bd_lscm_solver.js
if exist "%OUT_DIR%\bd_lscm_solver.wasm" echo [OK] %OUT_DIR%\bd_lscm_solver.wasm

echo.
echo ============================================
echo   编译完成！
echo ============================================
pause
