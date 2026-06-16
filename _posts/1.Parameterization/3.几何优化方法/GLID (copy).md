---
layout: post
title: "全局局部单射变形 (GLID) — 多连通域上的调和映射"
date:   2018-03-08 00:00:00
categories: Parameterization
---

> 本文整理自 *Globally Locally Injective Deformations*, 将 BDHM (有界失真调和映射) 从**单连通域**推广到**多连通域**。
> 核心贡献：(1) 多连通域的调和分解定理 (2) Newton-Eigen 正定 Hessian 修正 (3) 局部单射认证。

---

## 1. 多连通域的调和分解 (Theorem 4.1)

**定理 4.1 (调和分解).** 设 $$\Omega$$ 是多连通平面域，有 $$N$$ 个洞 $$K_1, \dots, K_N$$。在每个洞 $$K_i$$ 内任选一点 $$\rho_i$$，则任意调和映射 $$f : \Omega \to \mathbb{C}$$ 可表示为：

$$
f(z) = \widetilde{\Phi}(z) + \widetilde{\Psi}(z) + \sum_{i=1}^{N} \omega_i \, \ln |z - \rho_i|
$$

其中 $$\widetilde{\Phi}, \widetilde{\Psi} : \Omega \to \mathbb{C}$$ 是全纯函数，$$\omega_i \in \mathbb{C}$$ 为复系数。

> 该分解除了相差一个加法复常数外是唯一的（可设 $$\widetilde{\Psi}(z_0)=0$$）。求和项 $$\sum \omega_i \ln |z-\rho_i|$$ 是**多连通域特有的**——缺少它则表示空间不完备。

---

## 2. 有界失真定理 (Theorem 4.2)

**定理 4.2 (多连通域上的有界失真).** 定义在 $$\Omega$$ 上的平面调和映射 $$f$$，外边界 $$\gamma_0$$ 逆时针、内边界 $$\gamma_1 \dots \gamma_N$$ 顺时针，局部单射且全域满足 $$k \in [0,1)$$, $$\sigma_2 > 0$$, $$\sigma_1 < \infty$$ 的充要条件为：

$$
\oint_{\gamma_0} \frac{f_z'(w)}{f_z(w)} dw + \sum_{i=1}^{N} \oint_{\gamma_i} \frac{f_z'(w)}{f_z(w)} dw = 0 \tag{4a}
$$

$$
0 \le k(w) \le k \quad \forall w \in \partial\Omega \tag{4b}
$$

$$
\sigma_1(w) \le \sigma_1 \quad \forall w \in \partial\Omega \tag{4c}
$$

$$
\sigma_2 \le \sigma_2(w) \quad \forall w \in \partial\Omega \tag{4d}
$$

> 核心洞察：仅需在**边界**上约束失真，全域失真自然有界。与单连通域不同，外边界 $$\gamma_0$$ 的积分可以非零，这允许映射与恒等映射不同伦但仍局部单射。

实际算法不直接设硬上界 $$k,\sigma_1,\sigma_2$$，而是通过能量函数自然形成边界。每次迭代验证两个条件：

$$
|f_z(w)| > |f_{\bar z}(w)| \quad \forall w \in \partial\Omega \tag{5}
$$

---

## 3. 离散化 (Section 5)

对多连通域 polygon cage $$\hat P = \{z_1,\dots,z_m\}$$（外边界逆时针 + 内边界顺时针），全纯函数用 Cauchy 复重心坐标离散：

$$
\widetilde{\Phi}(z) = \sum_{j=1}^{m} \widetilde{C}_j(z) \, \phi_j, \qquad
\widetilde{\Psi}(z) = \sum_{j=1}^{m} \widetilde{C}_j(z) \, \psi_j
$$

其中 $$\widetilde{C}_j(z)$$ 有闭式表达式。多连通域的 Cauchy 坐标存在 $$2N$$ 维复零空间（对应洞的相似变换），需固定每个洞的前两个系数为零。

对数项 $$\sum \omega_i \ln|z-\rho_i|$$ 通过引入 $$2N$$ 个额外变量 $$\phi_j,\psi_j\;(j=m+1,\dots,m+N)$$ 表示：

$$
\sum_{j=m+1}^{m+N} (\phi_j+\psi_j) \, \ln|z - \rho_{j-m}|
$$

令 $$n = m + N$$，合并为统一形式：

$$
f(z) = \sum_{j=1}^{n} C_j(z) \phi_j + \sum_{j=1}^{n} C_j(z) \psi_j, \qquad
C_j(z) = \begin{cases}
\widetilde{C}_j(z), & j=1,\dots,m \\
\ln|z-\rho_{j-m}|, & j=m+1,\dots,n
\end{cases}
$$

Wirtinger 导数（设 $$\phi_j=\psi_j, \forall j=m+1,\dots,n$$）：

$$
f_z(z) = \sum_{j=1}^{n} D_j(z) \phi_j, \qquad
f_{\bar z}(z) = \sum_{j=1}^{n} D_j(z) \psi_j
$$

