---
layout: post
title: "几何变形 — 1.2 补充：Cauchy 重心坐标（Complex Barycentric Coordinates）"
categories: ["Parameterization", "Parameterization-GeometricOptimization"]
mathjax: true
---

前文介绍调和映照时已经用过普通重心坐标：在一个三角形内，函数值由三个顶点值线性插值得到，

$$
f(x)=\alpha f_i+\beta f_j+\gamma f_k.
$$

这种实值重心坐标适合分片线性网格映射；随后通过梯度、cot-Laplace 和边界条件求解离散调和映照。本文讨论的 Cauchy 重心坐标可以看作这个思路在复分析中的延伸：仍然用边界自由度控制内部映射，但不再逐三角形做实值线性插值，而是用 Cauchy 积分公式把边界上的复值数据延拓成区域内部的全纯/调和基函数。

---

Cauchy 重心坐标（Cauchy / Complex Barycentric Coordinates）是一类用复分析构造的二维坐标函数。它们最早用于平面形状变形，核心特点是：

> 用 Cauchy 积分公式把边界上的复值数据延拓到区域内部，得到全纯函数；再由全纯函数和反全纯函数组合出调和映射。

因此它和“扭曲有界调和映射”的关系非常直接：

1. Cauchy 坐标给出一个调和映射空间；
2. 调和性被写进基函数里，不需要额外求解 Laplace 方程；
3. 映射的复导数可以解析计算；
4. 局部单射和扭曲界可以通过 $f_z, f_{\bar z}$ 写成约束。

下面的逻辑按四步展开：先说明为什么需要这种坐标；再从 Cauchy kernel 构造离散坐标；然后把坐标用于调和映射表示；最后用复导数解释局部单射和扭曲约束。


## 1. 为什么需要 Cauchy 重心坐标

在平面变形中，我们希望有一种表示方式满足：

- 给定一个 cage / polygon 边界；
- 边界移动后，内部点自动平滑移动；
- 映射足够光滑；
- 最好能直接控制局部翻转和扭曲。

传统实值重心坐标（如 mean value coordinates、Wachspress coordinates）通常写成：

$$
f(z)=\sum_i \lambda_i(z) w_i,
$$

其中 $\lambda_i(z)$ 是实值坐标，$w_i$ 是变形后 cage 顶点。

这种方式简单直观，但它不天然给出**共形/调和结构**。Cauchy 坐标的思路不同：把平面点看成复数，用复分析构造内部函数。

如果边界上给定一个复值函数 $F(\zeta)$，Cauchy 积分公式启发我们定义：

$$
h(z)=\frac{1}{2\pi i}\oint_{\partial\Omega}
\frac{F(\zeta)}{\zeta-z}\,d\zeta,
\qquad z\in\Omega.
$$

这称为 Cauchy transform。只要 $z$ 在区域内部，$h(z)$ 对 $z$ 是全纯函数。

这一步非常关键：

> Cauchy transform 把边界数据变成内部全纯函数。

全纯函数自动满足 Cauchy-Riemann 方程，因此其实部和虚部都是调和函数。

---
## 2. 基本原理

复重心坐标仍然遵循“用边界控制内部”的思路。设原始 cage 顶点为
$z_j$，变形后的顶点为 $f_j$，如果一组复值坐标函数 $k_j(z)$ 满足

$$
\sum_j k_j(z)=1,\qquad
\sum_j k_j(z)z_j=z,
$$

那么由

$$
g(z)=\sum_j k_j(z)f_j
$$

定义的映射就至少能精确复现平移、旋转和一致缩放，也就是相似变换。换句话说，如果目标顶点本身来自某个相似变换 $f$，即 $f_j=f(z_j)$，那么内部映射也会恢复出同一个 $f$。

这里和实值重心坐标有一个重要差别：复重心坐标通常不要求复现所有仿射变换。若要精确复现一般仿射变换，不仅 $k_j(z)$ 本身要有线性精度，坐标的共轭也必须满足相应的线性精度：

