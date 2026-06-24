---
layout: post
title: "有界失真映射：从理论到算法（完整版）"
categories: ["Parameterization", "Parameterization-GeometricOptimization"]
---

> 本文整合三篇 SIGGRAPH 核心论文的理论与算法，系统梳理**局部单射 + 有界失真**平面映射的三条技术路线：
> **(0) Lipman 2012** — *Bounded Distortion Mapping Spaces for Triangular Meshes*：三角网格上的凸映射空间（网格路线）；
> **(1) BDHM** — *Bounded Distortion Harmonic Mappings in the Plane* (SIGGRAPH 2015)：单连通域调和子空间 + SOCP 优化；
> **(2) GLID** — *Globally Locally Injective Deformations* (SIGGRAPH Asia 2017)：多连通域 Newton-Eigen 框架。
> 补充 Wirtinger 导数、Cauchy 重心坐标等预备知识，覆盖从理论基础到工程实现的全链路。

---

## 第一部分：数学基础

### 1.1 Wirtinger 导数

将平面点表为复数 $$z = x + iy$$，平面映射表为 $$f(z) = u(x,y) + i v(x,y)$$。其实 Jacobian 矩阵为：

$$
J_f = \begin{pmatrix} u_x & u_y \\ v_x & v_y \end{pmatrix}
$$

复分析中引入 **Wirtinger 导数**（又称 $$\partial$$ / $$\bar\partial$$ 导数），把 $$x,y$$ 方向的偏导组合：

$$
f_z \equiv \frac{\partial f}{\partial z} = \frac{1}{2}(f_x - i f_y),
\qquad
f_{\bar z} \equiv \frac{\partial f}{\partial \bar z} = \frac{1}{2}(f_x + i f_y)
$$

映射在点 $$z$$ 附近的一阶 Taylor 展开为：

$$
f(z+dz) \approx f(z) + f_z(z) \cdot dz + f_{\bar z}(z) \cdot d\bar z
$$

**Wirtinger 导数的几何意义：**

| 导数 | 几何含义 | 简记 |
|------|---------|------|
| $$f_z$$ | **共形部分**：复数乘法 = 旋转 + 一致缩放 | 描述局部相似变换 |
| $$f_{\bar z}$$ | **反共形部分**：偏离共形的拉伸、剪切、翻转 | 描述局部畸变程度 |

若 $$f_{\bar z} = 0$$，则映射简化为 $$df = f_z dz$$（复数乘法），局部无穷小圆仍映射为圆——即**共形映射**（保角）。若 $$f_{\bar z} \neq 0$$，局部无穷小圆变为椭圆，其长短轴（即 Jacobi 矩阵的奇异值）为：

$$
\sigma_1(z) = |f_z(z)| + |f_{\bar z}(z)|, \qquad
\sigma_2(z) = \big| |f_z(z)| - |f_{\bar z}(z)| \big|
$$

Jacobian 行列式可改写为：

$$
\det J_f(z) = |f_z(z)|^2 - |f_{\bar z}(z)|^2 = \sigma_1(z) \cdot \sigma_2(z) \cdot \operatorname{sgn}
$$

因此 $$\det J_f > 0$$ 等价于 $$|f_z| > |f_{\bar z}|$$（局部保向，无翻转）。

**局部共形扭曲**（Beltrami 系数 / Jacobian 条件数）：

$$
K_f(z) = \frac{\sigma_1(z)}{\sigma_2(z)} = \frac{|f_z(z)| + |f_{\bar z}(z)|}{|f_z(z)| - |f_{\bar z}(z)|}
$$

有界扭曲条件 $$K_f(z) \le K$$（$$K \ge 1$$）等价于：

$$
|f_{\bar z}(z)| \le \kappa \cdot |f_z(z)|, \qquad
\kappa = \frac{K-1}{K+1} \in [0,1)
$$

| 边界情况 | $$\kappa$$ | 含义 |
|---------|------------|------|
| $$K = 1$$ | $$\kappa = 0$$ | 共形映射（$$f_{\bar z}=0$$） |
| $$K = 3$$ | $$\kappa = 0.5$$ | 最大拉伸 3× 最小拉伸 |
| $$K \to \infty$$ | $$\kappa \to 1$$ | 允许翻转（$$|f_z| \approx |f_{\bar z}|$$） |

