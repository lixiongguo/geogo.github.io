---
name: wasm-base-modules
overview: 为 BaseMesh 和 Solver 两个基础模块重新生成 WASM，按文件夹划分模块，创建 Emscripten 绑定文件和 CMake 构建系统。
todos:
  - id: fix-mesh-cpp-wasm
    content: 修改 BaseMesh/Mesh.cpp，为 Lscm.h 引入和 parameterize() 方法添加 __EMSCRIPTEN__ 条件编译排除
    status: pending
  - id: create-wasm-dir-makefile
    content: 新建 wasm/ 目录和 Makefile，配置多模块编译目标（base-mesh / solver / all / clean），包含 Eigen 路径和 Emscripten 选项
    status: pending
  - id: create-base-mesh-binding
    content: 创建 wasm/bindings_base_mesh.cpp，通过 Embind 暴露 Mesh OBJ 读写、高斯曲率、QC 误差
    status: pending
    dependencies:
      - fix-mesh-cpp-wasm
  - id: create-solver-binding
    content: 创建 wasm/bindings_solver.cpp，通过 Embind 暴露 Solver 四种优化算法、AugmentedLagrangian、MixedIntegerProgram
    status: pending
    dependencies:
      - create-wasm-dir-makefile
  - id: build-and-verify
    content: 使用 make build-all 编译两个 WASM 模块，验证输出文件生成且无链接错误
    status: pending
    dependencies:
      - create-base-mesh-binding
      - create-solver-binding
---

## 产品概述

为 conformal-parameterization C++ 项目重建 WebAssembly 构建体系，按源码文件夹划分独立 WASM 模块。首先生成 BaseMesh（网格数据结构与 I/O）和 Solver（数值优化求解器）两个基础模块，输出到 `assets/wasm/` 目录供前端调用。

## 核心功能

- **BaseMesh WASM 模块**（`base_mesh.js` + `base_mesh.wasm`）：暴露半边缘网格数据结构，支持 OBJ 文件读写、顶点/边/面遍历、高斯曲率计算、拟共形误差评估
- **Solver WASM 模块**（`solver.js` + `solver.wasm`）：暴露梯度下降、Newton、Trust Region、L-BFGS 四种优化算法，以及增广拉格朗日约束优化和混合整数最小二乘求解器
- 每个模块独立编译、独立加载，通过 Embind 向 JavaScript 暴露类型和 API
- 自动处理 WASM 环境下的 MOSEK 存根和条件编译

## 技术栈

- **编译器**：Emscripten `em++`（C++ → WebAssembly）
- **C++ 标准**：`-std=c++17`
- **JS 绑定**：Embind（`--bind`）
- **外部依赖**：Eigen 3.4（header-only，通过 `-I` 引入）
- **构建工具**：GNU Make

## 实现方案

### 整体策略

在 `conformal-parameterization/` 下新建 `wasm/` 目录，放置各模块的 Embind 绑定文件和一个统一的 Makefile。Makefile 通过多目标（`build-base-mesh`、`build-solver`、`build-all`）分别编译各模块，输出到 `assets/wasm/`。

### 关键设计决策

1. **解决 Mesh.cpp → Lscm.h 硬依赖**：在 `Mesh.cpp` 中为 `#include "Lscm.h"` 和 `parameterize()` 方法添加 `#ifndef __EMSCRIPTEN__` 条件编译。BaseMesh WASM 模块不需要参数化功能，该功能属于未来的 Parameterization WASM 模块。

2. **Include 路径策略**：所有源文件使用扁平 `#include "xxx.h"` 路径，因此 Makefile 通过 `-I BaseMesh -I Solvers -I Solvers/Mosek` 分别添加各模块到 include 搜索路径。BaseMesh 模块只加 `-I BaseMesh`，Solver 模块需同时加 `-I BaseMesh`（因依赖 Types.h）和 `-I Solvers -I Solvers/Mosek`。

3. **模块独立性**：每个 WASM 模块有独立的 MODULARIZE 导出名（`BaseMeshModule`、`SolverModule`），互不依赖，可独立加载。

4. **MOSEK 处理**：Solver.cpp 已有 `#if defined(USE_MOSEK) && !defined(__EMSCRIPTEN__)` 的条件编译逻辑，WASM 环境自动使用 MosekStub.h（所有方法返回 false）。trustRegion() 方法会优雅降级输出 "Unable to solve QP"。

### 目录结构

```
conformal-parameterization/
├── wasm/                              # [NEW] WASM 构建目录
│   ├── Makefile                       # [NEW] 多目标构建脚本，支持 build-base-mesh / build-solver / build-all / clean
│   ├── bindings_base_mesh.cpp         # [NEW] BaseMesh Embind 绑定，暴露 Mesh、GaussianCurvature、QuasiConformalError
│   └── bindings_solver.cpp            # [NEW] Solver Embind 绑定，暴露 Solver、AugmentedLagrangian、MixedIntegerProgram
├── BaseMesh/
│   └── Mesh.cpp                       # [MODIFY] 为 #include "Lscm.h" 和 parameterize() 添加 __EMSCRIPTEN__ 条件排除
└── Solvers/                           # 无需修改（已有 WASM 条件编译）
```

输出文件：

```
assets/wasm/
├── base_mesh.js                       # [NEW] BaseMesh WASM 模块 JS 胶水代码
├── base_mesh.wasm                     # [NEW] BaseMesh WASM 二进制
├── solver.js                          # [NEW] Solver WASM 模块 JS 胶水代码
└── solver.wasm                        # [NEW] Solver WASM 二进制
```

### 关键代码结构

**bindings_base_mesh.cpp** — BaseMesh Embind 绑定核心接口：

```
// 暴露 Mesh 类：OBJ 读写、顶点/边/面访问
EMSCRIPTEN_BINDINGS(BaseMeshModule) {
    emscripten::class_<Mesh>("Mesh")
        .constructor<>()
        .function("read", &Mesh::read)
        .function("write", &Mesh::write)
        ;
    // 高斯曲率（自由函数）
    emscripten::function("gaussianCurvatureAngleDeficit", ...);
}
```

**bindings_solver.cpp** — Solver Embind 绑定核心接口：

```
EMSCRIPTEN_BINDINGS(SolverModule) {
    emscripten::class_<Solver>("Solver")
        .constructor<>()
        .function("gradientDescent", &Solver::gradientDescent)
        .function("newton", &Solver::newton)
        .function("trustRegion", &Solver::trustRegion)
        .function("lbfgs", &Solver::lbfgs)
        ;
}
```

### 实现备注

- **性能**：WASM 编译使用 `-O3` 优化，`ALLOW_MEMORY_GROWTH=1` 允许动态内存增长以适应大网格
- **向后兼容**：Mesh.cpp 的条件编译仅在 `__EMSCRIPTEN__` 宏定义时生效，不影响原生 C++ 编译
- **日志**：Solver 中的 `std::cout` 输出（如迭代次数）在 WASM 中会默认输出到浏览器控制台
- **风控**：不修改 Solver/ 下任何文件，不改动现有 `.h/.cpp` 的 API 签名，仅对 Mesh.cpp 做最小条件排除