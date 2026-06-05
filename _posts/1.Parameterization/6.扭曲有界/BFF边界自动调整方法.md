---
layout: post
title: "曲面展开-BFF边界优先展开"
categories: [Parameterization, "Parameterization-ConformalMapping"]
---

## 2.5边界自动调整方法 BFF (Boundary First Flattening)



![image-20260529132033157](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260529132033157.png)

### 算法核心洞察

前面介绍的 CETM、Circle Patterns、Ricci 流等方法，都是**同时求解内部和边界**的共形参数化。Sawhney & Crane (2017) 提出了一个截然不同的思路：**先处理边界，再处理内部**——这就是 BFF（Boundary First Flattening）的核心洞察。

![image-20250318173816762](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250318173816762.png)

**关键思想**：共形映射 $f = a + bi$ 是共轭调和映射对。由调和函数的性质，**边界值唯一决定了内部值**。因此我们可以：

1. **先**在边界上确定目标曲率分布（如均匀分布 → 圆形边界）
2. **再**用 Poisson 方程将边界信息传播到内部
3. **最后**通过 Hilbert 变换得到共轭函数

这种方式将耦合的非线性问题解耦为两个线性子问题，既简化了计算，又支持实时交互式编辑。

### 数学基础：Cherrier 方程

Cherrier 方程是带边流形上的 Yamabe 方程，描述了共形因子 $u$ 在内部和边界上分别满足的条件：

$$
\begin{array} { r c l c l }
{ \Delta u } & { = } & { K - e ^ { 2 u } \widetilde { K } } & { \mathrm { on } } & { M } \\[6pt]
{ \frac { \partial u } { \partial n } } & { = } & { \kappa - e ^ { u } \widetilde { \kappa } } & { \mathrm { on } } & { \partial M }
\end{array}
$$

其中：
- $\Delta$ 是 Laplace-Beltrami 算子
- $K, \kappa$ 分别是当前度量的内部高斯曲率和边界测地曲率
- $\widetilde{K}, \widetilde{\kappa}$ 是目标度量的对应曲率
- $u$ 是共形因子，满足 $\widetilde{g} = e^{2u}g$

**对于平坦参数化**（目标度量是欧氏度量）：$\widetilde{K} = 0, \widetilde{\kappa}$ 由用户指定。

![image-20251026164745483](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026164745483.png)

对内部方程(1)进行积分，结合 Gauss-Bonnet 定理：

![image-20251026164937672](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026164937672.png)

其中 $\Omega$ 是离散网格的角盈。

同样对边界方程(2)进行积分：

![image-20251026165025429](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026165025429.png)

其中定义在边界上的 $h$ 称为 **Neumann 值**，它编码了边界曲率信息。

### 共轭对偶

![image-20260529130728969](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260529130728969.png)

### Poincaré-Steklov 算子：边界条件转换

BFF 的核心机制是 **Poincaré-Steklov 算子**——将 Poisson 方程的 Dirichlet 边界条件与 Neumann 边界条件相互转换。BFF 支持两种输入模式：

**模式 1：Curvature 驱动（Neumann → Dirichlet）**

指定目标边界曲率 $\widetilde{\kappa}$，算法自动确定边界形状：

![image-20251026182359225](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026182359225.png)

**模式 2：Position 驱动（Dirichlet → Neumann）**

直接指定目标边界位置 $g$（如映射到单位圆），算法求解内部：

![image-20251026182335699](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026182335699.png)

### Hilbert 变换：从调和函数到共形映射

共形映射 $f = a + bi$ 由一对共轭调和函数组成。给定调和函数 $a$，其共轭 $b$ 满足 Cauchy-Riemann 方程：

$$
\frac{\partial b}{\partial x} = -\frac{\partial a}{\partial y}, \quad \frac{\partial b}{\partial y} = \frac{\partial a}{\partial x}
$$

等价于 $\nabla b = (\nabla a)^\perp$（将 $a$ 的梯度旋转 $90^\circ$）。

![image-20251026182754319](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026182754319.png)

**离散 Hilbert 变换步骤**：
1. 在每个三角面上计算 $\nabla a$（通过重心坐标梯度）
2. 将梯度旋转 $90^\circ$ 得到 $\nabla b$ 的面估计
3. 将面梯度面积加权插值到顶点
4. 对 $\nabla b$ 求散度，解 Poisson 方程 $L \cdot b = \text{div}(\nabla b)$

计算出 Neumann 值 $h$ 后，即可将边界延拓到内部：

![image-20251026182551767](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026182551767.png)

### 算法流程

![image-20250318174618349](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250318174618349.png)

**Curvature 模式完整流程**：

```
1. 计算离散边界曲率 κ_i（每个边界顶点处的转向角缺陷）
2. 设定目标边界曲率 κ̃_i（默认：均匀分布 2π/B → 圆形边界）
3. 计算 Neumann 数据 h_i = κ_i - κ̃_i
4. 解 Poisson 方程 L·a = 0，边界条件 ∂a/∂n = h
5. Hilbert 变换：∇b = (∇a)^⊥ → 解 Poisson 得 b
6. (a, b) 即为共形参数化 UV 坐标
```

**Position 模式流程**：

```
1. 指定目标边界位置 g（如单位圆上的点）
2. 构建边界-内部分块 Laplacian：L_II · a_I = -L_IB · g
3. 分别对 U 和 V 分量求解
4. 拼接得到完整 UV
```

**交互式编辑**：用户可以拖拽边界顶点实时调整参数域形状：

![image-20251026182908277](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026182908277.png)



## Poisson 方程离散化

Poisson 方程 $\Delta a = b$ 是一种椭圆型偏微分方程，自然界中应用广泛（如热扩散）。在三角网格上离散化后转化为稀疏线性系统：

$$
A a = P \phi
$$

其中 $A \in \mathbb{R}^{V \times V}$ 为 **cotan-Laplace 矩阵**：

$$
A_{ij} = -\frac{1}{2}\left(\cot\beta_p^{ij} + \cot\beta_q^{ij}\right),\quad
A_{ii} = -\sum_{ij \in E} A_{ij}
$$

$P$ 是 Mass 矩阵（对角 lumped mass：每个顶点面积 = 相邻面面积的 1/3 之和）。

### 边界条件的分块处理

将网格顶点分为内部点（$I$）与边界点（$B$），对矩阵 $A$ 分块：

**Neumann 边界条件**：

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
\end{bmatrix}
$$

其中 $h$ 是 Neumann 边界数据（编码边界曲率差）。

**Dirichlet 边界条件**（$a_B = g$ 已知）：

$$
A_{II}\, a_I = \phi_I - A_{IB}\, g
$$

消去边界未知量后得到仅关于内部变量的对称正定系统，可直接用 Cholesky 分解求解。

---

> **代码实现**：BFF 算法的完整 C++ 源码、WebAssembly 编译命令、JavaScript 调用接口和复杂度分析已统一归集到 [代码实现汇总](https://lixiongguo.github.io/parameterization/2019/12/01/代码实现汇总/#1-bff-边界优先展开)。
> 
> 在线演示：[https://lixiongguo.github.io/uv-unwrap.html](https://lixiongguo.github.io/uv-unwrap.html)，选择 **"BFF (边界优先展开)"**。

**参考文献**：

- Sawhney, R., & Crane, K. (2017). *Boundary First Flattening.* ACM Transactions on Graphics (SIGGRAPH 2017).
- Bobenko, A.I., Pinkall, U., Springborn, B. (2006). *Discrete conformal maps and ideal hyperbolic polyhedra.*
