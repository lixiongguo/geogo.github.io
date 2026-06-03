param(
    [string[]]$Targets = @("uv_unwrap_simple"),
    [switch]$Clean = $false
)

$ErrorActionPreference = "Stop"

$buildRoot = $PSScriptRoot
$cppRoot = Split-Path -Parent $buildRoot
$repoRoot = Split-Path -Parent $cppRoot
$srcRoot = Join-Path $cppRoot "conformal-parameterization"
$omtRoot = Join-Path $cppRoot "MongeAmpere\optimal_mass_transport"
$outDir = Join-Path $repoRoot "assets\wasm"
$tmpDir = Join-Path $buildRoot "build"

$emsdkPath = Join-Path $cppRoot "emsdk"
$eigenInc = Join-Path $cppRoot "deps\eigen-3.4.0"
$glmInc = Join-Path $cppRoot "deps\glm"
$stbInc = Join-Path $cppRoot "deps\stb"

if (!(Test-Path (Join-Path $emsdkPath "emsdk_env.ps1"))) {
    Write-Host "[ERROR] emsdk not found at: $emsdkPath" -ForegroundColor Red
    exit 1
}

Push-Location $emsdkPath
. ".\emsdk_env.ps1" | Out-Null
Pop-Location

$emxx = Get-Command "em++.bat" -ErrorAction SilentlyContinue
if (!$emxx) { $emxx = Get-Command "em++" -ErrorAction SilentlyContinue }
if (!$emxx) {
    Write-Host "[ERROR] em++ not found. Please activate emsdk first." -ForegroundColor Red
    exit 1
}

foreach ($required in @($srcRoot, $eigenInc, $glmInc)) {
    if (!(Test-Path $required)) {
        Write-Host "[ERROR] Required path not found: $required" -ForegroundColor Red
        exit 1
    }
}

