---
name: rebuild-wasm
overview: 重新构建 WASM 模块：创建缺失的3个 compat binding 文件（uv_unwrap_field、uv_unwrap_abel_jacobi、bd_deformation），更新 Makefile 添加对应构建目标，然后执行 make build-all 完成构建。
todos:
  - id: create-field-compat
    content: 新建 bindings_uv_unwrap_field_compat.cpp，实现 UvUnwrapFieldSolver 的 ccall 接口（QuadCover 三步管线 + HOF + MIQ）
    status: completed
  - id: create-abel-compat
    content: 新建 bindings_uv_unwrap_abel_jacobi_compat.cpp，实现 UvUnwrapAbelJacobiSolver 的 ccall 接口（AbelJacobiParameterization + genus/divisor 统计）
    status: completed
  - id: create-bd-deform-compat
    content: 新建 bindings_bd_deformation_compat.cpp，实现 BdDeformationSolver 的 ccall 接口（增量 bounded distortion 优化）
    status: completed
  - id: update-makefile
    content: 更新 Makefile，新增 field-compat、abel-compat、bd-deform-compat 三个构建目标及源文件组/include/clean/help/.PHONY
    status: completed
    dependencies:
      - create-field-compat
      - create-abel-compat
      - create-bd-deform-compat
  - id: run-build
    content: 在 cpp/conformal-parameterization/wasm/ 目录执行 make build-all 编译全部 WASM 模块
    status: completed
    dependencies:
      - update-makefile
---

## 用户需求

重新编译所有 WASM 模块。当前 macOS 环境下 em++ 已可用，Eigen 库已就绪。需要补齐缺失的 compat binding 文件，更新 Makefile 构建目标，最终编译生成可用的 `.js` / `.wasm` 文件。

## 核心功能

- 为 `uv_unwrap_field`（全局场求解器）、`uv_unwrap_abel_jacobi`（Abel-Jacobi 参数化）、`bd_deformation`（有界失真变形）三个模块创建 ccall compat binding
- 在 Makefile 中新增对应的 `build-field-compat`、`build-abel-compat`、`build-bd-deform-compat` 构建目标
- 更新 `build-all`、`clean`、`help`、`.PHONY` 以覆盖新目标
- 执行构建，输出至 `assets/wasm/`

## 技术栈

- **编译器**：Emscripten em++（`cpp/emsdk/`），C++17
- **数学库**：Eigen 3.4.0（`cpp/deps/eigen-3.4.0/`）
- **构建系统**：GNU Make（`cpp/conformal-parameterization/wasm/Makefile`）
- **JS 交互**：ccall API（`EMSCRIPTEN_KEEPALIVE` + `extern "C"`，无 `--bind`）

## 实现方案

### 总体策略

参照已有的 `bindings_dgp_basic_compat.cpp` 和 `bindings_uv_unwrap_simple_compat.cpp` 模式，为三个缺失模块创建 compat binding 文件。每个 binding 文件使用全局静态变量管理状态、`extern "C"` 导出 ccall 兼容函数。Makefile 新增对应的源文件组、include 路径和构建目标。

### 关键技术决策

- **重用 compat 编译标志**：`EM_FLAGS_COMPAT`（`-s MODULARIZE=1 -s ALLOW_MEMORY_GROWTH=1 -s WASM=1 -s EXPORTED_FUNCTIONS=['_malloc','_free'] -s EXPORTED_RUNTIME_METHODS=['ccall','cwrap','getValue','setValue']`）
- **内存管理**：JS 端手动 `_malloc/_free`，C++ 端返回静态 buffer 指针（无拷贝），与已有 compat 模块一致
- **状态隔离**：每个模块独立全局静态变量，互不干扰
- **bd_deformation 特殊设计**：`setup_mesh` 上传 2D 顶点/面数据并持久化；`optimize_step` 每次以当前 UV 为起点调用 `bounded_distortion::solveBoundedDistortionMap` 推进优化，更新 UV 并返回迭代数

### 性能考量

- 编译使用 `-O3` 优化
- `get_uv_result()` 和 `get_uv_ptr()` 直接返回 `std::vector<double>::data()` 指针，无拷贝
- `bd_deformation` 的 `optimize_step` 增量迭代，避免每步重建求解器

## 修改文件清单

```
cpp/conformal-parameterization/wasm/
├── bindings_uv_unwrap_field_compat.cpp      # [NEW] 全局场求解器 compat binding
├── bindings_uv_unwrap_abel_jacobi_compat.cpp # [NEW] Abel-Jacobi compat binding
├── bindings_bd_deformation_compat.cpp       # [NEW] 有界失真变形 compat binding
└── Makefile                                  # [MODIFY] 新增3个target + 更新all/clean/help/.PHONY
```

