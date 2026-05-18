---
layout: post
title: "pybind11 封装 MongeAmpere++ C++ 库的调试全记录"
date: 2026-05-15
tags: [pybind11, C++, optimal-transport, MongeAmpere, CGAL, Eigen]
---

用 pybind11 将 MongeAmpere++（最优传输/蒙日-安培方程求解器）封装为 Python 模块，本文记录从零搭建到调通链路的全过程与遇到的坑。

---

## 1. 背景与目标

**C++ 库**：MongeAmpere++，基于 CGAL + Eigen，提供半离散最优传输求解（`ot_solve`、`kantorovich`、`lloyd` 等）。

**目标**：用 pybind11 封装核心函数，使 Python 端的 reflector-master（反射镜光学设计项目）可以直接调用。

**核心 API 需求**（reflector 期望的接口）：

| 函数 | 用途 |
|------|------|
| `Density_2(X, values)` | 创建二维分段线性密度 |
| `optimal_transport_2(mu, Y, nu, w0)` | 求解半离散 OT |
| `conforming_lloyd_2(mu, Y, psi, hull)` | Laguerre cell 质心 |
| `delaunay_2(Z, weights)` | 加权 Delaunay 三角化 |
| `optimized_sampling_2(density, N)` | 蓝噪声采样 |

---

## 2. 环境准备

```bash
# 安装 pybind11
pip3 install --break-system-packages pybind11

# 确认 cmake 目录
python3 -c "import pybind11; print(pybind11.get_cmake_dir())"
# → /opt/homebrew/lib/python3.14/site-packages/pybind11/share/cmake/pybind11
```

依赖链：`pybind11` + `Eigen3` + `CGAL` + `Boost(timer, chrono)`。

---

## 3. pybind11 核心机制详解

### 3.1 基础结构：最小绑定示例

pybind11 的核心是 `PYBIND11_MODULE` 宏，它生成一个 Python 模块：

```cpp
#include <pybind11/pybind11.h>
namespace py = pybind11;

int add(int a, int b) { return a + b; }

PYBIND11_MODULE(mymodule, m) {
    m.doc() = "my module docstring";
    m.def("add", &add, "Add two numbers",
          py::arg("a"), py::arg("b"));
}
```

编译为 `mymodule.cpython-3xx.so` 后，Python 端直接 `import mymodule; mymodule.add(1, 2)`。

### 3.2 必需的头文件

在本项目中用到四个 pybind11 头文件，各有不同用途：

```cpp
#include <pybind11/pybind11.h>   // 基础：PYBIND11_MODULE、py::class_、m.def
#include <pybind11/eigen.h>      // ★ numpy ↔ Eigen 自动转换（零拷贝）
#include <pybind11/stl.h>        // std::string、std::vector、std::map 自动转换
#include <pybind11/numpy.h>      // 直接操作 numpy 数组（py::array_t<T>）
```

### 3.3 绑定函数：`m.def()`

最常用模式——绑定自由函数，指定参数名和默认值：

```cpp
m.def("density_from_image", &density_from_image,
      py::arg("filename"),
      "Build a piecewise-linear density from a grayscale image");

m.def("ot_solve", &ot_solve,
      py::arg("density"), py::arg("X"), py::arg("masses"),
      py::arg("x0")      = py::none(),   // ← Python None 作为默认值
      py::arg("eps_g")   = 1e-7,         // ← C++ 默认值
      py::arg("maxiter") = 200,
      py::arg("verbose") = true,
      "Solve semi-discrete optimal transport");
```

pybind11 会自动生成带关键词参数签名的 Python 函数：

```python
psi = _mongeampere.ot_solve(mu._data, Y, nu,
                             x0=None, eps_g=1e-7, maxiter=200, verbose=False)
```

### 3.4 绑定类：`py::class_<T>`

将 C++ struct 暴露为 Python class：

```cpp
py::class_<DensityData, std::shared_ptr<DensityData>>(m, "_DensityData")
    .def(py::init<>())                        // 默认构造函数
    .def("num_vertices", &DensityData::num_vertices)
    .def("get_vertices", &DensityData::get_vertices,
         "Return vertices as (N,2) ndarray")  // 附带 docstring
    .def_readwrite("total_mass", &DensityData::total_mass);
```

