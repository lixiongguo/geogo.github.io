# Incremental Flattening Reproduction (Core Stages)

This folder provides a runnable reproduction of the key stages from
**Global Parameterization by Incremental Flattening (Myles et al., TOG 2012)**:

1. Flattening (iterative metric flattening),
2. Cone curvature rounding (to nearest `k * pi/2`).

The implementation outputs:

- `cones.csv`: per-vertex boundary/flatten/candidate flags, original and final curvatures, rounded targets.
- `edge_metric.csv`: intrinsic edge lengths before/after optimization.
- `vertex_log_scale.csv`: solved log-scale factors (`u` / `phi`) per vertex.
- `summary.txt`: run parameters and stage statistics.

## Build and run

```powershell
cd cpp\build\incremental-flattening
.\build_incremental_flattening.ps1
```

Custom input/output:

```powershell
.\build_incremental_flattening.ps1 `
  -ModelPath "..\..\..\assets\Models2\torus_F7680.obj" `
  -OutDir "..\..\..\assets\CP_Models\incremental_torus"
```

## Notes

- This implementation focuses on the paper's **metric evolution core**:
  flattening + cone rounding.
- Full homology-loop holonomy rounding and final seamless global ARAP solve
  are not included yet.
- The code is intended as a practical, inspectable base for extending to the
  complete pipeline described in the paper and your article.