$$
\sum_j \overline{k_j(z)}\,z_j=\overline{z}.
$$

实值重心坐标天然满足这一点，因此通常可以复现仿射变换；复值坐标一般不满足。这个限制在变形里反而常常是优点，因为一般仿射变换包含非一致缩放和剪切，而这些形变容易带来不自然的局部拉伸。Cauchy 坐标更偏向保留共形结构，优先表达旋转与一致缩放。

另一个差别是插值性。传统 Lagrange 型坐标常要求

$$
g(z_j)=f_j,
$$

也就是 cage 顶点必须严格插值到目标顶点。复重心坐标不一定强制这个条件；它更关注由边界数据诱导出的内部映射是否平滑、自然，并在整体上贴近目标边界。放松严格插值后，映射空间更柔和，也更适合和扭曲控制结合。

从连续角度看，设 $\Omega$ 是一个单连通平面区域，边界为光滑闭曲线 $S=\partial\Omega$。对内部点 $z\in\Omega$ 和边界点 $w\in S$，可以引入复核函数

$$
k(w,z):S\times\Omega\to\mathbb C.
$$

它是连续版的“坐标函数”。为了让它像重心坐标一样工作，需要满足两个基本精度条件：

$$
\oint_S k(w,z)\,dw=1,
\qquad
\oint_S k(w,z)w\,dw=z.
$$

注意这里的积分是复积分，其中

$$
dw=T(w)\,ds,
$$

$T(w)$ 是边界在 $w$ 处的单位切向量，$ds$ 是弧长微元。给定边界上的复值目标函数 $f:S\to\mathbb C$ 后，内部映射可以写成

$$
g(z)=\oint_S k(w,z)f(w)\,dw.
$$

因此，构造 Cauchy 重心坐标的核心问题就变成：找到合适的核函数 $k(w,z)$，使它满足常数精度和线性精度，并且产生的内部映射具有全纯/调和结构。下一节的 Cauchy kernel 正是最自然的选择。


## 3. Cauchy kernel 与离散化

连续情形中最自然的核函数是 Cauchy kernel：

$$
C(w,z)=\frac{1}{2\pi i}\frac{1}{w-z}.
$$

它满足前面要求的常数精度和线性精度：

$$
\oint_S C(w,z)\,dw=1,
\qquad
\oint_S C(w,z)w\,dw=z,
$$

因为这正是 Cauchy 积分公式在 $h(w)=1$ 和 $h(w)=w$ 两个特殊函数上的结果。更一般地，如果 $h$ 在区域内全纯且边界上可取值，那么

$$
h(z)=\frac{1}{2\pi i}\oint_S \frac{h(w)}{w-z}\,dw.
$$

所以 Cauchy kernel 不只是满足重心坐标的两个精度条件，它实际上能复现所有全纯函数。把边界上的目标函数 $f:S\to\mathbb C$ 代入，就得到

$$
g(z)=\frac{1}{2\pi i}\oint_S \frac{f(w)}{w-z}\,dw.
$$

这里要区分两件事：Cauchy 积分公式中的 $h$ 是已经定义在整个区域内的全纯函数；而变形问题中的 $f$ 通常只在边界上给定。Cauchy transform 的作用，就是从边界函数 $f$ 生成区域内部的全纯函数 $g$。

实际形状变形中，边界 $S$ 通常是一个多边形 cage。设顶点为

$$
v_0,v_1,\ldots,v_{n-1},
$$

目标边界函数在顶点上的值为 $w_j=f(v_j)$，并在每条边上线性插值。于是连续积分可以拆成逐边积分：

$$
g(z)=\frac{1}{2\pi i}
\sum_j\int_{e_j}\frac{f(w)}{w-z}\,dw.
$$

由于每条边上的 $f(w)$ 对端点值 $w_j,w_{j+1}$ 是线性的，整个 $g(z)$ 对所有顶点目标值也是线性的。因此它可以整理成

