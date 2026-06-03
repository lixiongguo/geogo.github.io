---
layout: post
category: Parameterization
categories: ["Parameterization", "Parameterization-DifferentialForm"]
title: "第3章 §3.3 Gortler 1-form方法与q-CCM"
---

 **$q$-CCM** 可以看作 CCM 在**多边界、任意亏格**上的推广：内部顶点仍满足正权重凸组合（对应后文公式 (7)(8) 的调和条件），但在 seam 上额外加入 $q$ -fold 旋转约束 $e^{i2\pi r/q}$。

**与 HGP / q-CCM 的关系**：HGP 在覆盖空间 $\tilde{S}_q$ 上求**分段调和**的复坐标 $z = u + iv$，最小化 $\|Lz\|^2$（调和能量），并在 seam 上施加旋转约束 (6)。因此 q-CCM 可以理解为：**在 branched cover 上的调和映照 + 离散凸组合单射性保证**。

**Eells–Sampson 定理**（连续理论背景）：若目标流形 $(N,h)$ 具有非正截面曲率（如 $\mathbb{R}^2$），则任意同伦类的调和映射存在且光滑。这是调和映射理论存在性的经典结果；在参数化实践中，更常用的是离散线性系统直接求解。



与 Tutte 嵌入定理的对照：

| | 连续（Rado） | 离散（Tutte / Floater） |
| -- | ------------ | ----------------------- |
| 域 | Jordan 域 $\Omega$ | 3-连通平面三角网格 |
| 边界条件 | $\partial\Omega \to \partial D$ 同胚 | 边界顶点固定到**严格凸**多边形 |
| 内部条件 | $\Delta u = 0$ | $v_i = \sum_j w_{ij} v_j$，$w_{ij} > 0$ |
| 结论 | 调和映射是同胚 | 平面嵌入无自交、三角面正面积 |

Tutte (1963) 与 Floater (1997) 的离散结果可以看作 Rado 定理在**分段线性、凸组合**设定下的组合版本。Gortler 的 index counting 方法则进一步把这一单射性论证**代数拓扑化**，使结论可推广到多边界与高亏格（通过 $q$-fold branched cover 把 singular 点转化为 wheel 结构）。


---
这篇文章提出了一种对**任意亏格（arbitrary genus）**曲面进行参数化的方法，能够同时保证 **局部单射（local injectivity）** 与 **无缝（seamless）**，且计算效率较高。其核心贡献是定义了 **$q$-CCM（$q$-convex combinatorial map，凸组合映射）**，其中 $q$ 用于约束角度为 $2\pi/q$，对于四边形网格化取$q=4$，这是对经典 **Tutte 参数化** 和 **Gortler 凸组合方法**的推广。

### 全文逻辑导图

建议按下面顺序理解本文：

1. **对象层**：什么是离散 1-形式（边上的变量），以及 exact / closed / co-closed / harmonic 的关系。  
2. **单射层**：用 $\operatorname{scg}$ 定义 index，再用离散 Poincare-Hopf 公式给出全局守恒。  
3. **局部判据层**：顶点分型（边界 / regular / singular）与 wheel / doubly-wheel 如何把“无翻折”变成组合判据。  
4. **推广层**：从 Tutte（单连通凸边界）推广到 $q$-CCM（任意拓扑）。  
5. **全局层**：在 genus $g>0$ 时用 $2g$ 维调和空间调节 period，得到无缝参数化。

可以把主线概括成一句话：  
**局部可积（1-形式） + 全局守恒（index） + 邻域可嵌入（wheel） + 周期控制（harmonic period）**。

### Gortler 的凸组合参数化框架

下面通过离散 1-形式（discrete one form）证明 Tutte 定理，并将基本结论推广到多边界网格情况。

Tutte 算法仅适用于单连通凸边界；对于多连通非凸边界以及更复杂拓扑，需要 Gortler 等工作的拓展思路。Tong06 的一个关键视角是：用离散 1-形式的符号变化来计数 index，再由 Poincare-Hopf 型结论控制参数化的局部单射性。

