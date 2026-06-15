---
name: wasm-base-modules
overview: 为 6 个模块生成 WASM：BaseMesh（网格基础）、CutSeamMesh（切割网格，BaseMesh 补充）、Solver（优化求解器）、LSCM、ABF、ARAP（SimpleParam 三个子文件夹），按文件夹划分，自包含编译。
todos:
  - id: fix-mesh-cpp-wasm
    content: "修改 BaseMesh/Mesh.cpp：用 #ifndef __EMSCRIPTEN__ 包裹 #include \"Lscm.h\"（第5行）和 Mesh::parameterize() 方法体（第52-65行）"
    status: completed
  - id: create-wasm-build-system
    content: 新建 wasm/ 目录和 Makefile，配置 6 个模块编译目标（build-base-mesh/build-cutseam-mesh/build-solver/build-lscm/build-abf/build-arap/build-all/clean），设置 Eigen 路径和 Emscripten 公共选项
    status: completed
  - id: create-bindings-base
    content: 创建 bindings_base_mesh.cpp 和 bindings_cutseam_mesh.cpp：BaseMesh 暴露 Mesh+高斯曲率+QC误差；CutSeamMesh 暴露切割构造+索引映射+同调基构建
    status: completed
    dependencies:
      - fix-mesh-cpp-wasm
  - id: create-bindings-solver
    content: 创建 bindings_solver.cpp：暴露 Solver（4种优化算法+MeshHandle）+ AugmentedLagrangian（solve+Config）+ MixedIntegerProgram（solve+Constraint）
    status: completed
    dependencies:
      - create-wasm-build-system
  - id: create-bindings-param
    content: 创建 bindings_lscm.cpp、bindings_abf.cpp、bindings_arap.cpp：分别暴露 Lscm+Scp、AbfPlusPlus+LinAbf、ARAP+Tutte 参数化算法
    status: completed
    dependencies:
      - fix-mesh-cpp-wasm
      - create-wasm-build-system
  - id: build-and-verify
    content: 编译全部 6 个 WASM 模块，验证 assets/wasm/ 下生成 .js 和 .wasm 文件，无编译链接错误
    status: completed
    dependencies:
      - create-bindings-base
      - create-bindings-solver
      - create-bindings-param
---

## 产品概述

为 conformal-parameterization C++ 项目重建 WebAssembly 构建体系，按源码文件夹划分 6 个独立自包含的 WASM 模块：**BaseMesh**（网格数据与 I/O）、**CutSeamMesh**（割缝网格与同调基）、**Solver**（数值优化）、**LSCM**（Lscm + Scp 共形映射）、**ABF**（AbfPlusPlus + LinAbf 角度展平）、**ARAP**（ARAP + Tutte 刚体参数化）。每个模块编译其全部依赖的源文件，可独立加载运行，输出到 `assets/wasm/` 目录。后续可按相同模式扩展 ConeParam、CutSeamParam 等模块。

## 核心功能

- **BaseMesh 模块** (`base_mesh.js/.wasm`)：OBJ 文件读写、半边缘网格遍历、高斯曲率计算（角度缺陷法 / 单位面积密度）、准共形误差评估（QcError）
- **CutSeamMesh 模块** (`cutseam_mesh.js/.wasm`)：沿割缝边复制顶点构建切割网格（`buildFromSeamEdges` / `buildFromSeamVertexPairs`）、原始顶点/面索引反向查询、切割边界边判定、Tree-Cotree 同调基构建与自动切割
- **Solver 模块** (`solver.js/.wasm`)：梯度下降、Newton、Trust Region、L-BFGS 四种无约束优化算法，以及 AugmentedLagrangian 约束优化、MixedIntegerProgram 混合整数最小二乘
- **LSCM 模块** (`lscm.js/.wasm`)：Least Squares Conformal Maps（Cholesky 分解）+ Spectral Conformal Parameterization（特征值分解）
- **ABF 模块** (`abf.js/.wasm`)：Angle Based Flattening++（Augmented Lagrangian 迭代）+ Linear ABF（SparseLU 直接求解）
- **ARAP 模块** (`arap.js/.wasm`)：As-Rigid-As-Possible（L-BFGS 迭代）+ Tutte 重心坐标嵌入（SparseLU 边界固定）
- 每个模块通过 Embind 暴露对应的 C++ 类和方法，支持 ES Module 方式加载（MODULARIZE=1）

