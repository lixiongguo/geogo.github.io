---
layout: post
title: "几何变形 — 1.2 补充：Cauchy 重心坐标（Complex Barycentric Coordinates）"
categories: ["Parameterization", "Parameterization-GeometricOptimization"]
mathjax: true
---

Cauchy 重心坐标（Cauchy Barycentric Coordinates）是一种基于复分析的基函数，它为多边形区域上的**调和映射**提供了一组天然的基底。本文将介绍 Cauchy 重心坐标的定义、推导，并着重说明其与调和映射的关系——这也是 BDHM/GLID 方法能够将调和性"硬编码"到表示中的数学基础。

---

## 1. 定义

给定复平面上的一个简单多边形 $\partial\Omega = \{v_0, v_1, \ldots, v_{n-1}\}$（按逆时针排列），对内部任意点 $z \in \Omega$，定义 Cauchy 重心坐标 $C_k(z)$ 如下：

$$
C_k(z) = \frac{1}{2\pi i} \oint_{\partial\Omega} \frac{\zeta - v_k}{\zeta - z} \cdot \frac{d\zeta}{\zeta - v_k}
$$

对于折线多边形，可将围道积分离散化为边上的线段积分。令边向量 $A_j = v_j - v_{j-1}$、$A_j^+ = v_{j+1} - v_j$（索引模 $n$），对每条边解析积分后得到闭合形式：

$$
\boxed{C_k(z) = \frac{1}{2\pi i} \left[ B_{k}^+ \frac{\log(B_k^+ / B_k)}{A_k^+} \;-\; B_{k}^- \frac{\log(B_k / B_k^-)}{A_k} \right]}
$$

其中：
- $B_k = v_k - z$（当前顶点到查询点的向量）
- $B_k^+ = v_{k+1} - z$（下一个顶点到查询点的向量）
- $B_k^- = v_{k-1} - z$（上一个顶点到查询点的向量）
- $A_k^+ = v_{k+1} - v_k$，$A_k = v_k - v_{k-1}$

这正是 `CauchyCoordinates.cpp` 中 `cauchyCoordinatesSingle` 函数的核心公式。

---

## 2. 复导数（一阶与二阶）

为了后续在优化中使用牛顿法，还需要 Cauchy 坐标的复导数。对 $C_k(z)$ 关于 $z$ 求导：

**一阶导数**：

$$
C_k'(z) = \frac{\partial C_k}{\partial z} = \frac{1}{2\pi i} \left[ \frac{\log(B_k / B_k^-)}{A_k} - \frac{\log(B_k^+ / B_k)}{A_k^+} \right]
$$

对应代码中的 `derivativesOfCauchyCoordSingle`，由矩阵 $D \in \mathbb{C}^{N \times n}$ 存储，其中 $D_{ik} = C_k'(z_i)$。

**二阶导数**：

$$
C_k''(z) = \frac{\partial^2 C_k}{\partial z^2} = \frac{1}{2\pi i} \cdot \frac{B_k^+ - B_k^-}{B_k^- \cdot B_k \cdot B_k^+}
$$

对应 `secondDerivativesOfCauchyCoordSingle`，由矩阵 $E \in \mathbb{C}^{N \times n}$ 存储。

---

## 3. 多连通区域的处理

对于带有 $h$ 个孔洞的多连通区域（multiply-connected domain），Cauchy 重心坐标需要以下处理：

### 3.1 丢失自由度

每个孔洞会引入 **2 个冗余自由度**。因此对每个孔洞，需要从基底中移除 2 个系数。代码中通过 `removeTwoCoeffPerHoleFlags` 实现：每个孔洞边界后的前两个顶点对应的基函数被移除。

### 3.2 孔洞中心项

移除冗余基函数后，需要在基底中补充**孔洞中心项**：

$$
C_{\text{hole}}(z) = \log|z - h_j|, \quad j = 1, \ldots, h
$$

其中 $h_j$ 是孔洞内部的一个代表点（通过 `pointInPolygon` 算法计算）。这些项本身也是调和函数（$\Delta \log|z-h_j| = 0$ 在 $z \neq h_j$ 处）。

---

## 4. 与调和映射的核心关系

> 这是 Cauchy 重心坐标最重要的性质：**Cauchy 重心坐标本身是调和函数，因此它们的线性组合自动保持调和性。**

### 4.1 调和映射的复分解

回顾调和映射的一般理论（详见 [BHDM 正文](扭曲有界调和映射.md) 第1.2节），平面区域上的调和映射 $f = u + iv$ 总可分解为全纯部分与反全纯部分的共轭：

$$
f(z) = h(z) + \overline{g(z)}
$$

其中 $h(z)$ 和 $g(z)$ 是 $\Omega$ 上的全纯函数。反之，任意两个全纯函数的这种组合也自动是调和的。

### 4.2 Cauchy 重心坐标作为调和基底

利用 Cauchy 重心坐标，可以将全纯函数 $h$ 和 $g$ 展开为：