$$
D_j(z) = \begin{cases}
\widetilde{D}_j(z), & j=1,\dots,m \\
1/(z-\rho_{j-m}), & j=m+1,\dots,n
\end{cases}
$$

> $$D_j(z)$$ 全纯，故 $$f_z, f_{\bar z}$$ 也全纯。该表示共有 $$2n$$ 个复变量 $$\{\phi_j, \psi_j\}_{j=1}^n$$，复零空间维数为 $$4N+N+1$$。

---

## 4. 等距能量 (Section 6)

能量函数 $$E(z) = E(\sigma_1(z), \sigma_2(z))$$ 基于 Jacobi 奇异值，保刚体不变性。常用选择：

| 能量 | 表达式 | 特点 |
|------|--------|------|
| **ARAP** | $$(\sigma_1-1)^2 + (\sigma_2-1)^2$$ | 经典，但 $$\sigma_2\to 0$$ 时有限，不利于局部单射 |
| **对称 Dirichlet** | $$\frac{1}{2}(\sigma_1^2+\sigma_2^2 + \sigma_1^{-2}+\sigma_2^{-2})$$ | $$\sigma_2\to 0$$ 时 → ∞，自然屏障 |
| **Exp Dirichlet** | $$\exp(s \cdot E_{\text{iso}})$$ | 重度惩罚高失真，低平均 vs 低最大失真的权衡 |
| **Advanced MIPS** | 用户控制面积/角度保持平衡 | 灵活调控 |

**关键简化**：利用 $$|f_z|^2, |f_{\bar z}|^2$$ 的二次性：

$$
\frac{\sigma_1^2+\sigma_2^2}{2} = |f_z|^2 + |f_{\bar z}|^2, \qquad
\sigma_1\sigma_2 = |f_z|^2 - |f_{\bar z}|^2
$$

对称 Dirichlet 改写为 $$|f_z|^2, |f_{\bar z}|^2$$ 的光滑函数。

**边界积分**（根据 Theorem 4.2 仅需边界约束）：

$$
E^f = \oint_{\partial\Omega} E(w) \, ds
$$

---

## 5. 梯度与 Hessian 的闭式表达

令 $$D = (D_1,\dots,D_n) \in \mathbb{C}^{1\times n}$$。定义实矩阵：

$$
\mathbf{D} = \begin{bmatrix} \operatorname{Re}(D) & -\operatorname{Im}(D) \\ \operatorname{Im}(D) & \operatorname{Re}(D) \end{bmatrix} \in \mathbb{R}^{2 \times 2n}
$$

单点梯度（$$4n \times 1$$ 实向量）：

$$
\nabla E(z) = 2 \begin{bmatrix} \alpha_1 \mathbf{D}^T \mathbf{f}_z \\ \alpha_2 \mathbf{D}^T \mathbf{f}_{\bar z} \end{bmatrix} \in \mathbb{R}^{4n \times 1}
$$

单点 Hessian（$$4n \times 4n$$ 矩阵）：

$$
\nabla^2 E(z) = \begin{bmatrix} \mathbf{D}^T & 0 \\ 0 & \mathbf{D}^T \end{bmatrix} \; \mathbf{K} \; \begin{bmatrix} \mathbf{D} & 0 \\ 0 & \mathbf{D} \end{bmatrix}
$$

其中 $$\mathbf{K} \in \mathbb{R}^{4 \times 4}$$：

$$
\mathbf{K} = \begin{bmatrix}
2\alpha_1 I + 4\beta_1 \mathbf{f}_z \mathbf{f}_z^T & 4\beta_3 \mathbf{f}_z \mathbf{f}_{\bar z}^T \\
4\beta_3 \mathbf{f}_{\bar z} \mathbf{f}_z^T & 2\alpha_2 I + 4\beta_2 \mathbf{f}_{\bar z} \mathbf{f}_{\bar z}^T
\end{bmatrix}
$$

参数 $$\{\alpha_1,\alpha_2,\beta_1,\beta_2,\beta_3\}$$ 依能量而异（见原文 Table 1）。

### P2P 位置约束

软约束能量：

$$
E_{\text{p2p}}^f = \frac{1}{2} \sum_{i=1}^{|P|} |f(p_i) - q_i|^2
$$

全能量：$$E_{\text{Def}}^f = E^f + \lambda E_{\text{p2p}}^f$$

---

## 6. Newton-Eigen：正定 Hessian 修正 (Section 7)

Hessian $$\nabla^2 E^f$$ 一般不保证正定。核心观察：单点 Hessian 的**最近 Frobenius 范数 PSD 矩阵**可闭式求得。

**关键性质**：
1. $$\nabla^2 E(z)$$ 的非平凡特征向量可表示为 $$\mathbf{B} = [\mathbf{D}\; 0; 0\; \mathbf{D}]$$ 的行与 $$\mathbf{K}$$ 特征向量的乘积
2. $$\mathbf{K}$$ 的特征值与 $$\nabla^2 E(z)$$ 相同（仅差正比例）
3. 问题归约为 $$4\times4$$ 矩阵 $$\mathbf{K}$$ 的解析特征值分解

**$$\mathbf{K}$$ 的 4 个特征值**：

