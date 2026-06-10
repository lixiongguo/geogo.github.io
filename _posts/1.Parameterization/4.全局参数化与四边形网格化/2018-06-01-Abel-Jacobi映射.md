---
layout: post
category: Parameterization
categories: ["Parameterization", "Parameterization-QuadRemeshing"]
title: "Abel-Jacobi映射"
---

顾险峰老师的计算共形理论将四边形网格化从"工程技巧"提升为可判定的数学问题。将曲面视为**黎曼曲面**，通过复分析工具实现全局参数化。**任何一个四边形网格都可以诱导出一个共形结构（conformal structure）**。具体来说：

- 四边形网格的每个面可以映射为单位正方形 $[0,1] \times [0,1]$，面与面之间的转移函数是平移 + 旋转 $90^\circ$ 的整数倍
- 这种转移函数自然是全纯（复解析）的——因为平移和旋转都是共形变换
- 因此，四边形网格的图册（atlas）本身就是一个共形图册，曲面被赋予了共形结构

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260530062135832.png" alt="image-20260530062135832" style="zoom: 67%;" />

反过来，给定一个共形结构，是否总能找到一个"好"的四边形网格？答案是否定的——这是一个受全局拓扑约束的问题。

##### Poincaré–Hopf 定理（一般形式）

设 $V$ 为曲面 $M$ 上的光滑向量场，$p$ 为孤立奇点，$I(p)$ 为奇点指数（绕奇点一圈向量转过的圈数除以 $2\pi$），则：

$$
\sum_{p \in \text{奇点}} I(p) = \chi(M)
$$

##### 四边形网格的特化

对四边形网格引导场（cross field），价数为 $k$ 的顶点指数为 $I(v) = 1 - k/4$。设价数为 $k$ 的顶点数量为 $n_k$，代入得：

- 奇异点指数之和必须等于曲面的欧拉示性数：

$$
\sum_{k \neq 4} (4 - k) \, n_k = 4\chi(M)
$$

这是 **Poincaré-Hopf 定理** 的直接推论——四边形网格的指数可以定义为 $I(v) = 1 - k/4$。

理想四边形网格在普通 4-价顶点附近曲率为零，曲率集中在 extraordinary vertex 上。若顶点价数为 $n$，局部锥角为
$$
\Theta_v = n \cdot \frac{\pi}{2},  K_v = 2\pi - \Theta_v = \left(4 - n\right)\frac{\pi}{2}.
$$

这正是 Poincaré-Hopf 指数 $I(v) = 1 - n/4$ 的几何含义——奇异点 index 以 $\frac{1}{4}$ 为单位，来自 $2\pi$ 与 $\frac{\pi}{2}$ 对称性的比例关系。

然而Poincaré-Hopf 只是**必要条件**，不是充分条件。从共形结构到四边形网格 需要额外满足 **Abel 约束。



## 除子与Riemann-Roch定理

设亚纯函数 $q$ 在 $p_i$ 处有零点或极点（阶 $n_i$，正为零点、负为极点），除子为：

$$
(q) = \sum_i n_i \, p_i
$$

设 $D$ 是奇异点的除子（divisor），即每个奇异点的"度数"（degree = 4 - 价数）构成一个形式线性组合。四边形网格的存在性等价于：存在一个亚纯二次微分（meromorphic quadratic differential）$\omega$ 使得 $(\omega)$（$\omega$ 的除子）恰好是 $D$。

除子

根据刘维尔定理，在紧黎曼面(封闭，有界的黎曼面)上，**有界全纯函数一定是常函数**，所以要研究紧黎曼面用**亚纯函数(meromorphic)**

对于紧黎曼面 $S$ 上的亚纯函数 $f$，其在各点的零点/极点的加权和称为**主除子（principal divisor）**：

$$
\operatorname{div}(f) = \sum_{p \in S} \operatorname{ord}_p(f) \cdot p
$$

其中 $\operatorname{ord}_p(f)$ 是 $f$ 在点 $p$ 的阶数：
- $\operatorname{ord}_p(f) = k > 0$：$f$ 在 $p$ 处有 $k$ 阶零点
- $\operatorname{ord}_p(f) = -k < 0$：$f$ 在 $p$ 处有 $k$ 阶极点
- $\operatorname{ord}_p(f) = 0$：$f$ 在 $p$ 处正则且非零

