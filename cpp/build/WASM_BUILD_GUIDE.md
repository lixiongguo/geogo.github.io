# WASM 编译与测试指南

当前已打包多个 WASM 目标，包括 **uv_unwrap_simple**、**dgp_basic**、**uv_unwrap_field**、**abel_jacobi** 和 **omt**，对应多个页面。

## 目录结构

```
cpp/
├── build/                                      # WASM 打包入口
│   ├── build_wasm_all.ps1                      # Windows 统一构建脚本（支持 5 个目标）
│   ├── build_wasm_vector_field.ps1             # 向量场求解器单独构建脚本
│   ├── build_wasm_power_diagram.ps1            # Power Diagram 单独构建脚本
│   ├── Makefile                                # Linux/Mac Makefile
│   ├── WASM_BUILD_GUIDE.md                     # 本文档
│   ├── uv-unwrap-simple/
│   │   └── wasm_uv_unwrap_simple.cpp           # WASM C 接口 (uv_unwrap_simple)
│   ├── dgp-basic/
│   │   └── wasm_dgp_basic.cpp                  # WASM C 接口 (dgp_basic)
│   ├── uv-unwrap-field/
│   │   └── wasm_uv_unwrap_field.cpp            # WASM C 接口 (uv_unwrap_field)
│   ├── abel-jacobi/
│   │   └── wasm_uv_unwrap_abel_jacobi.cpp      # WASM C 接口 (abel_jacobi)
│   └── omt/
│       └── wasm_omt.cpp                        # WASM C 接口 (omt)
├── conformal-parameterization/                 # 参数化算法源码（新目录结构）
│   ├── BaseMesh/                               # 网格基础数据结构
│   │   ├── Mesh.cpp / Mesh.h
│   │   ├── Vertex.cpp / Vertex.h
│   │   ├── Edge.cpp / Edge.h
│   │   ├── Face.cpp / Face.h
│   │   ├── HalfEdge.cpp / HalfEdge.h
│   │   ├── MeshIO.cpp / MeshIO.h
│   │   ├── QcError.cpp / QcError.h
│   │   ├── GaussianCurvature.cpp / GaussianCurvature.h
│   │   └── Types.h
│   ├── CutSeamMesh/                            # 基于 BaseMesh 的 seam cut 网格扩展
│   │   └── CutSeamMesh.cpp / CutSeamMesh.h
│   ├── Parameterization/                       # 参数化算法
│   │   ├── Parameterization.cpp / .h           # 基类
│   │   ├── LSCM/                               # LSCM, SCP
│   │   ├── ABF/                                # ABF++, LinABF, AugmentedLagrangian
│   │   ├── ARAP/                               # ARAP, Tutte
│   │   ├── BFF/                                # Boundary First Flattening
│   │   ├── Bounded/                            # Bounded LSCM
│   │   ├── Conformal/                          # CETM, CirclePatterns
│   │   ├── HoloOneForm/                        # Holomorphic One-Form
│   │   ├── IncrementalFlattenning/             # Incremental Flattening
│   │   ├── QuadCover/                          # QuadCover
│   │   ├── RicciFlow/                          # Ricci Flow
│   │   ├── uv_unwrap_field/                    # MIQQuad, PGP
│   │   └── Abel_Jacoi/                         # Abel-Jacobi 全局参数化
│   ├── Solvers/                                # 求解器
│   │   ├── Solver.cpp / Solver.h
│   │   ├── CrossFieldIntegerProgram.cpp / .h
│   │   ├── QPSolver.h
│   │   └── Mosek/
│   ├── Topology/                               # 拓扑工具
│   │   └── TreeCotreeBasis.h
│   └── VectorFileds/                           # 向量场
│       ├── PrincipalCurvatureField.cpp / .h
│       ├── ComplexPolyField.cpp / .h
│       ├── trivial_connection.cpp
│       ├── nrosy_trivial_connection.cpp
│       └── vector_field_unified_wasm.cpp
├── deps/
│   ├── eigen-3.4.0/
│   └── glm/
└── emsdk/
```

## WASM 模块

