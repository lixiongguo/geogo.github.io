$ErrorActionPreference = "Stop"

$buildRoot = $PSScriptRoot
$cppRoot = Split-Path -Parent $buildRoot
$repoRoot = Split-Path -Parent $cppRoot
$outDir = Join-Path $repoRoot "assets\wasm"

$emsdkPath = Join-Path $cppRoot "emsdk"
$eigenInc = Join-Path $cppRoot "deps\eigen-3.4.0"
$srcFile = Join-Path $cppRoot "VectorFileds\vector_field_unified_wasm.cpp"

if (!(Test-Path (Join-Path $emsdkPath "emsdk_env.ps1"))) {
  Write-Host "[ERROR] emsdk not found: $emsdkPath" -ForegroundColor Red
  exit 1
}
foreach ($p in @($eigenInc, $srcFile)) {
  if (!(Test-Path $p)) {
    Write-Host "[ERROR] missing required path: $p" -ForegroundColor Red
    exit 1
  }
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

New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$output = Join-Path $outDir "vector_field_solver.js"

Write-Host "Building vector_field_solver wasm..." -ForegroundColor Cyan
Write-Host "  Source: $srcFile" -ForegroundColor Cyan
Write-Host "  Output: $output" -ForegroundColor Cyan

& $emxx.Source `
  -std=c++17 -O2 -flto `
  "-I$eigenInc" `
  -s MODULARIZE=1 `
  -s EXPORT_NAME="VectorFieldSolver" `
  -s ALLOW_MEMORY_GROWTH=1 `
  -s INITIAL_MEMORY=268435456 `
  -s WASM=1 `
  "-s" "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','getValue','setValue']" `
  -s FORCE_FILESYSTEM=0 `
  -s ENVIRONMENT=web `
  "-s" "EXPORTED_FUNCTIONS=['_malloc','_free','_compute_trivial_nrosy_field','_compute_4rosy_field','_get_nrosy_theta','_get_nrosy_theta_size','_get_nrosy_last_time_ms','_get_nrosy_last_algorithm']" `
  $srcFile `
  -o $output

if ($LASTEXITCODE -ne 0) {
  Write-Host "[FAILED] vector_field_solver build" -ForegroundColor Red
  exit 1
}

Write-Host "[DONE] vector_field_solver build success" -ForegroundColor Green
Get-ChildItem -Path $outDir -Filter "vector_field_solver.*" | ForEach-Object {
  $kb = [math]::Round($_.Length / 1024, 1)
  Write-Host "  $kb KB  $($_.Name)"
}
