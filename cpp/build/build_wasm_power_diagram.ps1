<#
.SYNOPSIS
  Build Geogram (Emscripten) + wasm_power_diagram for semi-discrete-ot.html

.DESCRIPTION
  1) Configure & compile Geogram from a source tree (clone).
  2) Link MA power-diagram code into assets/wasm/wasm_power_diagram.{js,wasm}

.PARAMETER GeogramSource
  Path to Geogram source (default: sibling of repo under MyDoc/geogram)

.PARAMETER RebuildGeogram
  Force re-configure Geogram even if lib already exists

.PARAMETER SkipGeogram
  Only rebuild wasm wrapper (Geogram lib must already exist)

.EXAMPLE
  .\build_wasm_power_diagram.ps1
  .\build_wasm_power_diagram.ps1 -RebuildGeogram
#>

param(
    [string]$GeogramSource = "C:\Users\lixio\OneDrive\Desktop\MyDoc\geogram",
    [switch]$RebuildGeogram,
    [switch]$SkipGeogram,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$buildRoot = $PSScriptRoot
$cppRoot = Split-Path -Parent $buildRoot
$repoRoot = Split-Path -Parent $cppRoot
$maRoot = Join-Path $cppRoot "MongeAmpere"
$outDir = Join-Path $repoRoot "assets\wasm"
$tmpDir = Join-Path $buildRoot "build-power-diagram"

$emsdkPath = Join-Path $cppRoot "emsdk"
$geogramBuild = Join-Path $GeogramSource "build\Emscripten-clang-Release"
$geogramInstall = Join-Path $GeogramSource "install-emscripten"

if (!(Test-Path (Join-Path $emsdkPath "emsdk_env.ps1"))) {
    Write-Host "[ERROR] emsdk not found: $emsdkPath" -ForegroundColor Red
    exit 1
}
if (!(Test-Path $GeogramSource)) {
    Write-Host "[ERROR] Geogram source not found: $GeogramSource" -ForegroundColor Red
    exit 1
}
if (!(Test-Path (Join-Path $maRoot "src\ma_power_diagram.cpp"))) {
    Write-Host "[ERROR] MongeAmpere power diagram sources missing under: $maRoot" -ForegroundColor Red
    exit 1
}

Push-Location $emsdkPath
. ".\emsdk_env.ps1" | Out-Null
Pop-Location

# Geogram's Emscripten-clang.cmake locates emcc via EMSCRIPTEN (directory containing emcc.py).
$env:EMSCRIPTEN = (Resolve-Path (Join-Path $emsdkPath "upstream\emscripten")).Path

$emcmake = Join-Path $env:EMSCRIPTEN "emcmake.ps1"
if (!(Test-Path $emcmake)) {
    $emcmake = Join-Path $env:EMSCRIPTEN "emcmake.bat"
}

$emxx = Get-Command "em++.bat" -ErrorAction SilentlyContinue
if (!$emxx) { $emxx = Get-Command "em++" -ErrorAction SilentlyContinue }
if (!$emxx) {
    Write-Host "[ERROR] em++ not in PATH. Activate emsdk first." -ForegroundColor Red
    exit 1
}

$cmake = Get-Command "cmake" -ErrorAction SilentlyContinue
if (!$cmake) {
    Write-Host "[ERROR] cmake not found in PATH." -ForegroundColor Red
    exit 1
}

function Ensure-Ninja {
    $existing = Get-Command "ninja" -ErrorAction SilentlyContinue
    if ($existing) { return $existing.Source }

    $toolsDir = Join-Path $buildRoot "tools"
    $ninjaExe = Join-Path $toolsDir "ninja.exe"
    if (Test-Path $ninjaExe) {
        $env:PATH = "$toolsDir;$env:PATH"
        return $ninjaExe
    }

    Write-Host "Downloading ninja (required to build Geogram on Windows)..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
    $zip = Join-Path $toolsDir "ninja-win.zip"
    $url = "https://github.com/ninja-build/ninja/releases/download/v1.12.1/ninja-win.zip"
    Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
    Expand-Archive -Path $zip -DestinationPath $toolsDir -Force
    Remove-Item $zip -Force
    if (!(Test-Path $ninjaExe)) { throw "Failed to install ninja to $ninjaExe" }
    $env:PATH = "$toolsDir;$env:PATH"
    Write-Host "Installed ninja: $ninjaExe" -ForegroundColor Green
    return $ninjaExe
}

function Find-GeogramLibrary {
    param([string[]]$SearchRoots)
    foreach ($root in $SearchRoots) {
        if (!(Test-Path $root)) { continue }
        $candidates = Get-ChildItem -Path $root -Recurse -Filter "libgeogram.a" -ErrorAction SilentlyContinue
        foreach ($c in $candidates) { return $c.FullName }
    }
    return $null
}

function Build-GeogramEmscripten {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Step 1: Geogram (Emscripten-clang)" -ForegroundColor Cyan
    Write-Host "  source: $GeogramSource" -ForegroundColor Cyan
    Write-Host "  build:  $geogramBuild" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    if ($Clean -and (Test-Path $geogramBuild)) {
        Remove-Item -Recurse -Force $geogramBuild
    }
  if ($Clean -and (Test-Path $geogramInstall)) {
        Remove-Item -Recurse -Force $geogramInstall
    }

    if (Test-Path $geogramBuild) {
        Remove-Item -Recurse -Force $geogramBuild
    }
    New-Item -ItemType Directory -Path $geogramBuild -Force | Out-Null

    $commonArgs = @(
        "-S", $GeogramSource,
        "-B", $geogramBuild,
        "-DCMAKE_BUILD_TYPE=Release",
        "-DVORPALINE_PLATFORM:STRING=Emscripten-clang",
        "-DGEOGRAM_WITH_GRAPHICS:BOOL=OFF",
        "-DGEOGRAM_LIB_ONLY:BOOL=ON",
        "-DGEOGRAM_WITH_LUA:BOOL=OFF",
        "-DGEOGRAM_WITH_TETGEN:BOOL=OFF",
        "-DGEOGRAM_WITH_TRIANGLE:BOOL=OFF",
        "-DGEOGRAM_WITH_HLBFGS:BOOL=OFF",
        "-DCMAKE_INSTALL_PREFIX=$geogramInstall"
    )

    Ensure-Ninja | Out-Null

    if (Test-Path $geogramBuild) {
        Remove-Item -Recurse -Force $geogramBuild
        New-Item -ItemType Directory -Path $geogramBuild -Force | Out-Null
    }
    & $emcmake cmake @commonArgs "-G" "Ninja" "-DEMSCRIPTEN_DIR:PATH=$env:EMSCRIPTEN"
    if ($LASTEXITCODE -ne 0) { throw "Geogram cmake configure failed (emcmake + Ninja)" }

    & cmake --build $geogramBuild --config Release -j 4
    if ($LASTEXITCODE -ne 0) { throw "Geogram build failed" }

    & cmake --install $geogramBuild --config Release
    if ($LASTEXITCODE -ne 0) { throw "Geogram install failed" }

    Write-Host "[DONE] Geogram installed to $geogramInstall" -ForegroundColor Green
}

function Write-Efile($funcs) {
    $efile = Join-Path $tmpDir "wasm_power_diagram.efile"
    $json = "[" + (($funcs | ForEach-Object { "`"$_`"" }) -join ",") + "]"
    $json | Out-File -FilePath $efile -Encoding ascii -NoNewline
    return "@$efile"
}

function Build-WasmPowerDiagram {
    param([string]$GeogramLib)

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Step 2: wasm_power_diagram" -ForegroundColor Cyan
    Write-Host "  => $outDir\wasm_power_diagram.js" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

    $geogramInc = Join-Path $GeogramSource "src\lib"
    $maInc = Join-Path $maRoot "include"
    $wrapper = Join-Path $buildRoot "power-diagram\wasm_power_diagram.cpp"
    $maSrc = Join-Path $maRoot "src\ma_power_diagram.cpp"

    $exports = @(
        "_malloc", "_free",
        "_compute_power_diagram_js",
        "_free_buffer",
        "_wasm_test"
    )
    $efile = Write-Efile $exports

    $libDir = Split-Path -Parent $GeogramLib
    $emFlags = @(
        "-std=c++17",
        "-O2",
        "-I$geogramInc",
        "-I$maInc",
        "-L$libDir",
        "-lgeogram",
        "-s", "WASM=1",
        "-s", "ALLOW_MEMORY_GROWTH=1",
        "-s", "INITIAL_MEMORY=268435456",
        "-s", "ENVIRONMENT=web",
        "-s", "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','UTF8ToString','getValue','setValue']",
        "-s", "EXPORTED_FUNCTIONS=$efile"
    )

    $outJs = Join-Path $outDir "wasm_power_diagram.js"
    & $emxx.Source @emFlags $wrapper $maSrc "-o" $outJs
    if ($LASTEXITCODE -ne 0) { throw "wasm_power_diagram link failed" }

    Write-Host "[DONE] $outJs" -ForegroundColor Green
}

# --- main ---

if ($Clean) {
    Remove-Item -Recurse -Force $tmpDir -ErrorAction SilentlyContinue
}

if (-not $SkipGeogram) {
    $existingLib = Find-GeogramLibrary @($geogramInstall, $geogramBuild)
    if ($RebuildGeogram -or !$existingLib) {
        Build-GeogramEmscripten
    } else {
        Write-Host "Geogram lib exists, skip build (use -RebuildGeogram to force): $existingLib" -ForegroundColor DarkGray
    }
}

$geogramLib = Find-GeogramLibrary @($geogramInstall, $geogramBuild)
if (!$geogramLib) {
    Write-Host "[ERROR] libgeogram.a not found under $geogramInstall or $geogramBuild" -ForegroundColor Red
    exit 1
}
Write-Host "Using Geogram library: $geogramLib" -ForegroundColor DarkGray

Build-WasmPowerDiagram -GeogramLib $geogramLib

Write-Host ""
Write-Host "Output:" -ForegroundColor Green
Get-ChildItem (Join-Path $outDir "wasm_power_diagram.*") | ForEach-Object {
    Write-Host ("  {0:N1} KB  {1}" -f ($_.Length / 1KB), $_.Name)
}
