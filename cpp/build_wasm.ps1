param(
    [Parameter(Mandatory = $true)]
    [string]$Target
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$MakeDir = Join-Path $ScriptDir "conformal-parameterization\wasm"
$Manifest = Join-Path $ScriptDir "wasm_packages.yaml"

function Resolve-PackageBlock([string]$Name) {
    if (-not (Test-Path $Manifest)) { return $null }
    $raw = Get-Content $Manifest -Raw
    if ($raw -match "(?ms)^\s*$([regex]::Escape($Name)):\s*\r?\n(?:[ \t].*\r?\n)+") {
        return $Matches[0]
    }
    return $null
}

function Resolve-MakeTarget([string]$Name) {
    switch ($Name) {
        "page" { return "build-page-all" }
        "page-all" { return "build-page-all" }
        "all" { return "build-all" }
        default {
            $block = Resolve-PackageBlock $Name
            if ($block -and ($block -match "make_target:\s*(\S+)")) { return $Matches[1] }
            return ""
        }
    }
}

function Resolve-MakeDir([string]$Name) {
    $block = Resolve-PackageBlock $Name
    if ($block -and ($block -match "make_dir:\s*(\S+)")) {
        $rel = $Matches[1].Trim('"').Trim("'")
        return (Join-Path $ScriptDir ($rel -replace '/', '\'))
    }
    return $MakeDir
}

$MakeTarget = Resolve-MakeTarget $Target
if (-not $MakeTarget) {
    Write-Error "Unknown target: $Target"
}

$ResolvedMakeDir = Resolve-MakeDir $Target

$EmsdkEnv = Join-Path $RepoRoot "cpp\emsdk\emsdk_env.ps1"
if (Test-Path $EmsdkEnv) { . $EmsdkEnv }

# Prefer package-local build.ps1 when GNU make is unavailable (common on Windows)
$LocalBuildPs1 = Join-Path $ResolvedMakeDir "build.ps1"
$HasMake = [bool](Get-Command make -ErrorAction SilentlyContinue)

if ((Test-Path $LocalBuildPs1) -and -not $HasMake) {
    Write-Host "[build_wasm.ps1] make missing; using $LocalBuildPs1"
    & $LocalBuildPs1
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    return
}

Write-Host "[build_wasm.ps1] make -C $ResolvedMakeDir $MakeTarget"
Push-Location $ResolvedMakeDir
try {
    & make $MakeTarget
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
    Pop-Location
}
