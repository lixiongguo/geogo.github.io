---
layout: post
title: "Harmonic Global Parametrization — q-CCM 与 HGP"
categories: ["Parameterization", "Parameterization-GeometricOptimization"]
mathjax: true
---

> **论文**：Alon Bright, Edward Chien, Ofir Weber. [*Harmonic Global Parametrization with Rational Holonomy*](https://doi.org/10.1145/3072959.3073646). ACM Transactions on Graphics (SIGGRAPH), 36(4), 2017.

## 1. 概述

平面映射与变形是图形学核心问题（图像变形、纹理映射、四边形网格化、方向场设计等）。**Harmonic Global Parametrization (HGP)** 对**任意亏格**三角网格，在给定锥点与**有理 holonomy**（$2\pi/q$ 的整数倍）下，同时追求：

- **局部单射 (local injectivity)**：无 fold-over；
- **无缝 (seamless)**：cone metric 沿 seam 两侧差旋转；
- **可计算**：通常 1–2 次 SOCP，Myles et al. 2014 benchmark 上鲁棒性高。

理论核心是 **$q$-CCM**（$q$-**convex combination maps**，$q$-凸组合映射）——注意英文是 **combination** 而非 combinatorial。关键策略：

1. 在切开曲面 $S_c$ 上求**线性** $q$-CCM（调和 + seam 旋转）；
2. 用 **$q$-fold 分支覆盖** $\tilde{S}_q$ 上的 **index counting** 证明 Theorem 6.1（**不是**「先在覆盖空间做 Tutte 嵌入再投影」的构造算法）。

加速实现见 [FastHGP](扭曲有界-全局调和参数化2-FastHGP.md)。

| 前驱 | 局限 | HGP |
| :--- | :--- | :--- |
| Tutte / Floater CCM | 圆盘、凸边界 | 切开 + 有理 holonomy |
| Gortler et al. 2006 | 圆盘/环面 index 定理 | 任意拓扑 + 锥点 |
| Tong et al. 2006 | 多 patch，$\pi/2$ holonomy | 单 patch $S_c$，$2\pi/q$ 倍数 |

**$q$-CCM**（$q$-**convex combination maps**）是对经典 **Tutte 参数化**与 **Gortler 凸组合 / index counting** 的推广：$q$ 约束角度为 $2\pi/q$ 的有理倍数；四边形网格化取 $q=4$。直接求带锥角与 seam 旋转的 $q$-CCM 是**线性**问题；**局部单射性**则通过 **$q$-fold 分支覆盖** $\tilde{S}_q$ 上的 **mostly harmonic 1-form** 与 **index counting**（Theorem 6.1）证明——覆盖用于**证明**，HGP 算法在切开曲面 $S_c$ 上求解，**不必**显式构造 $\tilde{S}_q$。

---

## 2. $q$-CCM：定义、几何直觉与 Tutte 退化

### 2.1 正式定义（线性系统）

给定带锥点的曲面 $S$ 与 $q\in\mathbb{Z}^+$，沿 seam graph $G_s$ 切开得 $S_c$。**$q$-CCM** 是下列系统在 $S_c$ 上关于 $z_i=f(v_i)\in\mathbb{C}$ 的解：

- **(6)** seam 边旋转（§4）；
- **(7)** 非 seam 顶点正权调和；
- **(14)** seam 非锥顶点旋转调和（(8) 为 degree-2 特例）。

这是 BCW17 的**正式定义**。$q$-CCM 空间为仿射子空间（$w_{ij}>0$ 固定，$r_{ij}$ 由 holonomy 给定）。

### 2.2 几何直觉（等价表述，非独立定义）

下列四条件帮助理解 $q$-CCM 解的**几何含义**；它们由线性系统 + 正确诱导度量共同实现，不应与 (6)(7)(14) 并列当作「当且仅当」定义。

**（i）凸组合性**（非 seam 内部顶点）：存在 $w_{ij}>0$，

$$
f(v_i) = \sum_{v_j \in N(v_i)} w_{ij}\, f(v_j),
$$

即像点位于邻居像的凸包内——对应 (7)。

**（ii）锥角约束**：锥点 $v_c$ 处总角

$$
\Theta_{v_c} = \frac{2\pi k_c}{q}, \quad k_c \in \mathbb{Z}.
$$

**（iii）边界转角**（若有边界）：边界分量 $B_j$ 的 turning angle 为 $2\pi l_j/q$。

**（iv）Seam 旋转**：对 seam 边 $e_{ij}$（端点 $v_i^a,v_j^a$ 与 $v_i^b,v_j^b$），

$$
z_j^a - z_i^a = e^{i\frac{2\pi r_{ij}}{q}}\,(z_j^b - z_i^b), \quad r_{ij} \in \{0,\ldots,q-1\}.
\tag{6}
$$

> **与旧笔记的修正**：$q$ **不是**「每个角都等于 $2\pi/q$」，而是有理角的**分母**；$k_c,l_j,r_{ij}$ 各自为整数指标。

### 2.3 与 Tutte 参数化的关系

- **$q=1$**、无锥、圆盘：退化为 **Tutte 嵌入**（内部正权凸组合，边界固定凸多边形）；
- **$q=2$**：holonomy 为 $\pi$ 的倍数；与某些共形/双倍覆盖构造相关，但不宜简单说「等价于全纯微分」；
- **$q=4$**：经典四边形无缝（holonomy $\equiv 0 \pmod{\pi/2}$，cross field 的 $4$-fold 对称）；
- **$q=6$**：hexagonal seamless（论文 Fig.2：球面 3 锥、锥角 $2\pi/3$），**不是**泛泛的「等边三角网格化」。

### 2.4 CCM 在切开圆盘上的推广

**$q$-CCM** 可看作 Floater **CCM** 在**切开圆盘** $S_c$ 上的推广：内部仍为正权凸组合（(7)），但 seam 上通过 (6) 的 $q$-fold 旋转实现有理 holonomy，从而处理多边界与任意亏格（经锥点吸收拓扑）。

**与 HGP 的关系**：HGP 在切开曲面 $S_c$ 上求 $z=u+iv$，**软**最小化 $\|Lz\|^2$（调和能量），**硬**施加 (6) 与 $F_{cb}$ 上 Lipman frame。$q$-CCM 是理论对象；HGP 是其 SOCP 实现。（旧笔记写「在 $\tilde{S}_q$ 上求分段调和」是算法直觉的简写；实现始终在 $S_c$ 上。）

### 2.5 核心思想：覆盖空间与凸映射（旧笔记四步叙事）

直接构造 $q$-CCM 是带锥角约束的**线性**问题。旧笔记用四步概括「覆盖 + 凸映射」直觉；BCW17 **正式证明**走 index counting（§9），下列第三步须按 §9.8 理解。

#### 第一步：锥点「展开」——覆盖空间变「平」

基曲面锥点 $v_c$ 处锥角 $\Theta_c = 2\pi k_c/q$（$k_c \neq 1$ 时非平坦）。绕 $v_c$ 走一圈，像在平面只转 $k_c/q$ 圈。在 **$q$-fold 分支覆盖** $\tilde{S}_q$ 上，$v_c$ 的原像复制 $q$ 份并按旋转关系粘合；绕原像一圈后像累积

$$
q \cdot \frac{k_c}{q} = k_c \in \mathbb{Z}
$$

个完整圈——**角 deficit 在覆盖上被整数化**，锥点从「角 bookkeeping」角度被展开。（**不**等于 $\tilde{S}_q$ 上无分歧、必为圆盘；见 §7.4、§8.5。）

#### 第二步：Riemann–Hurwitz 判断覆盖空间的拓扑

$$
\chi(\tilde{S}_q) = q\chi(S) - \sum_{P \in \mathcal{R}}(e_P - 1).
$$

- 闭合曲面无锥：$q\chi(S)=q(2-2g)$，$g>0$ 时 $\chi<0$，覆盖**不会**是圆盘——需**锥点**吸收亏格；
- 锥点的 $\sum(e_P-1)$ 与边界转角共同调节 $\chi(\tilde{S}_q)$；
- 这正是 (GB) 的含义：锥点配置须使 **index 预算**（式 (9)(10)）平衡。

> 旧笔记写「RH 保证 $\chi(\tilde{S}_q)>0$ / 圆盘」过强；(GB)+(RH) 保证的是 **Theorem 6.1 的代数闭合**，例 C 中 $\chi(\tilde{S}_q)=-10$ 仍成立。

#### 第三步：Tutte 定理与 M-矩阵（圆盘特例）

若 $\tilde{S}_q$ **恰为**拓扑圆盘（或具固定凸边界的正 Euler 曲面），Tutte 嵌入定理保证：边界固定到凸多边形、内部正权凸组合的 CCM 在**整个** $\tilde{S}_q$ 上**全局**单射（无翻转、无重叠）。

**机制**：凸组合 ⟺ 带 Dirichlet 边界的离散 Laplace；系数矩阵为 **M-matrix**（对角占优、不可约）⟹ **离散极大值原理** ⟹ 内部极值在边界 ⟹ 单射。

> **修正**：HGP **一般证明不经过此步**；高亏格 / 非圆盘覆盖用 **index counting**（§9），非 Tutte 直接套用。

#### 第四步：投影与局部单射

覆盖上单射映射 $\tilde{f}:\tilde{S}_q\to\mathbb{R}^2$ 经覆盖投影回到基曲面：

$$
f = \tilde{f} \circ P_q^{-1}: S \to \mathbb{R}^2.
$$

$P_q$ 在非分歧点处局部微分同胚。**旧笔记**称由此得 $f$ 局部单射；**正确链条**是：Theorem 6.1 先在 $\tilde{S}_q$ 上证内部全 **wheel**（等价于无翻转），再推出 $f$ 在 $S$ 上局部单射——投影公式是几何对应，不是证明的充分条件。

**小结**：Riemann–Hurwitz 在旧叙事中扮演**拓扑可行性 / index 预算**角色；单射性最终由 **(5)(9)(10)** 与 $s=0$ 闭合（§9.6），而非「圆盘 + Tutte + 投影」三步缺一不可。

---

## 3. 背景：CCM、离散 1-form 与 index counting

### 3.1 Tutte 定理与 M-矩阵

CCM 等价于离散调和。Tutte 定理：3-连通平面、边界凸、内部正权 CCM ⇒ **全局**平面嵌入。

**机制**：凸组合 ⟺ 离散 Laplace 方程；系数矩阵为 **M-matrix**（对角占优、不可约）⟹ 离散极大值原理 ⟹ 内部无翻转。这是圆盘情形 index 为 0 的代数版本。

### 3.2 Gortler 离散 1-form

对平面坐标 $z=x+iy$，CCM 诱导 1-form $\rho=\Delta z$。**Index** 由 $\rho$ 在顶点/面处的符号变化计数；离散 Poincaré–Hopf：

$$
\sum_v \mathrm{ind}(v) + \sum_f \mathrm{ind}(f) = \chi.
$$

Gortler 用此统一证明 Tutte、多孔洞圆盘、环面嵌入等。详见 [离散 1-form 与 index counting](../4.全局参数化与四边形网格化/微分形式介绍5-离散1-形式.md)。

### 3.3 高亏格与覆盖

闭合曲面调和 1-form 维数为 $2g$（Mercat 2001）。Gortler 对环面给出嵌入定理；更高亏格需更强条件。HGP 引入**锥点**与 **$q$-fold 分支覆盖**，在 $\tilde{S}_q$ 上对 **mostly harmonic 1-form** 做 index counting，从而得到 Theorem 6.1。

---

## 4. Seamless、cone metric 与 holonomy

### 4.1 Cone metric 与无缝

若 seam 两侧边等长，$f$ 拉回 $\mathbb{R}^2$ 标准度量得 **cone metric** $g_f$：除锥点外平坦。$f$ **无缝**当 seam 两侧像差**保向等距**中的旋转；四边形经典为 $\pi/2$，HGP 推广为 $2\pi/q$ 的倍数。

### 4.2 切开与 holonomy

沿 **seam graph** $G_s$（含所有锥点、连接边界分量）切开得 $S_c$。**Holonomy**：绕 $S\setminus C$ 闭路平行移动的总转角。Myles–Zorin (2012)：seam 旋转角 $\{r_{ij}\}$ 与 homology 基 holonomy 线性相关（模 $2\pi$）。

### 4.3 三类有理角

| 概念 | 记号 |
| :--- | :--- |
| 锥角 | $\theta_i = 2\pi k_i/q$ |
| 边界转角 | $2\pi l_j/q$ |
| Seam 旋转 | $2\pi r_{ij}/q$ |

锥角、转角由线性系统**间接**固定；求解后须**检验**诱导度量是否达标（§9.3）。

---

## 5. 线性调和系统（详）

### 5.1 变量

- $v_i \notin V_s$：一个 $z_i$；
- seam 顶点度数 $d$：副本 $z_i^0,\ldots,z_i^{d-1}$。

### 5.2 方程 (7)

$$
\sum_{v_j \in N(v_i)} w_{ij}(z_i - z_j) = 0, \quad v_i \in V \setminus V_s, \quad w_{ij} > 0.
\tag{7}
$$

### 5.3 方程 (8) / (14)

度数为 2 的 seam 顶点（Figure 6）：

$$
\sum_{v_j \in N^*(v_i^0)} w_{ij}(z_i^0 - z_j)
+ \sum_{v_j \in N^*(v_i^1)} w_{ij}\, e^{i\frac{2\pi r_1}{q}}(z_i^1 - z_j) = 0.
\tag{8}
$$

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107101000576.png)

