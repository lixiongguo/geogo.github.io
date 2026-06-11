param(
    [string]$ModelPath = "",
    [string]$OutDir = "",
    [string]$SingularityCsv = "",
    [int]$N = 4,
    [switch]$AutoSingularity
)

$ErrorActionPreference = "Stop"

$buildRoot = Split-Path -Parent $PSScriptRoot
$cppRoot   = Split-Path -Parent $buildRoot
$repoRoot  = Split-Path -Parent $cppRoot
$vfRoot    = Join-Path $cppRoot "VectorFileds"
$srcRoot   = Join-Path $cppRoot "conformal-parameterization"
$simpleDir = Join-Path $srcRoot "uv_unwrap_simple"
$eigenInc  = Join-Path $cppRoot "deps\eigen-3.3.9"
$outBinDir = Join-Path $PSScriptRoot "bin"
$exe       = Join-Path $outBinDir "nrosy_trivial_connection.exe"

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

New-Item -ItemType Directory -Path $outBinDir -Force | Out-Null

$sources = @(
    (Join-Path $vfRoot "nrosy_trivial_connection.cpp"),
    (Join-Path $srcRoot "Mesh.cpp"),
    (Join-Path $srcRoot "MeshIO.cpp"),
    (Join-Path $srcRoot "Parameterization.cpp"),
    (Join-Path $srcRoot "geometry\QcError.cpp"),
    (Join-Path $srcRoot "Vertex.cpp"),
    (Join-Path $srcRoot "Edge.cpp"),
    (Join-Path $srcRoot "Face.cpp"),
    (Join-Path $srcRoot "HalfEdge.cpp"),
    (Join-Path $simpleDir "Lscm.cpp")
)

$includes = @(
    "/I`"$srcRoot`"",
    "/I`"$simpleDir`"",
    "/I`"$vfRoot`"",
    "/I`"$eigenInc`""
)

Write-Host "Building nrosy_trivial_connection..." -ForegroundColor Cyan
$compileArgs = @(
    "/EHsc", "/O2", "/std:c++17", "/MD",
    "/D_USE_MATH_DEFINES",
    "/Fe:$exe"
) + $includes + $sources

& cl.exe @compileArgs
if ($LASTEXITCODE -ne 0) { exit 1 }
Write-Host "[DONE] $exe" -ForegroundColor Green

if (!$ModelPath) {
    $candidates = @(
        (Join-Path $repoRoot "assets\Models2\torus_F7680.obj"),
        (Join-Path $repoRoot "assets\Models\cathead_F248.obj")
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { $ModelPath = $c; break }
    }
}
if (!$OutDir -and $ModelPath) {
    $name = [System.IO.Path]::GetFileNameWithoutExtension($ModelPath)
    $OutDir = Join-Path $repoRoot ("assets\CP_Models\nrosy_tc_" + $name)
}
if (!(Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }

$args = @($ModelPath, $OutDir, "--n", "$N")
if ($SingularityCsv) {
    $args += @("--singularity-csv", $SingularityCsv)
} elseif ($AutoSingularity) {
    $args += @("--auto-singularity")
}

Write-Host "Running: $exe $($args -join ' ')" -ForegroundColor Cyan
Push-Location $outBinDir
& $exe @args
$code = $LASTEXITCODE
Pop-Location
if ($code -ne 0) { exit $code }

