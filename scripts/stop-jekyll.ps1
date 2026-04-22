# Jekyll Docker 停止脚本
# 用于停止后台运行的 Jekyll 容器

Write-Host "停止 Jekyll 容器..." -ForegroundColor Cyan

$containers = docker ps -a --filter "ancestor=jekyll/jekyll" --format "{{.ID}}" 2>$null

if ($containers) {
    foreach ($container in $containers) {
        Write-Host "停止容器: $container" -ForegroundColor Yellow
        docker stop $container 2>$null | Out-Null
    }
    Write-Host "Jekyll 已停止" -ForegroundColor Green
} else {
    Write-Host "没有运行中的 Jekyll 容器" -ForegroundColor Gray
}

Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