$$
h(z) = \sum_{k=0}^{n-1} \phi_k \, \Phi_k(z), \quad g(z) = \sum_{k=0}^{n-1} \psi_k \, \Psi_k(z)
$$

其中 $\Phi_k(z), \Psi_k(z)$ 是由 Cauchy 核构造的基函数。代入调和分解：

$$
\boxed{f(z) = \sum_{k=0}^{n-1} \phi_k \, \Phi_k(z) \;+\; \overline{\sum_{k=0}^{n-1} \psi_k \, \Psi_k(z)}}
$$

### 4.3 矩阵形式：$C \cdot \phi + \overline{C \cdot \psi}$

在代码实现中，这一关系被紧凑地表示为矩阵运算。定义：

- $C \in \mathbb{C}^{N \times n}$ 为 Cauchy 重心坐标矩阵：$C_{ik} = C_k(z_i)$
- $\phi \in \mathbb{C}^n$ 为全纯部分系数（对应"虚拟顶点"位置）
- $\psi \in \mathbb{C}^n$ 为反全纯部分系数

则变形后的位置 $x_i'$ 为：

$$
x_i' = \sum_k C_{ik} \phi_k + \overline{\sum_k C_{ik} \psi_k}
$$

即 `CauchyScene.cpp` 第 87 行：

```cpp
prep_.xp2pDeform = prep_.C * prep_.phi + (prep_.C * prep_.psy).conjugate();
```

### 4.4 复导数：$f_z$ 和 $f_{\bar{z}}$

利用 Cauchy 坐标的导数矩阵 $D$（一阶导）和 $E$（二阶导），可以直接计算调和映射的复导数：

$$
f_z(z_i) = \sum_k D_{ik} \phi_k, \quad f_{\bar{z}}(z_i) = \overline{\sum_k D_{ik} \psi_k}
$$

这对应 `HarmonicMapEnergy.cpp` 第 48-49 行：

```cpp
const VecC fz = D * phi;
const VecC gz = D * psy;
```

### 4.5 调和性自动满足

**关键优势**：由于 Cauchy 重心坐标 $\{C_k(z)\}$ 本身都是调和函数（$\Delta C_k = 0$），无论优化变量 $\{\phi_k, \psi_k\}$ 取何值，$f(z) = C \cdot \phi + \overline{C \cdot \psi}$ 都**自动是调和的**。这被称为"硬编码"调和性——优化器无需将 $\Delta f = 0$ 作为显式约束处理。

---

## 5. 在 BDHM/GLID 中的作用

Cauchy 重心坐标在 BDHM 和 GLID 方法中发挥了关键的"表示"作用：

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Cauchy 坐标  │ ──▶ │  调和映射表示      │ ──▶ │  非线性优化        │
│  C, D, E    │     │  f = Cφ + conj(Cψ)│     │  搜索 φ, ψ       │
└─────────────┘     └──────────────────┘     └──────────────────┘
                            │
                    f_z = D·φ
                    f_̅z = conj(D·ψ)
                            │
                    ┌───────▼────────┐
                    │  边界采样点上    │
                    │  SOC 凸约束     │
                    │  + ARAP 正则项  │
                    └────────────────┘
```

1. **Cauchy 坐标矩阵** $C$ — 将离散系数 $\phi, \psi$ 映射到连续变形 $x'$
2. **导数矩阵** $D$ — 用于计算复导数 $f_z, f_{\bar{z}}$，进而计算扭曲能量和约束
3. **二阶导矩阵** $E$ — 用于牛顿法中的 Hessian 计算和 SPD 凸化

---

## 6. 虚拟顶点（Virtual Vertices）

在实际变形应用中，边界控制顶点 $v_k$ 被偏移到内侧形成"虚拟边界"（`polygonOffset`），虚拟边界上的顶点称为**虚拟顶点**（virtual vertices）。初始时：

$$
\phi_k^{(0)} = v_k^{\text{virt}}, \quad \psi_k^{(0)} = 0
$$

即初始变形为恒等变形（$x_i' = x_i$）。用户通过拖拽虚拟顶点来驱动变形，所有内部网格顶点通过 Cauchy 重心坐标的线性组合自动跟随。

---

## 7. 总结

| 性质 | 说明 |
|------|------|
| **数学定义** | 复围道积分 $\frac{1}{2\pi i} \oint \frac{\zeta - v_k}{\zeta - z} \frac{d\zeta}{\zeta - v_k}$ |
| **调和性** | $\Delta C_k(z) = 0$，天然是调和函数 |
| **线性组合** | $f(z) = C\phi + \overline{C\psi}$ 自动保持调和 |
| **复导数** | $f_z = D\phi,\; f_{\bar{z}} = \overline{D\psi}$ |
| **多连通** | 每孔洞移除 2 个自由度，补充 $\log\|z-h_j\|$ 项 |
| **在 BDHM 中的角色** | 提供调和的基函数空间，将调和性"硬编码"到表示中 |
