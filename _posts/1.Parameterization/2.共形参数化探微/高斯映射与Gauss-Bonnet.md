---
layout: post
title: "高斯映射与 Gauss-Bonnet 定理"
categories: ["Parameterization", "Parameterization-ConformalMapping"]
mathjax: true
---

> 本文从 [离散微分几何](离散微分几何%20(copy).md) 中抽离：**高斯映射**、**拓扑度（正/负覆盖）**、**戴克公式**与 **Gauss-Bonnet（局部 / 全局 / 离散）**。曲线曲率、法曲率与测地曲率、主曲率、Theorema Egregium 仍见原文。

## 1. 高斯映射（Gauss map）

曲面上每个点 $p \in S$ 存在唯一的单位法向量 $N(p)$，垂直于其切平面。将 $N(p)$ 平移到单位球面 $S^2$ 的对应位置，就得到了**高斯映射**

$$
N:\; p \mapsto N(p)\in S^2
$$

（下文亦记作 $\varphi$。）

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251124184622415.png)

**高斯映射的微分（Weingarten 映射）**：$\mathrm{d}N(X)$ 称为 **Weingarten 映射**（形状算子），它量化了法向量随曲面弯曲的变化速率：

$$
\mathrm{d}N_p(v) = \frac{\partial N}{\partial v} = -W_p(v).
$$

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260617121044362.png" alt="image-20260617121044362" style="zoom: 33%;" />

![image-20260617121329525](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260617121329525.png)

![image-20260617122126496](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260617122126496.png)

在局部坐标下，$W = I^{-1}\cdot II$，其中 $I$ 是第一基本形式矩阵，$II$ 是第二基本形式矩阵。

**Gauss 曲率与 Gauss 映照的关系**：

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251125150744255.png)

曲面上一点 $p$ 的高斯曲率 $K(p)$ 定义为该点高斯映射的面积放大率：

$$
K(p) = \lim_{A \to 0} \frac{\mathrm{Area}\bigl(N(A)\bigr)}{\mathrm{Area}(A)}.
$$

这等价于 Weingarten 映射的行列式：

$$
K = \frac{LN-M^2}{EG-F^2} = \det(W).
$$

---

## 2. 拓扑度：正覆盖与负覆盖

$K=\det(W)$ 是**局部**的面积放大率。把整张闭曲面 $M$ 映到单位球面 $S^2$ 时，还要问：球面被盖了几层？这就是高斯映射的**拓扑度**（Brouwer degree）$\deg(N)$。

### 2.1 正覆盖与负覆盖

高斯映射 $N:M\to S^2$ 把曲面上每一点的单位法向送到天球上的一点。对天球上一个「普通」方向 $q\in S^2$（正则值），原像 $N^{-1}(q)$ 是曲面上有限个点——每个点表示「曲面在这里的法向正好指向 $q$」。

在每个原像点 $p$，看 $N$ 是否保持定向：

| | **正覆盖**（$K(p)>0$） | **负覆盖**（$K(p)<0$） |
|:---|:---|:---|
| 局部形状 | 椭圆点：碗状 / 凸或凹 | 双曲点：马鞍 |
| $\mathrm{d}N_p$ | $\det>0$，保向 | $\det<0$，反向 |
| 对天球的贡献 | **$+1$ 层** | **$-1$ 层** |
| 图像直觉 | 法向扫过天球时与球面定向一致 | 法向扫过时「倒着盖」一层 |

因此拓扑度不是「盖了几层」的普通计数，而是**代数层数**：

$$
\deg(N)
=\underbrace{(\text{正覆盖次数})}_{K>0\text{ 的原像个数}}
-\underbrace{(\text{负覆盖次数})}_{K<0\text{ 的原像个数}}
=\sum_{p\in N^{-1}(q)}\operatorname{sign}K(p).
$$

对任意正则值 $q$ 这个差都相同——所以 $\deg(N)$ 是整体不变量，不依赖你盯着天球上哪一个方向。

用面积语言说同一件事：正曲率区域把面积**正向**推到 $S^2$，负曲率区域**反向**推上去；带符号总面积除以 $4\pi$ 就是度：

$$
\deg(N)=\frac{1}{4\pi}\int_M K\,dA
=\frac{1}{4\pi}\Biggl(\int_{K>0}K\,dA+\int_{K<0}K\,dA\Biggr).
$$

（第二项本身为负，相当于减去负覆盖的面积。）

### 2.2 例子

