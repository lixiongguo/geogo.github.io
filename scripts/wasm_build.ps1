# wasm_build.ps1 - 使用 emsdk 编译 conformal-parameterization 为 WebAssembly
# 使用方法: powershell -ExecutionPolicy Bypass -File scripts\wasm_build.ps1

Write-Host "==================================="
Write-Host "Conformal Parameterization WASM Build (PowerShell)"
Write-Host "==================================="

# 获取脚本所在目录的绝对路径
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# 设置路径
$EmsdkPath = Join-Path $ProjectRoot "cpp\emsdk"
$SrcDir = Join-Path $ProjectRoot "cpp\conformal-parameterization"
$OutDir = Join-Path $ProjectRoot "assets\wasm"

Write-Host "项目根目录: $ProjectRoot"
Write-Host "EMSDK 路径: $EmsdkPath"
Write-Host "源码目录: $SrcDir"
Write-Host "输出目录: $OutDir"
Write-Host ""

# 检查 emsdk 是否存在
if (-not (Test-Path $EmsdkPath)) {
    Write-Host "[错误] 未找到 emsdk 目录: $EmsdkPath" -ForegroundColor Red
    exit 1
}

# ============ 步骤 1-3: 安装并激活 emsdk ============
$emccAvailable = $false
if (Get-Command emcc -ErrorAction SilentlyContinue) {
    $emccAvailable = $true
}

if (-not $emccAvailable) {
    Write-Host "[警告] 未找到 emcc，尝试安装 Emscripten SDK..."
    Write-Host ""

    # 进入 emsdk 目录
    Push-Location $EmsdkPath

    # 更新 emsdk
    Write-Host "[步骤 1/4] 更新 emsdk..."
    git pull 2>&1 | Out-Null
    Write-Host "  (git pull 完成)" -ForegroundColor Gray

    # 安装最新版本
    Write-Host ""
    Write-Host "[步骤 2/4] 安装最新版 Emscripten (这可能需要几分钟)..."
    
    # 使用 emsdk.ps1 (PowerShell 脚本)
    $EmsdkPs1 = Join-Path $EmsdkPath "emsdk.ps1"
    if (Test-Path $EmsdkPs1) {
        & "$EmsdkPs1" install latest 2>&1 | Tee-Object -Variable INSTALL_OUTPUT
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[错误] emsdk install 失败 (退出码: $LASTEXITCODE)" -ForegroundColor Red
            Write-Host $INSTALL_OUTPUT -ForegroundColor Red
            Pop-Location
            exit 1
        }
    } else {
        # 回退到 python emsdk.py
        $PythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $PythonCmd) {
            $PythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
        }
        
        if ($PythonCmd) {
            $EmsdkPy = Join-Path $EmsdkPath "emsdk.py"
            & $PythonCmd.Name $EmsdkPy install latest 2>&1 | Tee-Object -Variable INSTALL_OUTPUT
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "[错误] emsdk install 失败" -ForegroundColor Red
                Pop-Location
                exit 1
            }
        } else {
            Write-Host "[错误] 未找到 python，无法运行 emsdk" -ForegroundColor Red
            Pop-Location
            exit 1
        }
    }

    # 激活最新版本
    Write-Host ""
    Write-Host "[步骤 3/4] 激活 Emscripten..."
    
    if (Test-Path $EmsdkPs1) {
        & "$EmsdkPs1" activate latest 2>&1 | Out-Null
    } else {
        $PythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $PythonCmd) {
            $PythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
        }
        if ($PythonCmd) {
            $EmsdkPy = Join-Path $EmsdkPath "emsdk.py"
            & $PythonCmd.Name $EmsdkPy activate latest 2>&1 | Out-Null
        }
    }

    Pop-Location
    Write-Host ""
}

# ============ 步骤 4: 激活 Emscripten 环境 ============
Write-Host "[步骤 4/4] 激活 Emscripten 环境..."

# 查找并设置 emsdk 工具到 PATH
Write-Host "  正在查找 emsdk 工具..."

# 查找 node.exe
$NodeExe = Get-ChildItem -Path $EmsdkPath -Recurse -Filter "node.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($NodeExe) {
    $NodeDir = Split-Path -Parent $NodeExe.FullName
    if ($env:PATH -notlike "*$NodeDir*") {
        $env:PATH = "$NodeDir;$env:PATH"
        Write-Host "    添加 node 路径: $NodeDir" -ForegroundColor Gray
    }
}