$$
g(z)=\sum_j C_j(z)w_j.
$$

这就是离散 Cauchy 重心坐标的来源：每个 $C_j(z)$ 都来自与顶点 $v_j$ 相邻的两条边积分贡献。下一节给出这个逐边积分的闭式形式。

## 4. 从积分形式到顶点坐标

上一节已经说明：当边界函数沿多边形每条边线性插值时，Cauchy transform 可以按顶点目标值分解。本节把这个分解单独写清楚，方便后面进入闭式计算。

设源区域 $\Omega\subset\mathbb{C}$ 的边界是一个逆时针多边形：

$$
\partial\Omega=(v_0,v_1,\ldots,v_{n-1}).
$$

在边界上定义一个分段线性的复值函数 $F$，并令其在顶点处的值为：

$$
F(v_j)=w_j.
$$

其中 $w_j$ 可以理解为目标 cage 顶点或待优化的复系数。

由于 $F$ 沿每条边线性变化，Cauchy transform 对 $w_j$ 也是线性的，因此可以写成：

$$
h(z)=\sum_{j=0}^{n-1} C_j(z) w_j.
$$

这里的 $C_j(z)$ 就是 Cauchy 重心坐标。

换句话说：

> 先用 Cauchy transform 延拓边界函数，再把延拓结果按顶点值 $w_j$ 分解，得到的系数就是 Cauchy 坐标。

它和普通重心坐标一样，也有“线性组合重构函数”的形式；区别在于 $C_j(z)$ 是复值、全纯的。

因此前几节完成的是“坐标怎么来”的部分：从连续 Cauchy 积分，经过多边形边界离散化，得到顶点系数 $C_j(z)$。下一步只剩下计算问题：如何把每条边的积分写成可实现的闭式公式。

---

## 5. 边积分的闭式形式

令第 $j$ 条边为：

$$
e_j=[v_j,v_{j+1}],
$$

边向量为：

$$
a_j=v_{j+1}-v_j.
$$

对边上的点做参数化：

$$
\zeta(t)=v_j+t a_j,\qquad t\in[0,1].
$$

记：

$$
b_j=v_j-z,\qquad b_{j+1}=v_{j+1}-z=b_j+a_j.
$$

边上的边界函数是：

$$
F(\zeta(t))=(1-t)w_j+t w_{j+1}.
$$

代入 Cauchy transform：

$$
\frac{1}{2\pi i}
\int_{e_j}
\frac{F(\zeta)}{\zeta-z}\,d\zeta
=
\frac{a_j}{2\pi i}
\int_0^1
\frac{(1-t)w_j+t w_{j+1}}{b_j+t a_j}\,dt.
$$

因此该边对两个端点 $w_j,w_{j+1}$ 的坐标贡献可以解析算出。

定义：

$$
R_j(z)=\log\frac{b_{j+1}}{b_j}.
$$

则：

$$
\int_0^1 \frac{dt}{b_j+t a_j}
=
\frac{R_j}{a_j},
$$

$$
\int_0^1 \frac{t\,dt}{b_j+t a_j}
=
\frac{a_j-b_jR_j}{a_j^2},
$$

$$
\int_0^1 \frac{(1-t)\,dt}{b_j+t a_j}
=
\frac{b_{j+1}R_j-a_j}{a_j^2}.
$$

所以边 $e_j$ 对 $w_j$ 和 $w_{j+1}$ 的贡献分别是：

$$
\frac{a_j}{2\pi i}
\frac{b_{j+1}R_j-a_j}{a_j^2}w_j,
$$

$$
\frac{a_j}{2\pi i}
\frac{a_j-b_jR_j}{a_j^2}w_{j+1}.
$$

把相邻两条边对同一个顶点的贡献相加，就得到每个 $C_j(z)$。

实现时需要注意：