第二项将扇区 1 的边差旋转到扇区 0 坐标系后参与调和平均。高 degree 见附录 (14)。

---

## 6. 局部单射性：分支覆盖与单射定义

映射 $f$ **局部单射**：每个三角形**正向**映射，边不自交。

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250227112126656.png" alt="局部单射示意" style="zoom:50%;" />

---

## 7. $q$-fold 分支覆盖 $\tilde{S}_q$

### 7.1 构造（图 A/B/C）

给定 $q$-CCM $f$，定义 $f_n := e^{2\pi n i/q} f$。复制 $q$ 份 $S_c^0,\ldots,S_c^{q-1}$，按 (6) 将 seam 边粘合（像平行同向），得 $\tilde{S}_q$，覆盖映射 $P_q:\tilde{S}_q\to S$。

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250924184009210.png)

- **图 A/B**：$q$ 份副本沿 seam 粘合；
- **图 C**：覆盖上内部顶点常为 **wheel**，便于 index counting。

$\tilde{S}_q$ **不必是圆盘**（例 C：穿孔环面覆盖为亏格 5、双穿孔曲面）。

### 7.2 覆叠 vs 分支覆盖（旧笔记保留）

| | **覆叠 (covering)** | **分支覆盖 (branched cover)** |
| :--- | :--- | :--- |
| 局部 | 处处微分同胚 | 分歧点处 $z\mapsto z^{e_P}$ |
| 万有覆叠 | 单连通，$\pi_1=0$ | 一般非单连通 |
| 1-form | $\omega=df$ 单值 | 在 $\tilde{S}_q$ 上拼接 mostly harmonic 形式 |