## 技术栈

- **编译器**：Emscripten `em++`（C++17 → WebAssembly）
- **C++ 标准**：`-std=c++17`
- **JS 绑定**：Embind（`--bind`）
- **外部依赖**：Eigen 3.4（header-only，通过 `-I$(EIGEN_PATH)` 引入，默认路径 `./eigen-3.4.0`）
- **构建工具**：GNU Make
- **优化**：`-O3`，`ALLOW_MEMORY_GROWTH=1` 支持大网格动态内存增长

## 实现方案

### 模块自包含编译策略

每个 WASM 模块编译时将所有依赖的 `.cpp` 源文件一并编译链接，避免跨模块运行时依赖。Makefile 从 `wasm/` 目录构建，源代码以 `../` 上级路径引用。

| 模块 | 源文件 | 依赖关系 | 导出名 |
| --- | --- | --- | --- |
| BaseMesh | BaseMesh/ 全部 8 .cpp + Parameterization.cpp | 独立 | `BaseMeshModule` |
| CutSeamMesh | BaseMesh/ 全部 + Parameterization.cpp + CutSeamMesh.cpp | 自包含 BaseMesh | `CutSeamMeshModule` |
| Solver | Solvers/ Solver.cpp + AugmentedLagrangian.cpp + MixedIntegerProgram.cpp | Types.h（header-only） | `SolverModule` |
| LSCM | BaseMesh/ 全部 + Parameterization.cpp + Lscm.cpp + Scp.cpp | 自包含 BaseMesh | `LSCMModule` |
| ABF | BaseMesh/ 全部 + Parameterization.cpp + Solver.cpp + AugmentedLagrangian.cpp + AbfPlusPlus.cpp + LinAbf.cpp | 自包含 BaseMesh + Solver | `ABFModule` |
| ARAP | BaseMesh/ 全部 + Parameterization.cpp + Solver.cpp + ARAP.cpp + Tutte.cpp | 自包含 BaseMesh + Solver | `ARAPModule` |


### 核心问题：Mesh.cpp 的 Lscm 依赖解除

`BaseMesh/Mesh.cpp` 第 5 行 `#include "Lscm.h"` 和第 52–65 行 `Mesh::parameterize()` 方法直接创建 `Lscm` 实例调用参数化。此依赖在 BaseMesh/CutSeamMesh/LSCM/ABF/ARAP 模块 WASM 编译时会引入不必要的 Lscm 头文件依赖。

**解决方案**：用 `#ifndef __EMSCRIPTEN__` / `#endif` 包裹这两处，所有 WASM 模块编译时自动跳过。各 SimpleParam 模块通过各自的算法类（Lscm/Scp/AbfPlusPlus 等）提供 `parameterize()` 功能，不依赖 Mesh 的这一便捷方法。

### CutSeamMesh 特殊处理

`CutSeamMesh.h` 使用 `#include "../BaseMesh/Mesh.h"`（相对上级路径），`CutSeamMesh.cpp` 使用 `#include "../BaseMesh/MeshIO.h"`。编译器会根据文件位置自动解析这些相对路径，Makefile 仅需为扁平 `#include "xxx.h"` 提供 `-I` 搜索路径。`TreeCotreeBasis.h` 为 14KB header-only 模板文件（namespace `topology`），无需单独编译，包含在 CutSeamMesh 绑定目标中。

### Include 路径配置

从 `wasm/` 目录编译，所有源文件通过 `../` 引用。为扁平 `#include "xxx.h"` 配置 `-I` 搜索路径：