展开写为：

$$
\operatorname{div}(f) = \sum_i m_i P_i - \sum_j n_j Q_j
$$

其中 $\{P_i\}$ 是零点、$\{Q_j\}$ 是极点，$m_i,n_j$ 为相应的重数。主除子的总度数恒为零：$\deg(\operatorname{div}(f)) = \sum_p \operatorname{ord}_p(f) = 0$。

#### 奇异点与除子的对应

对四边形网格，价数为 $k$ 的顶点 $v$ 对应除子中的点 $p_v$，其**度数**（degree）为

$$
d_v = 4 - k.
$$

3-价顶点为度 $+1$（零点），5-价顶点为度 $-1$（极点）。除子 $D = \sum_v d_v \cdot p_v$ 记录了所有奇异点的带符号重数。参数化中，同一顶点对应锥角 $k\pi/2$ 的锥奇异点；Gauss-Bonnet 给出

$$
\sum_v K_v = 2\pi\chi(M) \quad \Longleftrightarrow \quad \sum_{k \neq 4} (4-k)\, n_k = 4\chi(M),
$$

两种表述通过整数等值线的拓扑结构完全同构。

### Riemann-Roch

$$
\ell(D) - \ell(K - D) = \deg(D) + 1 - g
$$

其中 $K$ 是典范除子，$g$ 是亏格。这个公式限制了**在给定亏格下能配置多少以及何种奇异点**。




## Abel定理与Abel-Jacobian映射

### 周期矩阵与 Jacobi 簇

设 $\{\zeta_1, \dots, \zeta_g\}$ 为全纯 1-形式的基，定义 $A$ 周期矩阵和 $B$ 周期矩阵：

$$
\mathbf{A}_{ij} = \int_{a_i} \zeta_j,
\mathbf{B}_{ij} = \int_{b_i} \zeta_j, i,j = 1,\dots,g
$$

周期矩阵（Riemann 矩阵）：

$$
\Pi = \mathbf{A}^{-1} \mathbf{B} \in \mathbb{C}^{g \times g}
$$

$\Pi$ 满足 Riemann 双线性关系：对称且 $\operatorname{Im}(\Pi) > 0$（正定）。

格 $\Gamma$ 由列向量生成：

$$
\Gamma = \{\mathbf{A} m + \mathbf{B} n \mid m, n \in \mathbb{Z}^g\}
$$

**Jacobi 簇**：$J(S) = \mathbb{C}^g / \Gamma$ 是 $g$ 维复环面。

四边形网格无缝化要求周期为整数：

$$
\int_{a_i} \zeta_j \in \mathbb{Z} + i\mathbb{Z},
\int_{b_i} \zeta_j \in \mathbb{Z} + i\mathbb{Z}
$$



在 $2g$ 个同调基底 $\{a_1, \ldots, a_g, b_1, \ldots, b_g\}$ 上对 1-form 积分，得到 $2g$ 个周期向量：

$$
\text{Period}(a_i) = \int_{a_i} \omega \in \mathbb{C}^g, \quad
\text{Period}(b_i) = \int_{b_i} \omega \in \mathbb{C}^g
$$

这些周期组成了曲面的**周期矩阵（Period Matrix）**。要让接缝两侧的参数坐标完美拼接，所有周期必须是**整数**（或至少是高斯整数 $\mathbb{Z} + i\mathbb{Z}$）。周期矩阵的整数化是四边形网格化的核心困难——它既是一个优化问题（如 MIQ 的混合整数规划），也有着深刻的复几何解释（周期矩阵的列张成了 $\mathbb{C}^g$ 中的格点 $\Gamma$）。

另外，设 $\{\varphi_1, \cdots, \varphi_g\}$ 为 $\Omega^1$（$\mathbb{C}$ 上全纯微分构成的线性空间）的正规基（canonical basis），满足

$$
\int_{a_i} \varphi_j = \delta_{ij}, \quad i, j = 1, \cdots, g,
$$

其中 $\delta_{ij}$ 为 Kronecker 符号。

对于每一条闭曲线 $\gamma$，沿 $\gamma$ 对各个全纯微分基积分，得到 $\mathbb{C}^g$ 中的向量

$$
\lambda_\gamma = \left(\int_{\gamma} \varphi_1, \cdots, \int_{\gamma} \varphi_g\right).
$$

