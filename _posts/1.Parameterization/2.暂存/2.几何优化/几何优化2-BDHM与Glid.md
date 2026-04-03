类似 Lipman 的方法，但是这里用的是复函数理论的方法来构建扭曲受限空间。

将 2D 平面变形视为一个复映射，那么我们知道调和映射是有比较好的性质那样也就是对应了更好的变形效果，所以本研究的主要目的就是通过数值方法寻找一个这样比较好的映射。

### 1. 复调和映射的基本性质

1）首先一个复调和映射可以分解为一个全纯函数与另一个反全纯函数的和：

$$f(z) = h(z) + \overline{g(z)}$$

![image-20250326191459767](..\..\..\imgs\image-20250326191459767.png)

其中 $h(z)$ 和 $g(z)$ 是 $\Omega$ 上的全纯函数。对应的复导数为：

$$f_z = h'(z), \quad f_{\bar{z}} = \overline{g'(z)}$$

其中 $f_z = \frac{1}{2}\left(\frac{\partial f}{\partial x} - i\frac{\partial f}{\partial y}\right)$，$f_{\bar{z}} = \frac{1}{2}\left(\frac{\partial f}{\partial x} + i\frac{\partial f}{\partial y}\right)$。

#### 1.1.1 Corollary 1

由此得到一个推论 Corollary 1：

![image-20250326191727770](..\..\..\imgs\image-20250326191727770.png)

> **Corollary 1**：若 $f$ 是调和映射，则 $f_z$ 是全纯的，$f_{\bar{z}}$ 是反全纯的。映射 $f$ 是保向的（orientation-preserving）当且仅当 $|f_z| > |f_{\bar{z}}|$。

通过复导数 $f_z$ 与 $f_{\bar{z}}$ 的全纯与反全纯性质来研究 $f$ 的调和性。

#### 1.1.2 f 的 Jacobian 以及奇异值

![image-20250326192504209](..\..\..\imgs\image-20250326192504209.png)

$f$ 的 Jacobian 行列式可以通过复导数表达：

$$J_f = |f_z|^2 - |f_{\bar{z}}|^2$$

![image-20250326192435124](..\..\..\imgs\image-20250326192435124.png)

对应地，$f$ 的 Jacobian 矩阵的两个奇异值为：

$$\sigma_1 = |f_z| + |f_{\bar{z}}|, \quad \sigma_2 = |f_z| - |f_{\bar{z}}|$$

（假设 $|f_z| \geq |f_{\bar{z}}|$，即 $J_f \geq 0$）

#### 1.1.3 f 的 Dilation 的定义，用其来度量 Conformal Distortion

![image-20250326192719066](..\..\..\imgs\image-20250326192719066.png)

Dilation（伸缩比）定义为：

$$K_f(z) = \frac{\sigma_1}{\sigma_2} = \frac{|f_z| + |f_{\bar{z}}|}{|f_z| - |f_{\bar{z}}|}$$

等价地，用 Beltrami 系数 $\mu = f_{\bar{z}} / f_z$ 表示：

$$K_f = \frac{1 + |\mu|}{1 - |\mu|}$$

当 $K_f = 1$ 时，$f$ 是共形映射；$K_f$ 越大，扭曲越严重。

### 1.2 有界扭曲映射（Bounded Distortion Mapping）

我们要求尽可能扭曲小的 2D 变形，可以考虑给扭曲施加一个界 $K$，我们求解可接受 bound 范围内的扭曲。

#### 1.2.1 定义 Bound 映射

![image-20250326192833404](..\..\..\imgs\image-20250326192833404.png)

> **Definition 1**（Bounded Distortion Mapping）：映射 $f: \Omega \to \mathbb{C}$ 称为 $K$-bounded 的，如果满足：
> 1. $f$ 是调和的（$\Delta f = 0$）
> 2. $f$ 是保向的（$J_f > 0$，即 $|f_z| > |f_{\bar{z}}|$）
> 3. Dilation 有界：$K_f(z) \leq K, \; \forall z \in \Omega$

等价地，条件 2 和 3 可以写为：

$$|f_{\bar{z}}| \leq \kappa \, |f_z|, \quad \kappa = \frac{K-1}{K+1} \in [0, 1)$$

容易证明满足上面条件的 $f$ 是单射。

#### 1.2.2 边界值决定映射

对于 Harmonic 映射，边界值全部决定了映射的形态，那么上面 bound 定义可以将考察范围缩小到边界：

![image-20250326193102908](..\..\..\imgs\image-20250326193102908.png)

> **Theorem 2**：若调和映射 $f$ 在边界 $\partial\Omega$ 上满足 $|f_{\bar{z}}| \leq \kappa |f_z|$，则 $f$ 在内部 $\Omega$ 上自动满足同样的约束（由全纯/反全纯函数的最大模原理）。

