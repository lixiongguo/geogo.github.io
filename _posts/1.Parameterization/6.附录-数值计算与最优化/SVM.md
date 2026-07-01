---
layout: post
title: "支持向量机 (SVM) 与凸优化"
category: Parameterization
categories: ["Parameterization", "Parameterization-Appendix"]
mathjax: true
---

支持向量机 (Support Vector Machine, SVM) 是经典的**二分类**线性判别器：在特征空间中寻找**最大间隔 (maximum margin)** 超平面。其训练问题可写为**凸二次规划 (QP)**；通过 **Lagrange 对偶**得到仅含对偶变量 $\alpha_i$ 的有限维问题，稀疏解对应**支持向量**。对偶 QP 常用 **SMO (Sequential Minimal Optimization)** 等坐标下降法求解——每步只优化两个 $\alpha$，子问题有闭式解。

本篇与《凸优化与KKT条件》《QP与SOCP》衔接：SVM 是约束 QP + 对偶理论 + KKT 互补松弛的标准课堂例。

---

## 1. 几何直观

给定训练集 $\{(\boldsymbol{x}_i,y_i)\}_{i=1}^{m}$，$\boldsymbol{x}_i\in\mathbb{R}^n$，标签 $y_i\in\{+1,-1\}$。

**线性可分**时，存在超平面 $\boldsymbol{w}^T\boldsymbol{x}+b=0$ 使 $y_i(\boldsymbol{w}^T\boldsymbol{x}_i+b)>0$。归一化 $\|\boldsymbol{w}\|=1$ 后，样本 $i$ 到超平面的**函数间隔**为 $y_i(\boldsymbol{w}^T\boldsymbol{x}_i+b)$；**几何间隔**为 $y_i(\boldsymbol{w}^T\boldsymbol{x}_i+b)/\|\boldsymbol{w}\|$。

SVM 选择**最大几何间隔**的分离超平面。间隔最大的超平面由**距其最近的若干点**唯一确定——这些点称为**支持向量 (support vectors)**，对应约束在最优处**活跃**。

```
        ●  y=+1
    ●       ○  y=-1
  ●   |   ○
      |←δ→|   最大间隔 δ = 2/‖w‖
    ●   |   ○
        ○
```

---

## 2. 原始问题 (Primal)

### 2.1 硬间隔（线性可分）

要求所有样本正确分类且函数间隔至少为 $1$：

$$
\begin{aligned}
\min_{\boldsymbol{w},\,b}\quad & \frac{1}{2}\|\boldsymbol{w}\|^2 \\
\text{s.t.}\quad & y_i(\boldsymbol{w}^T\boldsymbol{x}_i+b)\ge 1,\quad i=1,\ldots,m.
\end{aligned}
\tag{P-hard}
$$

目标 $\frac{1}{2}\|\boldsymbol{w}\|^2$ 凸；约束对 $(\boldsymbol{w},b)$ **仿射**（$y_i\boldsymbol{w}^T\boldsymbol{x}_i+y_i b\ge 1$）。可行域非空时 (P-hard) 为**严格凸 QP**，最优解唯一。

等价地，最大化几何间隔 $\displaystyle\frac{2}{\|\boldsymbol{w}\|}$ 与最小化 $\|\boldsymbol{w}\|^2$ 同一解（差单调变换）。

### 2.2 为什么需要软间隔？

硬间隔 (P-hard) 隐含一个强假设：**存在**超平面使所有样本满足 $y_i(\boldsymbol{w}^T\boldsymbol{x}_i+b)\ge 1$。实际中这一假设常常不成立，或成立但**不该**被强行满足。软间隔正是为下列情形引入的。

#### （1）线性不可分：硬间隔问题无解

二维例子：绝大多数 $+$ 在左下，$-$ 在右上，但混入一个**异类点**。

```
    ○  y=-1
  ○   ○
    ●  ← 孤立的 y=+1，任何直线都无法同时分开
  ●   ●
●
```

此时 (P-hard) 的约束集**为空**，QP **不可行**——不存在任何 $(\boldsymbol{w},b)$ 满足全部 $m$ 条不等式。优化器无法给出分类器。