| Target | 别名 | 输出文件（js/wasm） | 入口源文件 | 算法依赖 |
|--------|------|---------------------|-----------|---------|
| `uv_unwrap_simple` | `simple` | `uv_unwrap_simple.js/wasm` | `cpp/build/uv-unwrap-simple/wasm_uv_unwrap_simple.cpp` | LSCM, Tutte, SCP, LinABF, ABF++, ARAP, CirclePatterns, CETM, RicciFlow, QcError |
| `dgp_basic` | `dgp` | `dgp_basic.js/wasm` | `cpp/build/dgp-basic/wasm_dgp_basic.cpp` | GaussianCurvature, PrincipalCurvatureField |
| `uv_unwrap_field` | `field` | `uv_unwrap_field.js/wasm` | `cpp/build/uv-unwrap-field/wasm_uv_unwrap_field.cpp` | QuadCover, MIQQuad, HolomorphicOneForm, LSCM, QcError |
| `abel_jacobi` | `global_cross_fields` | `uv_unwrap_abel_jacobi.js/wasm` | `cpp/build/abel-jacobi/wasm_uv_unwrap_abel_jacobi.cpp` | AbelJacobi, AbelJacobiParameterization, LSCM, QcError |
| `omt` | — | `omt_solver.js/wasm` | `cpp/build/omt/wasm_omt.cpp` | OMT Image Interpolation |

### 公共依赖

- `MESH_SRCS`：`BaseMesh/Mesh.cpp MeshIO.cpp Vertex.cpp Edge.cpp Face.cpp HalfEdge.cpp` 和 `CutSeamMesh/CutSeamMesh.cpp`
- `SOLVER_SRCS`：`Solvers/Solver.cpp`
- `PARAMETERIZATION_SRCS`：`Parameterization/Parameterization.cpp`
- 所有目标均引用 `<Eigen/Core>`（路径：`../deps/eigen-3.4.0`）

## 编译命令

### Windows（PowerShell）

```powershell
# 进入构建目录
cd cpp\build

# 编译所有目标
.\build_wasm_all.ps1 -Targets all

# 只编译 uv_unwrap_simple
.\build_wasm_all.ps1 -Targets uv_unwrap_simple

# 编译多个目标
.\build_wasm_all.ps1 -Targets uv_unwrap_simple,dgp_basic,uv_unwrap_field

# 编译向量场求解器
.\build_wasm_vector_field.ps1
```

### Linux/Mac (Makefile)

```bash
cd cpp/build
make uv_unwrap_simple
make clean
```

### 编译参数说明

| 参数 | 值 | 说明 |
|------|-----|------|
| 编译器 | `em++` | Emscripten C++ 编译器 |
| C++ 标准 | `-std=c++17` | C++17 |
| 优化 | `-O2 -flto` | O2 优化 + 链接时优化 |
| Eigen | `-I../deps/eigen-3.4.0` | 线性代数库 |
| GLM | `-I../deps/glm` | 向量/矩阵库 |
| MODULARIZE | `1` | 模块化输出，通过工厂函数加载 |
| WASM | `1` | 输出 .wasm 二进制 |
| ALLOW_MEMORY_GROWTH | `1` | 允许动态增长内存 |
| ENVIRONMENT | `web` | 目标环境为浏览器 |
| FORCE_FILESYSTEM | `0` | 不强制文件系统支持 |

## Emscripten 导出函数（`_` 前缀规则）

每个 WASM 目标通过 `EXPORTED_FUNCTIONS` 指定对外暴露的 C 函数列表。

**关键规则**：`extern "C"` 声明的函数在 `EXPORTED_FUNCTIONS` 中必须加 `_` 前缀，但 JavaScript 端通过 `ccall()` 调用时**不加** `_` 前缀。

### 导出函数

**C++ 端（wasm_uv_unwrap_simple.cpp）**：
```cpp
extern "C" {
    EMSCRIPTEN_KEEPALIVE int solve_lscm(double* posPtr, int posLen, ...);
    EMSCRIPTEN_KEEPALIVE int solve_tutte_circle(double* posPtr, int posLen, ...);
    EMSCRIPTEN_KEEPALIVE int solve_tutte_square(double* posPtr, int posLen, ...);
    EMSCRIPTEN_KEEPALIVE int solve_scp(double* posPtr, int posLen, ...);
    EMSCRIPTEN_KEEPALIVE double* get_uv_result();
    EMSCRIPTEN_KEEPALIVE int get_uv_result_size();
    EMSCRIPTEN_KEEPALIVE double get_last_time_ms();
    EMSCRIPTEN_KEEPALIVE void dispose();
}
```

