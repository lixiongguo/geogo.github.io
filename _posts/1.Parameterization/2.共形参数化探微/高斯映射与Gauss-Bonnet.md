---
layout: post
title: "高斯映射与 Gauss-Bonnet 定理"
categories: ["Parameterization", "Parameterization-ConformalMapping"]
mathjax: true
---

##  角盈（angular excess）

平面上任意三角形内角和恒为 $\pi$。曲面上画一个「三角形」（三边为测地线），内角和一般不再是 $\pi$——多出来（或少掉）的那一截，就叫**角盈**：

$$
\varepsilon(\Delta)=\alpha_1+\alpha_2+\alpha_3-\pi.
$$

| 曲面 | 内角和 | 角盈 $\varepsilon$ | 直观 |
|:---|:---|:---|:---|
| 平面 / 柱面（$K=0$） | $=\pi$ | $0$ | 与欧氏几何相同 |
| 球面（$K>0$） | $>\pi$ | $>0$ | 「鼓起来」，角被撑大 |
| 双曲面（$K<0$） | $<\pi$ | $<0$（角亏） | 「凹下去」，角被收小 |

经典例子：单位球面上以三条经纬测地线围成的三角形，若三内角都是直角，则 $\varepsilon=3\cdot\frac{\pi}{2}-\pi=\frac{\pi}{2}$，而该三角形恰好盖住球面的 $1/8$，面积 $A=\frac{\pi}{2}$（单位球面 $K\equiv 1$）——此时 $\varepsilon/A=1=K$，角盈与面积之比就是曲率。

### 高斯曲率的内蕴定义：角盈 / 面积

**内蕴**是说：只用量度（测地距离、测地三角形内角）就能定义，不必知道曲面如何嵌进 $\mathbb{R}^3$，也不必用法向量。

取包含点 $p$ 的测地三角形 $\Delta$，面积记为 $A(\Delta)$。局部 Gauss-Bonnet 给出

$$
\int_\Delta K\,dA = \varepsilon(\Delta).
$$

当 $\Delta$ 缩向 $p$、$A(\Delta)\to 0$ 时，$\int_\Delta K\,dA \approx K(p)\,A(\Delta)$，故

$$
K(p)=\lim_{\Delta\ni p,\,A(\Delta)\to 0}\frac{\varepsilon(\Delta)}{A(\Delta)}.
\tag{内蕴定义}
$$

口诀：**高斯曲率 = 角盈密度**——单位面积上「内角和相对平面多出来多少」。

| 曲面 | 小三角形 | $\varepsilon/A$ | $K(p)$ |
|:---|:---|:---|:---|
| 平面 | 角盈 $\to 0$ | $\to 0$ | $0$ |
| 单位球面 | 角盈 $\approx A$ | $\to 1$ | $1$ |
| 马鞍面 | 角亏（$\varepsilon<0$） | $<0$ | $<0$ |

推广到测地 $n$ 边形：相对平面 $(n-2)\pi$ 的超出量

$$
\varepsilon=\sum_{i=1}^{n}\alpha_i-(n-2)\pi.
$$

**角亏（angle defect）**是同一概念的另一面：在三角网格顶点处，平面上该有 $2\pi$，实际一环内角和少了多少，

$$
K(v)=2\pi-\sum\theta_j,
$$



## 2. 高斯映射（Gauss map）

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

**Weingarten 映射的几何含义**：

- $\mathrm{d}N$ 是高斯映射 $N$ 的微分；
- 在点 $p$ 处，$\mathrm{d}N(X)$ 给出沿切方向 $X$ 移动时法向的变化率；
- 单位法向的变化不能有法向分量，故 $\mathrm{d}N(X)\in T_p M$（恒切于曲面）；
- 也可把 $\mathrm{d}N(X)$ 看成单位球 $S^2$ 上的切向量（$N(p)\in S^2$ 处的切空间）。

**例：参数化圆柱面** $f(u,v)=(\cos u,\,\sin u,\,v)$：

