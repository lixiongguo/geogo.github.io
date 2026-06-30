---
layout: post
title: "Provably Good Planar Mappings — 可证明的平面映射"
category: Parameterization
categories: ["Parameterization", "Parameterization-GeometricOptimization"]
mathjax: true
---

> **论文**：Roi Poranne, Yaron Lipman. [*Provably Good Planar Mappings*](https://doi.org/10.1145/2601097.2601123). ACM Transactions on Graphics (SIGGRAPH), 33(4), 2014.

## 概述

平面映射与变形是图形学中的核心问题（图像变形、角色动画、配准、形状分析等）。**Provably Good Planar Mappings** 提出一套框架：在通用光滑函数基上构造映射，使"好"的性质——**无折叠（单射）、光滑、低畸变**——不仅在配准点上成立，而且可**证明**在整个定义域上成立。

变形即映射 $f:\Omega \to \mathbb{R}^2$；**Jacobian** $J_f$ 描述局部线性近似，**畸变**度量映射质量。本文路线：在 **meshless** 光滑基（B-Spline、TPS、Gaussian）上，于**配准点（collocation points）**施加**凸约束**，再用连续性模把离散保证**传播到全域**——桥接 mesh 方法的可控性与 meshless 的光滑性。

---

## 1. 动机：mesh 与 meshless 的鸿沟

用户拖动**手柄** $\{(\mathbf{p}_i,\mathbf{q}_i)\}$ 驱动区域 $\Omega\subset\mathbb{R}^2$ 的变形，要求：光滑、无 fold-over、畸变不超过阈值 $K$。常见路线各有短板：

| 方法类型 | 优势 | 不足 |
| :--- | :--- | :--- |
| **Mesh-based**（三角网格、ARAP、SLIM、[Lipman 2012 投影](https://doi.org/10.1145/2185520.2185604) 等） | 可控制单射 / 畸变 | 要足够光滑需极密单元，慢；交互变形易出现尖点 |
| **Meshless**（B-Spline、TPS、Gaussian、MVC 等） | 构造上天然光滑 | 难避免折叠，难控制畸变；MVC 等仅在有限点证明单射 |

本文目标：**meshless 的光滑基 + 可证明的全局单射与畸变界**。

---

## 2. 线性变形空间

选取有限组基函数 $\mathcal{F}=\{\varphi_k\}_{k=1}^n$，$\varphi_k:\Omega\to\mathbb{R}$。平面映射写为

$$
f(\mathbf{x}) = \begin{pmatrix} u(\mathbf{x}) \\ v(\mathbf{x}) \end{pmatrix}
= \sum_{k=1}^{n} \mathbf{c}_k\,\varphi_k(\mathbf{x}),
\qquad \mathbf{c}_k\in\mathbb{R}^2,
\tag{1}
$$

系数矩阵 $\mathbf{C}=[\mathbf{c}_1,\ldots,\mathbf{c}_n]\in\mathbb{R}^{2\times n}$ 为优化变量。基函数光滑 ⇒ $f$ 光滑；但**不**加约束时，$\mathbf{C}$ 任意取值会产生任意 fold-over 与畸变。

**关键**：$J_f(\mathbf{x})$ 对 $\mathbf{C}$ **仿射**（梯度 $\nabla u,\nabla v$ 为 $\mathbf{C}$ 的线性函数），故可在配准点上把奇异值约束写成 **SOCP / SDP** 可解的凸集——这是与 [Lipman 2012](https://doi.org/10.1145/2185520.2185604) 网格投影一脉相承、但搬到 meshless 系数空间的核心。

### 2.1 三类实验基函数

| 基 | 形式（示意） | 特点 |
| :--- | :--- | :--- |
| **B-Spline** | 张量积三次均匀 B 样条 | 局部支撑、交互常用 |
| **TPS** | $\varphi(\|\mathbf{x}-\mathbf{x}_k\|)=r^2\log r$ | 插值型、整体光滑 |
| **Gaussian** | $\exp(-\|\mathbf{x}-\mathbf{x}_k\|^2/(2s^2))$ | 形状感知（shape-aware）径向基 |

论文 Table 1 给出各基 $\nabla\varphi$ 的**梯度连续性模** $\omega_{\nabla\varphi}(t)$（见 §5），用于全域传播分析。

---

## 3. 畸变度量：Jacobian 奇异值

在 $\mathbf{x}$ 处，$f=(u,v)^T$ 的 Jacobian

$$
J_f(\mathbf{x}) = \begin{pmatrix} \partial_x u & \partial_y u \\ \partial_x v & \partial_y v \end{pmatrix}.
$$

奇异值 $\Sigma(\mathbf{x})\ge\sigma(\mathbf{x})\ge 0$ 度量两主方向的拉伸。$D(\mathbf{f},\mathbf{x})=D(\Sigma,\sigma)$，$D=1$ 为无畸变。

**等距畸变**（长度保持）：

$$
D_{\text{iso}}(\mathbf{x}) = \max\bigl\{\Sigma(\mathbf{x}),\; 1/\sigma(\mathbf{x})\bigr\}.
\tag{2}
$$

$D_{\text{iso}}=1$ $\Leftrightarrow$ $\Sigma=\sigma=1$（局部刚体）。

**共形畸变**（角度保持）：

$$
D_{\text{conf}}(\mathbf{x}) = \Sigma(\mathbf{x}) / \sigma(\mathbf{x}).
\tag{3}
$$

$D_{\text{conf}}=1$ $\Leftrightarrow$ $\Sigma=\sigma$（局部相似变换）。

### 3.1 相似 / 反相似分解（凸约束的基础）

将 $J_f$ 分解为**相似部分**与**反相似部分**（对 $\mathbf{C}$ 线性）：

$$
J_s f = \begin{pmatrix} \nabla u \\ \nabla v \end{pmatrix}^{\!\top}\!\cdot\!\text{（相似模板）},\quad
J_a f = \begin{pmatrix} \nabla u \\ \nabla v \end{pmatrix}^{\!\top}\!\cdot\!\text{（反相似模板）}.
$$

（论文式 (19)：用逆时针旋转 $\frac{\pi}{2}$ 的矩阵把 $\nabla u,\nabla v$ 配对。）则有

$$
\Sigma = \|J_s\| + \|J_a\|,\qquad \sigma = \|J_s\| - \|J_a\|
$$

（要求 $\|J_s\|\ge\|J_a\|$）。等距界 $\Sigma\le K$、$\sigma\ge K^{-1}$ 化为对 $\|J_s\|,\|J_a\|$ 的范数约束；$\sigma>0$ 与 $\det J_f>0$ 共同保证局部单射（§7）。

---

## 4. 配准点、填充距离与连续性模

### 4.1 配准点上的约束

在配准点集 $\mathcal{Z}=\{\mathbf{z}_j\}_{j=1}^m\subset\Omega$ 上要求

$$
D(f;\mathbf{z}_j) \le K,\qquad \sigma(\mathbf{z}_j) > 0.
\tag{4}
$$

直接在整个 $\Omega$ 上施加无穷多条约束不可行；理论保证：若 $\mathcal{Z}$ **足够密**，且 (4) 在 $\mathcal{Z}$ 上成立，则对**所有** $\mathbf{x}\in\Omega$ 可界定畸变与单射性。

**填充距离（fill distance）** 量化密度：

$$
h(\mathcal{Z},\Omega) = \max_{\mathbf{x}\in\Omega}\;\min_{\mathbf{z}\in\mathcal{Z}} \|\mathbf{x}-\mathbf{z}\|.
\tag{5}
$$

即 $\Omega$ 中离配准点**最远**的点到最近配准点的距离。$h$ 越小，离散采样越密。

### 4.2 连续性模

函数 $g:\mathbb{R}^2\to\mathbb{R}$ 具有连续性模 $\omega$（**$\omega$-连续**），若

$$
|g(\mathbf{x}) - g(\mathbf{y})| \leq \omega(\|\mathbf{x} - \mathbf{y}\|), \quad \forall \mathbf{x}, \mathbf{y} \in \Omega,
\tag{6}
$$

其中 $\omega:\mathbb{R}^+\to\mathbb{R}^+$ 连续、严格单调且 $\omega(0)=0$。它上界函数随距离的变化速率。

**Lemma 2**：若 $\nabla u,\nabla v$ 均为 $\omega$-连续，则奇异值函数 $\Sigma,\sigma$ 为 $2\omega$-连续。对式 (1) 的映射，$\omega$ 由基函数梯度模 $\omega_{\nabla\varphi}$ 与系数 $\mathbf{C}$ 通过矩阵范数组合得到（论文式 (8)–(9)）。

| 基 | $\omega_{\nabla\varphi}(t)$（示意） |
| :--- | :--- |
| 三次 B-Spline | $4\delta t / (3\Delta^2)$，$\Delta$ 为网格间距 |
| TPS | 局部 $O(t(5.8+5\log t))$ |
| Gaussian | 与 $s$ 相关的 $O(t)$ 界 |

---

## 5. 全局畸变界：Lemma 1 与三种策略

设在所有 $\mathbf{z}\in\mathcal{Z}$ 上等距畸变受控 $D_{\text{iso}}(\mathbf{z})\le K$，即

$$
\Sigma(\mathbf{z}) \leq K, \qquad \sigma(\mathbf{z}) \geq \frac{1}{K}.
\tag{10}
$$

记 $h=h(\mathcal{Z},\Omega)$，$\omega=\omega_{\Sigma,\sigma}$ 为奇异值的连续性模。由 **Lemma 1**，对任意 $\mathbf{x}\in\Omega$：

$$
D_{\text{iso}}(\mathbf{x}) \leq \max\left\{ K + \omega(h),\; \frac{1}{K^{-1} - \omega(h)} \right\},
\qquad\text{需 } K^{-1} > \omega(h).
\tag{11}
$$

**共形**情形：若在配准点还有 $\Sigma(\mathbf{z})\le K_{\text{conf}}$、$\sigma(\mathbf{z})\ge\delta>0$（$\delta$ 防止 $\sigma\to 0$ 失去单射），则

$$
D_{\text{conf}}(\mathbf{x}) \leq \frac{K_{\text{conf}} + \omega_{\text{co}}(h)}{\delta - \omega_{\text{co}}(h)},
\qquad \delta > \omega_{\text{co}}(h).
\tag{13}
$$

式 (11)(13) 把**离散配准点界 $K$**、**密度 $h$**、**基的光滑性 $\omega$** 三者联系起来——这就是 **provably** 的含义：交互时只在稀疏 active set 上解 SOCP，后处理可用更密网格**认证**全域界。

### 5.1 三种畸变控制策略

| 策略 | 已知 | 求 |
| :--- | :--- | :--- |
| **1. 认证** | $\mathcal{Z}$、配准点界 $K$ | 全域最大畸变 $\bar{K}$（由 (11) 直接算） |
| **2. 加密网格** | 配准点界 $K$、目标全域界 $\bar{K}$ | 所需填充距离 $h$（反解 (14)(15)） |
| **3. 反推约束** | $\mathcal{Z}$、目标全域界 $\bar{K}$ | 配准点上应施加的 $K$（式 (16)(17)） |

交互阶段用粗网格（如 $200\times 200$ 配准点）实时求解；用户满意后切换到策略 2，用 $3000$–$6000$ 点网格**证明**单射与畸变界（论文实验）。

---

## 6. 单射性：从配准点到全域

**局部单射**：$\det J_f(\mathbf{x})>0$。因 $\sigma(\mathbf{x})>0 \Rightarrow \det J_f\ge 0$ 且 $\det J_f$ 连续，在连通域上符号不变；故**只需** $\sigma(\mathbf{x})>0$ 处处成立，并在每连通分量上**一点**验证 $\det J_f>0$。

**全局单射**（单连通 $\Omega$）：若 $f$ 局部单射且 $f|_{\partial\Omega}$ 单射，则 $f$ 在 $\Omega$ 上单射（proper map 论证）。

由 (11)：当 $K^{-1}>\omega(h)$ 时，$\sigma(\mathbf{x})\ge K^{-1}-\omega(h)>0$，结合 (4) 在配准点成立 ⇒ **全域无 fold-over**。共形界 (13) 中 $\delta>\omega_{\text{co}}(h)$ 起同样作用。

---

## 7. 配准点上的凸约束与 SOCP

在 active 配准点 $\mathbf{z}$ 上，等距约束 (10) 化为（论文式 (21)–(23)）：

$$
\|J_s f(\mathbf{z})\| \le t,\quad \|J_a f(\mathbf{z})\| \le s,\quad t+s \le K,
$$

其中 $t,s$ 为辅助变量——标准**二阶锥规划（SOCP）**形式。

下界 $\sigma\ge K^{-1}$ 即 $\|J_s\|-\|J_a\|\ge K^{-1}$，涉及**锥的补集**，非凸。沿用 Lipman 2012 的 **frame** 技巧：引入单位向量 $\mathbf{d}$，用半空间

$$
J_s f(\mathbf{z})^\top \mathbf{d} \ge r
$$

凸化内接于锥补（论文式 (25)(26)）；每步根据上一步 $J_s$ 更新 $\mathbf{d}$（式 (27)），使可行域尽量大。该约束同时迫使 $\det J_f>0$。

**共形**约束写为 frame 形式 (28)。**手柄**位置约束用软能量（式 (29)(30)）或硬约束；软约束保证交互时 SOCP 始终可行（畸变过紧时手柄暂时"拖不动"）。

---

## 8. 优化问题与 Active Set 算法

原无限维问题

$$
\min_f\; E_{\text{pos}}(f) + \lambda E_{\text{reg}}(f)
\quad\text{s.t.}\quad D(f;\mathbf{x})\le K,\;\forall \mathbf{x}\in\Omega
$$

离散为（论文式 (18)）：

$$
\min_{\mathbf{C}}\; E_{\text{pos}}(f) + \lambda E_{\text{reg}}(f)
\quad\text{s.t.}\quad D(f;\mathbf{z}) \le K,\;\forall \mathbf{z}\in\bar{\mathcal{Z}},
\tag{18}
$$

其中 $\bar{\mathcal{Z}}\subseteq\mathcal{Z}$ 为**active set**。正则项常用：

- **双调和能量** $E_{\text{bi}}$：$\int \|H_u\|_F^2+\|H_v\|_F^2$（对 $\mathbf{C}$ 二次）；
- **ARAP 能量** $E_{\text{arap}}$：在预采样点 $\mathbf{r}_i$ 上 $\sum_i \|J_f(\mathbf{r}_i)-R_i\|_F^2$，经 frame 化为二次项 (33)。

### 8.1 Active Set 更新（交互关键）

配准点布在均匀矩形网格上。每步：

1. 计算所有 $\mathbf{z}\in\mathcal{Z}$ 的 $D(f;\mathbf{z})$；
2. 找畸变的**局部极大**；若 $D(\mathbf{z})>K_{\text{on}}$（如 $K_{\text{on}}=0.1+0.9K$），将 $\mathbf{z}$ 加入 $\bar{\mathcal{Z}}$；
3. 若 $D(\mathbf{z})<K_{\text{off}}$（如 $0.5+0.5K$），从 $\bar{\mathcal{Z}}$ 移除；
4. 保留少量均匀分布的**常驻**配准点以防手柄快速移动时约束突变。

实践中每步仅激活少量孤立点（图 3A–3C：杆弯曲时激活点防止塌陷；去掉约束则出现奇点）。对 active 点解 SOCP（MOSEK 等内点法），复杂度随 $|\bar{\mathcal{Z}}|$ 近线性（论文图 7）。

### 8.2 算法概要

```
输入：手柄 {(p_i, q_i)}，基函数 F，配准网格 Z，畸变界 K
输出：变形 f

初始化：预计算 φ_k(z), ∇φ_k(z)；frame d←(1,0)；Z̄←∅；常驻点 Z^fix
重复（用户拖动手柄）:
  用当前 C 评估 D(z), z∈Z
  按 K_on, K_off 更新 active set Z̄
  解 SOCP (18)：手柄能量 + 正则 + 在 Z̄∪Z^fix 上的畸变锥约束
  更新 frame d（式 27）
后处理（可选）:
  加密 Z，用策略 2 计算 h，认证全域畸变 < K̄
```

---

## 9. 算例与对比

### 9.1 椭圆投影式子问题（与 KKT 笔记的联系）

把点 $\mathbf{p}$ 投影到椭圆 $\{(x_1/a)^2+(x_2/b)^2\le 1\}$ 可视为 $\min \frac12\|\mathbf{x}-\mathbf{p}\|^2$ s.t. 凸不等式——见 [凸优化与 KKT 条件](../6.附录-数值计算与最优化/2019-07-14-凸优化与KKT条件.md) 例 3。Provably Good 框架把类似**凸约束**搬到每个配准点的 Jacobian 上，再传播到全域。

### 9.2 论文实验摘要

| 实验 | 设置 | 现象 |
| :--- | :--- | :--- |
| **B-Spline 杆**（图 5） | $6\times 6$ 均匀三次 B 样条，$E_{\text{bi}}+\lambda E_{\text{arap}}$ | 无约束时出现两个奇点；$K=2,3,4$ 时策略 3 用 $3000$ 网格认证全域畸变 |
| **TPS 方块**（图 8） | 25 基、中间两点旋转 | 无约束子方块 fold-over 消失；$K=5$ 需 $\approx 6000$ 点认证 |
| **鸟图**（图 9） | meshless ARAP ± 畸变约束 | Photoshop ARAP 在手柄处尖点折叠；光滑基无约束仍 fold；加约束后双射 |
| **圆盘**（图 10） | vs Schüller 2013、Lipman 2012 | 网格法保证单射但不够光滑；本文同样 $D_{\text{iso}}\le 5$ 且更光滑 |
| **Shape-aware Gaussian**（图 11） | 40 个高斯、$K=3$ | vs Schüller：手柄处无尖点 |

---

## 10. 小结

| 概念 | 作用 |
| :--- | :--- |
| 线性空间 (1) | B-Spline / TPS / Gaussian；$J_f$ 对系数仿射 |
| 配准点 $\mathcal{Z}$、active set $\bar{\mathcal{Z}}$ | 稀疏凸约束；交互时可变 |
| 奇异值 $\Sigma,\sigma$ | $D_{\text{iso}}, D_{\text{conf}}$；$J_s,J_a$ 分解 |
| 连续性模 $\omega$、填充距离 $h$ | Lemma 1：离散 → 全域 |
| SOCP + frame | Lipman 2012 凸化搬到 meshless |
| 策略 1–3 | 认证 / 加密 / 反推 $K$ |

**局限**：基需已知 $\omega_{\nabla\varphi}$；非凸域可用欧氏距离版分析；3D 推广见 Lipman 后续工作（有界畸变调和映射、3D 单射映射等）。

**相关笔记**：[MLS / 梯度域变形](几何变形1-梯度域方法.md)、[AKAP 平面变形](AKAF.md)、[AQP](几何优化-AQP.md)、[SLIM](几何优化-SLIM.md)、[TinyAD](几何优化-TinyAD.md)（可微能量原型）、[凸优化与 KKT](../6.附录-数值计算与最优化/2019-07-14-凸优化与KKT条件.md)。

---

## 参考文献

- Poranne R., Lipman Y. *Provably good planar mappings*. SIGGRAPH 2014. [DOI](https://doi.org/10.1145/2601097.2601123)
- Lipman Y. *Bounded distortion harmonic mappings in the plane*. SIGGRAPH 2015. [DOI](https://doi.org/10.1145/2766989)
- Lipman Y. *Bounded distortion mapping spaces for triangular meshes*. SIGGRAPH 2012. [DOI](https://doi.org/10.1145/2185520.2185604)
- Schüller C., et al. *Locally injective mappings*. SGP 2013.
- Solomon J., et al. *As-Killing-As-Possible vector fields for planar deformation*. SIGGRAPH 2011.
- Sorkine O., Alexa M. *As-rigid-as-possible surface modeling*. SGP 2007.