软间隔把 $y_i(\boldsymbol{w}^T\boldsymbol{x}_i+b)\ge 1$ 放松为 $y_i(\boldsymbol{w}^T\boldsymbol{x}_i+b)\ge 1-\xi_i$，$\xi_i\ge 0$。取足够大的 $\xi_i$ 总可使约束可行（例如 $\boldsymbol{w}=\boldsymbol{0},b=0,\xi_i=1$），**(P-soft) 恒有可行解**。不可分数据从「无解」变为「在惩罚下求最优折中」。

#### （2）噪声与离群点：硬间隔对异常点过敏

即使数据**近似**可分，标签错误或测量噪声会使少数点远离本类簇。硬间隔要求**每一个**点都在间隔正确一侧，分离超平面会被这些点「拽」向极端位置：

- $\|\boldsymbol{w}\|$ 变大 → 几何间隔变**窄**（在其余点上）；
- 决策边界过度迁就离群点 → **泛化变差**。

软间隔允许对「难以满足」的样本付出 $\xi_i>0$ 的代价，在目标里用 $C\sum_i\xi_i$ 惩罚。等价于告诉模型：**少数违背间隔的样本可以接受，但不要太多、不要太狠**——间隔仍由**多数可靠样本**（支持向量）主导，离群点往往对应 $\alpha_i=C$、$\xi_i>0$，而不是绑架整条边界。

#### （3）$C$ 的含义：间隔宽度 vs 训练误差

(P-soft) 目标

$$
\underbrace{\frac{1}{2}\|\boldsymbol{w}\|^2}_{\text{希望间隔大（}\|\boldsymbol{w}\|\text{ 小）}}
\;+\;
\underbrace{C\sum_{i=1}^{m}\xi_i}_{\text{希望违背间隔的总量小}}.
$$

| $C$ | 行为 |
| :--- | :--- |
| **$C$ 很大** | 强烈惩罚 $\xi_i$ → 逼近硬间隔；间隔窄也要尽量分对每一个点；对噪声敏感 |
| **$C$ 很小** | 允许较多、较大的 $\xi_i$ → 更宽间隔、更多训练误分类/间隔内样本；边界更「平滑」、更抗噪 |
| **$C\to\infty$** | (P-soft) $\to$ (P-hard)（在可行时） |

因此 $C$ 不是随便的超参：它实现 **最大间隔** 与 **拟合训练标签** 之间的显式权衡，类似正则化强度。交叉验证选 $C$ 是标准做法。

#### （4）与 hinge 损失同一逻辑

可证 (P-soft) 等价于**无约束**形式（对 $\boldsymbol{w},b$）：

$$
\min_{\boldsymbol{w},b}\;
\frac{1}{2}\|\boldsymbol{w}\|^2
+ C\sum_{i=1}^{m}
\max\bigl(0,\; 1-y_i(\boldsymbol{w}^T\boldsymbol{x}_i+b)\bigr).
$$

右边求和项即 **hinge loss**：$y_i(\boldsymbol{w}^T\boldsymbol{x}_i+b)\ge 1$ 时损失为 $0$；在间隔内或错分则线性增长。软间隔不是「拍脑袋加松弛」，而是把「允许错分」写进**凸损失**，与最大间隔原则在同一框架里统一。

#### （5）核 SVM 里仍然需要

即使用 RBF 等核把数据映射到高维并**理论上**可分，实践中仍几乎总用软间隔：

- 有限精度、重复样本、标签噪声使「精确可分」无意义；
- 无限维特征下硬间隔可能**过拟合**（间隔在训练集上极大但测试差）；
- 对偶中 $0\le\alpha_i\le C$ 的上界正是软间隔的印记：$\alpha_i=C$ 的样本是「被 $C$ 截断」的难例。

**小结**：硬间隔追求「全体样本、精确、宽间隔」；真实数据往往不可分、有噪声、需控泛化。软间隔用 $\xi_i$ 度量违背程度、用 $C$ 控制惩罚，使问题**恒可行**、**抗离群**、**可调泛化**，并自然导出 hinge 损失与对偶中的 $\alpha_i\le C$。