- 复数 $\log$ 有分支问题；
- 查询点 $z$ 不能落在边界上；
- 多边形边界要保持一致方向；
- 数值上要处理 $z$ 接近边界或顶点的情况。

到这里，Cauchy 坐标已经从抽象积分变成了可计算的离散基函数。接下来讨论它为什么适合做平面变形，以及为什么后文会把它和 bounded distortion 放在一起。

## 6. Cauchy 坐标与变形

在 cage-based deformation 里，用户通常只移动外部 cage，内部网格或图像随之变形。一个实用的变形方法通常要同时满足两点：

- 尽量保留局部细节，例如角度、纹理和小尺度形状；
- 计算足够快，最好每个内部点只依赖 cage 的复杂度。

Cauchy 坐标正好服务于这两个目标。一方面，它产生的函数在区域内部全纯，非退化处接近共形，因此天然适合保持局部角度和细节；另一方面，离散形式只需要对 cage 边界做闭式积分，查询内部点时只和 cage 顶点数有关。

但这里有一个关键限制：对任意给定的源多边形和目标多边形，一般不存在一个全纯映射能严格把每条源边线性映到对应目标边。也就是说，若同时要求：

1. 内部映射全纯/共形；
2. 边界严格插值用户给定的目标 cage；
3. 每条边都按线性对应关系映射；

这三个条件通常是互相冲突的。因此 Cauchy 坐标的做法不是死守严格插值，而是把问题改写为一个有限维全纯函数空间里的优化问题。

更具体地，离散 Cauchy 坐标张成一个函数空间：

$$
g_u(z)=\sum_{j=0}^{n-1} C_j(z)u_j.
$$

其中 $u_j$ 不一定等于用户拖动后的目标顶点，而可以理解为一组“虚拟目标顶点”或边界系数。然后选择一个能衡量变形质量的能量 $E(g_u)$，求

$$
\min_{u_0,\ldots,u_{n-1}} E(g_u).
$$

这样做的含义是：保留 Cauchy 坐标带来的全纯/调和结构，同时通过优化让边界形状、用户约束和局部细节尽量满足需求。后续的扭曲有界调和映射也是类似思路：先用 Cauchy 坐标给出天然调和的函数空间，再用 $f_z$、$f_{\bar z}$ 和 Beltrami 系数对局部翻转与扭曲施加约束。

为了让这个优化框架成立，先要明确 Cauchy 坐标到底提供了哪些结构性保证：全纯、调和、光滑，以及和传统实值重心坐标的区别。

## 7. Cauchy 坐标的关键性质

### 7.1 全纯性

对固定边界数据 $F$，函数：

$$
h(z)=\frac{1}{2\pi i}\oint_{\partial\Omega}
\frac{F(\zeta)}{\zeta-z}\,d\zeta
$$

在 $\Omega$ 内是全纯的。

因此每个坐标函数 $C_j(z)$ 也是全纯函数。

### 7.2 调和性

全纯函数的实部和虚部都是调和函数：

$$
\Delta \operatorname{Re} C_j=0,\qquad
\Delta \operatorname{Im} C_j=0.
$$

所以任何线性组合：

$$
h(z)=\sum_j C_j(z)\phi_j
$$

仍然是全纯函数。

### 7.3 平滑性

在区域内部，Cauchy 坐标是 $C^\infty$ 的。它们不依赖三角网格离散，因此内部没有 piecewise-linear 映射常见的导数跳变。

### 7.4 和传统重心坐标的区别

| 性质 | 实值重心坐标 | Cauchy / Complex 坐标 |
|---|---|---|
| 坐标值 | 实数 | 复数 |
| 构造工具 | 几何权重 / 面积 / 角度 | Cauchy 积分公式 |
| 内部函数 | 通常是调和或近似调和 | 全纯，因此实虚部调和 |
| 是否插值顶点 | 通常插值 | 基本 Cauchy transform 不一定严格按普通 cage 方式插值 |
| 主要优点 | 简单、直观 | 共形/调和结构清晰，导数解析 |
| 主要用途 | cage deformation | conformal / harmonic deformation, bounded distortion optimization |

