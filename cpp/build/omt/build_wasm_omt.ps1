# build_wasm_omt.ps1 - Standalone build for Optimal Mass Transport WASM
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
  Write-Host "Building OMT WASM (Optimal Mass Transport Image Interpolation)" -ForegroundColor Cyan
  .\build_wasm_all.ps1 -Targets omt | Out-Host
  Write-Host "Done." -ForegroundColor Green
} finally {
  Pop-Location
}