### 2. 多边形边界的离散化

进一步考察边界（简单曲线）可以用一个简单多边形（Polygon）来进行离散化逼近。

#### 2.1 Cauchy 重心坐标

对于简单多边形，定义 Cauchy 重心坐标：

![image-20250326194001555](..\..\..\imgs\image-20250326194001555.png)

给定多边形 $\partial\Omega = \{v_0, v_1, \ldots, v_{n-1}\}$，Cauchy 重心坐标定义为：

$$w_k(z) = \frac{1}{2\pi i} \oint_{\partial\Omega} \frac{\zeta - v_k}{\zeta - z} \cdot \frac{d\zeta}{\zeta - v_k}$$

对于多边形（折线积分），可以化为：

$$w_k(z) = \frac{1}{2\pi i} \sum_{j=0}^{n-1} \int_{v_j}^{v_{j+1}} \frac{\zeta - v_k}{(\zeta - z)(\zeta - v_k)} \, d\zeta$$

#### 2.2 离散调和映射的分解

那么就可以将调和映射进一步分解：

![image-20250326193741329](..\..\..\imgs\image-20250326193741329.png)

> **Theorem 4**（离散调和映射分解）：对于多边形区域上的调和映射 $f$，存在系数 $\{\phi_k\}_{k=0}^{n-1}$ 和 $\{\psi_k\}_{k=0}^{n-1}$ 使得：

$$f(z) = \sum_{k=0}^{n-1} \phi_k \, \Phi_k(z) + \overline{\sum_{k=0}^{n-1} \psi_k \, \Psi_k(z)}$$

其中 $\Phi_k(z)$ 和 $\Psi_k(z)$ 是与 Cauchy 核相关的基函数。

并且对于复导数有：

![image-20250326194131187](..\..\..\imgs\image-20250326194131187.png)

$$f_z(z) = \sum_{k=0}^{n-1} \phi_k \, \Phi_k'(z), \quad f_{\bar{z}}(z) = \overline{\sum_{k=0}^{n-1} \psi_k \, \Psi_k'(z)}$$

所以现在 $f$ 就完全由 $\phi_k$、$\psi_k$ 系数来表征了。

### 2.3 凸化处理与最优化

为了做求解，需要做凸化处理，并导出最优化形式。

各 constrain 条件的凸化如下，用复导数来表示。

#### 约束 (5d)：正定性约束

![image-20250326194610150](..\..\..\imgs\image-20250326194610150.png)

$$|f_z|^2 - |f_{\bar{z}}|^2 \geq \varepsilon > 0$$

![image-20250326194555045](..\..\..\imgs\image-20250326194555045.png)

对于 5d) 的凸化：

![image-20250326194702236](..\..\..\imgs\image-20250326194702236.png)

用复导数表示为二阶锥约束（SOC）：

![image-20250326194647654](..\..\..\imgs\image-20250326194647654.png)

并进一步限制在二阶凸锥中：

![image-20250326195026284](..\..\..\imgs\image-20250326195026284.png)

$$\left\| \begin{pmatrix} 2\,\text{Re}(f_z) \\ 2\,\text{Im}(f_z) \end{pmatrix} \right\|_2 \leq |f_z|^2 + |f_{\bar{z}}|^2 - \varepsilon$$

#### 约束 (5b)：有界扭曲约束

对于 5b)：

![image-20250326194926784](..\..\..\imgs\image-20250326194926784.png)

$$|f_{\bar{z}}| \leq \kappa \, |f_z|, \quad \kappa = \frac{K-1}{K+1}$$

复导数表示：

![image-20250326194857851](..\..\..\imgs\image-20250326194857851.png)

并限制在二阶凸锥中：

![image-20250326195506007](..\..\..\imgs\image-20250326195506007.png)

$$\left\| \begin{pmatrix} 2\,\text{Re}(f_{\bar{z}}) \\ 2\,\text{Im}(f_{\bar{z}}) \end{pmatrix} \right\|_2 \leq (1-\kappa)|f_z|^2 - (1+\kappa)|f_{\bar{z}}|^2$$

对于非线性**边界条件 5a) 的处理**比较复杂，见原文 6.4 节。

#### 正则项

然后要加入正则项，可以选择 ARAP 能量：

![image-20250326195946561](..\..\..\imgs\image-20250326195946561.png)

$$E_{\text{reg}}(f) = \int_\Omega \left\| \nabla f - R(\nabla f) \right\|_F^2 \, dA$$

其中 $R(\nabla f)$ 是 $\nabla f$ 的最近旋转矩阵。由于这个能量也是非凸的所以做如下凸化，过程参考 Lipman 的文章：