### 2.3 软间隔原始问题

在 (P-hard) 上引入松弛变量 $\xi_i\ge 0$：

$$
\begin{aligned}
\min_{\boldsymbol{w},\,b,\,\boldsymbol{\xi}}\quad
& \frac{1}{2}\|\boldsymbol{w}\|^2 + C\sum_{i=1}^{m}\xi_i \\
\text{s.t.}\quad
& y_i(\boldsymbol{w}^T\boldsymbol{x}_i+b)\ge 1-\xi_i,\quad i=1,\ldots,m, \\
& \xi_i\ge 0,\quad i=1,\ldots,m.
\end{aligned}
\tag{P-soft}
$$

- $\xi_i=0$：样本在间隔外侧或边界上（正确分类且间隔 $\ge 1$）；
- $0<\xi_i<1$：正确分类但在间隔内；
- $\xi_i\ge 1$：被误分类。

(P-soft) 仍是凸 QP（$m$ 个不等式 + $m$ 个非负约束）。**硬间隔**为 $C\to\infty$ 的极限（在 (P-hard) 可行时）。

### 2.4 判别函数

最优 $(\boldsymbol{w}^*,b^*)$ 给出分类器

$$
f(\boldsymbol{x})=\mathrm{sign}\bigl(\boldsymbol{w}^{*T}\boldsymbol{x}+b^*\bigr).
$$

对偶求解后，$\boldsymbol{w}^*$ 常写为支持向量的线性组合（见 §4）。

---

## 3. Lagrangian 与对偶问题

以下以 **(P-soft)** 为准；(P-hard) 即去掉 $\xi_i$ 与上界 $C$（$\alpha_i\ge 0$ 无上界）。

### 3.1 Lagrangian

对不等式 $1-\xi_i-y_i(\boldsymbol{w}^T\boldsymbol{x}_i+b)\le 0$ 乘子 $\alpha_i\ge 0$；对 $\xi_i\ge 0$ 乘子 $\mu_i\ge 0$：

$$
\begin{aligned}
\mathcal{L}(\boldsymbol{w},b,\boldsymbol{\xi},\boldsymbol{\alpha},\boldsymbol{\mu})
= &\;\frac{1}{2}\|\boldsymbol{w}\|^2 + C\sum_i\xi_i \\
&+ \sum_{i=1}^{m}\alpha_i\bigl(1-\xi_i-y_i(\boldsymbol{w}^T\boldsymbol{x}_i+b)\bigr)
- \sum_{i=1}^{m}\mu_i\xi_i.
\end{aligned}
$$

### 3.2 对偶函数 $\theta$

对 $(\boldsymbol{w},b,\boldsymbol{\xi})$ 取极小（《凸优化与KKT条件》§对偶理论）：

$$
\frac{\partial\mathcal{L}}{\partial\boldsymbol{w}}=\boldsymbol{0}
\;\Rightarrow\;
\boldsymbol{w}=\sum_{i=1}^{m}\alpha_i y_i\boldsymbol{x}_i.
$$

$$
\frac{\partial\mathcal{L}}{\partial b}=0
\;\Rightarrow\;
\sum_{i=1}^{m}\alpha_i y_i=0.
$$

$$
\frac{\partial\mathcal{L}}{\partial\xi_i}=0
\;\Rightarrow\;
C-\alpha_i-\mu_i=0
\;\Rightarrow\;
0\le\alpha_i\le C
\quad(\mu_i=C-\alpha_i\ge 0).
$$

代入 $\mathcal{L}$，交叉项消去，得

$$
\theta(\boldsymbol{\alpha})
= \sum_{i=1}^{m}\alpha_i
- \frac{1}{2}\sum_{i,j=1}^{m}\alpha_i\alpha_j y_i y_j\,\boldsymbol{x}_i^T\boldsymbol{x}_j,
\qquad
\boldsymbol{\alpha}\in\mathbb{R}^m.
$$

