# Native build: CirclePatterns with MOSEK 11 (Windows MSVC)
# Usage: .\build_native_circle_patterns.ps1 [path\to\model.obj]

param(
    [string]$ModelPath = "",
    [string]$MosekRoot = "C:\Program Files\Mosek\11.0\tools\platform\win64x86",
    [switch]$SkipRun
)

$ErrorActionPreference = "Stop"

$buildRoot = Split-Path -Parent $PSScriptRoot
$cppRoot   = Split-Path -Parent $buildRoot
$repoRoot  = Split-Path -Parent $cppRoot
$srcRoot   = Join-Path $cppRoot "conformal-parameterization"
$coneDir   = Join-Path $srcRoot "uv_unwrap_cone"
$mosekDir  = Join-Path $srcRoot "Mosek"
$eigenInc  = Join-Path $cppRoot "deps\eigen-3.3.9"
$outDir    = Join-Path $PSScriptRoot "bin"
$exe       = Join-Path $outDir "test_circle_patterns.exe"

if (!(Test-Path $MosekRoot)) {
    Write-Host "[ERROR] Mosek not found at: $MosekRoot" -ForegroundColor Red
    exit 1
}

$mosekInc = Join-Path $MosekRoot "h"
$mosekLib = Join-Path $MosekRoot "bin"
$mosekDll = Join-Path $mosekLib "mosek64_11_0.dll"

# Locate MSVC
$cl = Get-Command cl.exe -ErrorAction SilentlyContinue
if (!$cl) {
    $vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vswhere) {
        $vsPath = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
        $vcvars = Join-Path $vsPath "VC\Auxiliary\Build\vcvars64.bat"
        if (Test-Path $vcvars) {
            cmd /c "`"$vcvars`" >nul 2>&1 && set" | ForEach-Object {
                if ($_ -match '^(.*?)=(.*)$') { Set-Item -Path "env:$($matches[1])" -Value $matches[2] }
            }
            $cl = Get-Command cl.exe -ErrorAction SilentlyContinue
        }
    }
}
if (!$cl) {
    Write-Host "[ERROR] MSVC cl.exe not found." -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Path $outDir -Force | Out-Null

$sources = @(
    (Join-Path $PSScriptRoot "test_circle_patterns.cpp"),
    (Join-Path $coneDir "CirclePatterns.cpp"),
    (Join-Path $mosekDir "MosekSolver.cpp"),
    (Join-Path $srcRoot "Solver.cpp"),
    (Join-Path $srcRoot "Mesh.cpp"),
    (Join-Path $srcRoot "MeshIO.cpp"),
    (Join-Path $srcRoot "Parameterization.cpp"),
    (Join-Path $srcRoot "QcError.cpp"),
    (Join-Path $srcRoot "Vertex.cpp"),
    (Join-Path $srcRoot "Edge.cpp"),
    (Join-Path $srcRoot "Face.cpp"),
    (Join-Path $srcRoot "HalfEdge.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\Lscm.cpp")
)

$includes = @(
    "/I`"$srcRoot`"",
    "/I`"$coneDir`"",
    "/I`"$mosekDir`"",
    "/I`"$eigenInc`"",
    "/I`"$mosekInc`"",
    "/I`"$(Join-Path $srcRoot 'uv_unwrap_simple')`""
)

$libs = @("/LIBPATH:`"$mosekLib`"", "mosek64_11_0.lib")

Write-Host "Building CirclePatterns + MOSEK 11..." -ForegroundColor Cyan
Write-Host "  MOSEK: $MosekRoot"

$compileArgs = @(
    "/EHsc", "/O2", "/std:c++17", "/MD",
    "/DUSE_MOSEK", "/D_USE_MATH_DEFINES",
    "/Fe:$exe"
) + $includes + $sources + @("/link") + $libs

& cl.exe @compileArgs
if ($LASTEXITCODE -ne 0) { exit 1 }

Copy-Item -Force $mosekDll $outDir
Write-Host "[DONE] $exe" -ForegroundColor Green

if (!$ModelPath) {
    $candidates = @(
        (Join-Path $repoRoot "assets\Models2\torus_F7680.obj"),
        (Join-Path $repoRoot "assets\Models2\bunny_F28576.obj")
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { $ModelPath = $c; break }
    }
}

if (!$SkipRun -and $ModelPath -and (Test-Path $ModelPath)) {
    Write-Host "Running: $exe `"$ModelPath`"" -ForegroundColor Cyan
    Push-Location $outDir
    & $exe $ModelPath
    $code = $LASTEXITCODE
    Pop-Location
    if ($code -ne 0) { exit $code }
} else {
    Write-Host "Run: $exe path\to\model.obj"
}