$\mathbb{C}^g$ 中的 $g$ 维复格点 $\Gamma$ 定义为

$$
\Gamma = \left\{ \sum_{k=1}^g (s_k \lambda_{a_k} + t_k \lambda_{b_k}) : s_k, t_k \in \mathbb{Z} \right\}.
$$

雅可比簇 **Jacobian Variety $J(S)$** 定义在黎曼面 $S$ 上，是紧商空间

$$
J(S) = \mathbb{C}^g / \Gamma.
$$

### Abel–Jacobi 映射

**Abel–Jacobi 映射**是将**几何对象**（点、除子、代数圈）转化为**复环面上的点**的桥梁。以某个固定基点 $p_0 \in S$ 为原点，Abel-Jacobian 映射 $\mu : S \to J(S)$ 定义为：对任意 $p \in S$

$$
\mu(p) = \left( \int_{p_0}^p \varphi_1, \dots, \int_{p_0}^p \varphi_g \right) \pmod \Gamma,
$$

其中积分沿任意路径进行。

对除子 $D = \sum_i d_i p_i$，Abel-Jacobi 映射为

$$
\mu(D) = \sum_i d_i \,\mu(p_i).
$$

亚纯函数除子 $(f)$ 通过 Abel-Jacobian 映射后满足 **Abel-Jacobi 定理**：

$$
\mu((f)) = \sum_{p \in S} \nu_p(f) \mu(p) = 0.
$$

**Abel 定理**（19世纪）给出了一个除子能否成为亚纯函数零极点的充要条件：
$$
\mu(D) \equiv 0 \pmod{\Gamma}
$$

除子 $D$ 在 Abel-Jacobi 映射下的像必须属于 Jacobi 簇的格点 $\Gamma$

### 示例

环面上不存在 5,7-三角化，即不存在恰有两个异常顶点、价数分别为 5 和 7 的三角化。

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260605111848155.png)

证明思路：将 5,7-三角化 $\mathcal{T}$ 的每个面视为欧氏等边三角形，可构造共形结构 $\mathcal{A}$。在面 $f$、边 $e$、顶点 $v$ 上分别取局部坐标 $z_f, z_e, z_v$；对价数为 $k$ 的奇异顶点，局部坐标与等距嵌入 $w_v$ 的关系为

$$
z_v = w_v^{\frac{6}{k}}.
$$

面、边与正则顶点之间的转移映射的旋转分量为 $e^{i \frac{n\pi}{3}}$（$n \in \mathbb{Z}$）的形式。在局部坐标上定义全纯微分

$$
\omega = (dz_f)^6 = (dz_e)^6 = (dz_v)^6.
$$

$\omega$ 全局良定义，但在奇异顶点处需延拓。由上式得

$$
dw_v = \frac{k}{6} (z_v)^{\frac{k-6}{6}} dz_v, 
(dw_v)^6 = \left(\frac{k}{6}\right)^6 (z_v)^{k-6} (dz_v)^6.
$$

因此 $\omega$ 是全局亚纯微分：5-价顶点 $q$ 为 $\omega$ 的极点（阶 $k-6=-1$），7-价顶点 $p$ 为零点（阶 $+1$）。

取典范全纯 1-形式 $\omega_0$（无零极点），定义亚纯函数

$$
f = \frac{\omega}{(\omega_0)^6},  (f) = (\omega) - 6(\omega_0) = p - q.
$$

由 Abel-Jacobi 定理，

$$
\mu((f)) = \mu(p) - \mu(q) = \int_{p_0}^p \omega_0 - \int_{p_0}^q \omega_0 = 0.
$$

这意味着在基本域内 $p$ 与 $q$ 必须重合，与 $p \neq q$ 矛盾。故环面上不存在 5,7-三角化。$\square$

该论证可以推广：对任意亏格，若奇异点除子 $D$ 在主除子意义下不可能（$\mu(D) \not\equiv 0 \pmod{\Gamma}$），则不存在以这些点为奇异点的四边形网格——即使 Poincaré-Hopf 和 Riemann-Roch 的必要条件都已满足。

一个给定拓扑的曲面能否被四边形网格化？能——当且仅当存在一组满足 **Poincaré-Hopf + Abel-Jacobi** 条件的奇异点配置，且这些奇异点对应的亚纯二次微分的所有周期可以同时整数化。