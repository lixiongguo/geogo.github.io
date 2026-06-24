## 边界自动调整方法 BFF (Boundary First Flattening)

曲面到平面的共形映射**不是唯一的**，根据RIemannn映射定理，任何平面图形都对应着一个共形映射，那一个自然的问题是能否通过控制平面边界调整共形映射？

CETM、Circle Patterns、Ricci 流等**同时求内部与边界**；BFF（Sawhney & Crane, 2017）**先边界、后内部**。

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260620212253121.png" alt="image-20260620212253121" style="zoom:50%;" />

### 算法核心洞察

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260620211906353.png" alt="image-20260620211906353" style="zoom: 33%;" />

共形映射 $f:M\to\mathbb{C}$ 写为 $f=a+b\mathrm{i}$，其中 $a,b$ 为共轭调和函数对；尺度因子 $e^u=|df|$ 由边界曲率/长度数据控制。

共形映射 $f=a+b\mathrm{i}$ 为共轭调和对；**边界值唯一决定内部**。流程：

1. 在 $\partial M$ 上确定目标曲率/长度；
2. Poisson 方程将边界信息传播到内部；
3. Hilbert 变换得到共轭分量 $b$。

### 数学基础：Cherrier 方程

Cherrier 方程（带边流形上的 Yamabe 方程）描述共形因子 $u$（$\tilde g=e^{2u}g$）：

$$
\begin{aligned}
\Delta u &= K - e^{2u}\widetilde K && \text{on } M,\\
\frac{\partial u}{\partial n} &= \kappa - e^{u}\widetilde\kappa && \text{on } \partial M.
\end{aligned}
$$

$K,\kappa$ 为当前度量曲率；$\widetilde K,\widetilde\kappa$ 为目标度量曲率。平坦参数化取 $\widetilde K=0$，$\widetilde\kappa$ 由用户指定。

共轭调和条件（Cauchy–Riemann）：

$$
J\nabla a=\nabla b,\qquad f=a+b\mathrm{i},\qquad \Delta a=\Delta b=0.
$$

对内部方程积分，结合 Gauss–Bonnet（圆盘 $\chi(M)=1$）：



$$
\int_M \Delta u\,dA=\int_{\partial M}\frac{\partial u}{\partial n}\,ds
=\int_M K\,dA-\int_M e^{2u}\widetilde K\,dA.
$$

$\widetilde K=0$ 时 $\displaystyle\int_{\partial M}\frac{\partial u}{\partial n}=\int_M K\,dA$；又 $\displaystyle\int_M K\,dA+\int_{\partial M}\kappa\,ds=2\pi$，故

$$
\int_{\partial M}\frac{\partial u}{\partial n}\,ds=2\pi-\int_{\partial M}\kappa\,ds=\Omega,
$$

$\Omega$ 为离散**角盈**（内部顶点角度亏损之和）。

对边界方程积分：

$$
\int_{\partial M}\frac{\partial u}{\partial n}\,ds=\int_{\partial M}(\kappa-e^u\widetilde\kappa)\,ds.
$$

离散边界上定义 **Neumann 数据** $h_i$（编码目标曲率差）：

$$
h_i=\kappa_i-\widetilde\kappa_i.
$$

### 共轭对偶

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260529130728969.png)

$$
f=a+b\mathrm{i},\quad J\nabla a=\nabla b,\quad |df|=e^u.
$$

$a$ 由 Poisson 方程（及边界条件）求得；$b$ 由 $\nabla b=(\nabla a)^\perp$ 经 Hilbert 变换恢复。

### Poincaré–Steklov 算子

将 Poisson 方程 $\Delta u=0$ 的 Dirichlet 迹与 Neumann 迹相互转换：

$$
\Lambda_D:\ a|_{\partial M}\mapsto \frac{\partial a}{\partial n}\Big|_{\partial M},\qquad
\Lambda_N:\ \frac{\partial a}{\partial n}\Big|_{\partial M}\mapsto a|_{\partial M}.
$$

**模式 1：Curvature 驱动（Neumann $\to$ Dirichlet）**

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026182359225.png)

给定 $\widetilde\kappa_i$，设 $h_i=\kappa_i-\widetilde\kappa_i$，解

$$
\Delta a=0\ \text{on }M,\qquad \frac{\partial a}{\partial n}=h\ \text{on }\partial M,
$$

得边界 $a|_{\partial M}$，再 Hilbert 求 $b$。

**模式 2：Position 驱动（Dirichlet $\to$ Neumann）**

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026182335699.png)

给定边界位置 $g=a|_{\partial M}$（如单位圆），分块 Laplacian 解内部：

$$
L_{II}\,a_I=-L_{IB}\,g.
$$

### Hilbert 变换

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026182754319.png)