**注意事项**：

- `std::shared_ptr<DensityData>` 模板参数启用智能指针管理，Python 端自动引用计数
- `.def_readwrite` 暴露成员变量为可读写属性
- `.def_readonly` 暴露为只读属性
- 不需要绑定所有成员，只暴露 Python 需要的接口

在函数中使用绑定的类：

```cpp
// C++ 侧接收 shared_ptr，pybind11 自动从 Python 对象提取
std::shared_ptr<DensityData> density_from_points(
    Eigen::Ref<const Eigen::MatrixXd> P, py::object values_obj);

// Python 侧
mu = _mongeampere.density_from_points(X, values)
```

### 3.5 numpy ↔ Eigen：`#include <pybind11/eigen.h>`

这是最核心的胶水层。引入 `pybind11/eigen.h` 后，以下类型的参数和返回值自动转换：

| C++ 参数类型 | Python 端传入 | 拷贝开销 |
|-------------|-------------|---------|
| `Eigen::Ref<const MatrixXd>` | `np.ndarray` (float64, 2D) | **零拷贝**（共享内存） |
| `Eigen::Ref<const VectorXd>` | `np.ndarray` (float64, 1D) | **零拷贝** |
| `Eigen::MatrixXd` (返回值) | 自动转为 `np.ndarray` | 一次拷贝 |
| `Eigen::VectorXd` (返回值) | 自动转为 `np.ndarray` | 一次拷贝 |
| `Eigen::MatrixXi` (返回值) | 自动转为 `np.ndarray` (int) | 一次拷贝 |

**关键约束**：`Eigen::Ref` 要求内存**连续且对齐**。从 Python 传入前必须保证：

```python
X = np.ascontiguousarray(my_array, dtype=np.float64)
```

否则会触发 `pybind11::error_already_set` 运行时异常。

### 3.6 可选参数：`py::object` + `is_none()`

Python 的 `None` 在 C++ 侧是 `py::object` 类型，用 `is_none()` 判断：

```cpp
Eigen::VectorXd
ot_solve(DensityData &d,
         Eigen::Ref<const Eigen::MatrixXd> X,
         Eigen::Ref<const Eigen::VectorXd> masses,
         py::object x0_obj,    // ← 可以是 None 或 ndarray
         ...)
{
    Eigen::VectorXd x;
    if (x0_obj.is_none()) {
        x = Eigen::VectorXd::Zero(X.rows());  // 默认值
    } else {
        x = x0_obj.cast<Eigen::VectorXd>();   // 显式转换
    }
    // ...
}
```

也可以通过 `py::array_t<double>` 直接读取 numpy 数组数据：

```cpp
auto arr = values_obj.cast<py::array_t<double>>();
std::copy(arr.data(), arr.data() + N, V.data());
```

### 3.7 返回多个值：`py::make_tuple`

C++ 函数通常需要返回多个值。pybind11 用 `py::make_tuple` 打包为 Python tuple：

```cpp
py::tuple
lloyd_step(DensityData &d,
           Eigen::Ref<const Eigen::MatrixXd> X,
           Eigen::Ref<const Eigen::VectorXd> w)
{
    Eigen::VectorXd masses;
    Eigen::MatrixXd centroids(X.rows(), 2);
    MA::lloyd(d.tri, d.funcs, X, w, masses, centroids);
    return py::make_tuple(masses, centroids);
}

// Python 端解包
masses, centroids = _mongeampere.lloyd_step(mu._data, Y, psi)
```

`py::make_tuple` 支持任意数量和类型的参数，只要每个参数有对应的 pybind11 类型转换器。

### 3.8 稀疏矩阵返回

Eigen 的 `SparseMatrix<double>` 也能自动转换。在 `kantorovich` 绑定中：

```cpp
py::tuple
kantorovich_eval(DensityData &d, ...) {
    Eigen::VectorXd  g;
    SparseMatrix     h;  // ← Eigen::SparseMatrix<double>
    double fval = MA::kantorovich(d.tri, d.funcs, X, w, g, h);
    return py::make_tuple(fval, g, h);  // 稀疏矩阵自动转为 scipy.sparse
}
```