| 模块 | -I 路径 |
| --- | --- |
| BaseMesh | `-I ../BaseMesh -I ../Parameterization` |
| CutSeamMesh | `-I ../BaseMesh -I ../CutSeamMesh -I ../Parameterization` |
| Solver | `-I ../BaseMesh -I ../Solvers -I ../Solvers/Mosek` |
| LSCM | `-I ../BaseMesh -I ../Parameterization -I ../Parameterization/SimpleParam/LSCM` |
| ABF | `-I ../BaseMesh -I ../Parameterization -I ../Parameterization/SimpleParam/ABF -I ../Solvers -I ../Solvers/Mosek` |
| ARAP | `-I ../BaseMesh -I ../Parameterization -I ../Parameterization/SimpleParam/ARAP -I ../Solvers -I ../Solvers/Mosek` |


### Emscripten 配置（所有模块共用）

- `--bind` 启用 Embind
- `-s MODULARIZE=1` 产出 ES Module
- `-s EXPORT_NAME="模块名"` 每模块不同导出名
- `-s ALLOW_MEMORY_GROWTH=1` 动态内存增长
- `-s EXPORTED_RUNTIME_METHODS="['ccall','cwrap','getValue','setValue']"` 导出辅助方法
- MOSEK 在 WASM 中通过已有的 `MosekStub.h` 和 `#ifndef __EMSCRIPTEN__` 条件编译自动排除

## 目录结构

```
conformal-parameterization/
├── wasm/                              # [NEW] WASM 构建目录
│   ├── Makefile                       # [NEW] 6 模块多目标构建脚本
│   ├── bindings_base_mesh.cpp         # [NEW] BaseMesh Embind 绑定
│   ├── bindings_cutseam_mesh.cpp      # [NEW] CutSeamMesh + TreeCotreeBasis 绑定
│   ├── bindings_solver.cpp            # [NEW] Solver Embind 绑定
│   ├── bindings_lscm.cpp              # [NEW] LSCM Embind 绑定（Lscm + Scp）
│   ├── bindings_abf.cpp               # [NEW] ABF Embind 绑定（AbfPlusPlus + LinAbf）
│   └── bindings_arap.cpp              # [NEW] ARAP Embind 绑定（ARAP + Tutte）
├── BaseMesh/
│   └── Mesh.cpp                       # [MODIFY] Lscm 依赖条件排除
├── CutSeamMesh/                       # 无需修改
├── Solvers/                           # 无需修改
└── Parameterization/                  # 无需修改
```

输出（`assets/wasm/`）：

```
assets/wasm/
├── base_mesh.js + base_mesh.wasm
├── cutseam_mesh.js + cutseam_mesh.wasm
├── solver.js + solver.wasm
├── lscm.js + lscm.wasm
├── abf.js + abf.wasm
└── arap.js + arap.wasm
```

## 关键代码结构

### bindings_base_mesh.cpp

```cpp
EMSCRIPTEN_BINDINGS(BaseMeshModule) {
    class_<Mesh>("Mesh")
        .constructor<>()
        .function("read", &Mesh::read)
        .function("write", &Mesh::write)
        .function("meanEdgeLength", &Mesh::meanEdgeLength)
        .function("delaunayize", &Mesh::delaunayize);

    function("gaussianCurvatureAngleDeficit", &geometry::gaussianCurvatureAngleDeficit);
    function("gaussianCurvaturePerArea", &geometry::gaussianCurvaturePerArea);

    class_<QuasiConformalError>("QuasiConformalError")
        .class_function("compute", &QuasiConformalError::compute)
        .class_function("color", &QuasiConformalError::color);
}
```

### bindings_cutseam_mesh.cpp