# 查找 python.exe
$PythonExe = Get-ChildItem -Path $EmsdkPath -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $PythonExe) {
    # 也可能叫 python3.exe
    $PythonExe = Get-ChildItem -Path $EmsdkPath -Recurse -Filter "python3.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
}
if ($PythonExe) {
    $PythonDir = Split-Path -Parent $PythonExe.FullName
    if ($env:PATH -notlike "*$PythonDir*") {
        $env:PATH = "$PythonDir;$env:PATH"
        Write-Host "    添加 python 路径: $PythonDir" -ForegroundColor Gray
    }
}

# 添加 emsdk 主目录到 PATH
if ($env:PATH -notlike "*$EmsdkPath*") {
    $env:PATH = "$EmsdkPath;$env:PATH"
    Write-Host "    添加 emsdk 路径: $EmsdkPath" -ForegroundColor Gray
}

# 设置 EMSCRIPTEN 环境变量
$env:EMSCRIPTEN = $EmsdkPath

Write-Host "  环境设置完成" -ForegroundColor Green
Write-Host ""

# 验证 emcc 是否可用
$emccAvailable = $false
if (Get-Command emcc -ErrorAction SilentlyContinue) {
    $emccAvailable = $true
}

if (-not $emccAvailable) {
    Write-Host "[错误] 未找到 emcc 编译器" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动执行以下步骤:"
    Write-Host "  cd $EmsdkPath"
    Write-Host "  .\emsdk activate latest"
    Write-Host "  .\emsdk_env.bat"
    Write-Host "  emcc --version"
    Write-Host ""
    Write-Host "然后重新运行此脚本"
    exit 1
}

$EMCC_VERSION = & emcc --version | Select-Object -First 1
Write-Host "[OK] 找到 emcc: $EMCC_VERSION" -ForegroundColor Green
Write-Host ""

# ============ 创建输出目录 ============
Write-Host "[2/3] 创建输出目录..."
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Write-Host "  输出目录: $OutDir"
Write-Host ""

# ============ 编译 WASM ============
Write-Host "[3/3] 编译 WASM 模块..."
Write-Host "  使用 C++17 标准，优化级别 O2"
Write-Host ""

# 切换到源码目录
Push-Location $SrcDir

# 编译选项
$EMCC_FLAGS = @(
    "-std=c++17",
    "-O2",
    "-Wall",
    "-I./deps",
    "-I./deps/Eigen",
    "-I.",
    "-s", "WASM=1",
    "-s", "MODULARIZE=1",
    "-s", "EXPORT_NAME='LSCMSolver'",
    "-s", "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','getValue','setValue','UTF8ToString','stringToUTF8','lengthBytesUTF8']",
    "-s", "ALLOW_MEMORY_GROWTH=1",
    "-s", "FORCE_FILESYSTEM=1",
    "-fno-exceptions"
)

# 源文件 (使用 wasm_main.cpp，提供 C 接口)
$SRCS = @(
    "wasm_main.cpp",
    "Mesh.cpp",
    "MeshIO.cpp",
    "Lscm.cpp",
    "Parameterization.cpp",
    "QcError.cpp",
    "Solver.cpp",
    "Vertex.cpp",
    "Edge.cpp",
    "Face.cpp",
    "HalfEdge.cpp"
)

# 输出文件
$OUTPUT_JS = Join-Path $OutDir "lscm_solver.js"
$OUTPUT_WASM = Join-Path $OutDir "lscm_solver.wasm"

Write-Host "执行编译命令..."
Write-Host "  emcc $($EMCC_FLAGS -join ' ') $($SRCS -join ' ') -o $OUTPUT_JS"
Write-Host ""

# 执行编译
# & emcc $EMCC_FLAGS $SRCS -o "$OUTPUT_JS"
$AllArgs = $EMCC_FLAGS + $SRCS + @("-o", $OUTPUT_JS)
& emcc @AllArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "[失败] 编译出错 (退出码: $LASTEXITCODE)" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "===================================" -ForegroundColor Green
Write-Host "编译完成!" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""

# 检查生成的文件
Write-Host "生成的文件:"
if (Test-Path $OUTPUT_JS) {
    Write-Host "  [OK] $OUTPUT_JS" -ForegroundColor Green
} else {
    Write-Host "  [警告] 未找到 $(Split-Path $OUTPUT_JS -Leaf)" -ForegroundColor Yellow
}

if (Test-Path $OUTPUT_WASM) {
    Write-Host "  [OK] $OUTPUT_WASM" -ForegroundColor Green
} else {
    Write-Host "  [警告] 未找到 $(Split-Path $OUTPUT_WASM -Leaf)" -ForegroundColor Yellow
}

# 检查是否生成了 worker 文件
$WorkerJs = Join-Path $OutDir "lscm_solver.worker.js"
if (Test-Path $WorkerJs) {
    Write-Host "  [OK] $WorkerJs" -ForegroundColor Green
}

