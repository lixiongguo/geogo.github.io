# 编译
.\emsdk activate latest
em++ lscm_solver.cpp -o ../assets/wasm/lscm_solver.js -O3 -std=c++17 "-ID:/third_party/eigen-3.4.0" --bind -s MODULARIZE=1 -s EXPORT_NAME="LCMSolver" -s ALLOW_MEMORY_GROWTH=1 -s TOTAL_MEMORY=256MB -s WASM=1




# LSCM Solver WASM 编译说明

本文档说明如何将 C++ LSCM 求解器编译为 WebAssembly 模块。

## 前置条件

### 1. 安装 Emscripten SDK

Emscripten 是一个 LLVM 到 WebAssembly 的编译器工具链。

**Windows 安装步骤：**

1. 下载并安装 Emscripten SDK：
   ```powershell
   # 下载 emsdk
   git clone https://github.com/emscripten-core/emsdk.git
   cd emsdk
   
   # 安装最新版本
   emsdk install latest
   
   # 激活
   emsdk activate latest
   
   # 设置环境变量 (当前会话)
   emsdk env
   ```

2. 验证安装：
   ```powershell
   em++ --version
   ```

### 2. 下载 Eigen 库

Eigen 是一个高性能的 C++ 线性代数库。

1. 从官网下载：[https://eigen.tuxfamily.org/index.php?title=Main_Page](https://eigen.tuxfamily.org/index.php?title=Main_Page)
2. 解压到合适的位置，例如：
   - `E:\Dev\libs\eigen-3.4.0\` (Windows)
   - `~/libs/eigen/` (macOS/Linux)

## 编译步骤

### 方法一：使用 Makefile (推荐)

```powershell
# 检查环境配置
make check

# 编译
make
```

**重要：** 首次使用前，请编辑 `Makefile` 中的 `EIGEN_PATH` 变量，指向你的 Eigen 库路径。

### 方法二：手动编译

```powershell
em++ lscm_solver.cpp -o ../assets/wasm/lscm_solver.js ^
    -O3 -std=c++17 ^
    -IE:/Dev/libs/eigen-3.4.0 ^
    --bind ^
    -s MODULARIZE=1 ^
    -s EXPORT_NAME="LCMSolver" ^
    -s ALLOW_MEMORY_GROWTH=1 ^
    -s TOTAL_MEMORY=256MB ^
    -s WASM=1
```

### 编译选项说明

| 选项 | 说明 |
|------|------|
| `-O3` | 最高级别优化 |
| `-std=c++17` | 使用 C++17 标准 |
| `-I<path>` | Eigen 头文件路径 |
| `--bind` | 启用 Embind (JS/C++ 互操作) |
| `-s MODULARIZE=1` | 导出 ES6 模块 |
| `-s EXPORT_NAME="LCMSolver"` | 模块变量名 |
| `-s ALLOW_MEMORY_GROWTH=1` | 允许动态内存增长 |
| `-s TOTAL_MEMORY=256MB` | WASM 内存大小 |
| `-s WASM=1` | 输出 WebAssembly |

## 输出文件

编译成功后，会生成两个文件：

1. `assets/wasm/lscm_solver.js` - JavaScript 胶水代码
2. `assets/wasm/lscm_solver.wasm` - WebAssembly 二进制文件

这两个文件都需要部署到 GitHub Pages。

## 验证部署

部署后，打开 `uv-unwrap.html`，控制台应该显示：

```
WASM LSCM 求解器加载成功 (Eigen 稀疏 Cholesky)
```

如果显示 WASM 加载失败，请检查：

1. 文件是否正确上传到 `assets/wasm/` 目录
2. GitHub Pages 是否正确配置
3. 浏览器控制台是否有跨域错误

## 性能对比

| 指标 | 旧版 (JS 稠密) | 新版 (WASM + Eigen) |
|------|---------------|---------------------|
| 算法 | 高斯消元 O(n³) | 稀疏 Cholesky ~O(n^1.5) |
| 内存 | O(n²) 稠密 | O(n) 稀疏 |
| 大模型 (10万+ 顶点) | 可能卡顿 | 流畅 |
| 数值稳定性 | 一般 | 更优 (Eigen 成熟实现) |

## 常见问题

### Q: 编译报错 "Eigen/Dense not found"

A: 检查 `-I` 参数路径是否正确，确保指向包含 `Eigen` 目录的父文件夹。

### Q: 运行时 WASM 加载失败

A: 可能是 WASM 文件未被 Jekyll 复制到输出目录。检查 `_config.yml` 中的 `keep_files` 配置。

### Q: 内存不足错误

A: 增加 `-s TOTAL_MEMORY=512MB` 或更大值。