| 曲面 | 正覆盖 | 负覆盖 | $\deg(N)$ |
|:---|:---|:---|:---|
| 凸闭曲面（椭球） | 每个方向恰好 1 次 | 无 | $1-0=1$ |
| 标准球面 | $N=\mathrm{id}$，处处正 | 无 | $1$ |
| 环面 | 外侧（正 $K$）各方向约 1 次 | 内侧孔洞（负 $K$）各方向约 1 次 | $1-1=0$ |

环面是最清楚的对照：外侧像「正着贴」天球，内侧马鞍区像「反着贴」；正、负各盖一层，代数度为零——尽管几何上法向仍然扫过整个球面。

对一般光滑映射 $f:M\to S^2$（$M$ 紧致、定向、无边界），定义相同：

$$
\deg(f)=\sum_{p\in f^{-1}(q)}\operatorname{sign}\bigl(\det\mathrm{d}f_p\bigr),
$$

只是高斯映射时 $\operatorname{sign}(\det\mathrm{d}N)=\operatorname{sign}K$。

---

## 3. 瓦尔特·戴克（Walther von Dyck）公式

德国数学家 **Walther von Dyck**（1856–1934；亦作 Dyck）在 1888 年左右把「任意亏格闭曲面」上的全曲率与 Euler 示性数明确连在一起。对 $\mathbb{R}^3$ 中紧致、定向、无边界的光滑曲面，有

$$
\deg(N)=\frac{1}{2}\,\chi(M),
\tag{Dyck}
$$

或写成更常见的积分形式：

$$
\int_M K\,dA = 2\pi\,\chi(M) = 4\pi\,\deg(N).
$$

这正是**全局 Gauss-Bonnet** 在嵌入曲面 + 高斯映射语言下的版本：

$$
\underbrace{\frac{1}{4\pi}\int_M K\,dA}_{\deg(N)}
=\underbrace{\frac{\chi(M)}{2}}_{\text{拓扑}}.
$$

| 亏格 $g$ | $\chi=2-2g$ | $\deg(N)=\chi/2$ | 全曲率 $\int K$ |
|:---|:---|:---|:---|
| $0$（球面） | $2$ | $1$ | $4\pi$ |
| $1$（环面） | $0$ | $0$ | $0$ |
| $2$ | $-2$ | $-1$ | $-4\pi$ |

**历史位置**：Gauss（局部三角形角盈）、Bonnet（光滑边界的测地曲率项）之后，把公式推广到**任意亏格闭曲面**并写成「全曲率 $=2\pi\chi$」的，主要归功于 Kronecker 与 **von Dyck**；今天口头说的「Gauss–Bonnet 全局定理」，很大一块其实是戴克这一步。

**注意**：$\deg(N)=\chi/2$ 针对的是曲面自身的高斯映射 $N:M\to S^2$。若改用管状邻域边界 $\partial\mathcal{N}\to S^{2}$ 的外法向映射，内外两层会使度数变成 $\chi(M)$（差一个因子 2）——定义不同，不要混用。

### 3.1 用向量场证明戴克公式（进而得全局 GB）

思路：**Poincaré–Hopf** 把 $\chi(M)$ 写成向量场零点指标之和；再造一个与高斯映射咬合的切向量场，使这些指标恰好等于「正覆盖 − 负覆盖」的两倍。

#### 预备：Poincaré–Hopf

设 $M$ 为紧致、定向、无边界的光滑曲面，$X$ 为 $M$ 上只有孤立零点的切向量场。在每个零点 $p$，取小圆绕 $p$ 一圈，看单位化 $X/\|X\|$ 沿切平面转了几圈，得指标 $\operatorname{ind}_p(X)\in\mathbb{Z}$。则

$$
\sum_{p:\,X(p)=0}\operatorname{ind}_p(X)=\chi(M).
\tag{PH}
$$

（与 $X$ 的选取无关——这正是 Euler 示性数的向量场定义。）

#### 构造：常向量的切向投影

取单位向量 $u\in S^2$，使 $u$ 与 $-u$ **都是**高斯映射 $N$ 的正则值（几乎处处成立）。在 $\mathbb{R}^3$ 里放常向量场 $U\equiv u$，再投影到曲面的切平面：

$$
X(p)=u-\bigl\langle u,\,N(p)\bigr\rangle N(p)\in T_p M.
$$

几何上：$X(p)$ 是「常风向 $u$」在曲面切平面上的分量。

**零点**：$\|X(p)\|=0$ ⟺ $u$ 与 $N(p)$ 平行 ⟺