**万有覆叠** $\tilde{S}\to S$：消去 $H_1$，闭曲线可缩；调和 1-form 变恰当 $\omega=df$，$f:\tilde{S}\to\mathbb{C}$ 单值共形。再通过 deck transformation 投影：

$$
f(p^{-1}(x)) = \{f(\tilde{x}) + \gamma \mid \gamma \in \Gamma\}.
$$

**$q$-fold 分支覆盖** $P_q$ 在分歧点局部 $z\mapsto z^{e_P}$（$e_P\ge 2$）。HGP 用的是**分支覆盖**（允许锥点展开），不是万有覆叠。

### 7.3 Mostly harmonic 1-forms

$q$-CCM 在 $\tilde{S}_q$ 上诱导 2 维实空间 $\tilde{\rho}^\alpha,\tilde{\rho}^\beta$；$\tilde{\rho}=a\tilde{\rho}^\alpha+b\tilde{\rho}^\beta$ 用于证明。

### 7.4 锥点「展开」直觉（含修正说明）

基曲面锥点 $v_c$ 处角 $\Theta_c=2\pi k_c/q$。绕 $v_c$ 一圈，像在平面只转 $k_c/q$ 圈。在 $\tilde{S}_q$ 上粘合 $q$ 份扇区后，绕原像一圈累积

