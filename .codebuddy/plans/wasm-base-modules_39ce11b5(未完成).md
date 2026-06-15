---
name: wasm-base-modules
overview: 为 BaseMesh、Solver 两个基础模块以及 SimpleParam 下 LSCM、ABF、ARAP 三个子文件夹模块生成 WASM，按文件夹划分，通过 Emscripten + Embind 编译输出。
---

<xml>
<plan_result>
<req>

## 产品概述

为 conformal-parameterization C++ 项目重建 WebAssembly 构建体系，按源码文件夹划分 5 个独立自包含的 WASM 模块：**BaseMesh**（网格数据与 I/O）、**Solver**（数值优化）、**LSCM**（Lscm + Scp 共形映射）、**ABF**（AbfPlusPlus + LinAbf 角度展平）、**ARAP**（ARAP + Tutte 刚体参数化）。每个模块编译其全部依赖的源文件，可独立加载运行，输出到 `assets/wasm/` 目录。后续可按相同模式扩展 ConeParam、CutSeamParam 等模块。

## 核心功能

- **BaseMesh 模块** (`base_mesh.js/.wasm`)：OBJ 文件读写、半边缘网格遍历、高斯曲率计算（角度缺陷法 / 单位面积密度）、准共形误差评估（QcError）
- **Solver 模块** (`solver.js/.wasm`)：梯度下降、Newton、Trust Region、L-BFGS 四种无约束优化算法，以及 AugmentedLagrangian 约束优化、MixedIntegerProgram 混合整数最小二乘
- **LSCM 模块** (`lscm.js/.wasm`)：Least Squares Conformal Maps（Cholesky 分解）+ Spectral Conformal Parameterization（特征值分解）
- **ABF 模块** (`abf.js/.wasm`)：Angle Based Flattening++（Augmented Lagrangian 迭代）+ Linear ABF（SparseLU 直接求解）
- **ARAP 模块** (`arap.js/.wasm`)：As-Rigid-As-Possible（L-BFGS 迭代）+ Tutte 重心坐标嵌入（SparseLU 边界固定）
- 每个模块通过 Embind 暴露对应的 C++ 类和方法，支持 ES Module 方式加载（MODULARIZE=1）
</req>

<tech>

## 技术栈

- **编译器**：Emscripten `em++`（C++17 → WebAssembly）
- **C++ 标准**：`-std=c++17`
- **JS 绑定**：Embind（`--bind`）
- **外部依赖**：Eigen 3.4（header-only，通过 `-I$(EIGEN_PATH)` 引入，默认路径 `./eigen-3.4.0`）
- **构建工具**：GNU Make
- **优化**：`-O3`，`ALLOW_MEMORY_GROWTH=1` 支持大网格动态内存增长

## 实现方案

### 模块自包含编译策略

每个 WASM 模块编译时将所有依赖的 `.cpp` 源文件一并编译链接，避免跨模块运行时依赖：

| 模块 | 源文件 | 依赖关系 |
| --- | --- | --- |
| BaseMesh | BaseMesh/ 全部 8 个 .cpp + Parameterization.cpp | 独立 |
| Solver | Solvers/ 3 个 .cpp（Solver / AugmentedLagrangian / MixedIntegerProgram） | Types.h（header-only） |
| LSCM | BaseMesh/ 全部 + Parameterization.cpp + Lscm.cpp + Scp.cpp | 自包含 BaseMesh |
| ABF | BaseMesh/ 全部 + Parameterization.cpp + Solver.cpp + AugmentedLagrangian.cpp + AbfPlusPlus.cpp + LinAbf.cpp | 自包含 BaseMesh + Solver |
| ARAP | BaseMesh/ 全部 + Parameterization.cpp + Solver.cpp + ARAP.cpp + Tutte.cpp | 自包含 BaseMesh + Solver |


### 核心问题：Mesh.cpp 的 Lscm 依赖解除

`BaseMesh/Mesh.cpp` 第 5 行 `#include "Lscm.h"` 和第 52–65 行 `Mesh::parameterize()` 方法直接创建 `Lscm` 实例调用参数化。此依赖在 BaseMesh/LSCM/ABF 模块 WASM 编译时会引入不必要的 Lscm 头文件依赖。

**解决方案**：用 `#ifndef __EMSCRIPTEN__` / `#endif` 包裹这两处，所有 WASM 模块编译时自动跳过。各 SimpleParam 模块通过各自的算法类（Lscm/Scp/AbfPlusPlus 等）提供 `parameterize()` 功能，不依赖 Mesh 的这一便捷方法。

### Include 路径配置

项目所有源文件使用扁平 `#include "xxx.h"` 引用，不包含路径前缀。Makefile 通过 `-I` 标志为每个模块配置正确的头文件搜索路径：

| 模块 | -I 路径 |
| --- | --- |
| BaseMesh | `-I BaseMesh -I Parameterization` |
| Solver | `-I BaseMesh -I Solvers -I Solvers/Mosek` |
| LSCM | `-I BaseMesh -I Parameterization -I Parameterization/SimpleParam/LSCM` |
| ABF | `-I BaseMesh -I Parameterization -I Parameterization/SimpleParam/ABF -I Solvers -I Solvers/Mosek` |
| ARAP | `-I BaseMesh -I Parameterization -I Parameterization/SimpleParam/ARAP -I Solvers -I Solvers/Mosek` |