$$
\begin{aligned}
\mathrm{d}f &= (-\sin u,\,\cos u,\,0)\,\mathrm{d}u + (0,\,0,\,1)\,\mathrm{d}v,\\
N &= (-\sin u,\,\cos u,\,0)\times(0,\,0,\,1) = (\cos u,\,\sin u,\,0),\\
\mathrm{d}N &= (-\sin u,\,\cos u,\,0)\,\mathrm{d}u.
\end{aligned}
$$

沿 $\partial/\partial u$ 方向的法曲率（圆截面弯曲，半径 $=1$）：

$$
\kappa_n\!\left(\frac{\partial}{\partial u}\right)
=\frac{\bigl\langle \mathrm{d}f(\partial_u),\,\mathrm{d}N(\partial_u)\bigr\rangle}
{\bigl|\mathrm{d}f(\partial_u)\bigr|^2}
=\frac{(-\sin u,\,\cos u,\,0)\cdot(-\sin u,\,\cos u,\,0)}
{|(-\sin u,\,\cos u,\,0)|^2}
=1.
$$

沿 $\partial/\partial v$ 有 $\mathrm{d}N(\partial_v)=0$，故 $\kappa_n(\partial_v)=0$。两主曲率 $1$ 与 $0$ ⟹ **$K=\kappa_1\kappa_2=0$**（柱面可展，与 §1 角盈为零一致）。

在局部坐标下，$W = I^{-1}\cdot II$，其中 $I$ 是第一基本形式矩阵，$II$ 是第二基本形式矩阵。

**Gauss 曲率与 Gauss 映照的关系**（外蕴写法，与 §1 角盈/面积内蕴定义等价）：

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251125150744255.png)

曲面上一点 $p$ 的高斯曲率也可写为高斯映射的**面积放大率**：

$$
K(p) = \lim_{A \to 0} \frac{\mathrm{Area}\bigl(N(A)\bigr)}{\mathrm{Area}(A)}.
$$

这等价于 Weingarten 映射的行列式：

$$
K = \frac{LN-M^2}{EG-F^2} = \det(W).
$$

---

## 3. 拓扑度：正覆盖与负覆盖

$K=\det(W)$ 是**局部**的面积放大率。把整张闭曲面 $M$ 映到单位球面 $S^2$ 时，还要问：球面被盖了几层？这就是高斯映射的**拓扑度**（Brouwer degree）$\deg(N)$。

### 3.1 正覆盖与负覆盖

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

### 3.2 例子

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

德国数学家 **Walther von Dyck**在 1888 年左右把「任意亏格闭曲面」上的全曲率与 Euler 示性数明确连在一起。对 $\mathbb{R}^3$ 中紧致、定向、无边界的光滑曲面，有

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

### 4.1 用向量场证明戴克公式（进而得全局 GB）

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

右边两项分别是正则值 $u$ 与 $-u$ 处的**代数覆盖数**。但拓扑度与正则值无关（§3）：

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

再用 §3 的面积公式 $\deg(N)=\dfrac{1}{4\pi}\displaystyle\int_M K\,dA$，立刻得到**闭曲面的全局 Gauss-Bonnet**：

$$
\int_M K\,dA=4\pi\deg(N)=2\pi\chi(M).
\tag{GB / 闭}
$$

#### 证明结构一览

```text
Poincaré–Hopf：Σ ind(X) = χ(M)
        ▲
        │  X = 常向量 u 的切向投影
        │  零点 = N⁻¹(u) ∪ N⁻¹(−u)
        │  ind = sign K  （正覆盖 +1，负覆盖 −1）
        │
Σ sign K|_{u} + Σ sign K|_{-u} = deg(N) + deg(N) = 2 deg(N)
        │
        ▼
戴克：deg(N) = χ/2
        │  deg = (1/4π)∫K
        ▼
全局 GB：∫_M K dA = 2π χ(M)
```

**与正/负覆盖的关系**：$u$ 与 $-u$ 各贡献一份相同的 $\deg(N)$，所以出现因子 $2$，戴克公式里才是 $\chi/2$ 而不是 $\chi$。

**有边界时**：还需边界测地曲率项；完整式见 §5.2。局部角盈（§1）是另一条几何入口，与上述拓扑证明互补。

---

## 5. Gauss-Bonnet 定理