$$
q \cdot \frac{k_c}{q} = k_c \in \mathbb{Z}
$$

个完整圈——**角 deficit 在覆盖上被整数化**。

> **修正**：这**不**意味着 $\tilde{S}_q$ 上「无锥点」或必为圆盘；分歧点仍在，$\chi(\tilde{S}_q)$ 由 (RH) 决定。旧笔记「锥点消除」应理解为**指标/bookkeeping 上的展开**，而非拓扑上变成无奇异圆盘。

---

## 8. Riemann–Hurwitz 与 Gauss–Bonnet

### 8.1 Riemann–Hurwitz

若 $\tilde{M}$ 是 $M$ 的 $N$ 叶分支覆盖，$\mathcal{R}$ 为 $\tilde{M}$ 上分歧点集，$e_P$ 为分歧指数：

$$
\chi(\tilde{M}) = N\,\chi(M) - \sum_{P \in \mathcal{R}}(e_P - 1).
\tag{RH}
$$

对 $\tilde{S}_q\to S$：$N=q$，$\mathcal{R}$ 为锥点原像上的分歧点。

### 8.2 Lemma 5.2（分歧指数——修正旧笔记错误）

锥点 $v_i$ 的 angle index 为 $k_i$（锥角 $2\pi k_i/q$）。在 $G_s$ 中度数为 1 时，绕 $v_i$ 粘合时 superscript 每步加 $k_i \pmod q$：