![image-20250326200338839](..\..\..\imgs\image-20250326200338839.png)

$$E_{\text{reg}}^{\text{convex}} = \int_\Omega \left( \|\nabla f\|_F^2 - 2\,\text{tr}(\nabla f \cdot R_0^T) \right) dA$$

其中 $R_0$ 是上一迭代的旋转矩阵（线性化）。

### 2.4 完整优化问题

以及外界输入的约束，终于问题就变成求解如下的**最优化问题**：

![image-20250326200049856](..\..\..\imgs\image-20250326200049856.png)

$$\min_{\{\phi_k, \psi_k\}} \; E_{\text{reg}}(f) + E_{\text{pos}}(f)$$

$$\text{s.t.} \quad |f_{\bar{z}}(z)| \leq \kappa \, |f_z(z)|, \quad \forall z \in \partial\Omega \tag{5b}$$

$$\quad |f_z(z)|^2 - |f_{\bar{z}}(z)|^2 \geq \varepsilon, \quad \forall z \in \partial\Omega \tag{5d}$$

$$\quad f(v_k) = f_k^{\text{target}}, \quad k = 0, \ldots, n-1 \tag{5a}$$

积分形式的能量用求和表达：

![image-20250326200432211](..\..\..\imgs\image-20250326200432211.png)

$$E(f) \approx \sum_{j \in \mathcal{M}} w_j \left\| \nabla f(z_j) - R_j \right\|_F^2$$

### 2.5 Active Set 方法

综合上面凸化的结果，利用 **Active Set** 方法，则可以得到如下表达式（注意这里采样了三个集合 $\mathcal{M}, \mathcal{A}, \mathcal{B}$）：

![image-20250326200819142](..\..\..\imgs\image-20250326200819142.png)

$$\min_{\{\phi_k, \psi_k\}} \; \sum_{j \in \mathcal{M}} w_j \left\| \nabla f(z_j) - R_j \right\|_F^2$$

$$\text{s.t.} \quad |f_{\bar{z}}(z_j)| \leq \kappa \, |f_z(z_j)|, \quad \forall j \in \mathcal{A}$$

$$\quad |f_z(z_j)|^2 - |f_{\bar{z}}(z_j)|^2 \geq \varepsilon, \quad \forall j \in \mathcal{B}$$

其中：
- $\mathcal{M}$：所有采样点集合
- $\mathcal{A} \subset \mathcal{M}$：active set 中有界扭曲约束被激活的点
- $\mathcal{B} \subset \mathcal{M}$：active set 中正定性约束被激活的点

对于 Conformal Mapping 可以更进一步简化：

![image-20250326200901879](..\..\..\imgs\image-20250326200901879.png)

当 $K \to 1$（即 $\kappa \to 0$）时，$|f_{\bar{z}}| = 0$，即 $f$ 是全纯的（共形映射）。此时优化退化为：

$$\min_{\{\phi_k\}} \; \sum_{j \in \mathcal{M}} w_j \, |f_z(z_j)|^2 \quad \text{s.t.} \quad \psi_k = 0, \; \forall k$$

### 3. GLID：基于牛顿法的方法

BDHM 那篇文章是通过求带约束凸优化的方法，而这里（GLID）通过将 Hessian 矩阵凸化，用求解无约束优化问题的牛顿法来做优化。

#### 3.1 Bounded 约束

1）引用 BDHM 中的结果，Bounded 的约束是（这里将从单连通拓展到多连通）：

![image-20250326201834471](..\..\..\imgs\image-20250326201834471.png)

$$|f_{\bar{z}}(z)| \leq \kappa \, |f_z(z)|, \quad \forall z \in \Omega$$

注意这里并不是同 BDHM 的优化方式，而是做牛顿法做全局优化。

#### 3.2 各向同性能量（Isometric Energy）

2）我们优化的能量是各向同性（Isometric Energy）：

![image-20250326202125560](..\..\..\imgs\image-20250326202125560.png)

$$E_{\text{iso}}(f) = \int_\Omega \left( \sigma_1^2 + \sigma_2^2 - 2 \right) dA = \int_\Omega \left( |f_z|^2 + |f_{\bar{z}}|^2 - J_f \right) dA$$

其中利用了 $\sigma_1^2 + \sigma_2^2 = 2(|f_z|^2 + |f_{\bar{z}}|^2)$ 和 $J_f = |f_z|^2 - |f_{\bar{z}}|^2$。

GLID 的核心思想是将此能量的 **Hessian 矩阵进行凸化**（修正负特征值），使其变为凸函数，然后使用牛顿法求解无约束优化问题，在迭代中投影到满足 bounded distortion 约束的可行域。