```cpp
EMSCRIPTEN_BINDINGS(CutSeamMeshModule) {
    class_<Mesh>("Mesh")  // 自包含基础 Mesh I/O
        .constructor<>()
        .function("read", &Mesh::read)
        .function("write", &Mesh::write);

    class_<CutSeamMesh, base<Mesh>>("CutSeamMesh")
        .constructor<>()
        .constructor<const Mesh&>()
        .function("buildFromSeamEdges", &CutSeamMesh::buildFromSeamEdges)
        .function("buildFromSeamVertexPairs", &CutSeamMesh::buildFromSeamVertexPairs)
        .function("originalVertexIndex", &CutSeamMesh::originalVertexIndex)
        .function("originalFaceIndex", &CutSeamMesh::originalFaceIndex)
        .function("isCutBoundaryEdge", select_overload<bool(int)const>(&CutSeamMesh::isCutBoundaryEdge))
        .function("seamVertexPairs", &CutSeamMesh::seamVertexPairs);

    // TreeCotreeBasis 静态方法（header-only，namespace topology）
    // buildClosedMeshBasis(const Mesh&) → vector<Cycle>
    // buildCutSeamMesh(const Mesh&) → CutSeamMesh
}
```

### bindings_solver.cpp

```cpp
EMSCRIPTEN_BINDINGS(SolverModule) {
    class_<MeshHandle>("MeshHandle").constructor<>();

    class_<Solver>("Solver")
        .constructor<>()
        .property("handle", &Solver::handle)
        .property("x", &Solver::x)
        .property("n", &Solver::n)
        .function("gradientDescent", &Solver::gradientDescent)
        .function("newton", &Solver::newton)
        .function("trustRegion", &Solver::trustRegion)
        .function("lbfgs", &Solver::lbfgs);

    class_<AugmentedLagrangianConfig>("AugmentedLagrangianConfig")
        .constructor<>()
        .property("rhoInit", &AugmentedLagrangianConfig::rhoInit)
        .property("rhoMax", &AugmentedLagrangianConfig::rhoMax)
        .property("rhoScale", &AugmentedLagrangianConfig::rhoScale)
        .property("tolOuter", &AugmentedLagrangianConfig::tolOuter)
        .property("tolInner", &AugmentedLagrangianConfig::tolInner)
        .property("maxOuter", &AugmentedLagrangianConfig::maxOuter)
        .property("maxInner", &AugmentedLagrangianConfig::maxInner);

    class_<AugmentedLagrangian>("AugmentedLagrangian")
        .constructor<int, int, AugmentedLagrangian::ConstraintFunc,
                     AugmentedLagrangian::JacobianFunc,
                     AugmentedLagrangian::ConstraintHessianFunc,
                     const AugmentedLagrangianConfig&>()
        .function("solve", &AugmentedLagrangian::solve);

    class_<MixedIntegerProgram>("MixedIntegerProgram")
        .constructor<int, std::vector<MixedIntegerProgram::Constraint>, double>()
        .function("solve", &MixedIntegerProgram::solve)
        .function("energy", &MixedIntegerProgram::energy);
}
```

### bindings_lscm.cpp / bindings_abf.cpp / bindings_arap.cpp

分别暴露 Lscm+Scp、AbfPlusPlus+LinAbf、ARAP+Tutte，均继承自 Parameterization，提供 `parameterize()` 和 `computeQcError()` 方法。ARAP 模块额外自包含 Solver 源文件。

## 实现备注

- **性能**：每个 WASM 模块包含全部依赖源文件的编译产物，文件体积约 200–500KB（gzip 后约 80–200KB）。不做跨模块共享以保持独立性和简单性。
- **向后兼容**：Mesh.cpp 的条件编译仅在 `__EMSCRIPTEN__` 宏定义时生效，不影响原生 C++（g++/clang++）编译。
- **日志**：Solver 中 `std::cout` 输出（迭代次数、约束违反）在 WASM 中输出到浏览器控制台。
- **MOSEK 降级**：trustRegion() 在 WASM 中因 MosekStub 返回 false 会输出 "Unable to solve QP"，调用方应使用 gradientDescent/newton/lbfgs 作为替代。
- **TreeCotreeBasis**：为 header-only 模板，包含在 CutSeamMesh 绑定中作为静态方法暴露，无需额外编译单元。