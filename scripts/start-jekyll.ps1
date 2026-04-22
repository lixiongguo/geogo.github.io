# Jekyll Docker Local Preview Script
# Usage: Double-click or run in PowerShell: .\start-jekyll.ps1

$ErrorActionPreference = "Stop"

Write-Host "Checking Docker Desktop status..." -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info 2>&1 | Out-Null
} catch {
    Write-Host "Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop first, then run this script again." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Docker is running, starting Jekyll..." -ForegroundColor Green

# Stop existing Jekyll container if any
$existingContainer = docker ps -a --filter "ancestor=jekyll/jekyll" --format "{{.ID}}" 2>$null
if ($existingContainer) {
    Write-Host "Stopping old container..." -ForegroundColor Yellow
    docker stop $existingContainer 2>$null | Out-Null
}

# Start Jekyll container
$sitePath = "c:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io"
docker run --rm -p 4000:4000 -v "${sitePath}:/site" jekyll/jekyll jekyll serve --incremental --force_polling --detach

Write-Host ""
Write-Host "Jekyll started!" -ForegroundColor Green
Write-Host "Access: http://localhost:4000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit (container will keep running in background)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