$$
N(p)=u\quad\text{或}\quad N(p)=-u.
$$

即零点集正好是 $N^{-1}(u)\cup N^{-1}(-u)$——天球上方向 $u$ 与 $-u$ 的全部原像（正/负覆盖点）。

#### 关键引理：指标 = 覆盖符号

在每个孤立零点 $p$，

$$
\operatorname{ind}_p(X)=\operatorname{sign}\bigl(\det\mathrm{d}N_p\bigr)=\operatorname{sign}K(p).
$$

对 $N(p)=u$ 与 $N(p)=-u$ **都成立**。

要点（2 维）：Weingarten 映射 $W=-\mathrm{d}N$，且 $\det W=K=\det(\mathrm{d}N)$（二维下 $(-1)^2=1$）。在零点附近把 $X$ 线性化，得到非退化线性场，其指标等于 $\operatorname{sign}(\det W)=\operatorname{sign}K$。因此：

- $K(p)>0$（正覆盖）⟹ $\operatorname{ind}_p=+1$；
- $K(p)<0$（负覆盖）⟹ $\operatorname{ind}_p=-1$。

#### 合成：戴克公式

由 (PH)：

$$
\chi(M)
=\sum_{N(p)=u}\operatorname{ind}_p(X)
+\sum_{N(p)=-u}\operatorname{ind}_p(X)
=\sum_{N(p)=u}\operatorname{sign}K(p)
+\sum_{N(p)=-u}\operatorname{sign}K(p).
$$

右边两项分别是正则值 $u$ 与 $-u$ 处的**代数覆盖数**。但拓扑度与正则值无关（§2）：

$$
\sum_{N(p)=u}\operatorname{sign}K(p)
=\deg(N)
=\sum_{N(p)=-u}\operatorname{sign}K(p).
$$

故

$$
\chi(M)=2\deg(N)
\qquad\Longleftrightarrow\qquad
\deg(N)=\frac12\chi(M).
\tag{Dyck}
$$

再用 §2 的面积公式 $\deg(N)=\dfrac{1}{4\pi}\displaystyle\int_M K\,dA$，立刻得到**闭曲面的全局 Gauss-Bonnet**：

$$
\int_M K\,dA=4\pi\deg(N)=2\pi\chi(M).
\tag{GB / 闭}
$$





---

## 4. Gauss-Bonnet 定理

**曲率的总和只与曲面的「洞数」有关，与具体的弯曲方式无关。**

先分清两件事，否则容易觉得「局部公式和全局公式长得一样」：

- **局部**：一块小区域上，**角盈（或角亏）= 这块上的全曲率**——纯几何，不谈整张曲面的亏格。
- **全局**：整张曲面积完，全曲率被拓扑 $\chi(M)$ 锁死。

中间那条「带边界区域」的通式，和全局公式长得像，是因为**本来就是同一条恒等式**；差别只在积分区域是曲面片 $D$ 还是整张 $M$。戴克公式则是全局定理用高斯映射度写出的版本。

### 5.1 局部：角盈 = 全曲率

最干净的局部形式是**测地三角形**（三边都是测地线，$\kappa_g\equiv 0$）。设内角为 $\alpha_1,\alpha_2,\alpha_3$，则

$$
\int_\Delta K\,dA = \alpha_1+\alpha_2+\alpha_3 - \pi.
\tag{局部 GB / 角盈}
$$

左边是三角形上的**全曲率**，右边是相对平面三角形的**角盈**（excess）：

> **角盈 = 全曲率。**

| 曲面 | 内角和 | 角盈 $\sum\alpha_i-\pi$ | 全曲率 |
|:---|:---|:---|:---|
| 平面 | $=\pi$ | $0$ | $0$ |
| 球面（正 $K$） | $>\pi$ | $>0$ | $>0$ |
| 双曲（负 $K$） | $<\pi$ | $<0$ | $<0$ |

推广到测地 $n$ 边形：$\displaystyle\int_D K\,dA=\sum\alpha_i-(n-2)\pi$。

若边界不是测地线，还要加上边界测地曲率；拐角用外角 $\theta_i$ 记账，通式写成

$$
\int_D K\,dA + \int_{\partial D}\kappa_g\,ds + \sum_i\theta_i = 2\pi\chi(D)
$$

（$D$ 为拓扑圆盘时右端 $=2\pi$）。测地三角形时 $\kappa_g=0$、$\theta_i=\pi-\alpha_i$，立刻回到 $\int K=\sum\alpha_i-\pi$。  
**局部定理的核心仍是角盈公式**；通式只是把「弯边界 / 拐角」也算进去。

