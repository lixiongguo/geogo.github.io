param(
    [string[]]$Targets = @("uv_unwrap_simple"),
    [switch]$Clean = $false
)

$ErrorActionPreference = "Stop"

$buildRoot = $PSScriptRoot
$cppRoot = Split-Path -Parent $buildRoot
$repoRoot = Split-Path -Parent $cppRoot
$srcRoot = Join-Path $cppRoot "conformal-parameterization"
$outDir = Join-Path $repoRoot "assets\wasm"
$tmpDir = Join-Path $buildRoot "build"

$emsdkPath = Join-Path $cppRoot "emsdk"
$eigenInc = Join-Path $cppRoot "deps\eigen-3.4.0"
$glmInc = Join-Path $cppRoot "deps\glm"

if (!(Test-Path (Join-Path $emsdkPath "emsdk_env.ps1"))) {
    Write-Host "[ERROR] emsdk not found at: $emsdkPath" -ForegroundColor Red
    exit 1
}

Push-Location $emsdkPath
. ".\emsdk_env.ps1" | Out-Null
Pop-Location

$emxx = Get-Command "em++.bat" -ErrorAction SilentlyContinue
if (!$emxx) { $emxx = Get-Command "em++" -ErrorAction SilentlyContinue }
if (!$emxx) {
    Write-Host "[ERROR] em++ not found. Please activate emsdk first." -ForegroundColor Red
    exit 1
}

foreach ($required in @($srcRoot, $eigenInc, $glmInc)) {
    if (!(Test-Path $required)) {
        Write-Host "[ERROR] Required path not found: $required" -ForegroundColor Red
        exit 1
    }
}

if ($Clean) {
    Remove-Item -Recurse -Force $tmpDir -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

function Write-Efile($name, $funcs) {
    $efile = Join-Path $tmpDir "$name.efile"
    $json = "[" + (($funcs | ForEach-Object { "`"$_`"" }) -join ",") + "]"
    $json | Out-File -FilePath $efile -Encoding ascii -NoNewline
    return "@$efile"
}

function Build-Target($name, $sources, $exportName, $funcs, $output) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Building: $name" -ForegroundColor Cyan
    Write-Host "  => $output" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    $efile = Write-Efile $name $funcs
    $includeFlags = @(
        "-I$srcRoot",
        "-I$(Join-Path $srcRoot "uv_unwrap_simple")",
        "-I$(Join-Path $srcRoot "Mosek")",
        "-I$eigenInc",
        "-I$glmInc"
    )

    $args = @(
        "-std=c++17",
        "-O2",
        "-flto"
    ) + $includeFlags + @(
        "-s", "MODULARIZE=1",
        "-s", "ALLOW_MEMORY_GROWTH=1",
        "-s", "INITIAL_MEMORY=268435456",
        "-s", "WASM=1",
        "-s", "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','UTF8ToString','getValue','setValue']",
        "-s", "FORCE_FILESYSTEM=0",
        "-s", "ENVIRONMENT='web'",
        "-s", "EXPORT_NAME=`"$exportName`"",
        "-s", "EXPORTED_FUNCTIONS=$efile"
    ) + $sources + @("-o", $output)

    & $emxx.Source @args
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed: $name"
    }
    Write-Host "[DONE] $name -> $output" -ForegroundColor Green
}

$meshSrcs = @(
    "Mesh.cpp",
    "MeshIO.cpp",
    "Solver.cpp",
    "Parameterization.cpp",
    "Vertex.cpp",
    "Edge.cpp",
    "Face.cpp",
    "HalfEdge.cpp"
) | ForEach-Object { Join-Path $srcRoot $_ }

$uvSimpleSources = @(
    (Join-Path $buildRoot "uv-unwrap-simple\wasm_uv_unwrap_simple.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\Lscm.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\Tutte.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\Scp.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\CirclePatterns.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\Cetm.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\RicciFlow.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\LinAbf.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\AbfPlusPlus.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\ARAP.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\HolomorphicOneForm.cpp"),
    (Join-Path $srcRoot "QcError.cpp")
) + $meshSrcs

$targetSet = @{}
foreach ($target in $Targets) {
    $targetSet[$target] = $true
}
$buildAll = $Targets.Count -eq 0 -or $targetSet.ContainsKey("all")

if ($buildAll -or $targetSet.ContainsKey("uv_unwrap_simple") -or $targetSet.ContainsKey("simple")) {
    Build-Target "uv_unwrap_simple" `
        $uvSimpleSources `
        "UvUnwrapSimpleSolver" `
        @(
            "_malloc","_free",
            "_solve_lscm","_solve_tutte_circle","_solve_tutte_square","_solve_scp",
            "_solve_linabf","_solve_abfpp","_solve_arap",
            "_solve_cp","_solve_cetm","_solve_ricci","_solve_hof",
            "_get_uv_result","_get_uv_result_size","_get_last_time_ms","_get_cp_fallback_to_cetm","_dispose",
            "_load_mesh_with_uv","_compute_qc_error",
            "_get_qc_errors","_get_qc_errors_size","_get_qc_colors","_get_qc_colors_size"
        ) `
        (Join-Path $outDir "uv_unwrap_simple.js")
}

Write-Host ""
Write-Host "Output files in ${outDir}:" -ForegroundColor Yellow
Get-ChildItem -Path $outDir -Filter "uv_unwrap_simple.*" | ForEach-Object {
    $size = "{0,8:N1} KB" -f ($_.Length / 1024)
    Write-Host "  $size  $($_.Name)" -ForegroundColor White
}
