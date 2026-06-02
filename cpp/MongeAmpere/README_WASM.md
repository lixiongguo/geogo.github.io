# Power Diagram WASM（`semi-discrete-ot.html`）

WASM 构建 **不链接 CGAL**，仅编译 `ma_power_diagram` + Geogram。CGAL 最优传输源码仍在同目录，见 [README.md](README.md)。

## 依赖

- [Emscripten](https://emscripten.org/)：本仓库 `cpp/emsdk`
- [Geogram](https://github.com/BrunoLevy/geogram) 源码（仅 clone 不够，需由脚本编译）
- **Ninja**：若 PATH 中没有，脚本会自动下载到 `cpp/build/tools/ninja.exe`

默认 Geogram 路径：

`C:\Users\lixio\OneDrive\Desktop\MyDoc\geogram`

可在构建时覆盖：`-GeogramSource "D:\path\to\geogram"`

## 构建（PowerShell）

```powershell
cd cpp\build
.\build_wasm_power_diagram.ps1
```

仅重链 WASM（已编好 Geogram）：

```powershell
.\build_wasm_power_diagram.ps1 -SkipGeogram
```

强制重编 Geogram：

```powershell
.\build_wasm_power_diagram.ps1 -RebuildGeogram
```

产物：`assets/wasm/wasm_power_diagram.js` + `.wasm`

## 源码

| 文件 | 说明 |
|------|------|
| `include/MA/ma_power_diagram.hpp` | Power 图 API |
| `src/ma_power_diagram.cpp` | Geogram 加权 Delaunay + 单元多边形 |
| `../build/power-diagram/wasm_power_diagram.cpp` | Emscripten 导出 `compute_power_diagram_js` |

## 前端

`semi-discrete-ot.html` 加载 `assets/wasm/wasm_power_diagram.js`，调用 `compute_power_diagram_js` / `free_buffer`。