**对偶问题** $\max_{\boldsymbol{\alpha}}\theta(\boldsymbol{\alpha})$ 在约束下为

$$
\begin{aligned}
\max_{\boldsymbol{\alpha}}\quad
& \sum_{i=1}^{m}\alpha_i
- \frac{1}{2}\sum_{i,j=1}^{m}\alpha_i\alpha_j y_i y_j\,\boldsymbol{x}_i^T\boldsymbol{x}_j \\
\text{s.t.}\quad
& \sum_{i=1}^{m}\alpha_i y_i = 0, \\
& 0\le\alpha_i\le C,\quad i=1,\ldots,m.
\end{aligned}
\tag{D-soft}
$$

**硬间隔** (P-hard) 对偶：同上，但 $0\le\alpha_i$（无 $C$ 上界）。

| 原始 | 对偶 |
| :--- | :--- |
| $\boldsymbol{w}\in\mathbb{R}^n$，$b\in\mathbb{R}$，$\boldsymbol{\xi}\in\mathbb{R}^m$ | $\boldsymbol{\alpha}\in\mathbb{R}^m$ |
| $m$ 个间隔约束 + $m$ 个 $\xi_i\ge 0$ | 1 个等式 $\sum\alpha_i y_i=0$ + 盒约束 $[0,C]$ |
| 二次目标 + 线性约束 | **纯二次目标** + 线性约束 |

(P-soft) 满足 Slater（例如取 $\boldsymbol{w}=\boldsymbol{0},b=0,\xi_i=1$ 在 $C$ 足够大时），故 **强对偶** $p^*=d^*$，KKT 充要。

### 3.3 KKT 与互补松弛

记 $f_i(\boldsymbol{x})=\boldsymbol{w}^T\boldsymbol{x}+b$。最优时：

| 条件 | 含义 |
| :--- | :--- |
| $\boldsymbol{w}=\sum_i\alpha_i y_i\boldsymbol{x}_i$ | 平稳性 |
| $\sum_i\alpha_i y_i=0$ | 平稳性 |
| $y_i f_i(\boldsymbol{x}_i)\ge 1-\xi_i$，$\xi_i\ge 0$ | 原始可行 |
| $0\le\alpha_i\le C$ | 对偶可行 |
| $\alpha_i(1-\xi_i-y_i f_i(\boldsymbol{x}_i))=0$ | 间隔约束互补 |
| $\mu_i\xi_i=0$，$\mu_i=C-\alpha_i$ | 松弛互补 |

**支持向量**的三种情形（软间隔）：

| $\alpha_i$ | 样本角色 |
| :--- | :--- |
| $\alpha_i=0$ | 非支持向量，约束松弛 |
| $0<\alpha_i<C$ | 在**间隔边界**上，$y_i f_i(\boldsymbol{x}_i)=1$ |
| $\alpha_i=C$ | **边界外**或误分类，$y_i f_i(\boldsymbol{x}_i)\le 1$ |

由 $0<\alpha_i<C$ 的样本可算阈值

$$
b^*=y_i-\boldsymbol{w}^{*T}\boldsymbol{x}_i
\quad\text{（对任一此类 }i\text{ 取平均更稳）}.
$$

---

## 4. 核技巧（简述）

将对偶中的内积 $\boldsymbol{x}_i^T\boldsymbol{x}_j$ 替换为 **核函数** $K(\boldsymbol{x}_i,\boldsymbol{x}_j)=\langle\phi(\boldsymbol{x}_i),\phi(\boldsymbol{x}_j)\rangle$，得到在特征空间 $\phi$ 中的最大间隔超平面，而无需显式构造 $\phi$。常用 $K$：线性、多项式、RBF $K(\boldsymbol{x},\boldsymbol{z})=\exp(-\gamma\|\boldsymbol{x}-\boldsymbol{z}\|^2)$。

对偶 (D-soft) 中 $\boldsymbol{x}_i^T\boldsymbol{x}_j\to K_{ij}$；判别函数

$$
f(\boldsymbol{x})=\mathrm{sign}\!\left(\sum_{i=1}^{m}\alpha_i^* y_i K(\boldsymbol{x}_i,\boldsymbol{x})+b^*\right).
$$

