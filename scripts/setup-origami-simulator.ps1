# Apply uv-unwrap integration patches to the Origami Simulator submodule.
$root = Split-Path -Parent $PSScriptRoot
$sim = Join-Path $root "origami-simulator"

if (-not (Test-Path $sim)) {
    Write-Error "Run: git submodule update --init origami-simulator"
    exit 1
}

Copy-Item (Join-Path $root "patches\origami-simulator\uvUnwrapBridge.js") (Join-Path $sim "js\uvUnwrapBridge.js") -Force

$indexPath = Join-Path $sim "index.html"
$index = Get-Content $indexPath -Raw
if ($index -notmatch "uvUnwrapBridge\.js") {
    $index = $index -replace '(<script type="text/javascript" src="js/main\.js"></script>)', "`$1`n    <script type=`"text/javascript`" src=`"js/uvUnwrapBridge.js`"></script>"
    Set-Content $indexPath $index -NoNewline
}

$mainPath = Join-Path $sim "js\main.js"
$main = Get-Content $mainPath -Raw
if ($main -notmatch "autoload=") {
    $old = @'
    model = model.replace(/'/g, ''); // avoid messing up query
    $(".demo[data-url='"+model+"']").click();
});
'@
    $new = @'
    model = model.replace(/'/g, ''); // avoid messing up query
    if (!/[?&]autoload=/.test(location.search)) {
        $(".demo[data-url='"+model+"']").click();
    }
});
'@
    if ($main.Contains($old)) {
        $main = $main.Replace($old, $new)
        Set-Content $mainPath $main -NoNewline
    }
}

Write-Host "Origami Simulator integration patches applied."
