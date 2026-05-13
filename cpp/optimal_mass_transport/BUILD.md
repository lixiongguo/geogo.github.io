# Optimal Mass Transport — 编译与运行记录

基于 Ruby Shamir 的 MATLAB 最优传输图像变形算法（Monge-Kantorovich + 梯度下降），C++17 移植版。

## 环境

| 组件 | 版本 | 来源 |
|------|------|------|
| macOS | 24 (Sequoia) | — |
| Apple Clang | 17.0.0 | Xcode CLT |
| CMake | 3.31 | brew |
| Eigen | 3.4.0 | 项目自带 `cpp/deps/eigen-3.4.0/` |
| stb_image | latest | GitHub master 下载 |

## 依赖安装

```bash
# stb_image 单头文件库（不需要 brew，直接 curl 下载）
mkdir -p cpp/deps/stb
curl -sL https://raw.githubusercontent.com/nothings/stb/master/stb_image.h \
     -o cpp/deps/stb/stb_image.h
curl -sL https://raw.githubusercontent.com/nothings/stb/master/stb_image_write.h \
     -o cpp/deps/stb/stb_image_write.h
```

## 目录结构

```
cpp/optimal_mass_transport/
├── CMakeLists.txt              # CMake 构建配置
├── optimal_mass_transport.h    # Header-only 核心算法库 (~770 行)
├── run_tests.cpp               # main 入口 — 7 个测试用例
├── transition_test.cpp         # 自定义过渡序列测试
├── build/                      # CMake 构建目录
└── output/                     # 输出图片目录
```

## 编译

```bash
cd cpp/optimal_mass_transport
mkdir -p build && cd build
cmake ..
make -j4
```

编译完成后生成两个可执行文件：
- `build/run_tests` — 7 个标准测试
- `build/transition_test` — 自定义图片过渡序列

### 编译遇到的问题及解决

#### 问题 1: Eigen `block().sum()` 断言崩溃（exit 134）

**现象:**
```
Assertion failed: ((i>=0) && ((BlockRows==1) && ...)), function Block, file Block.h, line 118.
```

**原因:** Eigen 3.4.0 的 debug 断言在调用 `matrix.row(i).sum()` 或 `matrix.block(...).sum()` 时，内部迭代器访问 Block 对象会触发越界检查断言（即使实际未越界）。AppleClang 17 的优化行为与 Eigen 的内联预期不兼容。

**解决:** 在 `optimal_mass_transport.h` 中，**在 `#include <Eigen/...>` 之前**添加：
```cpp
#ifndef EIGEN_NO_DEBUG
#define EIGEN_NO_DEBUG
#endif

#include <Eigen/Dense>
```

#### 问题 2: `.row(idx).sum()` 与 `.col(idx).sum()` 断言（exit 134，第二次）

**现象:** 定义 `EIGEN_NO_DEBUG` 后，`compute_initial_mapping()` 中的 `.row(idx0).sum()` / `.col(idx0).sum()` 仍然触发 `DenseCoeffsBase.h` 的 `operator()` 断言：
```
Assertion failed: (row >= 0 && row < rows() && col >= 0 && col < cols()),
  function operator(), file DenseCoeffsBase.h, line 112.
```

**原因:** `Eigen::MatrixXd::row(idx)` 返回 1×N 的 RowBlock，调用 `.sum()` 时内部迭代到每个元素都会经过 `operator()` 断言。关闭 `EIGEN_NO_DEBUG` 对于 Block 类型的 redux 操作不完全生效。

**解决:** 将 `compute_initial_mapping()` 中所有 `.row(idx).sum()` 和 `.col(idx).sum()` 替换为手动循环累加：
```cpp
// 替换前:
cum0 += myu_0.row(idx0).sum();
cum1 += myu_1.row(idx1).sum();

// 替换后: 添加辅助函数
inline double row_sum(const ImageMat& m, int r) {
    double s = 0.0;
    for (int c = 0; c < m.cols(); ++c) s += m(r, c);
    return s;
}
inline double col_sum(const ImageMat& m, int c) {
    double s = 0.0;
    for (int r = 0; r < m.rows(); ++r) s += m(r, c);
    return s;
}
cum0 += row_sum(myu_0, idx0);
cum1 += row_sum(myu_1, idx1);
```

