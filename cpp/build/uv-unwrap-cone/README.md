# uv_unwrap_cone 构建说明

## Web 演示（推荐）

页面：`uv_unwrap_cone_global.html`  
算法：Circle Pattern（WASM，无需 Mosek）、CETM、Ricci 流、Incremental Flattening

```powershell
cd cpp\build\uv-unwrap-cone
.\build_wasm_uv_unwrap_cone.ps1
```

输出：`assets/wasm/unwrap_cone_solver.js` + `unwrap_cone_solver.wasm`

本地预览（项目根目录）：

```powershell
python -m http.server 8080
```

浏览器打开：`http://localhost:8080/uv_unwrap_cone_global.html`

## 本地 Mosek 版 Circle Patterns

使用完整 `CirclePatterns.cpp`（Mosek 11 二次规划优化边权 + Newton 半径）：

```powershell
cd cpp\build\uv-unwrap-cone
.\build_native_circle_patterns.ps1 assets\Models2\torus_F7680.obj
```

需要：Visual Studio C++、Mosek 11（默认 `C:\Program Files\Mosek\11.0\tools\platform\win64x86`）。

输出：`bin\test_circle_patterns.exe`、`bin\cp_output.obj`（带 UV 的 OBJ）。

自定义 Mosek 路径：

```powershell
.\build_native_circle_patterns.ps1 -MosekRoot "D:\Mosek\11.0\tools\platform\win64x86" -ModelPath "model.obj"
```

说明：`MosekSolver` 已适配 MOSEK 11 API（移除 `MSK_initenv`、更新流回调签名等）。浏览器端仍用 `CirclePatternsWasm`（不链接 Mosek）。
