---
layout: post
title: "Surface Map Homology Inference"
date: 2026-06-17
category: Parameterization
categories: ["Parameterization", "Parameterization-ComputationalConformalGeometry"]
---

## 问题：不完美曲面映射的拓扑歧义

几何处理里常见的曲面映射 $\tilde f : A \to B$ 往往**不是**真正的同胚：可能是稀疏 landmark、functional map、最近点投影、带噪声/离群点的对应，或非单射、非满的区域覆盖。此时映射在几何上"大致对齐"，但**拓扑自由度**并未确定——同一对 genus $g$ 的闭曲面之间，存在 $|\mathrm{Sp}(2g,\mathbb{Z})|$ 种互不等价的同胚类（对 $g=1$ 即为环面的 Dehn twist 族）。

Born、Schmidt、Campen、Kobbelt 在 SGP 2021 / CGF 的论文 [*Surface Map Homology Inference*](https://doi.org/10.1111/cgf.14367) 提出：从这类**不完美输入映射**中，推断一个与某个真实同胚 $f$ 相容的**诱导同调映射** $f_* : H_1(A) \to H_1(B)$。核心保证是：无论输入多差，推断结果都不会在拓扑上退化——它总对应某个同胚所诱导的同调同构。

这与本系列其他拓扑笔记的分工如下：

| 方向 | 代表工作 | 回答的问题 |
| :--- | :--- | :--- |
| **单曲面同调基** | Tree-Cotree、Erickson–Whittlesey | 如何在一张网格上构造 handle / tunnel 环路基 |
| **持续同调** | Dey–Sun | 如何从噪声网格中鲁棒提取 handle / tunnel |
| **映射同调推断** | Born et al. 2021 | 给定两张曲面之间的**粗糙对应**，它们之间的环洞如何配对 |

---

## 背景：$H_1$、$H^1$ 与相交形式

### 同调：环路等价类

在闭可定向曲面 $S$ 上，**圈**（cycle）是嵌入的闭有向曲线；两圈**同调** $c \sim d$ 当且仅当 $c-d$ 是某个子区域的边界。同调类 $[c]$ 构成 Abel 群 $H_1(S)$，对 genus $g$ 曲面 $\mathrm{rank}\,H_1 = 2g$。

**代数相交数** $\omega(c,d)$ 统计两圈横截相交的带符号计数，对同调类不变，因而定义双线性形式 $\omega : H_1 \times H_1 \to \mathbb{Z}$。

选定同调基 $B_S = \{s_1,\ldots,s_{2g}\}$ 后，任意类 $[c] = [B_S h]$ 用整数系数 $h \in \mathbb{Z}^{2g}$ 表示。相交形式的 Gram 矩阵为

$$
\Omega_S \in \mathbb{Z}^{2g \times 2g}, \quad (\Omega_S)_{ij} = \omega(s_i, s_j).
$$

对两个类 $[c]=[B_S h_c]$、$[d]=[B_S h_d]$，

$$
\omega([c],[d]) = h_c^{\mathsf T}\,\Omega_S\, h_d.
$$

### 上同调：闭 1-形式等价类

**上同调群** $H^1(S)$ 由闭 1-形式模恰当 1-形式构成。沿圈积分

$$
\int_{[c]} [x] := \int_c x
$$

在同调类、上同调类上良定义，给出非退化双线性配对 $H_1 \times H^1 \to \mathbb{R}$。若只考虑沿所有圈积分为整数的闭 1-形式，则 $H_1$ 与 $H^1$ 为对偶 $\mathbb{Z}$-模。

对偶上同调基 $B^S = \{s^1,\ldots,s^{2g}\}$ 满足

$$
\int_{s_i} s^j = \delta_{ij}.
$$

离散实现上，Gu–Yau 等方法在网格边上为每个基圈 $s_i$ 解调和闭 1-形式，得到矩阵 $B^S \in \mathbb{R}^{|E| \times 2g}$（详见 `微分形式介绍5-离散1-形式` 与 `2019-05-01-全纯微分1-形式`）。

---

## 同胚诱导的同调 / 上同调映射

真同胚 $f : A \to B$ 将 $A$ 上的圈推前为 $B$ 上的圈，诱导同调同构

$$
f_*([c_A]) = [f(c_A)].
$$

对 1-形式，用拉回 $f^{-1}$（略写为 $f$）定义上同调映射

$$
f^*([x_A]) = [f(x_A)].
$$

在各自同调基 $B_A$、$B_B$ 下，$f_*$ 用整数矩阵 $M \in \mathbb{Z}^{2g \times 2g}$ 表示：$f_*([B_A h_A]) = [B_B\, M h_A]$。

**关键约束**：并非任意整数矩阵都是某个同胚的诱导映射。同胚保持圈的相交数，故 $M$ 必须满足**辛约束**（symplectic constraint）

$$
\boxed{\;\Omega_A = M^{\mathsf T}\,\Omega_B\, M\;}
\tag{8}
$$

当两曲面基具有相同相交图案（$\Omega_A = \Omega_B$）时，这正是 $\mathrm{Sp}(2g,\mathbb{Z})$ 的定义。该条件对同胚诱导映射**必要且充分**（Farkas–Kra、Magnus 等经典结果）。

对偶地，上同调映射用 $\bar M = M^{-\mathsf T}$ 表示，且

$$
\boxed{\;\bar M\,\Omega_A\,\bar M^{\mathsf T} = \Omega_B\;}
\tag{10}
$$

---

## 为何不用局部推前圈？

朴素想法：把 $A$ 上同调基圈 $a_j$ 沿 $\tilde f$ 推到 $B$，再闭合成圈，直接读 $M$ 的列。问题在于：

- 稀疏对应时圈可能**断裂**；
- 噪声 / 离群点使推前路径**偏离**正确同调类；
- 非单射导致**重覆盖**，局部积分"跳变"到错误的类。

局部方法对圈的选择极其敏感。论文改用**全局低频信息**：传输尽可能光滑的闭 1-形式（上同调代表），对插值误差更鲁棒。

---

## 算法概览

输入：genus $g$ 闭曲面三角网格 $A,B$；不完美映射 $\tilde f$（稠密点对应、functional map、稀疏 landmark 等均可）；可选同调基（否则用 Erickson–Whittlesey 自动生成）。

输出：整数矩阵 $M$，表示与某同胚相容的 $f_* : H_1(A) \to H_1(B)$。

```
1. 在 A、B 上各构造 2g 个调和上同调基 1-形式 B^A, B^B（Hodge 理论：每类唯一调和代表）
2. 将闭 1-形式编码为周期标量场 z = exp(2πi φ)（φ 沿边积分 a^j，复场连续且无歧义）
3. 用 f̃ 将 z^j 传到 B（稠密映射直接采样；稀疏对应则最小化拟合项 + 调和正则）
4. 在 B 上解码得到传输后的 1-形式 f̃(B^A)
5. 在辛约束 (10) 下，求整数矩阵 M̄ 使 B^B M̄ ≈ f̃(B^A)（整体最小二乘）
6. 同调矩阵 M = M̄^{-T}
```

**周期编码**的动机：$\tilde f$ 通常不可微，无法直接推前 1-形式；标量场只需逐点取值，functional map、软对应、插值都容易处理。闭性 + 整性保证 $\phi$ 的跳跃为整数，故 $z = e^{2\pi i \phi}$ 在曲面上单值（至多差全局相位）。

**调和代表**：对每个基圈 $a_j$，解

$$
da^j = 0,\quad \Delta a^j = 0,\quad \int_{a_i} a^j = \delta_{ij},
$$

离散化为 Gu–Yau 线性系统，同时解出全部 $a^j$。

---

## 核心优化：辛约束整数二次规划

理想情形下，沿基圈 $b_i$ 积分传输形式应给出

$$
M_{ij} = \int_{b_i} \tilde f(a^j), \quad \text{即 } \bar M = B^B{}^{\mathsf T}\,\tilde f(B^A).
\tag{16}
$$

对高质量稠密映射，(16) 直接成立。但对有缺陷的 $\tilde f$，插值后的 1-形式可能非闭、线性相关或落入错误的类。

**鲁棒形式**：不比较沿圈的积分，而直接比较 1-形式向量本身：

$$
\min_{\bar M \in \mathbb{Z}^{2g \times 2g}} \;\big\| B^B \bar M - \tilde f(B^A) \big\|_F^2
\quad \text{s.t.}\quad \bar M\,\Omega_A\,\bar M^{\mathsf T} = \Omega_B.
\tag{18}
$$

这是带二次等式约束的**整数二次规划**（IQP），变量数 $(2g)^2$，规模 $O(g^2)$，可用 Gurobi 等分支定界求解。辛约束将搜索空间限制在"某同胚所能诱导"的映射上，从全局正则化拓扑。

论文实验表明 (18) 远比基于积分的 (17) 抗噪：平均测地扰动可达包围盒对角线 24% 仍正确；60% 离群点、仅保留 0.5% 样本（12 点）时仍可推断正确同调（genus 1 实验）。

---

## 应用

### 1. 同调意义下的数据迁移

- **调和向量场**：在 cohomology 基下为实系数线性组合，经 $f^*$ 迁移系数，保持绕 handle 的流动一致。
- **方向场 / 十字场**：全局结构由沿基圈的**卷绕数**（turning number）编码，经 $f_*$ 迁移后在目标曲面重建同拓扑行为的场。与四边形网格化、frame field 管线直接相关。

### 2. 相容割图（cut graph）与同胚补全

经典流程：沿相容割图将两曲面各割成圆盘，再在公共域上逐片建立双射。割图的拓扑自由度需先固定。推断的 $f_*$ 可用来构造**拓扑相容**的割图对，进而完成从粗糙对应到真同胚的补全——与 seamless parametrization、compatible remeshing 等方向衔接。

### 3. 从 ad-hoc 输入快速获得拓扑对应

刚性对齐 + 最近点投影即可作为 $\tilde f$：虽不连续、非单射，常足以推断正确 $f_*$。也支持 functional map（$50\times 50$ 系数）、29 个 landmark（genus 4）等极简输入。

### 4. 区分"几何自然匹配"与"输入意图"

图 2 展示：同一对形状的三张稠密映射，黑圈像不同，推断的 $f_*$ 忠实反映**输入映射的拓扑意图**（如人为扭转），而非自动寻找"最自然"的同胚。这对理解 functional map 的拓扑歧义、以及用户标注驱动的对应尤为重要。

---

## 与全局参数化 / 四边形网格化的联系

- **Abel–Jacobi / 全纯 1-形式**（`2019-05-01-全纯微分1-形式`、`2019-06-01-Abel-Jacobi映射`）在**单曲面**上建立周期坐标；本文处理**两曲面之间**周期信息如何经 imperfect map 传输并对齐。
- **混合整数全局参数化**（`2018-01-01-全局参数化-混合整数优化方法`）在割缝图上求整数周期；推断的 $f_*$ 为跨曲面整数周期约束提供正确的同调配对。
- **PGP / QuadCover** 需要一致的 cross field 拓扑；$f_*$ 迁移的 turning number 可保证两曲面 quadrangulation 的相容性。

---

## 实现要点小结

| 模块 | 方法 |
| :--- | :--- |
| 同调基 | Erickson–Whittlesey 贪心算法，或用户给定 |
| 上同调基 | Gu–Yau 离散调和 1-形式 |
| 1-形式 ↔ 标量场 | $z = e^{2\pi i \int a}$，边上用幅角差解码 |
| 稀疏映射插值 | 对应点拟合 + $\|\Delta \tilde z\|^2$ 正则（权重 $\sim 10^{-3}$） |
| 拓扑约束 | $\bar M \Omega_A \bar M^{\mathsf T} = \Omega_B$ |
| 求解 | IQP (18)，$\bar M$ 整数；$M = \bar M^{-\mathsf T}$ |

---

## 参考文献

1. J. Born, P. Schmidt, M. Campen, L. Kobbelt. **Surface Map Homology Inference**. *Computer Graphics Forum* 40(5), Eurographics SGP 2021. [DOI: 10.1111/cgf.14367](https://doi.org/10.1111/cgf.14367)
2. X. Gu, S.-T. Yau. **Global Conformal Surface Parameterization**. SIGGRAPH 2003.（离散调和上同调基）
3. J. Erickson, K. Whittlesey. **Greedy Optimal Homotopy and Homology Generators**. SODA 2005.
4. H. M. Farkas, I. Kra. *Riemann Surfaces* (symplectic matrices ↔ homeomorphisms).
5. 相关笔记：`计算拓扑介绍1-单纯同调`、`计算拓扑介绍2-持续同调`、`treecotree`
