param(
    [ValidateSet("all", "page", "uv_unwrap_simple", "dgp_basic", "uv_unwrap_field", "uv_unwrap_abel_jacobi", "bd_lscm", "bd_deformation")]
    [string]$Target = "page"
)

$ErrorActionPreference = "Stop"
$cppRoot = $PSScriptRoot
$repoRoot = Split-Path -Parent $cppRoot
$emsdkPath = Join-Path $cppRoot "emsdk"
$wasmDir = Join-Path $cppRoot "conformal-parameterization\wasm"
$srcRoot = Join-Path $cppRoot "conformal-parameterization"
$outDir = Join-Path $repoRoot "assets\wasm"
$eigen = Join-Path $cppRoot "deps\eigen-3.4.0"

if (!(Test-Path (Join-Path $emsdkPath "emsdk_env.ps1"))) {
    Write-Host "[ERROR] emsdk not found at $emsdkPath" -ForegroundColor Red
    exit 1
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

$baseMesh = @(
    "BaseMesh\Mesh.cpp", "BaseMesh\MeshIO.cpp", "BaseMesh\Vertex.cpp", "BaseMesh\Edge.cpp",
    "BaseMesh\Face.cpp", "BaseMesh\HalfEdge.cpp", "BaseMesh\GaussianCurvature.cpp",
    "BaseMesh\QcError.cpp", "Parameterization\Parameterization.cpp"
) | ForEach-Object { Join-Path $srcRoot $_ }

$cutSeam = Join-Path $srcRoot "CutSeamMesh\CutSeamMesh.cpp"
$solver = @("Solvers\Solver.cpp", "Solvers\AugmentedLagrangian.cpp", "Solvers\MixedIntegerProgram.cpp") |
    ForEach-Object { Join-Path $srcRoot $_ }

$simpleParam = @(
    "Parameterization\SimpleParam\LSCM\Lscm.cpp", "Parameterization\SimpleParam\LSCM\Scp.cpp",
    "Parameterization\SimpleParam\ABF\AbfPlusPlus.cpp", "Parameterization\SimpleParam\ABF\LinAbf.cpp",
    "Parameterization\SimpleParam\ARAP\ARAP.cpp", "Parameterization\SimpleParam\ARAP\Tutte.cpp"
) | ForEach-Object { Join-Path $srcRoot $_ }

$cone = @(
    "Parameterization\ConeParam\ConeParameterization.cpp",
    "Parameterization\ConeParam\Conformal\CirclePatterns.cpp",
    "Parameterization\ConeParam\Conformal\Cetm.cpp",
    "Parameterization\ConeParam\RicciFlow\RicciFlow.cpp"
) | ForEach-Object { Join-Path $srcRoot $_ }

function Invoke-WasmBuild {
    param([string]$Name, [string]$Binding, [string[]]$Sources, [string[]]$Includes, [string]$ExportName, [switch]$Embind)
    $outJs = Join-Path $outDir "$Name.js"
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Building: $Name -> $outJs" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    $bindingPath = Join-Path $wasmDir $Binding
    $incFlags = $Includes | ForEach-Object { "-I$_" }
    $srcPaths = @($bindingPath) + $Sources
    $flags = @("-O3", "-std=c++17", "-s", "MODULARIZE=1", "-s", "ALLOW_MEMORY_GROWTH=1", "-s", "WASM=1",
               "-s", "EXPORT_NAME=$ExportName")
    if ($Embind) {
        $flags += @("--bind", "-s", "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','getValue','setValue']")
        if ($Name -eq "bd_lscm") {
            $flags += @("-s", "FORCE_FILESYSTEM=1", "-s", "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','getValue','setValue','FS']")
        }
    } else {
        $flags += @("-s", "EXPORTED_FUNCTIONS=['_malloc','_free']",
                    "-s", "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','getValue','setValue']")
    }
    & $emxx.Source @incFlags @srcPaths @flags "-o" $outJs
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $Name" }
    Write-Host "[DONE] $Name" -ForegroundColor Green
}

$incBase = @($eigen, (Join-Path $srcRoot "BaseMesh"), (Join-Path $srcRoot "Parameterization"))
$incSimple = $incBase + @(
    (Join-Path $srcRoot "Parameterization\SimpleParam\LSCM"),
    (Join-Path $srcRoot "Parameterization\SimpleParam\ABF"),
    (Join-Path $srcRoot "Parameterization\SimpleParam\ARAP"),
    (Join-Path $srcRoot "Parameterization\ConeParam"),
    (Join-Path $srcRoot "Parameterization\ConeParam\Conformal"),
    (Join-Path $srcRoot "Parameterization\ConeParam\RicciFlow"),
    (Join-Path $srcRoot "Solvers"), (Join-Path $srcRoot "Solvers\Mosek")
)
$incField = $incBase + @(
    (Join-Path $srcRoot "CutSeamMesh"),
    (Join-Path $srcRoot "Parameterization\GlobalFieldsParam"),
    (Join-Path $srcRoot "Parameterization\CutSeamParam"),
    (Join-Path $srcRoot "Parameterization\CutSeamParam\HoloOneForm"),
    (Join-Path $srcRoot "Parameterization\SimpleParam\LSCM"),
    (Join-Path $srcRoot "VectorFileds"),
    (Join-Path $srcRoot "VectorFileds\PrincipalCurvatureFields"),
    (Join-Path $srcRoot "Solvers"), (Join-Path $srcRoot "Solvers\Mosek")
)
$incAbel = $incBase + @(
    (Join-Path $srcRoot "CutSeamMesh"),
    (Join-Path $srcRoot "Parameterization\CutSeamParam"),
    (Join-Path $srcRoot "Parameterization\CutSeamParam\Abel_Jacoi"),
    (Join-Path $srcRoot "Parameterization\SimpleParam\LSCM")
)
$incBd = $incBase + @(
    (Join-Path $srcRoot "Parameterization\SimpleParam\LSCM"),
    (Join-Path $srcRoot "Bounded\bounded_distortion_mapping")
)

$fieldSrcs = $baseMesh + @($cutSeam) + $solver + @(
    (Join-Path $srcRoot "Parameterization\GlobalFieldsParam\GlobalFieldsParameterization.cpp"),
    (Join-Path $srcRoot "Parameterization\GlobalFieldsParam\QuadCover.cpp"),
    (Join-Path $srcRoot "Parameterization\GlobalFieldsParam\MIQQuad.cpp"),
    (Join-Path $srcRoot "Parameterization\CutSeamParam\CutSeamParameterization.cpp"),
    (Join-Path $srcRoot "Parameterization\CutSeamParam\HoloOneForm\HolomorphicOneForm.cpp"),
    (Join-Path $srcRoot "Parameterization\SimpleParam\LSCM\Lscm.cpp"),
    (Join-Path $srcRoot "VectorFileds\NRosyVectorFields.cpp"),
    (Join-Path $srcRoot "VectorFileds\PrincipalCurvatureFields\PrincipalCurvatureField.cpp")
)

$abelSrcs = $baseMesh + @($cutSeam) + @(
    (Join-Path $srcRoot "Parameterization\CutSeamParam\CutSeamParameterization.cpp"),
    (Join-Path $srcRoot "Parameterization\CutSeamParam\Abel_Jacoi\AbelJacobi.cpp"),
    (Join-Path $srcRoot "Parameterization\CutSeamParam\Abel_Jacoi\AbelJacobiParameterization.cpp"),
    (Join-Path $srcRoot "Parameterization\SimpleParam\LSCM\Lscm.cpp")
)

$bdSrcs = $baseMesh + @(
    (Join-Path $srcRoot "Parameterization\SimpleParam\LSCM\Lscm.cpp"),
    (Join-Path $srcRoot "Bounded\bounded_distortion_mapping\BoundedDistortionMapping.cpp")
)

$incBdDeform = @($eigen, (Join-Path $srcRoot "Bounded\bounded_distortion_mapping"))

$bdDeformSrcs = @(
    (Join-Path $srcRoot "Bounded\bounded_distortion_mapping\BoundedDistortionMapping.cpp")
)

$targets = @{
    "uv_unwrap_simple" = { Invoke-WasmBuild "uv_unwrap_simple" "bindings_uv_unwrap_simple_compat.cpp" ($baseMesh + $solver + $simpleParam + $cone) $incSimple "UvUnwrapSimpleSolver" }
    "dgp_basic"        = { Invoke-WasmBuild "dgp_basic" "bindings_dgp_basic_compat.cpp" $baseMesh $incBase "DgpBasicSolver" }
    "uv_unwrap_field"  = { Invoke-WasmBuild "uv_unwrap_field" "bindings_uv_unwrap_field_compat.cpp" $fieldSrcs $incField "UvUnwrapFieldSolver" }
    "uv_unwrap_abel_jacobi" = { Invoke-WasmBuild "uv_unwrap_abel_jacobi" "bindings_uv_unwrap_abel_jacobi_compat.cpp" $abelSrcs $incAbel "UvUnwrapAbelJacobiSolver" }
    "bd_lscm"          = { Invoke-WasmBuild "bd_lscm" "bindings_bd_lscm.cpp" $bdSrcs $incBd "BD_LSCMModule" -Embind }
    "bd_deformation"   = { Invoke-WasmBuild "bd_deformation" "bindings_bd_deformation_compat.cpp" $bdDeformSrcs $incBdDeform "BdDeformationSolver" }
}

$pageTargets = @("uv_unwrap_simple", "dgp_basic", "uv_unwrap_field", "uv_unwrap_abel_jacobi", "bd_lscm")

if ($Target -eq "page") {
    foreach ($t in $pageTargets) { & $targets[$t] }
} elseif ($Target -eq "all") {
    foreach ($t in $targets.Keys) { & $targets[$t] }
} else {
    & $targets[$Target]
}

Write-Host "`nOutput in $outDir" -ForegroundColor Yellow
Get-ChildItem $outDir -Filter "*.wasm" | Sort-Object Length -Descending |
    ForEach-Object { Write-Host ("  {0,8:N1} KB  {1}" -f ($_.Length / 1KB), $_.Name) }