**两个核心约束：**

$$
\begin{aligned}
|f_z(z)| > |f_{\bar z}(z)| \quad &\Longleftrightarrow \; \det J_f > 0 \quad \text{(局部无翻转，保向)} \\
|f_{\bar z}(z)| \le \kappa \cdot |f_z(z)| \quad &\Longleftrightarrow \; K_f(z) \le K \quad \text{(有界扭曲)}
\end{aligned}
$$

> 复分析的视角：第二复伸缩商（second complex dilatation）$$\nu_f = f_{\bar z} / f_z$$。若 $$f$$ 调和，则 $$f_z, f_{\bar z}$$ 为全纯函数，故 $$\nu_f$$ 在全域内**全纯**——其模 $$k(z) = |\nu_f|$$ 是次调和的，最大值在边界达到。

---

### 1.2 Cauchy 重心坐标与调和映射的有限维表示

平面调和映射的标准复分解：任意平面调和函数可写为两个全纯函数的和与共轭差：

$$
f(z) = \Phi(z) + \overline{\Psi(z)}
$$

其中 $$\Phi = h, \Psi = g$$ 均为全纯函数（此即 $$f(z) = h(z) + \overline{g(z)}$$，等价于调和条件 $$\Delta f = 0$$）。

**核心思想**：用有限基函数展开 $$\Phi, \Psi$$，使调和性被"硬编码"进基函数空间——无论系数如何选择，$$f$$ 自动是调和映射。

使用 **Cauchy 复重心坐标** (Weber et al. 2009, BDHM Appendix A)：给定边界多边形 cage 顶点 $$P = \{z_1, z_2, \dots, z_n\}$$（逆时针排列），全纯函数 $$\Phi, \Psi$$ 表示为：

$$
\Phi(z) = \sum_{j=1}^{n} C_j(z) \, \phi_j, \qquad
\Psi(z) = \sum_{j=1}^{n} C_j(z) \, \psi_j
$$

其中 $$C_j(z)$$ 定义为 Cauchy 积分公式应用于 piecewise linear 基函数 $$\lambda_j$$：

$$
C_j(z) = \frac{1}{2\pi i} \int_{\partial\Omega} \frac{\lambda_j(\zeta)}{\zeta - z} \, d\zeta
$$

这里 $$\lambda_j$$ 是 cage 顶点 $$z_j$$ 处的 piecewise linear 帽函数（在 $$z_j$$ 为 1，其余顶点为 0，边界上线性）。

**闭式表达** (BDHM Appendix A)：设 $$z_j$$ 的前后边分别为 $$e_j^- = [z_{j-1}, z_j]$$ 和 $$e_j^+ = [z_j, z_{j+1}]$$（取模 $$n$$），则：

$$
C_j(z) = \frac{1}{2\pi i}\left[
\frac{z_{j+1} - z}{z_{j+1} - z_j} \ln\frac{z_{j+1} - z}{z_j - z}
- \frac{z - z_{j-1}}{z_j - z_{j-1}} \ln\frac{z - z_{j-1}}{z_j - z}
\right]
$$

其一阶和二阶导数分别为：

$$
C_j'(z) = \frac{1}{2\pi i}\left[
\frac{1}{z_{j+1} - z_j} \ln\frac{z_{j+1} - z}{z_j - z}
+ \frac{1}{z_j - z_{j-1}} \ln\frac{z - z_{j-1}}{z_j - z}
\right]
$$

$$
C_j''(z) = \frac{1}{2\pi i}\left[
\frac{1}{(z_{j+1} - z_j)(z_{j+1} - z)} - \frac{1}{(z_{j+1} - z_j)(z_j - z)}
+ \frac{1}{(z_j - z_{j-1})(z - z_{j-1})} - \frac{1}{(z_j - z_{j-1})(z_j - z)}
\right]
$$

**Cauchy 坐标的性质：**