需要特别注意：Cauchy 坐标不是普通实值重心坐标的简单复数版本。它的核心不是“正权重插值”，而是“通过 Cauchy 积分构造全纯延拓”。

不过，仅有全纯函数还不够表达一般的平面调和变形。下一节使用复分析里的标准分解，把 Cauchy 坐标扩展成“全纯部分 + 反全纯部分”的调和映射空间。

---

## 8. 从全纯函数到调和映射

平面调和映射 $f:\Omega\to\mathbb{C}$ 可以写成：

$$
f(z)=h(z)+\overline{g(z)},
$$

其中 $h,g$ 都是全纯函数。

这是平面调和映射的标准复分解。

利用 Cauchy 坐标分别表示 $h$ 和 $g$：

$$
h(z)=\sum_j C_j(z)\phi_j,
$$

$$
g(z)=\sum_j C_j(z)\psi_j.
$$

于是调和映射写成：

$$
\boxed{
f(z)=
\sum_j C_j(z)\phi_j
+
\overline{\sum_j C_j(z)\psi_j}
}
$$

这就是 bounded distortion harmonic mapping 中最常用的表示：

$$
f(z)=C(z)\phi+\overline{C(z)\psi}.
$$

其中：

- $C(z)$：Cauchy 坐标行向量；
- $\phi$：全纯部分系数；
- $\psi$：反全纯部分系数。

如果在一组采样点 $z_i$ 上计算，矩阵形式为：

$$
x' = C\phi+\overline{C\psi}.
$$

这一表示的好处是：

> 无论 $\phi,\psi$ 怎么选，得到的 $f$ 都是调和映射。

也就是说，调和性已经被“硬编码”进基函数空间里。

有了这个表示后，问题就转向“如何保证这个调和映射不翻转、扭曲不过大”。这正需要研究 $f_z$ 和 $f_{\bar z}$。

## 9. 复导数与 Beltrami 系数

为了控制局部翻转和扭曲，需要研究映射的复导数。

对：

$$
f(z)=h(z)+\overline{g(z)}
$$

有：

$$
f_z=h'(z),
$$

