# MongeAmpere++

半离散最优传输（CGAL）+ 浏览器用 Power 图（Geogram）。

## 两套实现

| 模块 | 依赖 | 用途 |
|------|------|------|
| `optimal_transport.hpp`, `kantorovich.hpp`, `lloyd.hpp`, … | **CGAL**, Boost, Eigen, CImg | 完整 OT：Newton、Kantorovich 泛函、Lloyd |
| `ma_power_diagram.hpp` / `src/ma_power_diagram.cpp` | **Geogram** | 2D Power diagram → `semi-discrete-ot.html` WASM |

二者互不替换：OT 仍走 CGAL 的 regular triangulation 与网格求交；WASM 走 Geogram。

## 依赖（CGAL 原生构建）

- CGAL, Boost (timer, chrono), Eigen3, CImg
- SuiteSparse（可选，QR 求解）
- X11（Linux/macOS 上 CImg 显示；Windows 上 CMake 已跳过强制 X11）

## 构建 CGAL 测试

```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build .
```

## 构建 WASM Power 图

```powershell
cd cpp\build
.\build_wasm_power_diagram.ps1
```

见 [README_WASM.md](README_WASM.md)。

## 目录

- `include/MA/` — 头文件库（CGAL OT + Geogram Power）
- `include/CGAL/` — CGAL 增量构建补丁
- `tests/` — CGAL 单元测试；`test_power_diagram.cpp` 为 Geogram 可选测试
- `src/ma_power_diagram.cpp` — Geogram 实现

上游：[mrgt/MongeAmpere](https://github.com/mrgt/MongeAmpere)
