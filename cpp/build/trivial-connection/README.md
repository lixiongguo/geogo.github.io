# Trivial Connection Reproduction (Keenan Crane style)

This directory contains a runnable C++ prototype for the core idea of
Keenan Crane's **trivial connections** direction-field design:

1. Enforce Gauss-Bonnet compatible singularity indices.
2. Solve a minimum-norm discrete connection correction.
3. Integrate the connection to recover per-face field angles.

It now includes two executables:

- `trivial_connection.exe`: vector field (`N=1`) version.
- `nrosy_trivial_connection.exe`: `N`-RoSy version (default `N=4`) with period jumps.

## Build and run

```powershell
cd cpp\build\trivial-connection
.\build_trivial_connection.ps1 -ModelPath "..\..\..\assets\Models2\torus_F7680.obj" -AutoSingularity
```

Or provide your own singularities (`vertex,index`):

```powershell
.\build_trivial_connection.ps1 `
  -ModelPath "..\..\..\assets\Models2\torus_F7680.obj" `
  -OutDir "..\..\..\assets\CP_Models\trivial_connection_torus" `
  -SingularityCsv ".\singularity.csv"
```

## Outputs

- `connection.csv`: per-edge connection correction `phi`.
- `face_field.csv`: per-face angle and 3D direction vector.
- `singularity_used.csv`: singularity index and target curvature.

For N-RoSy:

```powershell
.\build_nrosy_trivial_connection.ps1 `
  -ModelPath "..\..\..\assets\Models2\torus_F7680.obj" `
  -OutDir "..\..\..\assets\CP_Models\nrosy_tc_torus" `
  -N 4 `
  -AutoSingularity
```

N-RoSy outputs:

- `edge_jumps.csv`: per-edge `phi`, integer jump `p`, residual.
- `face_nrosy_field.csv`: per-face angle modulo `2π/N` and direction vector.
- `singularity_used.csv`: integer charge `q` and index `q/N`.

## Model assumptions

- Current implementation supports **closed triangle meshes**.
- This is a practical reproduction of the core pipeline, not a full reimplementation
  of every optional step in all published variants.