#### 问题 3: `std::filesystem::create_directories` 链接失败

**现象:**
```
Undefined symbols for architecture arm64:
  "std::__1::__fs::filesystem::create_directories(...)"
```

**原因:** 虽然 C++17 启用了 `<filesystem>`，但 Apple Clang 17 的 libc++ 中某些 filesystem 函数需要显式链接或使用 `-std=c++17` 下的不同符号。

**解决:** 移除 `<filesystem>` 依赖，改用 POSIX 调用：
```cpp
// 替换前:
#include <filesystem>
fs::create_directories("output/");

// 替换后:
#include <sys/stat.h>
mkdir("output/", 0755);
```

#### 问题 4: CMake 不追踪 header 变化导致"修改无效"

**现象:** 修改 `optimal_mass_transport.h` 后 `make` 显示 `Built target run_tests` 但实际未重新编译，运行仍报旧错误。

**原因:** CMake 默认不自动追踪 header-only 依赖。当只有 `.h` 文件变化时，`make` 检测不到需要重新编译。

**解决:** 使用 clean-first 强制重建：
```bash
cmake --build . --clean-first
# 或
rm -rf build && mkdir build && cd build && cmake .. && make -j4
```

#### 问题 5: 图片相对路径错误

**现象:**
```
Error: Cannot open image: ../midas-journal-319-master/.../test_u0_ax_1.bmp
```

**原因:** 图片路径是相对于当前工作目录（CWD）的，不是相对于可执行文件的。从 `build/` 目录运行时路径解析为 `cpp/optimal_mass_transport/build/../midas-journal-319-master/...`（不存在）。

**解决:** 必须从 `cpp/optimal_mass_transport/` 目录运行：
```bash
cd cpp/optimal_mass_transport
./build/run_tests 1    # ✅ 正确
# 不能: cd build && ./run_tests 1  ❌ 错误
```

#### 问题 6: `compute_image_deformation_map` 潜在越界

**现象:** 梯度下降正常完成，但在 `transform()` 调用时偶发崩溃。

**原因:** 线性插值过程中 `ulx_nx = ul_x + square_edge_len` 可能超出图像边界。当密度图不能整数分割图像尺寸时会触发。

**解决:** 添加边界截断：
```cpp
int ulx_nx = std::min(ul_x + square_edge_len, img_h - 1);
int uly_ny = std::min(ul_y + square_edge_len, img_w - 1);
```

#### 调试方法

当出现 `exit 134 (SIGABRT)` 或 `exit 139 (SIGSEGV)` 时：

```bash
# 1. 缩小范围 —— 逐步添加 printf 定位崩溃行
# 2. 使用 lldb（macOS 原生调试器）
lldb ./build/run_tests
(lldb) run 1
(lldb) bt          # 崩溃时打印调用栈

# 3. 编译加 -O0 -g 保留调试符号
g++ -std=c++17 -I../deps/eigen-3.4.0 -I../deps/stb -O0 -g test.cpp -o test
```

## 运行

### 标准测试

```bash
cd cpp/optimal_mass_transport

# 测试 1-3: 初始映射验证
./build/run_tests 1    # x 轴 Monge-Kantorovich，test_u0_ax 图片，sel=12
./build/run_tests 2    # y 轴 Monge-Kantorovich，test_u0_bxy 图片，sel=16
./build/run_tests 3    # 同 2，加直方图均衡化

# 测试 4-6: 完整最优传输 + 变形序列
./build/run_tests 4    # flame 火焰图，sel=2，6 帧
./build/run_tests 5    # cloud 云图，sel=4，6 帧
./build/run_tests 6    # water 水图，sel=2，6 帧

# 测试 7: 无强度混合 + 均衡化方法对比
./build/run_tests 7    # cloud 图，两种均衡化方法
```

