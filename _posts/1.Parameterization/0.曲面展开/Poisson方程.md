---
layout: post
title: "数学理论-Poisson方程"
category: Math
---
## Poisson方程

Poisson 方程在自然界中应用广泛，比如热的扩散。其定义为 $\Delta a = b$，Laplace 方程是其中 $b=0$ 的特殊情况，是一种椭圆型偏微分方程，用算法进行数值计算时，将其离散化后可以通过**稀疏线性系统**来进行求解。

Poisson 方程限定了边界后，其边界条件有 **Dirichlet边界条件**与 **Neumann边界条件**。

**Dirichlet 边界条件**
$$
\begin{aligned}
\Delta a &= \phi \quad \text{on } M,\\
a &= g \quad \text{on } \partial M.
\end{aligned}
$$

**Neumann 边界条件**
$$
\begin{aligned}
\Delta a &= \phi \quad \text{on } M,\\
\frac{\partial a}{\partial n} &= h \quad \text{on } \partial M.
\end{aligned}
$$

在三角网格上进行离散化后即转化为如下线性方程组

$$
Aa = P\phi.
$$

其中 $A \in \mathbb{R}^{V \times V}$ 为 **cotan-Laplace 矩阵**。非对角元与对角元常用 cotangent 权表示为

$$
A_{ij} = -\frac{1}{2}\left(\cot\beta_p^{ij} + \cot\beta_q^{ij}\right),
$$

$$
A_{ii} = -\sum_{ij \in E} A_{ij}.
$$

$P$ 是 Mass 矩阵，在展平的场景下可设 $P = E$。

将网格顶点分为内部点与边界点，可对矩阵 $A$ 分块。

对于**Neumann 边界条件**，Poisson 问题可写为分块形式
$$
\begin{bmatrix}
A_{II} & A_{IB} \\
A_{IB}^T & A_{BB}
\end{bmatrix}
\begin{bmatrix}
a_I \\ a_B
\end{bmatrix}
=
\begin{bmatrix}
\phi_I \\ \phi_B - h
\end{bmatrix}.
$$

对于**Dirichlet 边界条件**，有 $a_B = g \in \mathbb{R}^{B}$，消去边界未知量后得到仅关于内部变量的方程

$$
A_{II}\, a_I = \phi_I - A_{IB}\, g.
$$



### 参考资料

经典教材《Numerical Optimization》（Nocedal & Wright）

## **参考文献**

[1] Tutte, W. T. (1963). *How to draw a graph*. Proceedings of the London Mathematical Society.

[2] Floater, M. S. (1997). *Parametrization and smooth approximation of surface triangulations*. CAGD.