$$
\frac{\partial b}{\partial x}=-\frac{\partial a}{\partial y},\quad
\frac{\partial b}{\partial y}=\frac{\partial a}{\partial x}
\quad\Leftrightarrow\quad \nabla b=(\nabla a)^\perp.
$$

离散步骤：面片上求 $\nabla a$ → 旋转 $90^\circ$ 得 $\nabla b$ → 插值到顶点 → 解 $L b=\mathrm{div}(\nabla b)$。

得到 $h$ 后，将边界延拓到内部：

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026182551767.png)

$$
\begin{bmatrix}L_{II}&L_{IB}\\ L_{IB}^T&L_{BB}\end{bmatrix}
\begin{bmatrix}a_I\\a_B\end{bmatrix}
=
\begin{bmatrix}0\\ h\end{bmatrix}
\quad\text{或}\quad
L_{II}a_I=-L_{IB}g\ (a_B=g).
$$

### 算法流程

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250318174618349.png)

**Curvature 模式**：$\kappa_i\to h_i=\kappa_i-\widetilde\kappa_i\to$ Poisson(Neumann) $\to$ Hilbert $\to (a,b)$。

**Position 模式**：指定 $g\to L_{II}a_I=-L_{IB}g\to (a,b)$。

交互编辑：拖拽边界顶点实时更新 $\widetilde\kappa$ 或 $g$。

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251026182908277.png)

---

## Poisson 方程离散化

$\Delta a=b$ 在三角网格上离散为 $A a=P\phi$，$A$ 为 cotan-Laplace 矩阵：

$$
A_{ij}=-\tfrac12\bigl(\cot\beta_p^{ij}+\cot\beta_q^{ij}\bigr),\quad
A_{ii}=-\sum_{j\sim i}A_{ij}.
$$

$P$ 为 lumped 质量矩阵。**Neumann**：$\phi_B-h$ 在边界行；**Dirichlet**：$a_B=g$ 已知时 $A_{II}a_I=\phi_I-A_{IB}g$。

> **代码实现**：[代码实现汇总](https://lixiongguo.github.io/parameterization/2019/12/01/代码实现汇总/#1-bff-边界优先展开)；在线演示 [uv-unwrap.html](https://lixiongguo.github.io/uv-unwrap.html) 选 **BFF**。

---

## Variational Surface Cut (VSC)

Sharp & Crane, SIGGRAPH 2018：用变分法求切割路径 $\gamma$，使展平后度量扭曲最小（无需显式参数化）。

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010142551440.png)

在曲面上求闭合切割曲线 $\gamma$，切开后的曲面片 $M_\gamma$ 可低扭曲展平。

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010192434507.png)

切割线光滑，可穿过三角形内部（不限于网格边）。

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010174554855.png)

传统组合优化在边上搜索；VSC 在连续曲线上用形状导数优化**展平扭曲**本身。

变形过程中共形因子 $u$ 满足 Yamabe 方程：

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010183229321.png)

$$
\Delta u=-K\ \text{on }M_\gamma,\qquad u=0\ \text{on }\partial M_\gamma.
$$

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010142836409.png)

连续变形 $\gamma(t)$，同时最小化扭曲并抑制切割长度。

用 Dirichlet 能量度量面积扭曲：

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010143206213.png)

$$
E_D(\gamma):=\int_{M_\gamma}|\nabla u|^2\,dA.
$$

仅最小化 $E_D$ 为 ill-posed（延长 $\gamma$ 可无限降扭曲），需约束长度：

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010143507440.png)

$$
E_L(\gamma):=\tfrac12\int_\gamma ds,\qquad
E(\gamma):=E_D(\gamma)+\alpha_L E_L(\gamma).
$$

**Céa 方法**（PDE 约束的形状优化）：

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010145117349.png)

对约束 $\Delta u=-K$、$u|_{\partial M_\gamma}=0$ 构造 Lagrangian，在临界点求形状导数 $D_\sigma E$。

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010192645924.png)

$$
\mathcal{L}=\int_{M_\gamma} j(u)\,dA+\int_{M_\gamma} p(\Delta u+K)\,dA+\int_{\partial M_\gamma}\lambda u\,ds.
$$

Dirichlet 能量下，沿切割法向 $n$ 的梯度流为

$$
\frac{d}{dt}\gamma=-\sigma^*\,n,\qquad
\sigma^*=\Bigl(\frac{\partial u^+}{\partial n}\Bigr)^2-\Bigl(\frac{\partial u^-}{\partial n}\Bigr)^2+\alpha_L\kappa_\gamma,
$$

$u^\pm$ 为 $\gamma$ 两侧尺度因子，$\kappa_\gamma$ 为切割曲线测地曲率。