SMO 仅依赖**核矩阵** $\boldsymbol{K}$ 的列/元素，与 §5 相同。

---

## 5. SMO 算法

(D-soft) 是 $m$ 维**盒约束 QP**，Hessian $Q_{ij}=y_i y_j\boldsymbol{x}_i^T\boldsymbol{x}_j$（或 $y_i y_j K_{ij}$）半正定。通用内点法可解，但 $m$ 很大时 $\mathcal{O}(m^3)$ 每步代价高。**SMO**（Platt, 1998）利用结构：每轮只优化 **2 个** $\alpha$，其余固定，子问题有**解析解**，无需通用 QP 求解器。

### 5.1 思想

完整 KKT 要求所有 $\alpha_i$ 同时满足等式 $\sum\alpha_i y_i=0$ 与盒约束。SMO 维护**可行** $\boldsymbol{\alpha}$，每步选一对 $(\alpha_p,\alpha_q)$：

1. 固定其余 $\alpha_i$，在二维子空间上**最大化**对偶目标（等价最小化 $-2\theta$）；
2. 解析更新 $\alpha_p,\alpha_q$ 使仍满足等式与 $[0,C]$；
3. 重复直至 KKT **数值意义下**成立。

每步代价 $\mathcal{O}(m)$（若缓存核列）至 $\mathcal{O}(m^2)$，内存可仅维护活跃核列。

### 5.2 两变量子问题

设当前选 $i,j$，其余 $\alpha_k$ 固定。等式 $\sum_k\alpha_k y_k=0$ 给出

$$
\alpha_i y_i + \alpha_j y_j = \zeta
\;\equiv\;
-\sum_{k\neq i,j}\alpha_k y_k
\quad\Rightarrow\quad
\alpha_i = y_i(\zeta - y_j\alpha_j).
$$

代入对偶目标，化为**单变量** $\alpha_j$ 的二次函数，在 $[L,H]\subseteq[0,C]$ 上求极值（$L,H$ 由 $\alpha_i$ 的盒约束推出）。

记 $Q_{uv}=y_u y_v K(\boldsymbol{x}_u,\boldsymbol{x}_v)$，$E_k=f(\boldsymbol{x}_k)-y_k$ 为**预测误差**（未阈值化）。Platt 的更新（$y_i\neq y_j$ 与 $y_i=y_j$ 分两种）核心为：

**不同类标签** $y_i\neq y_j$：

$$
\alpha_j^{\mathrm{new,unc}}=\alpha_j+\frac{y_j(E_i-E_j)}{Q_{ii}+Q_{jj}-2Q_{ij}},
$$

再 **clip** 到 $[L,H]$ 保证 $\alpha_i^{\mathrm{new}}\in[0,C]$。

**同类标签** $y_i=y_j$：公式类似，$L,H$ 区间不同。

更新后

$$
\alpha_i^{\mathrm{new}}=\alpha_i+y_i y_j(\alpha_j^{\mathrm{old}}-\alpha_j^{\mathrm{new}}).
$$

若 $|\alpha_j^{\mathrm{new}}-\alpha_j^{\mathrm{old}}|<\varepsilon$ 则跳过（进展太小）。

### 5.3 阈值 $b$ 的更新

仅用 $\alpha$ 更新不足以保持 $f(\boldsymbol{x}_k)=y_k$ 对非边界点；SMO 在更新 $\alpha_i,\alpha_j$ 后调整 $b$。记 $E_i,E_j$ 更新前后变化，Platt 给出分段规则：若 $0<\alpha_i^{\mathrm{new}}<C$ 用样本 $i$ 算 $b_1$，若 $0<\alpha_j^{\mathrm{new}}<C$ 用 $b_2$，否则 $b=(b_1+b_2)/2$。

### 5.4 选哪一对 $(i,j)$？（启发式）