- **全纯性**：$$C_j(z)$$ 在 cage 内部全纯（因为积分核 $$1/(\zeta-z)$$ 全纯）
- **常数精度**：$$\sum_{j=1}^n C_j(z) = 1$$
- **线性精度**：$$\sum_{j=1}^n C_j(z) \cdot z_j = z$$（可精确复现恒等映射）
- **导数闭式**：$$C_j'(z), C_j''(z)$$ 均有简洁的闭式表达式

> **技巧**：将多边形向外偏移约 0.1% 的 cage 边长得到 $$\hat P$$。在实际 cage 内部采样点处评估坐标和导数，避免 $$C_j(z), C_j'(z)$$ 在边界上的奇异性（$$z$$ 无限接近 cage 边时 $$\ln$$ 项发散）。

**矩阵表示：** 在一组采样点 $$\{z_i\}_{i=1}^m$$ 上，定义矩阵 $$C \in \mathbb{C}^{m \times n}$$, $$D \in \mathbb{C}^{m \times n}$$：

$$
C_{ij} = C_j(z_i), \qquad D_{ij} = C_j'(z_i)
$$

则映射值及 Wirtinger 导数可写为矩阵-向量乘积：

$$
f = C \phi + \overline{C \psi}, \qquad
f_z = D \phi, \qquad
f_{\bar z} = \overline{D \psi}
$$

优化变量从函数 $$f$$ 变为 $$2n$$ 个复系数：

$$
\phi, \psi \in \mathbb{C}^n
$$

---

### 1.3 为什么约束可以放在边界上

这个关键洞察来自调和映射的特殊结构：

