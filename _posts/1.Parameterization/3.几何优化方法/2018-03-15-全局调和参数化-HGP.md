---
layout: post
title: "Harmonic Global Parametrization — q-CCM 与 HGP"
categories: ["Parameterization", "Parameterization-GeometricOptimization"]
mathjax: true
---

> **论文**：Alon Bright, Edward Chien, Ofir Weber. [*Harmonic Global Parametrization with Rational Holonomy*](https://doi.org/10.1145/3072959.3073646). ACM Transactions on Graphics (SIGGRAPH), 36(4), 2017.

平面映射与变形是图形学核心问题（图像变形、纹理映射、四边形网格化、方向场设计等）。**Harmonic Global Parametrization (HGP)** 对**任意亏格**三角网格，在给定锥点与**有理 holonomy**（$2\pi/q$ 的整数倍）下，同时追求：

- **局部单射 (local injectivity)**：无 fold-over；
- **无缝 (seamless)**：cone metric 沿 seam 两侧差旋转；
- **可计算**：通常 1–2 次 SOCP，Myles et al. 2014 benchmark 上鲁棒性高。

理论核心是 **$q$-CCM**（$q$-**convex combination maps**，$q$-凸组合映射）

1. 在切开曲面 $S_c$ 上求**线性** $q$-CCM（调和 + seam 旋转）；
2. 用 **$q$-fold 分支覆盖（branched cover）** $\tilde{S}_q$ 上的 **index counting** 证明 Theorem 6.1。

**分支覆盖的作用**：把 seam 旋转造成的多值 $\mathrm{d}f$ 单值化，并把锥点变成可计入 index 预算的分歧点——从而把 Gortler 论证搬到任意拓扑。它是**证明装置，不是求解空间**；算法从不显式构造 $\tilde{S}_q$，也**不是**「先在覆盖上做 Tutte 再投影」。

| 前驱 | 局限 | HGP |
| :--- | :--- | :--- |
| Tutte / Floater CCM | 圆盘、凸边界 | 切开 + 有理 holonomy |
| Gortler et al. 2006 | 圆盘/环面 index 定理 | 任意拓扑 + 锥点 |
| Tong et al. 2006 | 多 patch，$\pi/2$ holonomy | 单 patch $S_c$，$2\pi/q$ 倍数 |

**$q$-CCM**（$q$-**convex combination maps**）是对经典 **Tutte 参数化**与 **Gortler 凸组合 / index counting** 的推广：$q$ 约束角度为 $2\pi/q$ 的有理倍数；四边形网格化取 $q=4$。直接求带锥角与 seam 旋转的 $q$-CCM 是**线性**问题；

**局部单射性**则通过 **$q$-fold 分支覆盖** $\tilde{S}_q$ 上的 **mostly harmonic 1-form** 与 **index counting**（Theorem 6.1）证明——覆盖用于**证明**，HGP 算法在切开曲面 $S_c$ 上求解，**不必**显式构造 $\tilde{S}_q$。



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

### 2.4 CCM 在切开圆盘上的推广

**$q$-CCM** 可看作 Floater **CCM** 在**切开圆盘** $S_c$ 上的推广：内部仍为正权凸组合（(7)），但 seam 上通过 (6) 的 $q$-fold 旋转实现有理 holonomy，从而处理多边界与任意亏格（经锥点吸收拓扑）。

**与 HGP 的关系**：HGP 在切开曲面 $S_c$ 上求 $z=u+iv$，**软**最小化 $\|Lz\|^2$（调和能量），**硬**施加 (6) 与 $F_{cb}$ 上 Lipman frame。$q$-CCM 是理论对象；HGP 是其 SOCP 实现。

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


---

## 6. 局部单射性：从 wheel 到 index

映射 $f$ **局部单射**：每个三角形**正向**映射，边不自交（一环邻域同胚于圆盘）。

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250227112126656.png" alt="局部单射示意" style="zoom:50%;" />

### 6.1 Wheel 顶点（Gortler）

对 CCM / $q$-CCM 的像，内部顶点 $v$ 的一环边角记为 $\gamma_i$。称 $v$ 为 **wheel**，若所有 $\gamma_i$ 同号且 $\sum|\gamma_i|=2\pi$。直观上：一环三角形形成有序扇形、无断裂交叉——$v$ 的局部邻域同胚于圆盘。

在本设定下（非锥内部顶点）：

$$
f\text{ 局部单射} \;\Longleftrightarrow\; \text{所有非锥内部顶点均为 wheel}.
$$

### 6.2 离散 1-form 与 index（温习）

对像坐标 $z_i=f(v_i)$，定义

$$
\rho^x_{ij}=\mathrm{Re}(z_j-z_i),\qquad
\rho^y_{ij}=\mathrm{Im}(z_j-z_i),\qquad
\rho^{\alpha,\beta}=\alpha\rho^x+\beta\rho^y.
$$

绕顶点/面一周，$\rho$ 的符号变化次数记为 $\mathrm{scg}$（恒为偶正整数）。**Index**：

$$
\mathrm{ind}_\rho(p)=\frac12\bigl(2-\mathrm{scg}_\rho(p)\bigr)\in\mathbb{Z},\quad \mathrm{ind}\le 1.
$$

闭网格上的 **index 公式**（离散 Poincaré–Hopf）：

$$
\sum_v \mathrm{ind}(v)+\sum_f \mathrm{ind}(f)=\chi.
\tag{5}
$$

**关键引理**（Gortler Lemma 3.7）：若顶点 $v$ **非 wheel**，则存在 $(\alpha,\beta)$ 使 $\rho^{\alpha,\beta}$ 非零且 $\mathrm{ind}(v)<0$。因此：若对**任意**非零 $\rho^{\alpha,\beta}$ 都有内部 $\mathrm{ind}=0$，则内部全为 wheel。

圆盘 Tutte 的证明正是：补 exterior face 后用 (5)，边界贡献顶满 $\chi$，迫使内部 $s=0$。HGP 不能在 $S_c$ 上直接照搬（seam 旋转使 $\mathrm{d}f$ 多值）——必须先经 **branched cover** 把问题送到 $\tilde{S}_q$ 上（§7.0），再对 mostly harmonic $\tilde{\rho}$ 做同一套 index counting。

---

## 7. $q$-fold 分支覆盖（branched cover）$\tilde{S}_q$

### 7.0 分支覆盖的作用（先读这一节）

**一句话**：branched cover 不是 HGP 的求解空间，而是把「带锥点 + 有理 holonomy 的 $q$-CCM」翻译成「Gortler 能做 index counting 的 mostly harmonic 1-form」的**证明装置**。

#### 为什么基曲面 $S$ / 切开面 $S_c$ 上不够？

Gortler 的 index 论证依赖两件事：

1. 有一组 **2 维**的、在内部几乎处处 **co-closed** 的 1-form $\rho^{\alpha,\beta}$；
2. 能在**闭网格**上写 $\sum\mathrm{ind}=\chi$，用边界/奇异点贡献顶满预算，迫使内部 $s=0$。

在 $S_c$ 上直接做会卡住：

| 障碍 | 原因 |
| :--- | :--- |
| Seam 旋转 | 绕 seam 走一圈，$f$ 的像差 $e^{i2\pi r/q}$，坐标增量**不是**单值 1-form |
| 锥点 | 角 $\neq 2\pi$，局部不是标准 wheel；index 贡献需单独记账 |
| 有理 holonomy | 绕闭路平行移动转 $2\pi k/q$，在基曲面上 1-form 多值 |

也就是说：$q$-CCM 在 $S_c$ 上是**良定的线性解**，但其诱导的「$\mathrm{d}f$」因旋转约束而**多值**——不能直接套 Gortler。

#### 分支覆盖具体解决什么？

构造 $\tilde{S}_q$ 的目的是三件事（对应证明三步）：

1. **消多值 → 单值 1-form**  
   取 $f$ 的 $q$ 个旋转副本 $f_n=e^{2\pi ni/q}f$，按 (6) 把像平行的 seam 粘合。粘合后，在 $\tilde{S}_q$ 上可定义**单值**的 $\tilde{\rho}^x,\tilde{\rho}^y$（§7.3）。有理 holonomy 被「展开」进覆盖的拓扑里。

2. **把锥点变成可计数的分歧点（branch points）**  
   必须是 **branched** cover，而不是普通 covering：锥点是 branch points，原像是 ramification points（Lemma 5.2）。普通 $q$-叶覆叠在锥点处无法正确粘合扇区。分歧指数 $e_P=q/\gcd(k_i,q)$ 决定该点在 index 公式里贡献多少（$1-N$）——这是 LHS 锥项的来源。

3. **提供正确的 $\chi$ 与 index 预算**  
   用 Riemann–Hurwitz 算 $\chi(\tilde{S}_q)$，用 (GB) 对齐锥角/转角，得到 RHS (9)。覆盖不必是圆盘（例 C：$\chi=-10$）；只要预算闭合，$s=0$ 仍成立。

```text
S 上的 q-CCM（多值 df / 锥角）
        │  复制 q 份 + 按 seam 旋转粘合
        ▼
Ŝ_q = q-fold branched cover
        │  定义单值 mostly harmonic ρ̃^{α,β}
        ▼
Gortler-style index counting  →  s=0  →  全 wheel  →  f 局部单射
```

#### 分支覆盖**不是**什么（常见误解）

| 误解 | 正确理解 |
| :--- | :--- |
| 在 $\tilde{S}_q$ 上跑 Tutte / 解线性系统再投影 | **算法始终在 $S_c$ 上**；$\tilde{S}_q$ 只出现在证明里 |
| 覆盖必须是圆盘，RH「保证」$\chi>0$ | 覆盖可以是高亏格、不连通；RH 只给 $\chi$，不保证圆盘 |
| 「branched」可换成普通 covering | 不行——锥点必须是 branch points，否则扇区粘合与 index 贡献都错 |
| 覆盖上的映射全局单射 ⟹ 基曲面局部单射 | 证明只证覆盖上**局部** wheel；拼出的平面图允许全局重叠 |

#### 与算法的接口

Theorem 6.1 把「$\tilde{S}_q$ 上 $s=0$」归约为「$F_{cb}$ 正向 + 角正确」。因此 HGP **只需**对锥/边界三角形加 frame，**从不**组装 $\tilde{S}_q$。branched cover 的「作用」全部消耗在理论保证上。

灵感来源：QuadCover / HexCover / stripe patterns 里的 $q$-fold branched cover；HGP 把它从「场的表示」转成「单射性证明的舞台」。

---

### 7.1 构造（论文 Figure 7：例 A/B/C）

给定 $q$-CCM $f$，令

$$
f_n := e^{2\pi n i/q}\, f,\qquad n=0,\ldots,q-1
$$

（$f$ 的 $q$ 个旋转副本）。取切开网格的 $q$ 份副本 $S_c^0,\ldots,S_c^{q-1}$，对每条 seam 边：按 (6)，在某个副本上存在像**平行且半边同向**的配对边；将它们粘合。商空间记为 $\tilde{S}_q$，覆盖映射 $P_q:\tilde{S}_q\to S$。

- **例 A**（圆盘 + 1 锥 $k=3$，$q=4$）：粘合后类似自交浸入的 4-叶邻域；
- **例 B**（圆盘 + 1 锥 $k=2$）：$\tilde{S}_q$ 可为**两个**圆盘（覆盖不必连通）；
- **例 C**（穿孔环面 + 两锥 $k=5$）：16 条粘合，拓扑远非圆盘。

粘合保持各副本定向一致，故 $\tilde{S}_q$ 是定向三角网格。拼出的平面图可能有**全局**重叠；证明只关心**局部**（wheel）。

> 实现 HGP **不必**显式构造 $\tilde{S}_q$；覆盖仅用于证明。

### 7.2 为何是 branched cover，而不是普通 covering / 万有覆叠

| | **普通覆叠 (covering)** | **分支覆盖 (branched cover)** | **万有覆叠** |
| :--- | :--- | :--- | :--- |
| 局部 | 处处微分同胚 | 分歧点处 $z\mapsto z^{e_P}$ | 单连通，$\pi_1=0$ |
| 锥点 | 无法容纳角 $\neq 2\pi$ 的奇异 | 锥点 = branch points | 消去全部 $H_1$，过强 |
| 与 HGP | 不够 | **正是所用** | 不是 HGP 的构造 |

- **必须 branched**：绕锥点走一圈，基曲面上角只转 $k_i/q$ 圈；在覆盖上粘合 $q$ 份扇区后，分歧点处局部像 $z\mapsto z^{e_P}$，角变成整数倍 $2\pi N$。这既解释「展开」，也给出 Lemma 5.2 的 $e_P$。
- **不必万有覆叠**：HGP 只需要把 **$q$-fold 有理旋转**单值化，不需要把所有闭路都可缩；万有覆叠无限叶，也无法用有限的 (RH)/(GB) 做 index 预算。
- **$q$ 叶的含义**：与 holonomy 群 $\{e^{i2\pi r/q}\}$ 同阶——副本数恰好够把所有 seam 旋转配对粘合。

### 7.3 Mostly harmonic 1-forms（证明的核心对象）

在 $\tilde{S}_q$ 上定义 2 维实空间的 1-form（论文 §5.1）——这是 branched cover **产出的分析对象**：

- 非粘合边 $\tilde{e}_{ij}$ 来自某副本 $S_c^n$：令
  $$
  \tilde{\rho}^x_{ij}=\mathrm{Re}\bigl(f_n(v_j^n)-f_n(v_i^n)\bigr),\quad
  \tilde{\rho}^y_{ij}=\mathrm{Im}\bigl(f_n(v_j^n)-f_n(v_i^n)\bigr).
  $$
- 粘合边：任取一侧定义即可——两侧像等距平行，故良定（这正是 (6) + $q$ 个旋转副本的作用）。
- 一般元：$\tilde{\rho}^{\alpha,\beta}=\alpha\tilde{\rho}^x+\beta\tilde{\rho}^y$。

称其为 **mostly harmonic**：由 $q$-CCM 的 (7)(8)/(14)，在 $\tilde{S}_q$ 的**非分歧内部顶点**上，$\tilde{\rho}^{\alpha,\beta}$ 满足加权 co-closed（离散调和）；面 closed。分歧点（锥点原像）与边界处一般不调和——故「mostly」。

对任意非零 $\tilde{\rho}^{\alpha,\beta}$：内部非分歧顶点/面的 index 贡献 $\le 0$（与 Gortler 圆盘情形相同）。此后 §8–§9 的全部计算，都是在这个 branched cover 上对 $\tilde{\rho}$ 做 index counting。

### 7.4 锥点「展开」：branched 的几何直觉

基曲面锥点 $v_c$ 处角 $\Theta_c=2\pi k_c/q$。绕 $v_c$ 一圈，像只转 $k_c/q$ 圈。在 $\tilde{S}_q$ 上粘合后，绕原像（ramification point）一圈累积 $k_c\in\mathbb{Z}$ 个完整圈——角 deficit 在覆盖上被**整数化**。

这正是「branch」的含义：投影 $P_q$ 在该点不是局部同胚，而是 $e_P$-对-1；index 公式用 $1-N$ 给它记账，而不是假装它是普通内部顶点。

> 展开 **不**意味着 $\tilde{S}_q$ 无锥或必为圆盘；分歧点仍在，$\chi$ 由 (RH) 决定。

---

## 8. Riemann–Hurwitz 与 Gauss–Bonnet

### 8.1 Riemann–Hurwitz

$$
\chi(\tilde{M}) = N\,\chi(M) - \sum_{P \in \mathcal{R}}(e_P - 1).
\tag{RH}
$$

对 $\tilde{S}_q\to S$：$N=q$，$\mathcal{R}$ 为锥点原像上的分歧点。

### 8.2 Lemma 5.2（分歧指数）

锥点 $v_i$ 的 angle index $k_i$（锥角 $2\pi k_i/q$）。$G_s$ 中度数为 1 时，绕 $v_i$ 粘合时副本标号每步加 $k_i\pmod q$：

- **分歧点个数** $= \gcd(k_i, q)$；
- **每个分歧指数** $e_P = q/\gcd(k_i, q)$。

（旧笔记误写 $e_P=k_i/\gcd$。）

**例 A**：$q=4,k=3$ → $\gcd=1$，1 个分歧点，$e_P=4$；覆盖上该点邻域锥角 $2\pi\cdot 4\cdot(3/4)=6\pi$。

### 8.3 Lemma 5.3（边界）

turning index $l_j$：$P_q^{-1}(B_j)$ 有 $\gcd(l_j,q)$ 个连通分量，各转角 $2\pi l_j/\gcd(l_j,q)$。

### 8.4 Lemma 5.4（边界 index 贡献）

若边界分量转角为 $2\pi\phi$（$\phi\in\mathbb{Z}$），则对其 **exterior face + 边界顶点**，任意非零 $\tilde{\rho}^{\alpha,\beta}$ 的总 index 贡献为 $\phi+1$。

（HGP 允许 $\phi<-1$，推广了 Gortler 的边界转角设定。）

### 8.5 Lemma 6.2（Gauss–Bonnet）

$|C|$ = **锥点个数**：

$$
q|C| - \sum_{v_i \in C} k_i + \sum_{j=1}^{m} l_j = q(2 - 2g - m).
\tag{GB}
$$

(GB)+(RH) 保证的是 Theorem 6.1 的**代数闭合**，**不**保证 $\chi(\tilde{S}_q)=1$。

### 8.6 例 C 的 $\chi$

穿孔环面 $g=1,m=1$，$\chi(S)=-1$；两锥 $k=5$，$q=4$；边界 $l=-2$。得 $\chi(\tilde{S}_q)=-10$（亏格 5、双穿孔）——远非圆盘，Theorem 6.1 仍适用。

---

## 9. Theorem 6.1：完整 index counting 证明

### 9.1 定理陈述（BCW17）

> **Theorem 6.1.** 设 $f$ 为 $S$ 上的 $q$-CCM，锥点与 holonomy 角给定旋转约束。若**锥三角形与边界三角形**均正向定向，且诱导度量实现目标锥角与边界转角，则 $f$ **局部单射**。

### 9.2 证明策略（五步）

```text
q-CCM f
  → 构造 Ŝ_q 与 mostly harmonic 1-forms ρ̃^{α,β}
  → 补 exterior faces 得闭网格，写 index 公式 (5)
  → RHS：用 (RH)+(GB)+Lemma 5.2/5.3 化成 (9)
  → LHS：内部 s≤0 + 分歧点贡献 + 边界贡献 = (10)
  → LHS=RHS ⇒ s=0 ⇒ 内部全 wheel ⇒ f 局部单射
```

### 9.3 归约：局部单射 ⟺ 覆盖上全 wheel

要证 $f$ 局部单射，只需证：对任意非零 $\tilde{\rho}^{\alpha,\beta}$，$\tilde{S}_q$ 上所有**非分歧内部顶点**满足 $\mathrm{ind}=0$（故为 wheel）。

理由：

1. $S_c$ 内部非 seam 顶点在 $\tilde{S}_q$ 上有 $q$ 个原像；若皆为 wheel，则 $f$ 在这些点局部单射；
2. seam 非锥顶点：各扇区经旋转粘合后，在 $\tilde{S}_q$ 上拼成完整 1-环；wheel 条件保证拼合后无翻转；
3. 锥点本身允许角 $\neq 2\pi$，不要求为 wheel——其贡献单独计入 LHS。

### 9.4 闭网格与 RHS（式 (9)）

对 $\tilde{S}_q$ 每个边界连通分量外加 **exterior face**，得闭网格 $\bar{S}_q$。对任意非零 $\tilde{\rho}$：

$$
\sum_v \mathrm{ind}(v)+\sum_f \mathrm{ind}(f)=\chi(\bar{S}_q).
\tag{5}
$$

由 (RH)、Lemma 5.2/5.3，并计入外侧面使 $\chi(\bar{S}_q)=\chi(\tilde{S}_q)+\sum_j\gcd(l_j,q)$：

$$
\begin{aligned}
\mathrm{RHS}
&= q(2-2g-m)-\sum_{P\in\mathcal{R}}(e_P-1)+\sum_j\gcd(l_j,q)\\
&= q(2-2g-m)-q|C|+\sum_{v_i\in C}\gcd(k_i,q)+\sum_j\gcd(l_j,q).
\end{aligned}
$$

再用 (GB) 消去 $q(2-2g-m)-q|C|$，得论文式 (9)：

$$
\mathrm{RHS}
= \sum_{v_i\in C}\gcd(k_i,q)+\sum_j\gcd(l_j,q)
-\sum_{v_i\in C}k_i+\sum_j l_j.
\tag{9}
$$

### 9.5 LHS（式 (10)）

将顶点/面分成三类：

**（i）内部贡献 $s$。**  
非锥、非边界的顶点与内部面：mostly harmonic ⟹ 各 $\mathrm{ind}\le 0$，记其总和为 $s\le 0$。若某处非 wheel，则某 $\tilde{\rho}$ 使该项严格负。

**（ii）分歧点（锥点原像）。**  
锥点 $v_i$ 上有 $\gcd(k_i,q)$ 个分歧点；每个在覆盖上相当于锥角 $2\pi N$ 的奇异点，其中

$$
N=\frac{k_i}{\gcd(k_i,q)}.
$$

类比 Gortler：此类点对非零 $\tilde{\rho}$ 的 index 贡献为 $1-N$。故锥点总贡献

$$
\sum_{v_i\in C}\gcd(k_i,q)\Bigl(1-\frac{k_i}{\gcd(k_i,q)}\Bigr)
=\sum_{v_i\in C}\bigl(\gcd(k_i,q)-k_i\bigr).
$$

（定理假设「诱导锥角正确」保证 $N$ 取上述值；「锥三角形正向」保证符号/定向与 index 公式相容。）

**（iii）边界 + exterior face。**  
由 Lemma 5.3/5.4：每个基边界 $B_j$ 对应 $\gcd(l_j,q)$ 个覆盖边界分量，各转角 $2\pi\,l_j/\gcd(l_j,q)$，每个贡献 $1+l_j/\gcd(l_j,q)$。总和

$$
\sum_j\bigl(\gcd(l_j,q)+l_j\bigr).
$$

（「边界三角形正向」+「转角正确」保证 Lemma 5.4 适用。）

于是

$$
\mathrm{LHS}
= s
+\sum_{v_i\in C}\bigl(\gcd(k_i,q)-k_i\bigr)
+\sum_j\bigl(\gcd(l_j,q)+l_j\bigr).
\tag{10}
$$

### 9.6 闭合：$s=0$

由 (5)：$\mathrm{LHS}=\mathrm{RHS}$。对比 (9)(10)，锥与边界项相消，得

$$
s=0.
$$

但 $s\le 0$ 且为各项 $\le 0$ 之和 ⟹ **每一项为 0**。故对任意非零 $\tilde{\rho}^{\alpha,\beta}$，内部非分歧顶点 $\mathrm{ind}=0$ ⟹ 全为 **wheel**。

再由 §9.3：$f$ 在 $S_c$ 内部无翻转；seam 顶点经扇区等距拼接亦为 wheel ⟹ **$f$ 在 $S$ 上局部单射**。∎

### 9.7 例 A 逐步验算（论文 §6.1）

圆盘：$g=0,m=1$，$q=4$，一锥 $k=3$（锥角 $3\pi/2$）。由 (GB)：$4\cdot 1-3+l=4$ ⟹ **$l=3$**（基边界转角 $3\pi/2$）。

覆盖上：1 个分歧点，$e_P=4$，锥角 $6\pi$；1 个边界分量，转角 $2\pi l/\gcd(l,q)=6\pi$。

- **RHS**（用 (RH) 中间式）：$q\chi(S)-\sum(e_P-1)+\sum\gcd(l)=4\cdot 1-(4-1)+1=4-3+1=2$。
- **LHS**：分歧点贡献 $1-N=1-3=-2$；边界（Lemma 5.4，$\phi=3$）贡献 $\phi+1=4$。故 $\mathrm{LHS}=s+(-2)+4$。
- $\mathrm{LHS}=\mathrm{RHS}$ ⟹ **$s=0$**。✓

### 9.8 为何只需约束 $F_{cb}$

Theorem 6.1 把「整体局部单射」**归约**为：锥邻域与边界邻域三角形正向 + 角正确。因此 **HGP 的 SOCP 只需对 $F_{cb}$（含锥或边界顶点的三角形）加 Lipman frame；内部单射由 index 预算自动保证**——这是算法设计的理论依据。







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