Python 端收到的是 `scipy.sparse.csc_matrix`（列压缩格式）：

```python
fval, gradient, hessian = _mongeampere.kantorovich(mu._data, Y, psi)
# hessian 是 scipy.sparse.csc_matrix
```

### 3.9 CMake 集成：`pybind11_add_module`

pybind11 提供专门的 CMake 函数 `pybind11_add_module`，替代 `add_library`：

```cmake
find_package(pybind11 REQUIRED)

pybind11_add_module(_mongeampere
    bindings.cpp
    helper.cpp
)

target_link_libraries(_mongeampere PRIVATE
    CGAL::CGAL
    Boost::timer
)
```

**特点**：
- 自动找到当前 Python 版本的 include 路径和链接库
- 自动设置正确的编译选项（`-fvisibility=hidden` 等）
- 输出文件名自动带 Python 版本后缀（如 `_mongeampere.cpython-314-darwin.so`）

### 3.10 自动部署：编译后拷贝 .so

在 `CMakeLists.txt` 中添加 `POST_BUILD` 命令，编译完成后自动拷贝：

```cmake
add_custom_command(TARGET _mongeampere POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
        "$<TARGET_FILE:_mongeampere>"                      # 源：构建产物
        "${MONGEAMPERE_PYTHON_DIR}/$<TARGET_FILE_NAME:_mongeampere>"  # 目标：Python 包目录
)
```

其中 `$<TARGET_FILE:_mongeampere>` 是 CMake 生成表达式，展开为 `.so` 的完整路径。这样每次 `make` 后 Python 端就能直接 import。

---

## 4. 文件结构

```
MongeAmpere/
├── include/MA/          # C++ 头文件（库本身）
├── tests/               # 原有 C++ 测试（含 stb_impl.cpp）
├── pybind/
│   ├── CMakeLists.txt   # pybind 模块的构建配置
│   ├── bindings.cpp     # C++ pybind11 绑定代码
│   └── build/           # 构建产物
└── python/
    └── MongeAmpere/
        ├── __init__.py  # Python 高级 API 封装
        └── _mongeampere*.so  # 编译产物（自动拷贝）
```

---

## 5. C++ 绑定代码核心设计

### 5.1 类型体系

MongeAmpere++ 的函数全部是**模板函数**，必须用具体类型实例化：

```cpp
using K = CGAL::Exact_predicates_inexact_constructions_kernel;
using Delaunay = CGAL::Delaunay_triangulation_2<K>;
using LinearFunc = MA::Linear_function<K>;
using Functions = std::map<Delaunay::Face_handle, LinearFunc>;
```

### 5.2 DensityData：持有三角剖分 + 密度函数

pybind11 不能直接暴露 CGAL 的 `Face_handle`、`Vertex_handle` 等内部类型，所以用一个 struct 把三角剖分和密度函数打包：

```cpp
struct DensityData {
    Delaunay  tri;         // 三角剖分
    Functions funcs;       // face → Linear_function 映射
    double    total_mass;  // 总质量
};
```

对外只暴露 `.num_vertices()`、`.get_vertices()`、`.get_values()` 等简单接口。

### 5.3 密度构造：两点一线

**从点集构造**（`density_from_points`）：

```cpp
// 1. 插入点到 Delaunay 三角剖分
d->tri.insert(pts.begin(), pts.end());

// 2. 对每个有限面，构造线性函数
for (auto f = d->tri.finite_faces_begin(); ...) {
    Point a = f->vertex(0)->point();
    Point b = f->vertex(1)->point();
    Point c = f->vertex(2)->point();
    d->funcs[f] = LinearFunc(a, pval[a], b, pval[b], c, pval[c]);
}
```

**从图像构造**（`density_from_image`）：直接调用 `MA::image_to_pl_function<Delaunay, LinearFunc>(filename, tri, funcs)`。

### 5.4 OT 求解：手动 Newton 法

不走库自带的 `MA::ot_solve`（它对初始空 cell 太严格，直接 `return`），而是在 pybind 里实现手动 Newton 迭代：