- $$f_z = \Phi'(z)$$ 是**全纯**函数（因为 $$\Phi$$ 全纯）；
- $$f_{\bar z} = \overline{\Psi'(z)}$$ 是**反全纯**函数；
- 全纯函数的模（如 $$|f_z|, |f_{\bar z}|$$）及其组合 $$k(z) = |f_{\bar z}|/|f_z|$$, $$\sigma_1(z) = |f_z| + |f_{\bar z}|$$ 是**次调和函数**（subharmonic）；
- 次调和函数满足**最大值原理**：最大值必在边界达到 $$\Rightarrow$$ 若边界上 $$\le K$$，则全域 $$\le K$$。

**推论**：要保证全域 $$k(z) \le k$$ 和 $$\sigma_1(z) \le \sigma_1$$，仅需在边界上约束这些量。这就是 Theorem 4（BDHM）/ Theorem 4.2（GLID）的本质。

在实际实现中，在边界上采样足够密的点 $$s_r$$，约束：

$$
|f_{\bar z}(s_r)| \le \kappa |f_z(s_r)|, \qquad
|f_z(s_r)|^2 - |f_{\bar z}(s_r)|^2 \ge \varepsilon
$$

前者保证有界扭曲，后者防止 Jacobian 退化。

---



### 2.4 BDHM 算法流程

#### 采样策略

- **$$M$$**：能量积分采样点（仅边界，通常数百个点）
- **$$A$$**：约束施加采样点（初始 = 边界全部顶点）
- **$$B$$**：验证采样点（稠密，用于全局失真上界评估）

#### SOCP 形式化

给定用户 P2P 操控点集 $$P = \{r_j \to q_j\}$$，求解：

$$
\begin{aligned}
\min_{\phi,\psi} \quad & \frac{1}{|M|} \sum_{p_j \in M} \Big( |f_z(p_j) e^{i\theta(p_j)} - 1|^2 + |f_{\bar z}(p_j)|^2 \Big) \; + \; \lambda \sum_{j=1}^{|P|} |f(r_j) - q_j|^2 \\
\text{s.t.} \quad & \psi_1 = 0 \quad (\text{消除常数自由度}) \\
\forall p \in A_k: \quad & |f_{\bar z}(p)| \le k \cdot \operatorname{Re}[f_z(p) e^{i\theta(p)}] \\
\forall p \in A_{\sigma_1}: \quad & |f_z(p)| + |f_{\bar z}(p)| \le \sigma_1 \\
\forall p \in A_{\sigma_2}: \quad & |f_{\bar z}(p)| \le \operatorname{Re}[f_z(p) e^{i\theta(p)}] - \sigma_2
\end{aligned}
$$

其中 $$f_z = D\phi$$, $$f_{\bar z} = \overline{D\psi}$$，优化变量是复系数向量 $$\phi, \psi \in \mathbb{C}^n$$。

#### 迭代流程

```
输入: cage P̂, 操控点集 P, 用户设 k, σ₁, σ₂
输出: 最优系数 φ, ψ

1. 初始化 θ(w) = 0, 活跃集 A_k = A_σ₁ = A_σ₂ = 边界全部顶点
2. 重复 (通常 1-3 轮):
   a. 求解 SOCP (19) → 得到当前映射 f
   b. 在 B 上评估 k(p), σ₁(p), σ₂(p)
   c. 若全部满足边界 → 解有效，进入下一轮
   d. 否则 → 将违反点加入对应活跃集，重新求解
   e. 更新 θ(w) = -arg f̃_z(w) (f̃_z 为当前最优估计)
   f. 更新活跃集:
      - 添加: k(p) > 0.95k 的局部极大值点; σ₁(p) > 0.945σ₁ 的局部极大值; σ₂(p) < 1.15σ₂ 的局部极小值
      - 移除: k(p) < 0.945k; σ₁(p) < 0.945σ₁; σ₂(p) > 1.2σ₂
3. 返回最终 φ, ψ
```

**三个独立活跃集的设计动机**：实践中很少出现多种约束同时违反的情况。分别为 $$k, \sigma_1, \sigma_2$$ 维护独立活跃集，显著减少了活跃约束的总数。

**θ 的迭代作用**：当 $$\theta = -\arg f_z$$ 时 $$\operatorname{Re}[f_z e^{i\theta}] = |f_z|$$，凸约束退化为原非凸约束。每轮 $$\theta$$ 用上轮最优 $$f_z$$ 的相位更新，使凸近似越来越紧。

#### 共形特例

当 $$K \to 1$$（$$\kappa \to 0$$）时，有界扭曲约束退化为 $$f_{\bar z} = 0$$，即 $$f$$ 为全纯函数，等价于仅保留 $$\phi$$ 系数（$$\psi = 0$$），Cauchy 坐标的共轭部分消失，映射完全是共形的。

---

### 2.5 全局验证与证书

SOCP 仅在有限采样点强制约束。为确保证书（certificate）可靠，BDHM 在稠密采样集 $$B$$ 上评估 $$k, \sigma_1, \sigma_2$$ 的局部极值：

- 若边界上无点违反 ⇒ 由 Theorem 4，全域满足
- 若有点违反 ⇒ 加入活跃集，重新求解并缩小可行域

BDHM 同时需验证 $$f_z$$ 在域内处处非零。由于 $$f_z = \Phi'$$ 全纯，利用 Cauchy 幅角原理：若边界积分恒为零且 $$|f_z| > |f_{\bar z}|$$ 在边界成立，则 $$f_z$$ 全域无零点。

---

### 2.6 Lipschitz 常数与更紧的边界条件

要将 Theorem 4 的无限多边界不等式化为有限个可计算的充分条件，需知道 $$f_z, f_{\bar z}$$ 在边界线段上的 Lipschitz 常数。

**Lipschitz 连续性的加法性质：** 若 $$g, q$$ 分别为 $$L_g, L_q$$-Lipschitz，则线性组合 $$a g + b q$$ 为 $$(|a|L_g + |b|L_q)$$-Lipschitz。

利用式 (9) $$f_z(z) = \sum_{j=1}^n C_j'(z) \phi_j$$，可得初始 Lipschitz 常数：

$$
L_{f_z} = \sum_{j=1}^{n} L_{C_j'} \cdot |\phi_j|, \qquad
L_{f_{\bar z}} = \sum_{j=1}^{n} L_{C_j'} \cdot |\psi_j|
$$

**Proposition 10 (Cauchy 坐标导数的 Lipschitz 常数).** $$C_j'(z)$$ 在域内（除 cage 顶点外）的 Lipschitz 常数为：

$$
L_{C_j'} = \frac{|z_{j+1} - z_{j-1}|}{2\pi \; d(z_{j-1}) \; d(z_j) \; d(z_{j+1})}
$$

其中 $$z_{j-1}, z_{j+1}$$ 是 cage 上与 $$z_j$$ 相邻的顶点，$$d(z_j)$$ 是点 $$z_j$$ 到当前线段 $$[v_1, v_2]$$ 的距离。在预处理阶段，BDHM 预计算一个 $$|B| \times n$$ 的 Lipschitz 常数矩阵（$$|B|$$ 是边界线段数，$$n$$ 是 cage 顶点数），运行时只需乘上动态变化的 $$|\phi_j|, |\psi_j|$$。

**优化：更紧的 Lipschitz 常数。** 利用 Cauchy 坐标的**常数精度**（$$\sum C_j'(z) = 0$$）和**线性精度**（$$\sum C_j'(z) z_j = 1$$），可用 $$\phi_j + b + a z_j$$ 替代 $$\phi_j$$ 来减小 Lipschitz 常数：

$$
f_z(z) = \sum_{j=1}^n C_j'(z)(\phi_j + b + a z_j), \qquad
L_{f_z}^{\text{opt}} = \sum_{j=1}^n L_{C_j'} \cdot |\phi_j + b + a z_j|
$$

其中 $$a, b \in \mathbb{C}$$ 可按需在每个线段上选择。若选择 $$a, b$$ 使 $$\phi_j + b + a z_j = 0$$ 对两个最大的 $$L_{C_j'}$$ 项成立，则这两项贡献为零，大幅降低了 Lipschitz 常数的量级。这让充分条件更紧致，允许更大的 Newton/优化步长。

**BDHM 的实用启发式：** 对每段，找到最大的 $$L_{C_r'}$$ 及其最大邻项 $$L_{C_q'}$$，解线性方程组：

$$
\phi_r + b + a z_r = 0, \qquad \phi_q + b + a z_q = 0
$$

得到 $$a, b$$，代入上式得到更紧的 $$L_{f_z}^{\text{opt}}$$。BDHM 报告此方法在典型模型上（$$n=78$$ cage 顶点、$$|B|=340$$ 个线段）效果显著。

### 2.7 无零点条件的高效验证 (Theorem 11)

除 Lipschitz 边界外，还需验证 $$f_z$$ 全域非零。BDHM 给出一个比数值积分快数个数量级的充分条件。

**Theorem 11.** 设 $$f$$ 是单连通域 $$\Omega$$ 上的复值调和映射，$$\theta(w)$$ 是边界上任意实值连续函数。定义 $$\gamma(w) = \operatorname{Re}[f_z(w) e^{i\theta(w)}]$$。若 $$\gamma(w) > 0$$ 在边界上处处成立，则 $$f_z$$ 在域内无零点。

**实际验证：** 利用 $$\gamma$$ 的 Lipschitz 常数，可以仅在边界样本点上验证。设 $$\theta$$ 为分段线性函数（取值 $$\theta(w_i) = -\arg f_z(w_i)$$），对每个线段 $$[w_{i-1}, w_i]$$（长度 $$l$$），充分条件为：

$$
(2 + |\theta_i - \theta_{i-1}|) \, l \, L_{f_z} < (2 - |\theta_i - \theta_{i-1}|) \, \frac{|f_z(w_{i-1})| + |f_z(w_i)|}{2}
$$

在 BDHM 的实现中，$$\theta$$ 的累积值通过相邻样本间的主值分支差计算（$$\Delta\theta_i = \operatorname{Arg}(f_z(w_i) / f_z(w_{i-1}))$$），避免了 $$\operatorname{arg}$$ 的分支跳跃问题。这可在约 15,000 个边界段上约 25ms 内完成验证。

## 第三部分：BDHM — 单连通域的 SOCP 框架

### 2.1 有界失真映射的定义

**定义 (有界失真映射).** 连续可微的平面映射 $$f : \Omega \subset \mathbb{C} \to \mathbb{C}$$ 称为 $$(k,\sigma_1,\sigma_2)$$-有界失真映射，若对 $$\forall z \in \Omega$$：

$$
0 \le k(z) \le k < 1, \qquad
\sigma_1(z) \le \sigma_1 < \infty, \qquad
0 < \sigma_2 \le \sigma_2(z)
$$

其中 $$k(z) = |f_{\bar z}|/|f_z|$$ 是伸缩商 (dilatation)，$$\sigma_1(z),\sigma_2(z)$$ 是 Jacobi 矩阵的奇异值。$$k,\sigma_1,\sigma_2$$ 为预设的全局常数。

**观察1.** $$(k,\sigma_1,\sigma_2)$$-有界失真映射必然是局部单射且保向的。

> 证明：$$\sigma_2(z) > 0$$ 蕴含 $$\det J_f = \sigma_1\sigma_2 > 0$$，即 Jacobian 处处非零且保向。又 $$\det J_f = |f_z|^2 - |f_{\bar z}|^2 > 0$$，得到 $$|f_z| > |f_{\bar z}|$$。

三个条件各司其职：

| 条件                         | 控制         | 失效后果             |
| ---------------------------- | ------------ | -------------------- |
| $$k(z) \le k$$               | 共形扭曲上限 | 局部角度畸变过大     |
| $$\sigma_1(z) \le \sigma_1$$ | 最大拉伸上限 | 局部面积过度放大     |
| $$\sigma_2 \le \sigma_2(z)$$ | 最小拉伸下限 | 局部塌缩退化（折叠） |

---

### 2.2 边界条件定理—— 从全域到边界

上述定义要求检查域中**每一个点**。以下定理将其简化为**仅需检查边界**：

**定理4 (BDHM).** 定义在单连通域 $$\Omega$$ 上的复值调和映射 $$f$$ 是 $$(k,\sigma_1,\sigma_2)$$-有界失真的充要条件为：

$$
\begin{aligned}
\oint_{\partial\Omega} \frac{f_z''(z)}{f_z(z)} \, dz &= 0  \\
0 \le k(w) \le k < 1, \quad &\forall w \in \partial\Omega  \\
\sigma_1(w) \le \sigma_1 < \infty, \quad &\forall w \in \partial\Omega  \\
0 < \sigma_2 \le \sigma_2(w), \quad &\forall w \in \partial\Omega 
\end{aligned}
$$

**积分为零条件的含义**：由 Cauchy 幅角原理，$$\frac{1}{2\pi i} \oint f_z''/f_z \, dz = N$$ 是 $$f_z$$ 在全域内的零点个数（计重数）。积分 = 0 等价于 $$f_z(z) \neq 0 \; \forall z \in \Omega$$，即共形部分处处非零。

**其余三个条件**是原定义中 $$k \le k < 1$$, $$\sigma_1 \le \sigma_1 < \infty$$, $$0 < \sigma_2 \le \sigma_2$$ 限制到边界上的版本。

**三个 Lemmas 的详细证明思路：**

| Lemma | 从边界条件                                                | 推导全域条件                      | 数学支撑                                                     |
| ----- | --------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------ |
| **5** | 积分为零 + $$k \le k$$ 在边界                             | $$k(z) = |\nu_f| \le k$$ 全域     | 积分为零 ⇒ $$f_z \neq 0$$ ⇒ $$\nu_f = f_{\bar z}/f_z$$ 全纯 ⇒ $$|\nu_f|$$ 次调和 ⇒ 最大值在边界 |
| **6** | $$\sigma_1 \le \sigma_1$$ 在边界                          | $$\sigma_1(z) \le \sigma_1$$ 全域 | $$f_z, f_{\bar z}$$ 全纯 ⇒ $$|f_z|, |f_{\bar z}|$$ 次调和 ⇒ $$\sigma_1 = |f_z|+|f_{\bar z}|$$ 次调和 ⇒ 最大值在边界 |
| **7** | 积分为零 + $$k \le k$$ + $$\sigma_2 \le \sigma_2$$ 在边界 | $$\sigma_2 \le \sigma_2(z)$$ 全域 | 边界上 $$|f_z| > |f_{\bar z}|$$ ⇒ $$\sigma_2 = |f_z|-|f_{\bar z}|$$；构造 $$\varsigma(z) = \sigma_2/|f_z(z)| + k(z)$$；利用 $$k(z)$$ 次调和 + $$1/|f_z|$$ 次调和 ⇒ $$\varsigma$$ 次调和 ⇒ 边界下界传播到全域 |

---

### 2.3 约束凸化——SOCP 的数学基础

定理4中 $$|f_{\bar z}| \le k |f_z|$$ 和 $$\sigma_2 \le |f_z| - |f_{\bar z}|$$ 都是**非凸**的（含变量在分母或非线性项 $$|f_z|$$）。

采用 [Lipman 2012] 的方法：引入辅助函数 $$\theta(w) : \partial\Omega \to \mathbb{R}$$，将非凸约束替换为**极大凸子集**。

**核心不等式：**

对于任意复数 $$w$$，$$\operatorname{Re}[w e^{i\theta}] \le |w|$$（实部不大于模），且当且仅当 $$\theta = -\arg w$$ 时取等号。

因此用 $$\operatorname{Re}[f_z e^{i\theta}]$$ 替代 $$|f_z|$$ 得到凸的（实际上是一个**二阶锥**）约束：

| 原非凸约束                            | 凸化约束                                                     | 锥类型     | 来源   |
| ------------------------------------- | ------------------------------------------------------------ | ---------- | ------ |
| $$\sigma_2 \le |f_z| - |f_{\bar z}|$$ | $$|f_{\bar z}| \le \operatorname{Re}[f_z e^{i\theta}] - \sigma_2$$ | SOC        | 式(12) |
| $$|f_{\bar z}| \le k \cdot |f_z|$$    | $$|f_{\bar z}| \le k \cdot \operatorname{Re}[f_z e^{i\theta}]$$ | SOC        | 式(15) |
| $$|f_z| + |f_{\bar z}| \le \sigma_1$$ | 保持原约束（已凸）                                           | Linear+SOC | 式(10) |

**推导第一个凸约束：**

由 $$\operatorname{Re}[f_z e^{i\theta}] \le |f_z|$$，代入 $$\sigma_2 \le |f_z| - |f_{\bar z}|$$：

$$
|f_{\bar z}| \le |f_z| - \sigma_2 \le \operatorname{Re}[f_z e^{i\theta}] \; \Longleftarrow \text{不成立，方向反了！}
$$

正确推导：目标是用 $$\operatorname{Re}[f_z e^{i\theta}]$$ 替代 $$|f_z|$$ 的下界。原约束重排为 $$|f_{\bar z}| + \sigma_2 \le |f_z|$$，然后应用 $$\operatorname{Re}[f_z e^{i\theta}] \le |f_z|$$：

$$
|f_{\bar z}| + \sigma_2 \le \operatorname{Re}[f_z e^{i\theta}] \quad \Longrightarrow \quad |f_{\bar z}| \le \operatorname{Re}[f_z e^{i\theta}] - \sigma_2
$$

**极大性的含义**：凸化后约束定义的空间是所有满足原非凸约束的**极大凸子集**——没有其他严格更大的凸子集仍满足原约束。这保证了凸近似是"最优"的。

**ARAP 能量的凸近似：**

ARAP 能量定义为 $$E_{\text{ARAP}} = \frac12 \int (\sigma_1-1)^2 + (\sigma_2-1)^2 \, da$$。在局部单射保向条件下可展开为：

$$
E_{\text{ARAP}} = \frac12 \int \big[ (|f_z|+|f_{\bar z}|-1)^2 + (|f_z|-|f_{\bar z}|-1)^2 \big] da
= \int (|f_z|-1)^2 + |f_{\bar z}|^2 \, da
$$

此能量含有非凸项 $$|f_z|$$，凸化近似为二次泛函：

$$
E_{\text{ARAP}}^{\text{convex}} = \int |f_z e^{i\theta} - 1|^2 + |f_{\bar z}|^2 \, da
$$

当 $$\theta = -\arg f_z$$ 时，$$f_z e^{i\theta} = |f_z|$$，凸化能量退化为原 ARAP。