### Emscripten 配置

- `--bind` 启用 Embind
- `-s MODULARIZE=1` 产出 ES Module
- `-s EXPORT_NAME="BaseMeshModule"` 等，每模块不同导出名
- `-s ALLOW_MEMORY_GROWTH=1` 动态内存增长
- `-s EXPORTED_RUNTIME_METHODS="['ccall','cwrap','getValue','setValue']"` 导出辅助方法
- MOSEK 在 WASM 中通过已有的 `MosekStub.h` 和 `__EMSCRIPTEN__` 条件编译自动排除

## 目录结构

```
conformal-parameterization/
├── wasm/                              # [NEW] WASM 构建目录
│   ├── Makefile                       # [NEW] 多目标构建脚本
│   ├── bindings_base_mesh.cpp         # [NEW] BaseMesh Embind 绑定
│   ├── bindings_solver.cpp            # [NEW] Solver Embind 绑定
│   ├── bindings_lscm.cpp              # [NEW] LSCM Embind 绑定
│   ├── bindings_abf.cpp               # [NEW] ABF Embind 绑定
│   └── bindings_arap.cpp              # [NEW] ARAP Embind 绑定
├── BaseMesh/
│   └── Mesh.cpp                       # [MODIFY] Lscm 依赖条件排除
└── Solvers/                           # 无需修改
```

输出：

```
assets/wasm/
├── base_mesh.js / base_mesh.wasm
├── solver.js / solver.wasm
├── lscm.js / lscm.wasm
├── abf.js / abf.wasm
└── arap.js / arap.wasm
```

## 关键代码结构

### bindings_base_mesh.cpp 核心暴露

```
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

### bindings_solver.cpp 核心暴露

```
EMSCRIPTEN_BINDINGS(SolverModule) {
    class_<Solver>("Solver")
        .constructor<>()
        .function("gradientDescent", &Solver::gradientDescent)
        .function("newton", &Solver::newton)
        .function("trustRegion", &Solver::trustRegion)
        .function("lbfgs", &Solver::lbfgs);

    class_<AugmentedLagrangian>("AugmentedLagrangian")
        .constructor<int,int,ConstraintFunc,JacobianFunc,ConstraintHessianFunc,Config>()
        .function("solve", &AugmentedLagrangian::solve);

    class_<MixedIntegerProgram>("MixedIntegerProgram")
        .constructor<int,vector<Constraint>,double>()
        .function("solve", &MixedIntegerProgram::solve);
}
```

### bindings_lscm.cpp 核心暴露

```
EMSCRIPTEN_BINDINGS(LSCMModule) {
    class_<Mesh>("Mesh")  // 自包含 Mesh I/O
        .constructor<>()
        .function("read", &Mesh::read)
        .function("write", &Mesh::write);

    class_<Lscm, emscripten::base<Parameterization>>("Lscm")
        .constructor<Mesh&>()
        .function("parameterize", &Lscm::parameterize)
        .function("computeQcError", &Lscm::computeQcError);

    class_<Scp, emscripten::base<Parameterization>>("Scp")
        .constructor<Mesh&>()
        .function("parameterize", &Scp::parameterize)
        .function("computeQcError", &Scp::computeQcError);
}
```

ABF、ARAP 模块的绑定文件同理，分别暴露 AbfPlusPlus/LinAbf 和 ARAP/Tutte。

## 实现备注

- **性能**：每个 WASM 模块包含全部依赖源文件的编译产物，文件体积约 200–500KB（gzip 后约 80–200KB）。不做跨模块共享以保持独立性和简单性。
- **向后兼容**：Mesh.cpp 的条件编译仅在 `__EMSCRIPTEN__` 宏定义时生效，不影响原生 C++（g++/clang++）编译。
- **日志**：Solver 中 `std::cout` 输出（迭代次数、约束违反）在 WASM 中输出到浏览器控制台。
- **MOSEK 降级**：trustRegion() 在 WASM 中因 MosekStub 返回 false 会输出 "Unable to solve QP"，调用方应使用 gradientDescent/newton/lbfgs 作为替代。
</tech>

<todolist>
<item id="fix-mesh-cpp-wasm" deps="">修改 BaseMesh/Mesh.cpp：用 #ifndef **EMSCRIPTEN** 包裹 #include "Lscm.h" 和 Mesh::parameterize() 方法体</item>
<item id="create-wasm-build-system" deps="">新建 wasm/ 目录和 Makefile，配置 5 个模块目标（build-base-mesh/build-solver/build-lscm/build-abf/build-arap/build-all/clean），设置 Eigen 路径和 Emscripten 选项</item>
<item id="create-bindings-all" deps="fix-mesh-cpp-wasm,create-wasm-build-system">创建 5 个 Embind 绑定文件：bindings_base_mesh.cpp（Mesh + 高斯曲率 + QC 误差）、bindings_solver.cpp（Solver + AL + MIP）、bindings_lscm.cpp（Lscm + Scp）、bindings_abf.cpp（Abf++ + LinAbf）、bindings_arap.cpp（ARAP + Tutte）</item>
<item id="build-and-verify" deps="create-bindings-all">编译所有 5 个 WASM 模块，验证 assets/wasm/ 下生成 .js 和 .wasm 文件，无链接错误</item>
</todolist>
</plan_result>
</xml>