```cpp
// 空 cell 安全的手动 Newton 迭代
auto f = [&](const VectorXd &w, VectorXd &out_m, ...) {
    double rv = MA::kantorovich(tri, funcs, X, w, out_g, out_h);
    out_m = out_g;           // ← kantorovich 在 g 里返回 cell 质量
    out_g = out_g - masses;  // 梯度 = 质量 - 目标质量
    return rv - masses.dot(w);
};

// 初始空 cell → 加大抖动重试
while (m.minCoeff() <= 1e-12 && retries++ < 15) {
    x = 0.01 * VectorXd::Random(N);
    fx = f(x, m, g, h);
}

// 线搜索保证每一步都不出空 cell
while (true) {
    x = w0 + alpha * d;
    fx = f(x, m, g, h);
    if (m.minCoeff() >= eps0 && g.norm() <= (1-alpha/2)*n0) break;
    alpha *= 0.5;
    if (alpha < 1e-12) { x = w0; break; }
}
```

---

## 6. 构建配置（CMakeLists.txt）

```cmake
find_package(pybind11 REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(CGAL REQUIRED)
find_package(Boost REQUIRED COMPONENTS timer chrono)

pybind11_add_module(_mongeampere
    bindings.cpp
    ${STB_IMPL}          # stb_image 实现文件
)

# 关键：编译后自动拷贝 .so 到 Python 包目录
add_custom_command(TARGET _mongeampere POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
        "$<TARGET_FILE:_mongeampere>"
        "${MONGEAMPERE_PYTHON_DIR}/$<TARGET_FILE_NAME:_mongeampere>"
)
```

构建：

```bash
cd pybind/build
cmake .. -Dpybind11_DIR=/opt/homebrew/lib/.../pybind11/share/cmake/pybind11
make -j8
```

---

## 7. Python 高级 API 封装

`__init__.py` 提供 reflector 期望的 API，底部调用 `_mongeampere` 模块：

```python
import numpy as np
from . import _mongeampere

class Density_2:
    def __init__(self, X, values=None):
        if isinstance(X, str):
            self._data = _mongeampere.density_from_image(X)
        else:
            self._data = _mongeampere.density_from_points(X, values)

    @property
    def vertices(self):  return self._data.get_vertices()
    @property
    def values(self):    return self._data.get_values()
    def mass(self):      return self._data.total_mass

def optimal_transport_2(mu, Y, nu, w0=None, verbose=True):
    Y = np.ascontiguousarray(Y, dtype=np.float64)
    nu = np.ascontiguousarray(nu, dtype=np.float64)
    return _mongeampere.ot_solve(mu._data, Y, nu, w0, ...)

def optimal_transport_presolve_2(Y, X, Y_w=None, X_w=None):
    # 零附近的小随机扰动 → 避免空 cell
    return 0.005 * np.random.randn(len(Y))

def conforming_lloyd_2(mu, Y, psi, hull_pts=None):
    masses, centroids = _mongeampere.lloyd_step(mu._data, Y, psi)
    # 投影到凸包边界
    ...

def delaunay_2(Z, weights):
    return _mongeampere.delaunay_2(Z, weights)

def optimized_sampling_2(density, N, n_iter=30):
    pts = density.random_sampling(N)
    for _ in range(n_iter):
        _, centroids = _mongeampere.lloyd_step(density._data, pts, weights)
        pts = centroids
    return pts
```

**关键约定**：传入 C++ 的 numpy 数组必须用 `np.ascontiguousarray(..., dtype=np.float64)` 保证内存连续。

---

## 8. 遇到的错误与解决方法

### 8.1 Eigen::Ref 导致模板推导冲突

**现象**：

```
error: no matching function for call to 'ot_solve'
candidate template ignored: deduced conflicting types for parameter 'Vector'
  ('Eigen::Ref<const Eigen::VectorXd>' vs. 'Eigen::VectorXd')
```

**原因**：pybind11 的 `Eigen::Ref<const Eigen::VectorXd>` 和输出 `Eigen::VectorXd` 是不同类型，C++ 模板无法统一推导。

**解决**：在调用模板函数前，先把 Ref 拷贝到普通 Eigen 类型：

```cpp
Eigen::MatrixXd X = X_ref;        // Ref → 普通类型
Eigen::VectorXd masses = masses_ref;
MA::ot_solve(d.tri, d.funcs, X, masses, x, ...);
```