$$
\lambda_1 = 2\alpha_1 \qquad \lambda_2 = 2\alpha_2
$$

$$
\lambda_{3,4} = s_1 \pm \sqrt{s_2^2 + 16\beta_3^2 |f_z|^2 |f_{\bar z}|^2}
$$

其中 $$s_{1,2} = \alpha_1 + 2\beta_1|f_z|^2 \pm (\alpha_2 + 2\beta_2|f_{\bar z}|^2)$$。

**修正**：将负特征值替换为 0，得 $$\nabla^2 E^+(w)$$，则边界积分：

$$
\nabla^2 E^{f+} = \oint_{\partial\Omega} \nabla^2 E^+(w) \, ds
$$

由于 PSD 矩阵的锥结构，积分保证 PSD。对 $$E_{\text{iso}}$$ 只有 $$\lambda_1 = 2\alpha_1$$ 可能为负，修正简化为：

$$
\mathbf{K}^+ = \begin{bmatrix}
\left(\frac{2\alpha_1}{|f_z|^2} + 4\beta_1\right) \mathbf{f}_z \mathbf{f}_z^T & 4\beta_3 \mathbf{f}_z \mathbf{f}_{\bar z}^T \\
4\beta_3 \mathbf{f}_{\bar z} \mathbf{f}_z^T & 2\alpha_2 I + 4\beta_2 \mathbf{f}_{\bar z} \mathbf{f}_{\bar z}^T
\end{bmatrix}
$$

> Newton-Eigen 比标准特征值分解**快得多**，且经大量实验验证所需迭代次数更少。

---

## 7. 局部单射认证 (Section 8)

### 条件 (5) 的有限化

利用 Wirtinger 导数的 Lipschitz 连续性和 **比 BDHM 更紧的 Lipschitz 常数**，将 (5) 转化为有限个不等式：

对每个边界线段 $$[v_i, v_{i+1}]$$（$$l = |v_i - v_{i+1}|$$）：

$$
\sigma_2(v_i) + \sigma_2(v_{i+1}) \ge (L_{f_{\bar z}} + L_{f_z}) \, l \tag{27}
$$

多连通域 Lipschitz 常数（Appendix H）：

$$
L_{f_z} = \frac{|f_z'(v_i)| + |f_z'(v_{i+1})|}{2} + \frac{l}{2}\left( \sum_{j=1}^{m} L_j |s_j - s_{j+1}| + \sum_{j=m+1}^{n} L_j^h |\phi_j| \right)
$$

其中 $$L_j = \frac{1}{2\pi d^2(z_j)}$$, $$L_j^h = \frac{2}{d^3(\rho_{j-m})}$$, $$s_j = \frac{\phi_j - \phi_{j-1}}{z_j - z_{j-1}}$$。

### 条件 (4a) 的等价形式

**定理 8.1.** 设全纯函数 $$g(z)$$ 在长度为 $$l$$ 的开放线段上 L-Lipschitz 连续，满足 $$|g(v_i)| + |g(v_{i+1})| > Ll$$，则：

$$
\int_{v_i}^{v_{i+1}} \frac{g'(z)}{g(z)} dz = \ln\left| \frac{g(v_{i+1})}{g(v_i)} \right| + i \operatorname{Arg} \frac{g(v_{i+1})}{g(v_i)}
$$

**推论 8.2.** 在 (27) 成立前提下，$$f_z$$ 在多连通多边形内无零点的充要条件为：

$$
\sum_{j=0}^{N} \sum_i \operatorname{Arg} \frac{f_z(v_i^{j+1})}{f_z(v_i^j)} = 0 \tag{30}
$$

> 证明：由 Cauchy 幅角原理 + Theorem 8.1，$$\ln|\cdot|$$ 在闭合边界上抵消，仅留幅角和。

**认证流程**：验证 (27) 全部成立 → 计算 (30) → 若为零则**保证全域局部单射**。

---

## 8. 算法总结

| 步骤 | 操作 |
|------|------|
| **预处理** | 构建 cage $$\hat P$$（向外偏移 0.1%），采样边界得点集 $$M$$(能量)、$$B$$(验证) |
| **每次交互** | 用户拖拽 P2P 操控点 → 调用 Newton-Eigen 求解 → 局部单射认证 |
| **认证** | (27) 不等式检查 + (30) 幅角和为零 → 通过则允许步长；否则回溯 |

---

## 附录：主要定理对比

| | BDHM (单连通) | GLID (多连通) |
|---|---|---|
| 调和分解 | $$f = \Phi + \Psi$$ | $$f = \widetilde\Phi + \widetilde\Psi + \sum \omega_i \ln|z-\rho_i|$$ |
| 边界积分 | $$\oint_{\gamma_0} \frac{f_z'}{f_z}dw = 0$$ | $$\oint_{\gamma_0} + \sum\oint_{\gamma_i} = 0$$ |
| 优化方法 | SOCP (凸化) | Newton-Eigen (Hessian PSD 修正) |
| Lipschitz 常数 | — | 更紧的解析公式 |
| 零空间 | $$1$$ 维 | $$4N+N+1$$ 维 |
