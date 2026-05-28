$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Push-Location $root

try {
  Write-Host "Building uv-unwrap-simple WASM (LSCM + Tutte + SCP + linABF + ABF++ + CP + CETM + Ricci)" -ForegroundColor Cyan
  .\build_wasm_all.ps1 -Targets uv_unwrap_simple | Out-Host
  Write-Host "Done." -ForegroundColor Green
} finally {
  Pop-Location
}