### bindings_uv_unwrap_field_compat.cpp

**功能**：封装 QuadCover（三步管线）、HolomorphicOneForm、MIQQuad 的 ccall 接口。模块名 `UvUnwrapFieldSolver`。

**导出函数**：

- `dispose()` — 释放 mesh 和状态
- `load_mesh(double* pos, int posLen, int* face, int faceLen)` — 从 flat 数组构建 Mesh
- `step1_compute_principal_field()` — 计算主曲率方向场（NRosyVectorFields + PrincipalCurvatureField）
- `step2_smooth_and_matching(int iters)` — 平滑交叉场 + computeMatching
- `step3_solve_quadcover(int opt)` — 构建 branch cover + 全局参数化
- `solve_hof()` — HolomorphicOneForm 参数化
- `solve_miq(int crossIters, int jumpRefinePasses)` — MIQ 混合整数参数化
- `get_uv_result_size()`, `get_uv_result()`, `get_last_time_ms()`, `get_miq_energy()` — 结果查询

**源文件**：baseMesh(9) + CutSeamMesh.cpp + Solver(3) + GlobalFieldsParameterization.cpp + QuadCover.cpp + MIQQuad.cpp + CutSeamParameterization.cpp + HolomorphicOneForm.cpp + Lscm.cpp + NRosyVectorFields.cpp + PrincipalCurvatureField.cpp

**Include 路径**：BaseMesh, CutSeamMesh, Parameterization, GlobalFieldsParam, CutSeamParam, HoloOneForm, SimpleParam/LSCM, VectorFileds, PrincipalCurvatureFields, Solvers, Solvers/Mosek

### bindings_uv_unwrap_abel_jacobi_compat.cpp

**功能**：封装 AbelJacobiParameterization（含 LSCM fallback）。模块名 `UvUnwrapAbelJacobiSolver`。

**导出函数**：

- `dispose()` — 释放状态
- `solve_abel_jacobi(double* pos, int posLen, int* face, int faceLen, int baseVertex, int, int, int, int)` — 构建 Mesh → 运行 AbelJacobiParameterization → 提取 UV
- `get_uv_result_size()`, `get_uv_result()`, `get_last_time_ms()` — 结果查询
- `get_genus()` — 亏格
- `get_built()` — AbelJacobi::isReady()
- `get_poincare_ok()`, `get_abel_ok()`, `get_lattice_residual()` — 除子检查结果

**源文件**：baseMesh(9) + CutSeamMesh.cpp + CutSeamParameterization.cpp + AbelJacobi.cpp + AbelJacobiParameterization.cpp + Lscm.cpp

### bindings_bd_deformation_compat.cpp

**功能**：封装 bounded_distortion::solveBoundedDistortionMap 增量优化。模块名 `BdDeformationSolver`。

**导出函数**：

- `set_options(double d_b, double min_alpha, double lscm_w, double dist_p, double pos_p, double ref_w, double smooth_w, double step, double bound_on)` — 配置 Options
- `setup_mesh(double* pos, int posLen, int* face, int faceLen)` — 上传 2D 顶点/面（pos 为 2*nV doubles）
- `get_vertex_count()` — 返回 nV
- `get_uv_ptr()` — 返回当前 UV 数据指针（2*nV doubles）
- `optimize_step(int maxSteps, int* idxPtr, int nA, double* tgtPtr)` — 运行 bounded distortion 优化 maxSteps 个 outer 迭代
- `get_last_iterations(), get_max_distortion(), get_min_jacobian(), get_flip_count()` — 统计查询

**源文件**：仅 `Bounded/bounded_distortion_mapping/BoundedDistortionMapping.cpp`

### Makefile 修改

新增变量和规则：

- `FIELD_COMPAT_SRCS` / `FIELD_COMPAT_INC` → `build-field-compat: $(OUTPUT_DIR)/uv_unwrap_field.js`
- `ABEL_COMPAT_SRCS` / `ABEL_COMPAT_INC` → `build-abel-compat: $(OUTPUT_DIR)/uv_unwrap_abel_jacobi.js`
- `BD_DEFORM_COMPAT_SRCS` / `BD_DEFORM_COMPAT_INC` → `build-bd-deform-compat: $(OUTPUT_DIR)/bd_deformation.js`
- 更新 `build-all` 依赖列表（追加3个新目标）
- 更新 `clean` 清理新增的 js/wasm
- 更新 `help` 文档
- 更新 `.PHONY` 声明