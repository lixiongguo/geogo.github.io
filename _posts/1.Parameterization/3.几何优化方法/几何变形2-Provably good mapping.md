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

变形（deformation）即映射 $f:\Omega \to \mathbb{R}^2$；**Jacobian 矩阵** $J_f$ 描述 $f$ 的局部线性近似，**畸变（distortion）** 度量映射质量。此前常见路线包括 cage-based 变形、ARAP 等 mesh 方法，以及各类无网格基函数方法；本文试图兼顾二者优点。

---

## 1. 动机：mesh 与 meshless 的鸿沟

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250715194749002.png)

图示摘录了论文摘要中的核心矛盾：

| 方法类型 | 优势 | 不足 |
| :--- | :--- | :--- |
| **Mesh-based**（三角网格、ARAP、SLIM 等） | 可控制单射性 / 畸变 | 难以光滑；要足够光滑需极多单元，很慢 |
| **Meshless**（B-Spline、TPS、Gaussian 等） | 构造上天然光滑 | 难以避免折叠，难以控制畸变 |

本文目标：**在 meshless 的光滑基函数上，加入可证明的全局单射与畸变保证**——桥接两类方法。

---

## 2. 方法：配准点上的凸约束

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250715195608225.png)

常用变形基函数包括 **B-Splines**、**Gaussian**、**Thin-Plate Splines (TPS)** 等。它们诱导一个**线性变形空间**（系数 $\mathbf{c}$ 决定映射）。

本文做法：

1. 在定义域 $\Omega$ 上选取一组**配准点（collocation points）** $\mathcal{Z}$；
2. 在这些点上施加**专门设计的凸约束**，防止折叠与高畸变；
3. 理论分析给出配准点的**密度**与约束类型，从而保证性质扩展到**整个** $\Omega$，而非仅在离散点上。

直观上：在有限个采样点"卡住"映射的可行域，再靠基函数的光滑性把约束传播到全域。

---

## 3. 畸变度量：Jacobian 奇异值

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250715203425906.png)

在点 $\mathbf{x}$ 处，映射 $f=(u,v)^T$ 的 Jacobian 为

$$
J\mathbf{f}(\mathbf{x}) = \begin{pmatrix} \partial_x u & \partial_y u \\ \partial_x v & \partial_y v \end{pmatrix}
$$

设其**最大、最小奇异值**为 $\Sigma(\mathbf{x})$、$\sigma(\mathbf{x})$（也记 $\Sigma(\mathbf{f};\mathbf{x})$）。它们度量映射在 $\mathbf{x}$ 附近把邻域沿两主方向拉伸的程度。一般畸变记为 $D(\mathbf{f},\mathbf{x}) = D(\Sigma(\mathbf{x}), \sigma(\mathbf{x}))$；$D=1$ 表示无畸变。

**两种常用度量**：

**等距畸变**（长度保持）：

$$
D_{\text{iso}}(\mathbf{x}) = \max\bigl\{\Sigma(\mathbf{x}),\; 1/\sigma(\mathbf{x})\bigr\}
$$

$D_{\text{iso}}=1$ 当且仅当 $\Sigma=\sigma=1$，即局部接近**刚体运动**。

**共形畸变**（角度保持）：

$$
D_{\text{conf}}(\mathbf{x}) = \Sigma(\mathbf{x}) / \sigma(\mathbf{x})
$$

$D_{\text{conf}}=1$ 当且仅当 $\Sigma=\sigma$，即局部为**相似变换**（刚体 + 各向同性缩放）。

---

## 4. $\omega$-连续：用连续性模控制奇异值变化

### 4.1 连续性模的定义

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250715204737220.png)

函数 $g:\mathbb{R}^2 \to \mathbb{R}$ 称为具有连续性模 $\omega$（**$\omega$-连续**），若

$$
|g(\mathbf{x}) - g(\mathbf{y})| \leq \omega(\|\mathbf{x} - \mathbf{y}\|), \quad \forall \mathbf{x}, \mathbf{y} \in \Omega
\tag{6}
$$