### 5.2 全局：全曲率 = 拓扑

对整张紧致定向曲面 $M$（可有边界）：

$$
\int_M K\,dA + \int_{\partial M} \kappa_g\,ds = 2\pi\chi(M).
\tag{全局 GB}
$$

- **闭曲面**：$\displaystyle\int_M K\,dA = 2\pi\chi(M)=2\pi(2-2g)$。总曲率只看亏格。
- **有边界**：真实边界的 $\kappa_g$ 参与平衡。

球面总曲率恒 $4\pi$，环面恒 $0$（外侧正、内侧负必须抵消）——这是**全局**结论，不是某个三角形的角盈。闭曲面情形与 §3 戴克公式一致：$\int K=4\pi\deg(N)=2\pi\chi$。**拓扑证明**见 §3.1（投影常向量场 + Poincaré–Hopf → 戴克 → GB）。

### 5.3 为什么两条公式「长得很像」？

因为通式对任意区域都成立：

$$
\underbrace{\int_{\text{区域}} K\,dA + \text{边界项}}_{\text{几何}} = 2\pi\,\chi(\text{区域}).
$$

| | 局部（典型说法） | 全局 |
|:---|:---|:---|
| 区域 | 一个三角形 / 小曲面片 $D$ | 整张 $M$ |
| 你记住的式子 | $\int_\Delta K=\sum\alpha_i-\pi$（角盈） | $\int_M K=2\pi\chi(M)$ |
| 右端含义 | 相对平面的角盈（几何） | Euler 示性数（拓扑） |
| 回答的问题 | 「这块有多弯？」 | 「整张曲面总曲率能是多少？」 |

把 $M$ 剖成许多小三角形，对每个写局部角盈公式再相加：内部边的边界项抵消，只剩总曲率与真实边界，右端累加成 $2\pi\chi(M)$——**全局 = 局部拼起来**。所以通式长得像全局，并不矛盾；真正要分开记的是：

- 局部口诀：**角盈 = 全曲率**；
- 全局口诀：**总曲率 = $2\pi\chi$**（闭曲面时再写成 $\deg(N)=\chi/2$）。

## 5. 离散高斯曲率（角亏）

对于三角网格上的内部顶点 $v_i$，其离散高斯曲率定义为**角亏**——$2\pi$ 减去该顶点周围所有三角形的内角之和：

$$
K(v_i) = 2\pi - \sum_{v_j \in N_1(v_i)} \theta_j,
$$

其中 $\theta_j$ 为顶点 $v_i$ 处各相邻三角形的内角（angle defect / 角度亏量）。

对于带边界的离散曲面，**边界点测地曲率**：

$$
\kappa_g(v_i) = \pi - \sum \theta_j.
$$

这是局部 Gauss-Bonnet 在一环邻域上的离散化：该有 $2\pi$，实际内角和少了多少，就是顶点处集中的全曲率。

三角网格上的**全局**离散 Gauss-Bonnet：

$$
\sum_{v_i \in V} K(v_i) = 2\pi\chi(M) = 2\pi(V - E + F).
$$

（有边界时，边界顶点用 $\kappa_g(v_i)=\pi-\sum\theta_j$ 计入左端。）其中每个 $K(v_i)$ 来自**局部**角亏，求和后满足**全局**拓扑约束。

如下图，环面总角度亏量趋近于 0（$\chi=2-2g=0$）。

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251028134522912.png)

---

## 6. 一条线串起来

```text
高斯映射 N : M → S²
    │  局部：K = det(dN) = 面积放大率
    │  整体：deg(N) = 正覆盖 − 负覆盖 = (1/4π)∫K
    ▼
投影常向量场 X + Poincaré–Hopf
    │  零点 = N⁻¹(u) ∪ N⁻¹(−u)，ind = sign K
    │  χ = 2 deg(N)
    ▼
戴克：deg(N) = χ(M)/2
    │
    ▼
全局 GB（闭）：∫K = 2π χ(M)
    │  局部角盈拼起来 / 有边界加 κ_g
    ▼
离散：Σ 角亏(vᵢ) = 2π (V−E+F)
```

与参数化的关系见 [离散微分几何](离散微分几何%20(copy).md) 中的 **Theorema Egregium**：高斯曲率内蕴 ⟹ 非零 $K$ 的曲面无法无扭曲展开。
