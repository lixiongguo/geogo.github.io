# Euclid（精简版）

本仓库内直接管理，**非 git submodule**。

当前仅保留与以下参数化算法相关的代码：

| 算法 | 头文件 | 实现 |
|------|--------|------|
| 全纯 1-形式 / 共形参数化 | `Parameterization/HolomorphicOneForms.h` | `Parameterization/src/HolomorphicOneForms.cpp` |
| 离散 Ricci 流 | `Parameterization/RicciFlow.h` | `Parameterization/src/RicciFlow.cpp` |

**依赖模块：** `Geometry/`（DEC、TriMeshGeometry）、`Topology/`（Chain、Homology/Homotopy、MeshTopology）、`Math/`（Numeric、Vector）、`MeshUtil/MeshDefs.h`、`Util/Assert.h`、`3rdparty/AlmostEquals.h`。

上游参考：[unclejimbo/Euclid](https://github.com/unclejimbo/Euclid)。