### 测试结果

```
Test 1  → output/test1_deformed.bmp      (初始映射, 360×360)
Test 2  → output/test2_deformed.bmp      (初始映射, 360×360)
Test 3  → output/test3_deformed.bmp      (初始映射+histeq)
Test 4  → output/test4_frame_1~6.bmp     (flame 序列, 170×170)
Test 5  → output/test5_frame_1~6.bmp     (cloud 序列, 316×478)
Test 6  → output/test6_frame_1~6.jpg     (water 序列, 250×250)
Test 7  → output/test7_deformed_eq0.bmp  (cloud, 总质量比均衡)
          output/test7_deformed_eq1.bmp  (cloud, 直方图均衡)
```

### 自定义过渡序列

```bash
cd cpp/optimal_mass_transport

# 如果图片尺寸不同，先缩放
sips -z 256 256 boat.png --out /tmp/boat_256.png

# 修改 transition_test.cpp 中的路径后编译运行
./build/transition_test
```

示例输出：

```
=== Cameraman → Boat Transition via Optimal Transport ===

Image 0 (cameraman): 256×256
Image 1 (boat):      256×256

Computing optimal mass transport...
Image sizes: 256×256  256×256
Density maps: 64×64
Initial mapping computed.
  iter 1  |ut| = 0.139989  thresh = 0.080000
  iter 2  |ut| = 0.010944  thresh = 0.080000
  stopped: ut converged (small deformations)

Generating 8-frame transition series...
  Frame 1/8 → output/cam2boat_01.bmp
  ...
  Frame 8/8 → output/cam2boat_08.bmp
Done!
```

## 算法架构

```
compute_optimal_mass_transport()
├── imread_to_gray()              # stb_image 读取灰度图
├── [均衡化] histeq() / 总质量比
├── compute_density_map()         # 图像分块平均 → 密度图
├── compute_initial_mapping()     # 1D Monge-Kantorovich (x/y 轴)
└── gradient_descent()
    ├── compute_ut()
    │   ├── computeP()            # 带比较项的 P 场
    │   ├── rotate_data()         # 90° 旋转
    │   ├── compute_divergence()  # 散度（中心差分）
    │   ├── solve_poisson_5pt()   # 5 点差分 + SparseLU
    │   ├── compute_gradient()    # 梯度
    │   ├── compute_jacobian()    # 雅可比（对角近似）
    │   └── mult_components()     # 组合 ut + 自适应步长 α
    └── 收敛判定: |ut| < 0.08 或 max_iter=8

create_image_series()
├── compute_image_deformation_map()  # 线性插值上采样
└── transform_intensity()            # 强度混合变形
```

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `square_edge_length` | 2~16 | 密度图方块边长（像素），值越小密度图越大 |
| `maximum_iterations` | 8 | 梯度下降最大迭代次数 |
| `convergence_threshold` | 0.08 | 平均变形大小收敛阈值 |
| `pure_omt_ratio` | 0.3 | 纯最优传输项权重（在 computeP 中） |
| `alpha` | 自适应 | 梯度下降步长，由 mult_components 计算 |
| `equalization_method` | 0=总质量比, 1=histeq | 密度均衡化方式 |

## CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.16)
project(OptimalMassTransport LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native")

set(EIGEN3_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/../deps/eigen-3.4.0")
add_library(Eigen3::Eigen INTERFACE IMPORTED)
set_target_properties(Eigen3::Eigen PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${EIGEN3_INCLUDE_DIR}")

set(STB_DIR "${CMAKE_SOURCE_DIR}/../deps/stb")

add_executable(run_tests run_tests.cpp)
target_include_directories(run_tests PRIVATE
    ${EIGEN3_INCLUDE_DIR} ${STB_DIR} ${CMAKE_SOURCE_DIR})
target_link_libraries(run_tests Eigen3::Eigen)
```
