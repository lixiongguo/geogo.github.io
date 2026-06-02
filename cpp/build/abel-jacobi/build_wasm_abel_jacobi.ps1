# Build uv_unwrap_abel_jacobi.wasm only
$buildRoot = Split-Path -Parent $PSScriptRoot
& (Join-Path $buildRoot "build_wasm_all.ps1") -Targets abel_jacobi