### 8.2 CGAL::Delaunay_triangulation_2 不接受加权点

**现象**：

```
error: no matching member function for call to 'insert'
candidate function not viable: no known conversion from
  'pair<Point_2<Epick>, double>' to 'const Point'
```

**原因**：`CGAL::Delaunay_triangulation_2` 的 `insert()` 接受裸 `Point`，不接受 `(Point, weight)` 对。

**解决**：加权 Delaunay（即 Regular Triangulation）应使用 `CGAL::Regular_triangulation_2<K>`：

```cpp
#include <CGAL/Regular_triangulation_2.h>
using RT = CGAL::Regular_triangulation_2<K>;
using WPoint = typename RT::Weighted_point;

RT rt;
std::vector<WPoint> wpts;
for (size_t i = 0; i < N; ++i)
    wpts.emplace_back(Point(P(i,0), P(i,1)), w(i));
rt.insert(wpts.begin(), wpts.end());
```

### 8.3 MA::ot_solve 对空 cell 过于严格

**现象**：`Error: computed minimum mass is non-positive ... the Laguerre cell is empty`，然后直接 `return`，不求解。

**原因**：`MA::ot_solve` 在第一步就检查 `eps0 <= 0`，如果初始权重导致任何 cell 质量为零，直接退出。

**解决**：不调用 `MA::ot_solve`，在 pybind 层实现手动 Newton 迭代（见 §5.4），加入空 cell 安全的线搜索和重试逻辑。

### 8.4 初始猜测产生空 cell

**现象**：初版 `optimal_transport_presolve_2` 用 `|Y - closest X|² - log(nu)` 作为初始猜测，结果权重过大导致 cell 为空。

**解决**：改为零附近的**小随机扰动** `0.005 * randn(M)`，和 C++ 测试中 `test_opttransport_gif.cpp` 的策略一致。

### 8.5 Delaunay 三角剖分的 Vertex 没有 info()

**注意点**：默认的 `Delaunay_triangulation_2<K>` 的 vertex 没有 `info()` 方法。不能用 `v->info()` 来存储顶点索引。替代方案是用 `std::map<Vertex_handle, size_t>` 建立映射。

---

## 9. 调试链路总结

```
Python 层                 C++ pybind 层              C++ 库层
─────────                ─────────────              ────────
Density_2(X, val)    →   density_from_points()  →  Delaunay + Linear_func
Density_2(img.png)   →   density_from_image()   →  image_to_pl_function
ot_solve(mu,Y,nu,w0) →   ot_solve(DensityData)  →  手动 Newton
lloyd_step(mu,Y,psi) →   lloyd_step(...)        →  MA::lloyd
delaunay_2(Z,w)      →   delaunay_2(RegularTri) →  Regular_triangulation
                             ↑
                     关键：Ref → 普通 Eigen 类型拷贝
                     关键：空 cell → 随机抖动 + 线搜索保护
                     关键：加权 Delaunay → Regular_triangulation_2
```

---

## 10. 文件清单

| 文件 | 作用 |
|------|------|
| `pybind/bindings.cpp` | C++ pybind11 绑定：DensityData、手动 Newton、delaunay_2 |
| `pybind/CMakeLists.txt` | 构建配置：pybind11 + CGAL + Eigen + Boost |
| `python/MongeAmpere/__init__.py` | Python 高级 API：Density_2、OT、Lloyd、采样 |
| `python/MongeAmpere/_mongeampere*.so` | 编译产物（自动生成） |

---

## 11. 后续：对接 reflector-master

reflector-master 期望 `import MongeAmpere as ma`，且 `ma` 模块需在 `sys.path` 中。因为我们的 `MongeAmpere/` 包在 `MongeAmpere/python/` 下，需要：

```python
sys.path.append('../MongeAmpere/python')  # 替代原来的 PyMongeAmpere-build
```

另外 reflector-master 是 Python 2 代码，还需迁移 `cPickle → pickle`、`scipy.misc.imread → imageio`、`except E, arg: → except E as arg:` 等。

---

*实测：核心链路（密度构造 → OT 求解 → Lloyd → Delaunay）调通，200 点 → 50 点 OT 求解可正常收敛。*