- **分歧点个数** $= \gcd(k_i, q)$；
- **每个分歧指数** $e_P = \dfrac{q}{\gcd(k_i, q)}$。

（旧笔记误写 $e_P=k_i/\gcd(k_i,q)$。）

**例**：$q=4,k_i=3$ → $\gcd=1$，1 个分歧点，$e_P=4$。

**例 A**（论文 Figure 7）：球面 $g=0$，1 锥 $k=3$，$q=4$ → 1 个分歧点、指数 4、锥角 $6\pi$。

### 8.3 Lemma 5.3（边界）

turning index $l_j$：$P_q^{-1}(B_j)$ 有 $\gcd(l_j,q)$ 个连通分量，各转角 $2\pi l_j/\gcd(l_j,q)$。

### 8.4 Lemma 6.2（Gauss–Bonnet）

$|C|$ = **锥点个数**（旧笔记误作「外部面/顶点数」）：

$$
q|C| - \sum_{v_i \in C} k_i + \sum_{j=1}^{m} l_j = q(2 - 2g - m).
\tag{GB}
$$

**拓扑可行性**：闭合曲面 $g>0$ 无锥时 $q\chi(S)=q(2-2g)<0$；需锥点使 (GB) 与 (RH) 协调。锥点配置须使 index 预算平衡——**不**保证 $\chi(\tilde{S}_q)=1$，只保证 Theorem 6.1 的代数闭合。

### 8.5 例 C 的 $\chi$ 计算（论文）

穿孔环面 $g=1,m=1$，$\chi(S)=-1$；两锥 $k=5,q=4$；边界 turning $l=-2$。$\tilde{S}_q$ 有 2 边界分量、2 分歧点各指数 4，得 $\chi(\tilde{S}_q)=-10$：亏格 5、双穿孔曲面——**远非圆盘**，但 Theorem 6.1 仍适用。

---

## 9. Theorem 6.1 与完整 index counting

### 9.1 定理

> 设 $f$ 为 $q$-CCM。**锥三角形**与**边界三角形**正向定向，诱导度量实现目标锥角与转角，则 $f$ **局部单射**。

### 9.2 证明归约

$f$ 局部单射 ⟺ 任意非零 $\tilde{\rho}$ 在 $\tilde{S}_q$ 内部顶点 $\mathrm{ind}=0$ ⟺ 各点为 **wheel**。

### 9.3 闭网格与公式 (5)

在 $\tilde{S}_q$ 各边界外加 **exterior face**（Gortler 技巧），得闭网格 $\bar{S}_q$：

$$
\sum_v \mathrm{ind}(v) + \sum_f \mathrm{ind}(f) = \chi(\bar{S}_q).
\tag{5}
$$

### 9.4 RHS 计算（式 (9)）

由 (RH)、Lemma 5.2/5.3、外侧面贡献，化简得：

$$
\mathrm{RHS} = \sum_{v_i\in C}\gcd(k_i,q) + \sum_j \gcd(l_j,q) - \sum_{v_i\in C} k_i + \sum_j l_j.
\tag{9}
$$

由 (GB) 可知 (9) 与 $q(2-2g-m) - q|C| + \sum k_i - \sum l_j$ 一致。

### 9.5 LHS 计算（式 (10)）

设内部（非锥非边界）贡献 $s\le 0$。锥角 $2\pi N$ 处分歧点 index 贡献 $1-N$（Lemma 5.4 类比）。锥点 $v_i$ 上 $\gcd(k_i,q)$ 个分歧点，各锥角 $2\pi k_i/\gcd(k_i,q)$：

