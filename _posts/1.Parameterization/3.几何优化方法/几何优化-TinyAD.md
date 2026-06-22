---
layout: post
title: "TinyAD"
date: 2026-06-17
category: Parameterization
categories: ["Parameterization", "Parameterization-GeometricOptimization"]
---

## 动机：几何优化里的求导瓶颈

网格参数化、形变、方向场设计、配准、可展曲面逼近等任务，核心往往是**非线性（常非凸）优化**。研究迭代中需要反复改动目标函数与求解器细节，但手动推导、实现梯度与 **Hessian** 既慢又易错；二阶信息虽能加速收敛，却因实现成本常被放弃。

现有自动微分（AD）工具在几何处理中常遇：

- 反向模式对**小局部问题**未必更快，且二阶导需额外遍；
- 动态分支/循环受限，或需显式枚举分支；
- 网格问题的**稀疏结构**需从计算图推断或手写装配；
- 与 Eigen / 网格库集成重，头文件与编译时间长。

Schmidt、Born、Bommes、Campen、Kobbelt 在 SGP 2022 提出 [**TinyAD**](https://github.com/patr-schm/TinyAD)：**仅依赖 Eigen 的 header-only C++ 库**，用**前向模式**对"微小"子问题求二阶导，再装配全局稀疏梯度/Hessian。论文主张：对网格上典型的**按元素（per-element）**能量，前向模式往往**最灵活且实际最快**。

- 论文：[TinyAD: Automatic Differentiation in Geometry Processing Made Simple](https://graphics.rwth-aachen.de/media/papers/341/TinyAD.pdf)（CGF 41(5), 2022）
- 示例仓库：[TinyAD-Examples](https://github.com/patr-schm/TinyAD-Examples)
- 演讲：[YouTube](https://youtu.be/FGG07HoVFEk)

---

## 核心思想：Tiny 子问题 + 前向二阶 AD

### 为何前向模式适合网格？

目标常形如

$$
f(x)=\sum_{e\in\mathcal{E}} f_e(x_e),\qquad x\in\mathbb{R}^n,
$$

每个元素 $e$（三角形、四面体、边……）只依赖**少量变量** $x_e\in\mathbb{R}^k$（$k$ 为 3–24 量级）。对每个 $f_e$ 用 $k$ 维前向 AD 求 $(f_e,g_e,H_e)$ 代价 $O(k^2)$–$O(k^3)$，再散射到全局稀疏矩阵——总复杂度接近手工推导，但**无需手写**。

渐近分析说反向模式对大规模 $n$ 更优；但当 $k$ 很小（如三角面 $k=6$）时，常数因子与无 tape、无图重建使**前向更快**（论文图 4：$k=6$ 时 TinyAD 比 ADOL-C 快约 73 倍）。

### 无计算图 tape

`TinyAD::Double<k>` 在每个标量上携带 $(v,g,H)$，编译期内联链式法则，**控制流与原始程序一致**——`if`、依赖变量的 `for` 均可，无需 retaping。

---

## API 两层接口

### 1. 稠密小问题：`TinyAD::Double<k>`

```cpp
using AD = TinyAD::Double<3>;
Eigen::Vector3 x = AD::make_active({0.0, -1.0, 1.0});
Eigen::Vector3 y(2.0, 3.0, 5.0);
AD angle = acos(x.dot(y) / (x.norm() * y.norm()));
Eigen::Vector3d g = angle.grad;
Eigen::Matrix3d H = angle.Hess;
```

- `AD(值, 变量下标)` 初始化活跃变量；
- 与 `double` 混用；可作为 `Eigen::Matrix` 标量类型；
- 支持初等函数、矩阵运算（行列式、逆、归一化等）。

### 2. 网格稀疏问题：`ScalarFunction` / `VectorFunction`

```cpp
auto func = TinyAD::scalar_function<2>(mesh.vertices());
func.add_elements<3>(mesh.faces(), [&](auto& element) {
    using T = TINYAD_SCALAR_TYPE(element);
    Eigen::Vector2 a = element.variables(/* 顶点句柄 */);
    // ... 计算面能量 ...
    return energy;
});
auto [f, g, H] = func.eval_with_derivatives(x);
auto [f, g, H_proj] = func.eval_with_hessian_proj(x);  // 投影正定 Hessian
```

- `scalar_function<d>`：每变量 $d$ 维（平面参数化 $d=2$，体积形变 $d=3$）；
- `add_elements<k>`：每个元素连接 $k$ 个变量句柄；
- 兼容 OpenMesh、Geometry Central、polymesh、libigl 风格矩阵；
- 提供 `newton_direction`、`line_search` 等基础 Newton 步工具。

**向量值目标**用 `VectorFunction`（如带约束的 KKT 系统）。

---

## 典型工作流：投影 Newton

论文图 2 用对称 Dirichlet 能量做平面参数化，核心循环：

```
x ← 初值（如 Tutte embedding）
重复:
  (f, g, H_proj) ← func.eval_with_hessian_proj(x)
  d ← 解 H_proj d = -g
  若 Newton decrement 足够小: 停止
  x ← line_search(x, d, f, g, func)
```

面能量示例：$A\,\big(\|J\|_F^2 + \|J^{-1}\|_F^2\big)$，$J$ 为仿射雅可比；**翻转检测** `det ≤ 0 → return INFINITY` 可在元素 lambda 内分支，AD 仍有效。

---

## 论文复现示例（第 4 节）

| 应用 | 能量 / 方法 |
| :--- | :--- |
| **曲面参数化** | Symmetric Dirichlet、projected Newton |
| **体积形变** | 非线性弹性 + 约束（四面体元素） |
| **Frame field** | 复数表示的 N-RoSy 能量 |
| **流形优化** | Stiefel 流形上的 retractions（自定义变量表示） |

这些实现在 TinyAD-Examples 中可对照论文公式直接改能量项，利于**可复现研究**。

---

## 与其他 AD 方案对比

| 工具 | 模式 | 二阶 | 分支 | 网格稀疏 |
| :--- | :--- | :--- | :--- | :--- |
| **TinyAD** | 前向 | ✓ | 自由 | `ScalarFunction` 原生 |
| ADOL-C | 反向 | ✓ | 需 retape | 着色推断 |
| Adept / FastAD | 反向 | 一阶为主 | 受限 | 手动 |
| PyTorch / TF | 反向 | 可能 | 动态图 | 稠密张量导向 |
| 手工推导 | — | ✓ | — | 最快但难维护 |
| 符号（SymPy 等） | — | ✓ | — | 表达式膨胀 |

**何时不用 TinyAD**：$k$ 或单元素变量数极大、仅需一阶导且 $n$ 上万时，反向模式或解析雅可比可能更合适。

---

## 与本博客其他优化笔记的关系

| 笔记 | 联系 |
| :--- | :--- |
| `全局调和参数化FastHGP` | HGP 用 MOSEK SOCP；若改罚函数/局部能量可借 TinyAD 快速试目标 |
| `SLIM` | 局部-全局 SLIM 代理能量可用 AD 组装 |
| `2018-03-20-扭曲有界的调和映射` | 有界畸变能量求导繁琐，TinyAD 类工具降低原型成本 |
| `圆填充与折纸` | 非线性约束优化原型 |

TinyAD **不提供**黑盒求解器（如 IPOPT）；它负责 $f,g,H$，Newton 步、流形投影、交替优化等仍由用户按问题定制——这与几何处理论文中大量**问题特定**求解策略一致。

---

## 使用与构建

```bash
git clone https://github.com/patr-schm/TinyAD.git
# CMake: add_subdirectory(TinyAD) + target_link_libraries(... TinyAD::TinyAD)
```

要求 C++17、Eigen3。MIT 许可。

---

## 设计要点小结

1. **编译期前向 AD** + Eigen 向量化 → 小 $k$ 极快。
2. **Per-element 装配** → 天然匹配网格稀疏模式，无需图着色。
3. **任意控制流** → 翻转惩罚、自适应三角剖分等可微分支。
4. **Header-only** → 易嵌入现有 C++ 几何代码库（如本仓库 `cpp/conformal-parameterization` 中的实验性集成）。

---

## 参考文献

1. P. Schmidt, J. Born, D. Bommes, M. Campen, L. Kobbelt. **TinyAD: Automatic Differentiation in Geometry Processing Made Simple**. *Computer Graphics Forum* 41(5), SGP 2022. [DOI](https://doi.org/10.1111/cgf.14787)
2. A. Griewank, A. Walther. *Evaluating Derivatives* — AD 理论基础。
3. P. Schmid. Tutorial on automatic differentiation in geometry processing, 2019.