$$
f_{\bar z}=\overline{g'(z)}.
$$

若：

$$
h(z)=C(z)\phi,\qquad g(z)=C(z)\psi,
$$

并定义 Cauchy 坐标的一阶导矩阵：

$$
D_{ij}=C_j'(z_i),
$$

则：

$$
f_z(z_i)=(D\phi)_i,
$$

$$
f_{\bar z}(z_i)=\overline{(D\psi)_i}.
$$

二阶导数也可以解析得到。若：

$$
E_{ij}=C_j''(z_i),
$$

则：

$$
f_{zz}(z_i)=(E\phi)_i,
$$

$$
f_{\bar z\bar z}(z_i)=\overline{(E\psi)_i}.
$$

这些导数用于：

- Newton / Gauss-Newton 优化；
- 扭曲能量梯度；
- 边界约束；
- 局部单射和 bounded distortion 判断。

---

## 10. 局部单射与扭曲约束

对平面映射 $f$，Jacobian 行列式可以写成：

$$
J_f=|f_z|^2-|f_{\bar z}|^2.
$$

因此局部无翻转等价于：

$$
|f_z|>|f_{\bar z}|.
$$

定义 Beltrami 系数：

$$
\mu(z)=\frac{f_{\bar z}}{f_z}.
$$

则局部单射要求：

$$
|\mu(z)|<1.
$$

共形扭曲（quasi-conformal distortion）为：

$$
K(z)=\frac{1+|\mu(z)|}{1-|\mu(z)|}.
$$

若希望：

$$
K(z)\le K_{\max},
$$

等价于：

$$
|\mu(z)|\le k,
$$

其中：

$$
k=\frac{K_{\max}-1}{K_{\max}+1}.
$$

代回 $f_z,f_{\bar z}$：

$$
|f_{\bar z}(z)|\le k |f_z(z)|.
$$

这就是 bounded distortion harmonic mapping 的核心约束形式。

再用 Cauchy 坐标矩阵写成：

$$
\left|\overline{D(z)\psi}\right|
\le
k\left|D(z)\phi\right|.
$$

由于模长约束含有未知方向，直接全局求解仍然非线性/非凸。实际算法会在当前解附近选定方向、线性化或构造凸子空间，使得优化可以用 SOCP 等凸优化工具处理。

上面的约束形式偏代数，下一节从奇异值角度重新解释同一件事：扭曲就是局部最大伸缩和最小伸缩的比值。

---

## 11. 奇异值解释

复导数还有一个更几何的解释。

局部线性映射的最大/最小奇异值为：

$$
\sigma_1=|f_z|+|f_{\bar z}|,
$$

$$
\sigma_2=|f_z|-|f_{\bar z}|.
$$

因此：

$$
K=\frac{\sigma_1}{\sigma_2}
=
\frac{|f_z|+|f_{\bar z}|}{|f_z|-|f_{\bar z}|}.
$$

局部无翻转要求：

$$
\sigma_2>0.
$$

也就是：

$$
|f_z|>|f_{\bar z}|.
$$

所以 Cauchy 坐标 + 调和表示的意义是：

1. $f$ 自动调和；
2. $f_z,f_{\bar z}$ 可由矩阵乘法得到；
3. 局部单射和扭曲可以直接写成 $|D\phi|,|D\psi|$ 的约束。

这也解释了为什么 bounded distortion 问题可以在 Cauchy 坐标空间中处理：坐标负责生成调和映射，导数矩阵负责把几何约束转成系数约束。

---

## 12. 为什么 bounded distortion 可以看边界

Bounded Distortion Harmonic Mappings in the Plane 的一个重要结论是：

> 对调和平面映射，局部单射和扭曲控制的条件可以转化为边界行为上的条件。

直观原因来自复分析中的最大值原理。

对于全纯函数 $h'(z)$、$g'(z)$，很多与模长相关的量（例如 $\log|h'|$、$\log|g'|$，在无零点区域）是调和函数或次调和函数。调和/次调和函数的极值通常由边界控制。

因此若能在边界上控制：

$$
|g'(z)|\le k |h'(z)|,
$$

并同时控制伸缩上下界，就能推出内部的扭曲界。

这就是 Bounded Distortion Harmonic Mapping 的效率来源：

- 不需要在整个二维区域内部密集施加约束；
- 只需在边界上足够密采样；
- Cauchy 坐标可以快速计算边界附近的导数；
- 优化变量只是 $\phi,\psi$ 这些复系数。

---

## 13. 多连通区域

如果区域有孔洞，情况会比 simply-connected domain 复杂。

对于单连通区域，调和函数基本可以表示为：

$$
\operatorname{Re} h(z)
$$

或全纯/反全纯组合。

但在多连通区域中，会出现额外的 harmonic measure / logarithmic basis。例如对每个孔洞中心 $a_j$，可以加入：

$$
\log|z-a_j|.
$$

它在不包含 $a_j$ 的区域内满足：

$$
\Delta \log|z-a_j|=0.
$$

这类项用来补足多连通区域中不能仅由单值全纯函数表示的调和自由度。

在工程实现中常见做法是：

1. 对每个边界分量计算 Cauchy 坐标；
2. 由于孔洞会带来冗余或线性相关自由度，需要移除部分系数；
3. 对每个孔洞加入一个 $\log|z-a_j|$ 类型的调和基；
4. 最终仍然组成一个调和映射空间。

原文中提到“每个孔洞移除 2 个自由度、再补充孔洞中心项”，可以理解为在数值基底层面消除冗余并补足多连通调和空间。

因此，单连通和多连通的差别主要体现在基函数空间的构造上；一旦基函数建好，后面的导数计算、扭曲约束和优化流程仍然保持同一套形式。

---

## 14. 算法流程

用 Cauchy 坐标做扭曲有界调和映射，大致流程如下。

### 14.1 预处理

给定源区域边界：

$$
v_0,\ldots,v_{n-1}.
$$

选择内部采样点、边界采样点或 handle 约束点：

$$
z_1,\ldots,z_m.
$$

计算：

$$
C_{ij}=C_j(z_i),
$$

$$
D_{ij}=C'_j(z_i),
$$

$$
E_{ij}=C''_j(z_i).
$$

### 14.2 参数化调和映射

设未知系数为：

$$
\phi,\psi\in\mathbb{C}^n.
$$

定义：

$$
f(z_i)= (C\phi)_i+\overline{(C\psi)_i}.
$$

### 14.3 施加约束

位置约束：

$$
f(p_\ell)=q_\ell.
$$

扭曲约束：

$$
|f_{\bar z}(s_r)|\le k|f_z(s_r)|.
$$

伸缩约束：

$$
\sigma_{\min}\le
|f_z|-|f_{\bar z}|,
$$

$$
|f_z|+|f_{\bar z}|\le\sigma_{\max}.
$$

其中 $s_r$ 通常取边界上的采样点。

### 14.4 优化目标

常见目标可以是：

- 最小移动量；
- 最小二阶变化；
- 最小 conformal distortion；
- 满足 handle 的最平滑变形。

例如：

$$
\min_{\phi,\psi}
\|A\phi+\overline{A\psi}-b\|^2
+\lambda E_{\mathrm{smooth}}.
$$

在 bounded distortion 框架中，还要加入锥约束或线性化后的凸约束，确保 $K\le K_{\max}$。

这套流程把全文的几个概念串在一起：Cauchy 坐标负责基函数，复导数负责局部几何量，Beltrami/奇异值负责约束，优化器负责在这些约束下选择系数。

---

## 15. 和 Green Coordinates 的关系

Cauchy / Complex barycentric coordinates 与 2D Green coordinates 有很深关系。Weber 等人的工作指出，基于 Cauchy 积分公式构造的复坐标和 Green 坐标在二维平面变形中是等价或紧密相关的。

直观上：

- Green coordinates 来自 Green 恒等式 / 调和函数边界表示；
- Cauchy coordinates 来自 Cauchy 积分公式；
- 在二维复平面中，二者都在表达“由边界数据确定内部调和/全纯函数”。

因此它们都适合 cage-based planar deformation，只是 Cauchy 坐标用复数形式把共形和调和结构表达得更简洁。

---

## 16. 这篇笔记的核心 takeaway

可以把 Cauchy 重心坐标理解成：

> 用复分析把边界上的自由度变成内部的全纯基函数；再用全纯 + 反全纯分解得到调和映射；最后通过复导数控制局部翻转和扭曲。

最重要的公式链是：

$$
h(z)=\frac{1}{2\pi i}\oint_{\partial\Omega}
\frac{F(\zeta)}{\zeta-z}d\zeta
$$

$$
h(z)=C(z)\phi,\qquad g(z)=C(z)\psi
$$

$$
f(z)=C(z)\phi+\overline{C(z)\psi}
$$

$$
f_z=D(z)\phi,\qquad
f_{\bar z}=\overline{D(z)\psi}
$$

$$
J_f=|f_z|^2-|f_{\bar z}|^2
$$

$$
K=\frac{|f_z|+|f_{\bar z}|}{|f_z|-|f_{\bar z}|}.
$$

只要记住这条链，Cauchy 坐标在扭曲有界调和映射里的作用就很清楚：

> 它不是单纯为了插值，而是为了给优化问题提供一个天然调和、可解析求导、便于施加扭曲约束的函数空间。

---
