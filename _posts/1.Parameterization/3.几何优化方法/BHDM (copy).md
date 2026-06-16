---
layout: post
title: "有界失真调和映射 (Bounded Distortion Harmonic Maps)"
date:   2018-03-01 00:00:00
categories: Parameterization
---

> 本文整理自 *Bounded Distortion Harmonic Mappings in the Plane*, SIGGRAPH 2015.
> 核心贡献：提出局部单射、有界失真的平面调和/共形映射的数学理论和算法。

---

## 1. 有界失真映射的定义

**定义 (有界失真映射).** 连续可微的平面映射 $$f : \Omega \subset \mathbb{C} \to \mathbb{C}$$ 称为一个 $$(k, \sigma_1, \sigma_2)$$-有界失真映射，如果对 $$\forall z \in \Omega$$：

$$
\begin{aligned}
0 \le k(z) \le k < 1, \quad &\text{(边界共形失真)} \\
\sigma_1(z) \le \sigma_1 < \infty, \quad &\text{(最大伸缩上界)} \\
0 < \sigma_2 \le \sigma_2(z), \quad &\text{(最小伸缩下界)}
\end{aligned}
$$

其中 $$k(z)$$ 是映射的伸缩商 (dilatation)，$$\sigma_1(z),\sigma_2(z)$$ 是 Jacobi 矩阵的奇异值，而 $$k,\sigma_1,\sigma_2$$ 是实数常数。

**观察.** $$(k,\sigma_1,\sigma_2)$$-有界失真映射必然是局部单射且保向的。

> 证明思路：$$\sigma_2(z) > 0$$ 保证 $$|f_z| \neq |f_{\bar z}|$$，再结合 $$k(z) < 1$$ 排除翻转情况，得到 $$|f_z| > |f_{\bar z}|$$。

---

## 2. 调和映射的边界条件 (Theorem 4)

定义中的条件涉及定义域中**每一个点**，而以下定理将其简化为**仅需检查边界**：

**定理4.** 定义在单连通域 $$\Omega$$ 上的复值调和映射 $$f$$ 是 $$(k,\sigma_1,\sigma_2)$$-有界失真的充要条件为：

$$
\begin{aligned}
\oint_{\partial\Omega} \frac{f_z''(z)}{f_z(z)} \, dz &= 0 \\
k(w) \le k < 1, \quad &\forall w \in \partial\Omega \\
\sigma_1(w) \le \sigma_1 < \infty, \quad &\forall w \in \partial\Omega \\
0 < \sigma_2 \le \sigma_2(w), \quad &\forall w \in \partial\Omega
\end{aligned}
$$

**证明核心 (Lemma 5-7):**

- **Lemma 5:** 条件 (5a)+(5b) ⇒ (4a)。$$f_z'' = 0$$ 使第二复伸缩商 $$\nu_f = f_{\bar z} / f_z$$ 为全纯函数，其模 $$k(z) = |\nu_f|$$ 是次调和的，最大值在边界达到。

- **Lemma 6:** 条件 (5c) ⇒ (4b)。$$f_z, f_{\bar z}$$ 全纯，故 $$|f_z|$$ 和 $$|f_{\bar z}|$$ 次调和，$$\sigma_1(z) = |f_z| + |f_{\bar z}|$$ 也次调和。

- **Lemma 7:** 条件 (5a)+(5b)+(5d) ⇒ (4c)。边界上 $$|f_z| > |f_{\bar z}|$$，构造辅助函数 $$\varsigma(z) = \sigma_2 / |f_z(z)| + k(z)$$，利用次调和性将边界的下界传播到全域。

---

## 3. 离散化：Cauchy 复重心坐标

将调和映射表示为 $$f = \Phi + \Psi$$，其中 $$\Phi, \Psi$$ 全纯。使用 **Cauchy 复重心坐标** (Weber et al. 2009) 离散化：

给定边界多边形 (cage) 顶点 $$\{z_1, z_2, \dots, z_n\}$$（逆时针），$$\Phi, \Psi$$ 表示为：

$$
\Phi(z) = \sum_{j=1}^n C_j(z) \, \phi_j, \qquad
\Psi(z) = \sum_{j=1}^n C_j(z) \, \psi_j
$$

其中 $$C_j(z)$$ 是第 $$j$$ 个全纯 Cauchy 重心坐标，$$\phi_j, \psi_j \in \mathbb{C}$$ 为未知复系数。其一阶导数为：

$$
f_z(z) = \Phi'(z) = \sum_{j=1}^n C_j'(z) \phi_j, \qquad
f_{\bar z}(z) = \Psi'(z) = \sum_{j=1}^n C_j'(z) \psi_j
$$

$$C_j(z), C_j'(z), C_j''(z)$$ 均有简洁的闭式表达式。选择任意系数 $$\{\phi_j, \psi_j\}$$ 即自动保证 $$f$$ 调和。

> 技巧：将多边形向外偏移 0.1% 生成 cage $$\hat P$$，避免 Cauchy 坐标在边界上的奇异性。

---

## 4. 凸化与 SOCP 优化

定理4的约束是非凸的。采用 [Lipman 2012] 的凸化方法：

引入辅助函数 $$\theta(w) : \partial\Omega \to \mathbb{R}$$，定义**极大凸子集**来替代非凸约束。

**约束 (5d) 的凸化：**

$$
\text{原约束: } \sigma_2 \le |f_z(w)| - |f_{\bar z}(w)|
$$

