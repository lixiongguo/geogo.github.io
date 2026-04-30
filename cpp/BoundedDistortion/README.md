# Bounded Distortion Mapping

基于 Lipman 2012 *"Bounded Distortion Mapping Spaces for Triangular Meshes"* 的 C++ 实现。

## 算法原理

对于三角网格上的分片线性映射，控制每个面的共形扭曲不超过给定上限 C，同时保证无翻转。使用 local-global 迭代方法：

- **Local 步**：对每个面的 Jacobian 矩阵做 SVD，将奇异值投影到 `[ε, C·σ₂]` 范围内
- **Global 步**：从投影后的 Jacobian 通过 Poisson 重构 UV 坐标

## 编译

### 纯 Eigen 版本（无需 libigl）

```bash
mkdir build && cd build
cmake .. -DHAS_LIBIGL=OFF
make
```

### 使用 libigl 版本

```bash
mkdir build && cd build
cmake .. -DHAS_LIBIGL=ON
make
```

## 用法

```bash
./bounded_distortion input.obj output.obj [C=10.0] [max_iter=50]
```

参数说明：
- `C`：扭曲上限，`σ₁/σ₂ ≤ C`，默认 10.0。越小越保角（C=1 为严格共形），但可能无法满足
- `max_iter`：最大迭代次数，默认 50

## 核心 API

```cpp
#include "bounded_distortion.h"

// 主函数
bdm::bounded_distortion_map(V, F, bnd, bnd_uv, U_init, options, result);

// 辅助函数
bdm::compute_local_frames(V, F, Pinv);
bdm::compute_jacobians(U, F, Pinv, J);
bdm::project_to_bounded_distortion_robust(J, C, eps);
bdm::lscm_initial_map(V, F, bnd, bnd_uv, U);
```

## 参考文献

1. Lipman, Y. "Bounded Distortion Mapping Spaces for Triangular Meshes." ACM TOG 2012.
2. Kovalsky, S.Z. et al. "Large-Scale Bounded Distortion Mappings." ACM TOG 2015.