| 启发式 | 做法 |
| :--- | :--- |
| **启发式 1** | 外循环：扫 $\alpha_i\in(0,C)$ 且违反 KKT 者；若无则扫全体 |
| **启发式 2** | 给定 $i$，选 $j$ 使 $|E_i-E_j|$ **最大**（期望每步对偶目标增量大） |
| **随机** | 不满足时随机选 $j\neq i$ |

KKT 违反（容忍 $\varepsilon$）示例：$\alpha_i=0$ 且 $E_i>-\varepsilon$；$\alpha_i=C$ 且 $E_i<\varepsilon$；$0<\alpha_i<C$ 且 $|E_i|>\varepsilon$。

### 5.5 算法流程（伪代码）

```
输入: 训练集 {(x_i, y_i)}, C, 核 K, 容差 ε
初始化: α ← 0, b ← 0, 计算 E_i = -y_i
while 存在 KKT 违反 (超过 ε):
    选 i（启发式 1）
    选 j ≠ i（启发式 2）
    保存 α_i^old, α_j^old
    计算 [L, H] 与 α_j^new（clip）
    若 |α_j^new - α_j^old| < ε: continue
    α_i^new ← α_i + y_i y_j (α_j^old - α_j^new)
    更新 b（Platt 规则）
    更新 E_k, k = 1..m（仅依赖 α 变化的两列核）
返回: α, b；预测 sign(Σ α_i y_i K(x_i, x) + b)
```

### 5.6 复杂度与实现要点

| 主题 | 说明 |
| :--- | :--- |
| 每步 | 更新 2 个 $\alpha$，$\mathcal{O}(m)$ 刷新 $E$ |
| 总迭代 | 实践中常 $\mathcal{O}(m)$–$\mathcal{O}(m^{2})$) 量级，无通用多项式上界保证 |
| 核缓存 | 存 $K_{ij}$ 或按列缓存，权衡内存与速度 |
| 与 QP 求解器 | 中小 $m$ 可用 OSQP、ECOS；大规模稀疏 SMO / 坐标下降仍常见 |
| 多类 | 一对一 / 一对多，每类一个二分类 SVM |

---

## 6. 小例（硬间隔）

$\boldsymbol{x}_1=(0,0),y_1=+1$；$\boldsymbol{x}_2=(2,0),y_2=-1$。线性可分，间隔边界为 $x_1=1$。

(P-hard) 一解为 $\boldsymbol{w}^*=(-1,0)^T$，$b^*=1$：$y_1(\boldsymbol{w}^{*T}\boldsymbol{x}_1+b^*)=1$，$y_2(\boldsymbol{w}^{*T}\boldsymbol{x}_2+b^*)=1$，两点均在间隔边界上，均为支持向量。

对偶：$\max\;\alpha_1+\alpha_2-2\alpha_2^2$（$Q_{11}=0,Q_{22}=4,Q_{12}=0$）s.t. $\alpha_1-\alpha_2=0$，$\alpha_i\ge 0$。令 $\alpha_1=\alpha_2=\alpha$ 得 $\max\;2\alpha-2\alpha^2$，最优 $\alpha^*=1/2$，$d^*=1/2=p^*$。还原 $\boldsymbol{w}^*=\sum_i\alpha_i y_i\boldsymbol{x}_i=(-1,0)^T$。

---

## 7. 与其它篇章的关系

| 篇章 | 联系 |
| :--- | :--- |
| 《凸优化与KKT条件》 | Lagrangian、对偶、KKT、互补松弛 |
| 《QP与SOCP》 | (P-soft) 为凸 QP；内点法 / 活动集法可替代 SMO |
| 《线性规划》 | 无约束方向上的对偶间隙、活跃集直觉 |
| MILP | 非凸扩展（特征选择整数）不在本篇 |

---

## 本篇小结

SVM 训练是**凸 QP**：原始 (P-soft) 最小化 $\|\boldsymbol{w}\|^2$ 与松弛惩罚；对偶 (D-soft) 为 $m$ 维二次目标 + 一线性等式 + 盒约束。**强对偶**下支持向量对应 $\alpha_i>0$。**SMO** 每步优化两个 $\alpha$，解析子问题 + KKT 启发式选点，是经典机器学习与凸优化交叉的标准算法。