**曲率的总和只与曲面的「洞数」有关，与具体的弯曲方式无关。**

先分清两件事（角盈见 §1），否则容易觉得「局部公式和全局公式长得一样」：

- **局部**：一块小区域上，**角盈（或角亏）= 这块上的全曲率**——纯几何，不谈整张曲面的亏格。
- **全局**：整张曲面积完，全曲率被拓扑 $\chi(M)$ 锁死。

中间那条「带边界区域」的通式，和全局公式长得像，是因为**本来就是同一条恒等式**；差别只在积分区域是曲面片 $D$ 还是整张 $M$。戴克公式则是全局定理用高斯映射度写出的版本。

### 5.1 局部：角盈 = 全曲率

§1 已引入角盈。局部 Gauss-Bonnet 说的正是：对测地三角形，

$$
\int_\Delta K\,dA = \varepsilon(\Delta)=\alpha_1+\alpha_2+\alpha_3 - \pi.
\tag{局部 GB}
$$

> **角盈 = 全曲率。**

球面直角三角形 $\varepsilon=\pi/2$ 且面积 $=\pi/2$（$K=1$）即其特例。测地 $n$ 边形：$\displaystyle\int_D K\,dA=\sum\alpha_i-(n-2)\pi$。

若边界不是测地线，还要加上边界测地曲率；拐角用外角 $\theta_i$ 记账，通式写成

$$
\int_D K\,dA + \int_{\partial D}\kappa_g\,ds + \sum_i\theta_i = 2\pi\chi(D)
$$

（$D$ 为拓扑圆盘时右端 $=2\pi$）。测地三角形时 $\kappa_g=0$、$\theta_i=\pi-\alpha_i$，立刻回到 $\int K=\varepsilon$。  
**局部定理的核心仍是角盈公式**；通式只是把「弯边界 / 拐角」也算进去。离散角亏 $K(v)=2\pi-\sum\theta_j$ 是同一思想在顶点一环上的版本（§1、§6）。

### 5.2 全局：全曲率 = 拓扑

对整张紧致定向曲面 $M$（可有边界）：

$$
\int_M K\,dA + \int_{\partial M} \kappa_g\,ds = 2\pi\chi(M).
\tag{全局 GB}
$$

- **闭曲面**：$\displaystyle\int_M K\,dA = 2\pi\chi(M)=2\pi(2-2g)$。总曲率只看亏格。
- **有边界**：真实边界的 $\kappa_g$ 参与平衡。

球面总曲率恒 $4\pi$，环面恒 $0$（外侧正、内侧负必须抵消）——这是**全局**结论，不是某个三角形的角盈。闭曲面情形与 §4 戴克公式一致：$\int K=4\pi\deg(N)=2\pi\chi$。**拓扑证明**见 §4.1（投影常向量场 + Poincaré–Hopf → 戴克 → GB）。

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

## 6. 离散高斯曲率（角亏）

对于三角网格上的内部顶点 $v_i$，其离散高斯曲率定义为**角亏**——$2\pi$ 减去该顶点周围所有三角形的内角之和：

$$
K(v_i) = 2\pi - \sum_{v_j \in N_1(v_i)} \theta_j,
$$

其中 $\theta_j$ 为顶点 $v_i$ 处各相邻三角形的内角（angle defect / 角度亏量）。

对于带边界的离散曲面，**边界点测地曲率**：

$$
\kappa_g(v_i) = \pi - \sum \theta_j.
$$

这是 §1 角盈思想在顶点一环上的离散化：该有 $2\pi$，实际内角和少了多少，就是顶点处集中的全曲率。

三角网格上的**全局**离散 Gauss-Bonnet：

$$
\sum_{v_i \in V} K(v_i) = 2\pi\chi(M) = 2\pi(V - E + F).
$$

（有边界时，边界顶点用 $\kappa_g(v_i)=\pi-\sum\theta_j$ 计入左端。）其中每个 $K(v_i)$ 来自**局部**角亏，求和后满足**全局**拓扑约束。

如下图，环面总角度亏量趋近于 0（$\chi=2-2g=0$）。

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251028134522912.png)