$$
\text{锥贡献} = \sum_{v_i\in C}\bigl(\gcd(k_i,q) - k_i\bigr).
$$

边界（Lemma 5.4）：turning $2\pi\phi$ 时外侧面+边界顶点 index 贡献 $\phi+1$。得

$$
\mathrm{LHS} = s + \sum_{v_i\in C}\bigl(\gcd(k_i,q) - k_i\bigr) + \sum_j \bigl(\gcd(l_j,q) + l_j\bigr).
\tag{10}
$$

### 9.6 闭合

$\mathrm{LHS}=\mathrm{RHS}$ 且 $s\le 0$、其余项由正向定向与角正确固定 ⟹ **$s=0$**。内部全 wheel ⟹ $f$ 在 $S_c$ 内部无翻转；seam 顶点经扇区等距拼接亦为 wheel ⟹ $f$ 在 $S$ 上**局部单射**。

### 9.7 例 A 验算（论文 §6.1）

球面+$q=4$+1 锥 $k=3$+边界 $l=1$：$\mathrm{RHS}=4\cdot 1 - 3 + 1 = 2$。锥+边界贡献 $\mathrm{LHS}=s+(-2)+4$，故 $s=0$ ✓。

### 9.8 与 Tutte 的关系（旧笔记第三步的修正）

| 旧笔记表述 | 修正 |
| :--- | :--- |
| $\tilde{S}_q$ 为圆盘时 Tutte 保证**全局**单射 | 证明**不依赖** $\chi(\tilde{S}_q)=1$；用 index counting，非 Tutte 直接套用 |
| 投影 $f=\tilde{f}\circ P_q^{-1}$ 保证局部单射 | 局部单射来自 **wheel / index**，不是来自覆盖投影的简单复合 |
| M-matrix / 极大值原理 | 对**圆盘 CCM** 成立；高亏格 $q$-CCM 用 Theorem 6.1 替代 |

**保留的直觉**：当 $\tilde{S}_q$ **恰为**拓扑圆盘且边界凸时，CCM 在覆盖上确为全局嵌入——这是 Gortler 圆盘定理的特例，**不是** HGP 一般证明链。

### 9.9 定理结论（旧笔记表述，已对齐 BCW17）

设 $f$ 为 $S$ 上的 $q$-CCM，锥点与角度系数给定 seam 旋转约束。若锥三角形与边界三角形以**保持定向**的方式映射，且诱导度量实现了目标锥角与边界转角，则由 **Theorem 6.1**（覆盖上 index counting，而非一般情形的 Tutte 全局嵌入），**$f$ 是局部单射的**。

---

## 10. HGP 算法实现

综合理论，HGP 归结为**带约束凸优化**（SOCP）。实现**不**显式构造 $\tilde{S}_q$。

### 10.1 调和性约束分项

**Seam edge 旋转（硬）**：

$$
z_j^a - z_i^a = e^{i\frac{2\pi r_{ij}}{q}}(z_j^b - z_i^b), \quad e_{ij} \in G_s.
$$

**Non-seam vertex 调和（软）**：

$$
\sum_{v_j \in N(v_i)} w_{ij}(z_i - z_j) = 0, \quad v_i \in V \setminus G_s.
$$

**Seam vertex 调和（软）**：

$$
\sum_{v_j \in N^*(v_i^0)} w_{ij}(z_i^0 - z_j) + \sum_{v_j \in N^*(v_i^1)} w_{ij}e^{i\frac{2\pi r_j}{q}}(z_i^1 - z_j) = 0.
$$

### 10.2 Lipman 单射性约束（仅 $F_{cb}$）

对**含锥点或边界顶点**的三角形 $t_j \in F_{cb}$：

$$
\mathrm{Re}\!\left(f_{\bar{z}}\, \overline{\left(\frac{f_z^j}{f_z^i}\right)}\right) - |f_z| \geq \epsilon.
$$

Theorem 6.1：$F_{cb}$ 正向定向 ⇒ 整体局部单射；无需全网格 Lipman（与 Lipman 2012 全投影不同）。Frame $d$ 每步更新（Lipman 式 (27)），初值 $d=(1,0)$。

约束亦与有界畸变调和映射 **BDHM**（陈仁杰等）精神相关；HGP 在 seamless + 有理 holonomy 设定下采用 frame 的 SOCP 形式。

### 10.3 完整优化模型