if ($Clean) {
    Remove-Item -Recurse -Force $tmpDir -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

function Write-Efile($name, $funcs) {
    $efile = Join-Path $tmpDir "$name.efile"
    $json = "[" + (($funcs | ForEach-Object { "`"$_`"" }) -join ",") + "]"
    $json | Out-File -FilePath $efile -Encoding ascii -NoNewline
    return "@$efile"
}

function Build-Target($name, $sources, $exportName, $funcs, $output, [string[]]$ExtraIncludes = @()) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Building: $name" -ForegroundColor Cyan
    Write-Host "  => $output" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    $efile = Write-Efile $name $funcs
    $includeFlags = @(
        "-I$srcRoot",
        "-I$(Join-Path $srcRoot "uv_unwrap_simple")",
        "-I$(Join-Path $srcRoot "Mosek")",
        "-I$eigenInc",
        "-I$glmInc"
    ) + $ExtraIncludes

    $args = @(
        "-std=c++17",
        "-O2",
        "-flto"
    ) + $includeFlags + @(
        "-s", "MODULARIZE=1",
        "-s", "ALLOW_MEMORY_GROWTH=1",
        "-s", "INITIAL_MEMORY=268435456",
        "-s", "WASM=1",
        "-s", "EXPORTED_RUNTIME_METHODS=['ccall','cwrap','UTF8ToString','getValue','setValue']",
        "-s", "FORCE_FILESYSTEM=0",
        "-s", "ENVIRONMENT='web'",
        "-s", "EXPORT_NAME=`"$exportName`"",
        "-s", "EXPORTED_FUNCTIONS=$efile"
    ) + $sources + @("-o", $output)

    & $emxx.Source @args
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed: $name"
    }
    Write-Host "[DONE] $name -> $output" -ForegroundColor Green
}

$meshSrcs = @(
    "Mesh.cpp",
    "MeshIO.cpp",
    "Solver.cpp",
    "Parameterization.cpp",
    "Vertex.cpp",
    "Edge.cpp",
    "Face.cpp",
    "HalfEdge.cpp"
) | ForEach-Object { Join-Path $srcRoot $_ }

$uvSimpleSources = @(
    (Join-Path $buildRoot "uv-unwrap-simple\wasm_uv_unwrap_simple.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\Lscm.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\Tutte.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\Scp.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\CirclePatterns.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\AugmentedLagrangian.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\Cetm.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\RicciFlow.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\LinAbf.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\AbfPlusPlus.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\ARAP.cpp"),
    (Join-Path $srcRoot "geometry\QcError.cpp")
) + $meshSrcs

$dgpBasicSources = @(
    (Join-Path $buildRoot "dgp-basic\wasm_dgp_basic.cpp"),
    (Join-Path $srcRoot "geometry\GaussianCurvature.cpp"),
    (Join-Path $srcRoot "geometry\PrincipalCurvatureField.cpp")
) + $meshSrcs

$uvFieldSources = @(
    (Join-Path $buildRoot "uv-unwrap-field\wasm_uv_unwrap_field.cpp"),
    (Join-Path $srcRoot "uv_unwrap_field\QuadCover.cpp"),
    (Join-Path $srcRoot "uv_unwrap_field\CrossFieldIntegerProgram.cpp"),
    (Join-Path $srcRoot "uv_unwrap_field\MIQQuad.cpp"),
    (Join-Path $srcRoot "uv_unwrap_field\HolomorphicOneForm.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\Lscm.cpp"),
    (Join-Path $srcRoot "geometry\PrincipalCurvatureField.cpp"),
    (Join-Path $srcRoot "geometry\QcError.cpp")
) + $meshSrcs

$abelJacobiSources = @(
    (Join-Path $buildRoot "abel-jacobi\wasm_uv_unwrap_abel_jacobi.cpp"),
    (Join-Path $srcRoot "Abel_Jacoi\AbelJacobi.cpp"),
    (Join-Path $srcRoot "Abel_Jacoi\AbelJacobiParameterization.cpp"),
    (Join-Path $srcRoot "uv_unwrap_simple\Lscm.cpp"),
    (Join-Path $srcRoot "QcError.cpp")
) + $meshSrcs

$abelJacobiIncludes = @(
    "-I$(Join-Path $srcRoot "Abel_Jacoi")"
)

$targetSet = @{}
foreach ($target in $Targets) {
    $targetSet[$target] = $true
}
$buildAll = $Targets.Count -eq 0 -or $targetSet.ContainsKey("all")

if ($buildAll -or $targetSet.ContainsKey("uv_unwrap_simple") -or $targetSet.ContainsKey("simple")) {
    Build-Target "uv_unwrap_simple" `
        $uvSimpleSources `
        "UvUnwrapSimpleSolver" `
        @(
            "_malloc","_free",
            "_solve_lscm","_solve_tutte_circle","_solve_tutte_square","_solve_scp",
            "_solve_linabf","_solve_abfpp","_solve_arap",
            "_solve_cp","_solve_cetm","_solve_ricci",
            "_get_uv_result","_get_uv_result_size","_get_last_time_ms","_get_cp_fallback_to_cetm",
            "_is_closed_mesh",
            "_dispose",
            "_load_mesh_with_uv","_compute_qc_error",
            "_get_qc_errors","_get_qc_errors_size","_get_qc_colors","_get_qc_colors_size"
        ) `
        (Join-Path $outDir "uv_unwrap_simple.js")
}

if ($buildAll -or $targetSet.ContainsKey("dgp_basic") -or $targetSet.ContainsKey("dgp")) {
    Build-Target "dgp_basic" `
        $dgpBasicSources `
        "DgpBasicSolver" `
        @(
            "_malloc","_free",
            "_load_mesh","_is_closed_mesh",
            "_compute_gauss_curvature_per_area","_get_gc_result","_get_gc_result_size",
            "_compute_principal_curvature_field","_get_pc_field","_get_pc_field_size",
            "_get_pc_k1k2","_get_pc_k1k2_size",
            "_dispose"
        ) `
        (Join-Path $outDir "dgp_basic.js")
}

if ($buildAll -or $targetSet.ContainsKey("uv_unwrap_field") -or $targetSet.ContainsKey("field")) {
    Build-Target "uv_unwrap_field" `
        $uvFieldSources `
        "UvUnwrapFieldSolver" `
        @(
            "_malloc","_free",
            "_load_mesh",
            "_step1_compute_principal_field",
            "_step2_smooth_and_matching",
            "_step3_solve_quadcover",
            "_solve_miq",
            "_solve_hof",
            "_get_last_time_ms",
            "_get_miq_energy",
            "_get_face_dirs","_get_face_dirs_size",
            "_get_matching","_get_matching_size",
            "_get_face_theta","_get_face_theta_size",
            "_get_edge_jumps","_get_edge_jumps_size",
            "_get_uv_result","_get_uv_result_size",
            "_dispose"
        ) `
        (Join-Path $outDir "uv_unwrap_field.js")
}

if ($buildAll -or $targetSet.ContainsKey("abel_jacobi") -or $targetSet.ContainsKey("global_cross_fields")) {
    Build-Target "abel_jacobi" `
        $abelJacobiSources `
        "UvUnwrapAbelJacobiSolver" `
        @(
            "_malloc","_free",
            "_load_mesh",
            "_is_closed_mesh",
            "_get_genus",
            "_build_abel_jacobi",
            "_solve_abel_jacobi",
            "_get_built",
            "_get_used_fallback",
            "_get_poincare_ok",
            "_get_abel_ok",
            "_get_lattice_residual",
            "_get_lattice_generators",
            "_get_lattice_generators_size",
            "_get_lattice_rows",
            "_get_lattice_cols",
            "_get_last_time_ms",
            "_get_uv_result",
            "_get_uv_result_size",
            "_dispose"
        ) `
        (Join-Path $outDir "uv_unwrap_abel_jacobi.js") `
        $abelJacobiIncludes
}

# ── OMT: Optimal Mass Transport Image Interpolation ──
$omtSources = @(
    (Join-Path $buildRoot "omt\wasm_omt.cpp")
)

if ($buildAll -or $targetSet.ContainsKey("omt")) {
    Build-Target "omt" `
        $omtSources `
        "OmTSolver" `
        @(
            "_malloc","_free",
            "_solve_omt_series",
            "_get_omt_last_time_ms",
            "_get_omt_result_data","_get_omt_result_size",
            "_get_omt_frame_width","_get_omt_frame_height","_get_omt_frame_count",
            "_omt_dispose"
        ) `
        (Join-Path $outDir "omt_solver.js") `
        @("-I$omtRoot", "-I$stbInc")
}

Write-Host ""
Write-Host "Output files in ${outDir}:" -ForegroundColor Yellow
@("uv_unwrap_simple.*", "uv_unwrap_field.*", "uv_unwrap_abel_jacobi.*") | ForEach-Object {
    Get-ChildItem -Path $outDir -Filter $_ -ErrorAction SilentlyContinue | ForEach-Object {
        $size = "{0,8:N1} KB" -f ($_.Length / 1024)
        Write-Host "  $size  $($_.Name)" -ForegroundColor White
    }
}
