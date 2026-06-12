---
name: build-direction-field-design
overview: 在 cpp/ddg-exercises/projects/direction-field-design 目录下构建该 CMake 项目
todos:
  - id: ensure-second-level-submodules
    content: 确保 geometry-central/polyscope 的二级子模块已初始化
    status: completed
  - id: cmake-configure
    content: 在 build 目录执行 cmake 配置
    status: completed
    dependencies:
      - ensure-second-level-submodules
  - id: cmake-build
    content: 并行编译项目，验证 main 和 test-connect 目标生成
    status: completed
    dependencies:
      - cmake-configure
---

## 产品概述

构建 `cpp/ddg-exercises/projects/direction-field-design` 项目，生成方向场设计可视化工具。

## 核心功能

- 使用 CMake 构建系统编译项目
- 生成 `main` 可执行文件（方向场设计可视化）
- 生成 `test-connect` 测试文件
- 确保 macOS Apple Silicon 环境下编译通过

## 技术栈

- 构建系统：CMake 3.10+
- 编译器：Apple Clang (macOS)
- 语言标准：C++11
- 依赖库：geometry-central（几何处理）、polyscope（可视化）、Eigen（线性代数）、googletest（单元测试）

## 实施方案

### 构建策略

项目结构已完整，依赖子模块（geometry-central、polyscope、googletest）均已初始化。采用标准 CMake 工作流：配置 → 构建。macOS Apple Silicon 需注意 OpenGL framework 链接。

### 关键技术决策

- **OpenGL 链接**：polyscope 在 macOS 上通过 `find_package(OpenGL)` 查找，通常能正确处理 framework 路径，若失败则需在 CMakeLists.txt 中显式设置 `-framework OpenGL`
- **编译优化**：CMakeLists.txt 已预设 `-mcpu=apple-m1`，无需额外配置
- **构建并行度**：使用 `-j$(sysctl -n hw.logicalcpu)` 充分利用 CPU 核心

### 实施注意事项

- 构建目录为 `projects/direction-field-design/build`
- 与 `cauchy_viz` 类似，需关注 polyscope 的 cmake 模块是否需要在 macOS 上做 OpenGL 适配
- 若 deps 子模块内部有 `.gitmodules`，需确保其二级子模块也已拉取