# Batch CirclePatterns: assets/Models -> assets/CP_Models
# Usage: .\run_cp_batch.ps1 [-Rebuild]

param(
    [switch]$Rebuild,
    [string]$MosekRoot = "C:\Program Files\Mosek\11.0\tools\platform\win64x86"
)

$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
$repoRoot  = (Resolve-Path (Join-Path $scriptDir "..\..\..")).Path
$modelsDir = Join-Path $repoRoot "assets\Models"
$outDir    = Join-Path $repoRoot "assets\CP_Models"
$binDir    = Join-Path $scriptDir "bin"
$exe       = Join-Path $binDir "test_circle_patterns.exe"
$logFile   = Join-Path $outDir "batch_log.txt"

if ($Rebuild -or !(Test-Path $exe)) {
    & (Join-Path $scriptDir "build_native_circle_patterns.ps1") -MosekRoot $MosekRoot -SkipRun
}

if (!(Test-Path $exe)) {
    Write-Host "[ERROR] Missing $exe" -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Path $outDir -Force | Out-Null

$models = Get-ChildItem -Path $modelsDir -Filter "*.obj" | Sort-Object Name
if ($models.Count -eq 0) {
    Write-Host "[ERROR] No .obj files in $modelsDir" -ForegroundColor Red
    exit 1
}

$header = "CirclePatterns batch $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$header | Set-Content -Path $logFile -Encoding UTF8

Write-Host $header -ForegroundColor Cyan
Write-Host "  Input:  $modelsDir"
Write-Host "  Output: $outDir"
Write-Host "  Models: $($models.Count)"
Write-Host ""

$ok = 0
$fail = 0
Push-Location $binDir
$prevEap = $ErrorActionPreference
try {
    foreach ($m in $models) {
        $outPath = Join-Path $outDir $m.Name
        Write-Host "[$($m.Name)]" -ForegroundColor Yellow
        $t0 = Get-Date
        $ErrorActionPreference = 'Continue'
        $runOut = cmd /c "`"$exe`" `"$($m.FullName)`" `"$outPath`" 2>&1"
        $code = $LASTEXITCODE
        $ErrorActionPreference = $prevEap
        if ($runOut) { $runOut | ForEach-Object { Write-Host $_ } }
        $dt = ((Get-Date) - $t0).TotalSeconds
        $line = "{0,-40} exit={1} time={2:N1}s" -f $m.Name, $code, $dt
        Add-Content -Path $logFile -Value $line
        if ($runOut) { Add-Content -Path $logFile -Value ($runOut | Out-String) }
        Add-Content -Path $logFile -Value "---"

        if ($code -eq 0 -and (Test-Path $outPath)) {
            $ok++
            Write-Host "  -> OK`n" -ForegroundColor Green
        } else {
            $fail++
            if (Test-Path $outPath) { Remove-Item -Force $outPath }
            Write-Host "  -> FAILED (exit $code)`n" -ForegroundColor Red
        }
    }
} finally {
    Pop-Location
}

$summary = "Done: $ok succeeded, $fail failed (of $($models.Count))"
Add-Content -Path $logFile -Value $summary
Write-Host $summary -ForegroundColor Cyan
Write-Host "Log: $logFile"

if ($fail -gt 0) { exit 1 }