记 $\operatorname{scg}_p(v)$ 和 $\operatorname{scg}_p(f)$ 为离散 1-形式 $\rho_{ij}$ 沿顶点或面周围发生正负号变化的次数。对于顶点，考虑从它出发或指向它的半边；对于面，考虑绕面一圈的全部半边。注意这两个值都是正偶数。

于是可以定义 $\rho$ 在顶点或面 $p$ 处的 index：

$$
\operatorname{ind}_{\rho}(p)=1-\frac{\operatorname{scg}_{\rho}(p)}{2}.
$$

由于 $\operatorname{scg}$ 是正偶数，所以 index 是不超过 1 的整数。若某个顶点的 index 为 0，则称其为非奇异顶点。

对闭合亏格为 $g$ 的网格曲面 $S$，非零 1-形式 $\rho$ 满足指标公式：

$$
\sum_{v\in V}\operatorname{ind}(v)+\sum_{f\in F}\operatorname{ind}(f)
=\chi(S)=2-2g.
$$

证明可以由符号变化计数得到：

$$
\begin{aligned}
\sum_{v\in V}\operatorname{ind}(v)+\sum_{f\in F}\operatorname{ind}(f)
&=\frac{1}{2}\sum_{v\in V}(2-\operatorname{scg}(v))
 +\frac{1}{2}\sum_{f\in F}(2-\operatorname{scg}(f))\\
&=V+F-\frac{1}{2}\left(\sum_{v\in V}\operatorname{scg}(v)+\sum_{f\in F}\operatorname{scg}(f)\right)\\
&=V+F-\frac{1}{2}(2E)\\
&=V+F-E\\
&=2-2g.
\end{aligned}
$$

