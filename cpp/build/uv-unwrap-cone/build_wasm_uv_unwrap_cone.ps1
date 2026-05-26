# Build unified_solver.js/wasm for uv_unwrap_cone_global.html (CP / CETM / Ricci)
# Usage: .\build_wasm_uv_unwrap_cone.ps1

$ErrorActionPreference = "Stop"

$buildRoot = Split-Path -Parent $PSScriptRoot
$cppRoot   = Split-Path -Parent $buildRoot
$repoRoot  = Split-Path -Parent $cppRoot
$srcRoot   = Join-Path $cppRoot "conformal-parameterization"
$coneDir   = Join-Path $srcRoot "uv_unwrap_cone"
$outDir    = Join-Path $repoRoot "assets\wasm"
$tmpDir    = Join-Path $buildRoot "build"

$emsdkPath = Join-Path $cppRoot "emsdk"
$eigenInc  = Join-Path $cppRoot "deps\eigen-3.4.0"

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
    Write-Host "[ERROR] em++ not found. Activate emsdk first." -ForegroundColor Red
    exit 1
}

foreach ($p in @($srcRoot, $coneDir, $eigenInc)) {
    if (!(Test-Path $p)) {
        Write-Host "[ERROR] Missing path: $p" -ForegroundColor Red
        exit 1
    }
}

New-Item -ItemType Directory -Path $outDir -Force | Out-Null
New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

$exported = @(
    "_malloc","_free",
    "_solve_cp","_get_cp_uv_result","_get_cp_uv_result_size","_get_cp_last_time_ms","_cp_dispose",
    "_solve_cetm","_get_cetm_uv_result","_get_cetm_uv_result_size","_get_cetm_last_time_ms","_cetm_dispose",
    "_solve_ricci","_get_ricci_uv_result","_get_ricci_uv_result_size","_get_ricci_last_time_ms","_ricci_dispose"
)
$efile = Join-Path $tmpDir "unified_solver.efile"
("[" + (($exported | ForEach-Object { "`"$_`"" }) -join ",") + "]") | Out-File -FilePath $efile -Encoding ascii -NoNewline

$meshSrcs = @(
    "Mesh.cpp","MeshIO.cpp","Parameterization.cpp",
    "Vertex.cpp","Edge.cpp","Face.cpp","HalfEdge.cpp"
) | ForEach-Object { Join-Path $srcRoot $_ }

$sources = @(
    (Join-Path $PSScriptRoot "wasm_unified_solver.cpp"),
    (Join-Path $coneDir "CirclePatternsWasm.cpp"),
    (Join-Path $coneDir "Cetm.cpp"),
    (Join-Path $coneDir "RicciFlow.cpp"),
    (Join-Path $srcRoot "Solver.cpp")
) + $meshSrcs

$output = Join-Path $outDir "unified_solver.js"

Write-Host "Building unified_solver (uv_unwrap_cone)..." -ForegroundColor Cyan
Write-Host "  Output: $output"

& $emxx.Source `
    -std=c++17 -O2 -flto `
    "-I$srcRoot" "-I$coneDir" "-I$eigenInc" `
    "-I$(Join-Path $srcRoot 'Mosek')" `
    "-I$(Join-Path $srcRoot 'uv_unwrap_simple')" `
    -s MODULARIZE=1 `
    -s EXPORT_NAME="UnifiedSolver" `
    -s ALLOW_MEMORY_GROWTH=1 `
    -s INITIAL_MEMORY=268435456 `
    -s WASM=1 `
    "-s" "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','UTF8ToString','getValue','setValue']" `
    -s FORCE_FILESYSTEM=0 `
    -s ENVIRONMENT=web `
    "-s" "EXPORTED_FUNCTIONS=@$efile" `
    @sources `
    -o $output

if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAILED] unified_solver build" -ForegroundColor Red
    exit 1
}

Write-Host "[DONE] unified_solver" -ForegroundColor Green
Get-ChildItem -Path $outDir -Filter "unified_solver.*" | ForEach-Object {
    $kb = [math]::Round($_.Length / 1024, 1)
    Write-Host "  $kb KB  $($_.Name)"
}