$$
\begin{aligned}
\min_{z}\quad & \|Lz\|^2 + \lambda\, E_{\text{pos}}(z) + \lambda_{\text{bi}} E_{\text{bi}} + \lambda_{\text{arap}} E_{\text{arap}} \\
\text{s.t.}\quad & \text{(6) 对所有 } e_{ij}\in G_s \quad \text{（硬）} \\
& \text{Lipman frame on } t_j \in F_{cb}
\end{aligned}
$$

- $E_{\text{pos}}$：手柄软约束（硬约束在畸变界过紧时可能不可行）；
- $E_{\text{bi}}$：双调和；$E_{\text{arap}}$：ARAP 型正则（论文式 (31)(32)）；
- 求解：MOSEK 等 SOCP；见 [凸优化与 KKT](../6.附录-数值计算与最优化/2019-07-14-凸优化与KKT条件.md)。

**核心 SOCP 骨架**（旧笔记公式，seam 硬、Lipman 在 $F_{cb}$）：

$$
\begin{aligned}
\min_{z}\quad & \|Lz\|^2 \\
\text{s.t.}\quad & z_j^a - z_i^a = e^{i\frac{2\pi r_{ij}}{q}}(z_j^b - z_i^b), \quad e_{ij} \in G_s \\
& \mathrm{Re}\!\left(f_{\bar{z}}\, \overline{\left(\frac{f_z^j}{f_z^i}\right)}\right) - |f_z| \geq \epsilon, \quad t_j \in F_{cb}
\end{aligned}
$$

Lipman 凸化约束及 **BDHM**（陈仁杰等，有界畸变调和映射）与 HGP 的 frame 形式精神相通；上式为论文实现的最小化核心。

### 10.4 成功后检验

检验锥角 $\approx 2\pi k_i/q$、边界转角 $\approx 2\pi l_j/q$、$F_{cb}$ 无翻转——线性解不自动保证度量角达标。

### 10.5 FastHGP

[FastHGP](扭曲有界-全局调和参数化2-FastHGP.md)：调和零空间维数 $\dim\approx 2(|\partial V|+|C|+n-1)$，KKT 矩阵 $K$、子空间基 $H$、**ATP** 初值、Projected Newton；Theorem 6.1 仍只需 $F_{cb}$。

---

## 11. 小结

| 概念 | 要点 |
| :--- | :--- |
| **$q$-CCM** | (6)(7)(14) 的解；$q$-convex **combination** |
| **几何四条件** | 直觉，非独立定义 |
| **$\tilde{S}_q$** | 证明用；旋转副本 + 粘合 |
| **Lemma 5.2** | $\gcd(k_i,q)$ 点，$e_P=q/\gcd(k_i,q)$ |
| **(GB)** | $\|C\|$=锥点个数 |
| **Theorem 6.1** | (9)(10) ⟹ $s=0$ ⟹ 局部单射 |
| **HGP** | 硬 (6) + 软调和 + $F_{cb}$ frames |

---

## 参考文献

1. Bright A., Chien E., Weber O. *Harmonic Global Parametrization with Rational Holonomy*. ACM TOG, 2017. [DOI](https://doi.org/10.1145/3072959.3073646)
2. Gortler S. J., Gotsman C., Thurston D. *Discrete One-Forms on Meshes and Applications to 3D Mesh Parameterization*. CAGD, 2006.
3. Floater M. S. *Parameterization and smooth approximation of surface triangulations*. CAGD, 1997.
4. Tutte W. T. *How to Draw a Graph*. Proc. LMS, 1963.
5. Tong Y., Alliez P., Desbrun M. *Quadrangulation with discrete harmonic forms*. SGP 2006.
6. Lipman Y. *Bounded Distortion Mapping Spaces for Triangular Meshes*. ACM TOG, 2012.
7. Myles R., Zorin D. *Global parametrization by incremental flattening*. SIGGRAPH Asia 2012.
8. Mercat C. *Discrete Riemann Surfaces and the Ising Model*. Comm. Math. Phys., 2001.
9. Pinkall U., Polthier K. *Computing Discrete Minimal Surfaces and Their Conjugates*. Exp. Math., 1993.
10. Hefetz E. F., Chien E., Weber O. *A Subspace Method for Fast Locally Injective Harmonic Mapping*. CGF, 2019.
11. Kälberer F., Nieser M., Polthier K. *QuadCover*. CGF, 2007.