其中 $\|\cdot\|$ 为欧氏范数，$\omega:\mathbb{R}^+ \to \mathbb{R}^+$ 为**连续、严格单调**且 $\omega(0)=0$ 的函数。

连续性模刻画函数**变化速率的上界**：距离 $\|\mathbf{x}-\mathbf{y}\|$ 越大，$g$ 的取值差不超过 $\omega(\|\mathbf{x}-\mathbf{y}\|)$。论文第 4 节说明如何计算奇异值函数 $\Sigma(\mathbf{x})$、$\sigma(\mathbf{x})$ 的连续性模，并据此界定整个映射的畸变。

### 4.2 从配准点到任意点

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250715203901258.png)

方法核心：界定某点 $\mathbf{x}$ 的畸变随其远离配准点 $\mathbf{z}\in\mathcal{Z}$ 而**至多增加多少**。

对许多实用基函数族 $\mathcal{F}$，给定系数 $\mathbf{c}$ 与域 $\Omega$，可计算模 $\omega = \omega_{\Sigma,\sigma}$，使奇异值函数 $\Sigma(\mathbf{x})$、$\sigma(\mathbf{x})$ 均为 $\omega$-连续。于是可界定奇异值在空间中变化幅度，进而界定畸变。

---

## 5. 全局畸变界：从离散约束到整个域

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250715204858420.png)

设在所有配准点 $\mathbf{z}\in\mathcal{Z}$ 上等距畸变受控：

$$
D_{\text{iso}}(\mathbf{z}) \leq K
$$

等价于

$$
\Sigma(\mathbf{z}) \leq K, \qquad \sigma(\mathbf{z}) \geq \frac{1}{K}
\tag{10}
$$

记 $h = h(\mathcal{Z}, \Omega)$ 为配准点集在 $\Omega$ 中的**填充距离（fill distance）**（点到最近配准点的最大距离），$\omega(h)$ 为相应的连续性模在 $h$ 处的取值。由 Lemma 1，对任意 $\mathbf{x}\in\Omega$：

$$
D_{\text{iso}}(\mathbf{x}) \leq \max\left\{ K + \omega(h),\; \frac{1}{K^{-1} - \omega(h)} \right\}
\tag{11}
$$

（需 $K^{-1} > \omega(h)$。）共形畸变有类似公式。

**含义**：只要在足够密的配准点上满足凸约束（控制 $K$），并由 $\omega$ 与 $h$ 量化光滑基的传播效应，即可得到**全域**畸变上界——这就是"provably good"中 **provably** 的来源。配准点越密（$h$ 越小），$\omega(h)$ 越小，全域界越紧。

---

## 6. 小结

| 概念 | 作用 |
| :--- | :--- |
| 光滑基函数 $\mathcal{F}$ | B-Spline / Gaussian / TPS，保证映射光滑 |
| 配准点 $\mathcal{Z}$ | 施加凸约束的离散采样 |
| 奇异值 $\Sigma, \sigma$ | 局部拉伸，定义 $D_{\text{iso}}, D_{\text{conf}}$ |
| 连续性模 $\omega$ | 界定奇异值随距离的变化 |
| 填充距离 $h$ | 配准点密度 → 全域保证 |

与后续工作的关系：同作者团队的 [Bounded Distortion Harmonic Mappings](https://doi.org/10.1145/2766989)（2015）将类似的全局保证推广到调和映射；[AQP](几何优化-AQP.md)、[SLIM](几何优化-SLIM.md) 等则是 mesh 上大规模优化的不同路线。

---



---

## 参考文献

- Poranne R., Lipman Y. *Provably good planar mappings*. SIGGRAPH 2014.
- Lipman Y. *Bounded distortion harmonic mappings in the plane*. SIGGRAPH 2015.
- Solomon J., et al. *As-Killing-As-Possible vector fields for planar deformation*. SIGGRAPH 2011.
- Sorkine O., Alexa M. *As-rigid-as-possible surface modeling*. SGP 2007.