**EXPORTED_FUNCTIONS（efile / JSON）**：
```json
["_malloc","_free","_solve_lscm","_solve_tutte_circle","_solve_tutte_square","_solve_scp","_get_uv_result","_get_uv_result_size","_get_last_time_ms","_dispose"]
```

**JavaScript 调用**：
```javascript
const solver = await UvUnwrapSimpleSolver();  // MODULARIZE=1 工厂函数
solver.ccall('solve_lscm', 'number',
  ['number','number','number','number','number','number'],
  [posPtr, posLen, facePtr, faceLen, anchor0, anchor1]);
```

## 本地测试（Python HTTP Server）

### 启动服务器

```powershell
# 从项目根目录启动（确保 assets/ 路径可访问）
python -m http.server 8080 --directory "c:\path\to\lixiongguo.github.io"
```

### 访问测试页面

浏览器打开：
```
http://localhost:8080/uv-unwrap.html
```

### 测试页面功能

`uv-unwrap.html` 只加载 `assets/wasm/uv_unwrap_simple.js`，页面启动时调用 `UvUnwrapSimpleSolver()`。

## WASM 调用流程

```mermaid
sequenceDiagram
    participant JS as JavaScript
    participant W as WASM Module
    participant C as C++ (wasm_*.cpp)
    participant A as Algorithm

    JS->>W: UvUnwrapSimpleSolver() 工厂函数
    W-->>JS: Module 实例

    JS->>JS: 构建 Float64Array(pos) + Int32Array(faces)
    JS->>W: _malloc(posBytes)
    W-->>JS: posPtr
    JS->>W: HEAPF64.set(flatPositions, posPtr/8)
    JS->>W: _malloc(faceBytes)
    W-->>JS: facePtr
    JS->>W: HEAP32.set(flatFaces, facePtr/4)

    JS->>W: ccall('solve_lscm', [posPtr,posLen,facePtr,faceLen,a0,a1])
    W->>C: solve_lscm()
    C->>A: Mesh::read() → parameterize(LSCM)
    A-->>C: UV 坐标存入 Mesh
    C-->>W: return 0

    JS->>W: ccall('get_uv_result')
    W-->>JS: uvPtr (HEAPF64 指针)
    JS->>W: ccall('get_uv_result_size')
    W-->>JS: uvSize
    JS->>JS: new Float64Array(HEAPF64.buffer, uvPtr, uvSize)

    JS->>W: _free(posPtr); _free(facePtr);
    JS->>W: ccall('dispose')
```

## 常见问题

### 1. `emcc: error: undefined exported symbol`

**原因**：`EXPORTED_FUNCTIONS` 中的函数名缺少 `_` 前缀。

**解决**：所有 `extern "C"` 函数在 `EXPORTED_FUNCTIONS` 中均需加 `_` 前缀，如 `_solve_lscm` 而非 `solve_lscm`。

### 2. `wasm-ld: error: ... undefined symbol`

**原因**：缺少源文件或 include 路径不正确。

**解决**：检查 `deps/` 目录结构是否完整，include 路径是否正确。

### 3. WASM 文件 MIME 类型错误

**现象**：浏览器报 `WebAssembly.instantiateStreaming` failed。

**解决**：Python 3.7+ 已内置 `application/wasm` MIME 类型。如使用其他服务器，确保配置了正确的 Content-Type。

## 版本记录

| 日期 | 变更 |
|------|------|
| 2026-06-12 | 更新所有构建脚本以适配新的 `conformal-parameterization` 目录结构（BaseMesh/Parameterization/Solvers/VectorFileds/Topology）；修复所有源码中的旧路径 include；更新文档 |
| 2026-05-26 | 按新文件结构改为只打包 `uv_unwrap_simple`（Tutte / LSCM / SCP） |
| 2026-05-11 | 整理依赖到 `cpp/deps/`，统一 Mac Makefile 和 Windows PowerShell 构建脚本 |
| 2026-05-11 | 修复 `EXPORTED_FUNCTIONS` 中函数名缺 `_` 前缀的编译错误 |
| 2026-05-11 | 创建本指南文档 |