$$
\text{凸化: } |f_{\bar z}(w)| \le \operatorname{Re}\left[ f_z(w) e^{i\theta(w)} \right] - \sigma_2
$$

由 $$\operatorname{Re}[f_z e^{i\theta}] \le |f_z|$$ 可知凸约束蕴含原约束。

**约束 (5b) 的凸化：**

$$
\text{原约束: } |f_{\bar z}(w)| \le k \cdot |f_z(w)|
$$

$$
\text{凸化: } |f_{\bar z}(w)| \le k \cdot \operatorname{Re}\left[ f_z(w) e^{i\theta(w)} \right]
$$

**ARAP 能量近似：**

$$E_{\text{ARAP}} = \frac{1}{2} \int (\sigma_1 - 1)^2 + (\sigma_2 - 1)^2 \, da$$

在局部单射保向条件下等价于：

$$E_{\text{ARAP}} = \int (|f_z| - 1)^2 + |f_{\bar z}|^2 \, da$$

凸化近似为二次泛函：

$$\int \left| f_z e^{i\theta} - 1 \right|^2 + |f_{\bar z}|^2 \, da$$

---

## 5. 算法流程

### 5.1 问题形式

给定用户操控点集 $$P = \{r_j \to q_j\}$$，求解 SOCP：

$$
\begin{aligned}
\min_{\phi,\psi} \quad & E_{\text{ARAP}} + \lambda E_{P2P} \\
\text{s.t.} \quad & \psi_1 = 0 \quad (\text{固定常数的自由度}) \\
\forall p \in A_k: \quad & |f_{\bar z}(p)| \le k \cdot \operatorname{Re}\left[ f_z(p) e^{i\theta(p)} \right] \\
\forall p \in A_{\sigma_1}: \quad & |f_z(p)| + |f_{\bar z}(p)| \le \sigma_1 \\
\forall p \in A_{\sigma_2}: \quad & |f_{\bar z}(p)| \le \operatorname{Re}\left[ f_z(p) e^{i\theta(p)} \right] - \sigma_2
\end{aligned}
$$

其中位置约束（软约束）：

$$E_{P2P} = \sum_{j=1}^{|P|} |f(r_j) - q_j|^2$$

ARAP 能量（仅边界采样）：

$$E_{\text{ARAP}} = \frac{1}{|M|} \sum_{j=1}^{|M|} \left( |f_z(p_j)e^{i\theta(p_j)} - 1|^2 + |f_{\bar z}(p_j)|^2 \right)$$

### 5.2 迭代凸优化 + 活跃集策略

1. **初始化** $$\theta = 0$$，活跃集 $$A_k, A_{\sigma_1}, A_{\sigma_2}$$ 为边界全部顶点
2. **求解 SOCP** → 得到映射 $$f$$
3. **全局验证** 失真边界（见 §6）
4. **更新** $$\theta(w) = -\arg \tilde f_z(w)$$（$$\tilde f_z$$ 为当前最优估计）
5. **更新活跃集**：添加违反约束的点；对仍在边界内的点，若局部极值接近阈值（如 $$k(p) > 0.95k$$）也加入；远低于阈值（$$<0.945k$$）则移除
6. 重复 2-5，直至能量收敛（通常 1-3 次迭代）

> 三个独立活跃集 $$A_k, A_{\sigma_1}, A_{\sigma_2}$$ 显著减少了活跃约束总数。

### 5.3 $$\theta$$ 的几何意义

关键在于 $$\operatorname{Re}[f_z e^{i\theta}]$$ 是 $$|f_z|$$ 的近似。当 $$\theta = -\arg f_z$$ 时：

$$e^{i\theta} = \frac{\overline{f_z}}{|f_z|}, \quad \operatorname{Re}[f_z e^{i\theta}] = |f_z|$$

此时凸约束退化为原非凸约束。迭代中 $$\theta$$ 不断逼近真实 $$f_z$$ 的相位，使凸近似越来越紧。

---

## 6. 全局验证

SOCP 仅在有限个采样点强制约束，需验证**全域**失真边界：

- 在稠密采样集 $$B$$ 上评估 $$k(p), \sigma_1(p), \sigma_2(p)$$
- 若满足边界 → 解有效，进入下一轮迭代
- 若违反 → 将违反点加入活跃集，重新求解

---

## 7. 用户交互

采用 **P2P (Point-to-Point)** 操作模式：

- 用户选择少量操控点（可在内部或边界）
- 拖动到目标位置
- 算法实时计算满足有界失真约束的调和映射
- 可调节 $$k, \sigma_1, \sigma_2$$ 参数控制失真程度

---

## 数学附录：Cauchy 重心坐标

**定义.** 对复平面上的多边形 cage $$\{z_1, z_2, \dots, z_n\}$$（逆时针），顶点 $$z_j$$ 的 Cauchy 复重心坐标 $$C_j(z)$$ 定义为 Cauchy 变换的离散形式：

$$C_j(z) = \frac{1}{2\pi i} \int_{\partial\Omega} \frac{\lambda_j(\zeta)}{\zeta - z} \, d\zeta$$

其中 $$\lambda_j$$ 是顶点 $$z_j$$ 的 piecewise linear 基函数。

**性质：**
- $$C_j(z)$$ 在 cage 内部全纯
- 常数精度：$$\sum C_j(z) = 1$$
- 线性精度：$$\sum C_j(z) \cdot z_j = z$$
- 一阶、二阶导数均有闭式表达式