其中 $\sum_v\operatorname{scg}(v)+\sum_f\operatorname{scg}(f)=2E$，因为对任意一条半边 $h$，有 $\rho_h=-\rho_{h'}$，不论 $\rho_h$ 的正负如何，它总会贡献一次符号变化；总的贡献等于半边总数，即边数的两倍。

**Tutte 定理实际上是指标定理（Poincare-Hopf）的推论。**

采用 index counting 方法可证明 Tutte 参数化局部单射性。定理：由 harmonic one form 张成的线性空间是 $2g$ 维。closedness 与 coclosedness 性质与 indices 相关。

> **重点**：  
> 从“边界凸 + 单连通”的经典 Tutte 场景，过渡到“任意拓扑”的关键是：把几何约束写进同调/上同调与调和形式框架。

HGP 算法的理论基础建立在 Gortler 的凸组合参数化之上。  
为避免概念重复，下文直接在前述 index 公式基础上继续展开“closed/co-closed、顶点分型、wheel 判据、q-CCM 与高亏格 period 控制”。

#### Closed / Co-closed 条件

若非零 1-形式 $\rho$ 在某面或顶点 $p$ 处是 **closed** 或 **co-closed** 的，则：

$$
\text{ind}_{\rho}(p) \leq 0
$$

直观上，closed / co-closed 意味着在该处"没有奇异性"，因此指标不会为正。

#### 顶点分型（这篇文章里最该抓住的分类）

从参数化单射性的角度，文中可把顶点理解为三类：

1. **边界顶点（boundary vertices）**  
   由边界条件直接控制，主要承担“外框不翻折”的作用。

2. **内部常规顶点（regular interior vertices）**  
   满足
   $$
   \operatorname{scg}_\rho(v)=2 \;\Longleftrightarrow\; \operatorname{ind}_\rho(v)=0.
   $$
   这类点是“无奇异”的局部区域，参数线在一环内拓扑结构最稳定。

3. **内部奇异顶点（singular interior vertices）**  
   满足
   $$
   \operatorname{scg}_\rho(v)\ge 4 \;\Longleftrightarrow\; \operatorname{ind}_\rho(v)\le -1.
   $$
   它们对应方向场/参数化中的离散奇异性，必须由全局 index 总量约束其数量与位置。

换句话说：**regular 点保证局部，singular 点受全局拓扑守恒约束**，两者合起来才构成可控的参数化结构。

#### 为什么 wheel / doubly-wheel 顶点是关键

文章强调的不是“只看某个指标值”，而是看顶点邻域的**组合结构是否是 wheel**（轮形一环）。  
直观上，wheel 表示：以顶点为中心的一环三角形形成一个有序扇形带，邻接关系没有断裂或交叉。

- **wheel 条件**保证局部拓扑是“盘状邻域”的标准拼接；
- 在此基础上再结合符号变化/角度顺序条件，可排除扇形重叠与反转；
- **doubly-wheel** 可以理解为同时在原网格邻域与对应对偶/符号结构上都保持这种有序轮形，从而把“局部单射”从几何直觉变成可验证的组合判据。

因此在证明中，wheel 顶点之所以关键，是因为它把“映射不重叠”转化成了“邻域循环顺序保持”的离散条件；  
而 index 定理负责全局守恒，wheel 判据负责局部可嵌入，这两者共同完成单射性论证。

### One-Forms on Meshes 的理论主线（补充）

下面按论文主线把“1-形式 -> 参数化”的逻辑补全。

#### 1) 离散 1-形式与参数差分

在网格每条有向边 $(i,j)$ 上定义实数 $\rho_{ij}$，满足反对称性：
$$
\rho_{ij}=-\rho_{ji}.
$$

若存在顶点函数（势函数）$u$ 使得
$$
u_j-u_i=\rho_{ij},
$$
则称 $\rho$ 是 **exact**（恰当）形式。更一般地：
- **closed**：每个面上边积分和为 0；
- **co-closed**：离散余微分为 0（与离散散度对应）；
- **harmonic**：同时 closed 且 co-closed。

论文里参数化并不是直接先求 $(u,v)$，而是先在边上构造满足拓扑与几何约束的 1-形式，再通过积分恢复顶点参数。

#### 2) 从 Tutte 到 q-CCM

经典 Tutte（单连通 + 凸边界）可理解为：构造一个“无正指标奇异点”的离散系统，从而保证局部单射。  
论文把这个思想推广为 **$q$-convex combinatorial map（$q$-CCM）**：

- $q$ 决定允许角度量化单位 $2\pi/q$；
- $q=4$ 时最对应四边形方向场和无缝参数化；
- 通过 1-形式的符号变化 index 约束，把局部翻折风险转成组合拓扑条件。

因此，$q$-CCM 可以看作“把 Tutte 的凸组合思想离散微分化 + 拓扑化”的统一框架。

#### 3) 指标约束为什么能控制单射

你前面写到的
$$
\sum_{v\in V}\operatorname{ind}(v)+\sum_{f\in F}\operatorname{ind}(f)=\chi(S)
$$
是核心约束。它的意义是：奇异性总量受 Euler 示性数锁定，不能随意出现。  
若在构造 1-形式时保证所有局部 index 不为正（或把正 index 限制在可控位置），则可排除大量局部折叠情形，进而得到局部单射性。

这就是论文把“几何单射”转成“拓扑计数 + 线性约束”的关键。

#### 4) 任意亏格上的无缝参数化（与 HGP/Quad 方向的关系）

对于 genus $g>0$，困难不再是局部闭合，而是**全局周期（period）**：沿非平凡同调环路积分可能不为 0。  
论文利用调和 1-形式空间维数 $2g$ 的事实，对周期进行参数化控制：

1. 先解满足局部条件（closed/co-closed）的 1-形式；
2. 再在调和基底上线性组合，调节环路 period；
3. 使最终积分得到的 $(u,v)$ 满足无缝拼接条件（转角/平移跳跃可控且与网格结构一致）。

这一步就是从“局部可积”到“全局无缝”的桥梁，也是后续 HGP 一类方法的理论来源。

#### 5) 对实现者最有用的结论

- **局部不翻折**：通过 index 约束与 closed/co-closed 条件来保证；
- **全局一致性**：通过调和基 + period 约束来保证；
- **高亏格可处理**：关键在于把拓扑复杂度集中到 $2g$ 维调和自由度，而不是在每条边上做非线性全局修补。

从这个角度看，`One-Forms on Meshes` 的贡献不只是“一个参数化算法”，而是提供了一个可复用的理论骨架：  
**离散微分形式（局部） + 同调周期（全局） + 指标定理（单射控制）**。



