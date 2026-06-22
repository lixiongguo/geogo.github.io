param(
    [Parameter(Mandatory = $true)]
    [string]$Target
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$MakeDir = Join-Path $ScriptDir "conformal-parameterization\wasm"
$Manifest = Join-Path $ScriptDir "wasm_packages.yaml"

function Resolve-MakeTarget([string]$Name) {
    switch ($Name) {
        "page" { return "build-page-all" }
        "page-all" { return "build-page-all" }
        "all" { return "build-all" }
        default {
            if (-not (Test-Path $Manifest)) { return "" }
            $raw = Get-Content $Manifest -Raw
            # minimal parse without external yaml module
            if ($raw -match "(?ms)^\s*$([regex]::Escape($Name)):\s*\r?\n(?:[ \t].*\r?\n)+") {
                $block = $Matches[0]
                if ($block -match "make_target:\s*(\S+)") { return $Matches[1] }
            }
            return ""
        }
    }
}

$MakeTarget = Resolve-MakeTarget $Target
if (-not $MakeTarget) {
    Write-Error "Unknown target: $Target"
}

$EmsdkEnv = Join-Path $RepoRoot "cpp\emsdk\emsdk_env.ps1"
if (Test-Path $EmsdkEnv) { . $EmsdkEnv }

Write-Host "[build_wasm.ps1] make -C $MakeDir $MakeTarget"
Push-Location $MakeDir
try {
    & make $MakeTarget
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    Pop-Location
}
