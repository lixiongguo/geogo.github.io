## uv-unwrap.html — 精简 WASM

`uv-unwrap.html` 仅依赖：

- `assets/wasm/uv_unwrap_simple.js` / `assets/wasm/uv_unwrap_simple.wasm`

包含算法：**LSCM**、**Tutte**（圆/方边界）、**SCP**，以及 **QC 扭曲** 可视化所需的 `compute_qc_error`。

WASM 入口目录：`cpp/build/uv-unwrap-simple/`

算法源码目录：`cpp/conformal-parameterization/uv_unwrap_simple/`

### 重新生成 WASM

```powershell
cd .\cpp\build
.\uv-unwrap-simple\build_wasm_uv_unwrap_simple.ps1
```

或：

```powershell
.\build_wasm_all.ps1 -Targets uv_unwrap_simple
```
