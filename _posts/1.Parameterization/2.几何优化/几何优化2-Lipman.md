---
layout: post
title: "曲面展开4-Lipman算法"
category: Parameterization
---

本文主要讲解的是如何控制三角网格(Mesh)上的分片线性映射$f$的共形扭曲(记为$\sigma$),并且同时确保$f$的局部单射性质，这个方法本身不是参数化方法而是对一般参数化方法(LSCM,ARAP等)进行加强。

三角网格上$M = (V,F,E)$定义的映射可以认为是分片连续线性的（CPL continous Piecewise Linear ，每个三角面线性的同时，相邻两个三角面在边界保持连续）将所有这样的映射的空间定义为$F^M$ ,而我们需要的是$\sigma$有限的子空间

### 对函数空间进行凸化

我们这样定义空间$F^M_C \subset F^M,常数C >=1,\sigma<=C$，不过麻烦的是$F^M_C $是**非凸的**，而我们要做的就是找一个比较好的凸的空间作为近似替代。

我们通过在每个面上定义一个坐标加$\oplus$，从而可以简易表达出的映射空间$F^{M,\oplus}_C \subset F^M_C$

具体做法如下

1）研究使仿射变换无翻转的并且其$\sigma$不大于一个常数C(C>=1)的空间$\mathcal A_C(f_j) $

2）对其中最大凸子空间的描述 $\mathcal A^{\oplus_j}_C(f_j) \subset \mathcal A_C(f_j)$ ，其是由在每个面$f_j$上定义一个坐标架$\oplus_j$

3）对所有面$f_j \in F$ 考虑$\mathcal A^{\oplus_j}_C(f_j)$并且考虑边上的连续性的约束,从而得到映射空间$F^{M,\oplus}_C \subset F^M_C$

4）对得到的映射空间$F^{M,\oplus}_C$进行优化

#### 三角面上的仿射映射与局部坐标系

对每个三角面定义$f_j \in F $定义其上的一个局部坐标系 $\oplus_j := [o_j,e_1^j,e_2^j]$

那么对于$f_j$上的任意一点$p$，可以表示成 $p = o_j + x_1 e_1^j + x_2 e_2^j$

![image-20251016061313250](..\..\..\..\imgs\image-20251016061313250.png)

我们可以定义在$f_j$上的仿射映射 $A_j : f_j \to \mathbb{R}^2$：

$$A_j(p) = \begin{pmatrix} a & b \\ c & d \end{pmatrix} (p - o_j) + t = A[p] + T$$

![image-20251016061255492](..\..\..\..\imgs\image-20251016061255492.png)

其中

$$A = \begin{pmatrix} a & b \\ c & d \end{pmatrix} \in \mathbb{R}^{2 \times 2}, \quad [p] = \begin{pmatrix} x_1 \\ x_2 \end{pmatrix}, \quad T = \begin{pmatrix} t_1 \\ t_2 \end{pmatrix}$$

![image-20251016062307282](..\..\..\..\imgs\image-20251016062307282.png)

从而就可以表达为如下的限制条件（无翻转 + 共形扭曲有界）：

$$\sigma_1(A_j) - \sigma_2(A_j) \geq 0 \tag{4.2}$$

$$\frac{\sigma_1(A_j)}{\sigma_2(A_j)} \leq C \tag{4.3}$$

![image-20251016062408865](..\..\..\..\imgs\image-20251016062408865.png)

**注意到**我们可以写成如下的矩阵形式，从而更方便后续的处理。将仿射映射用目标三角形与源三角形的顶点坐标表示：

$$A_j = [u_1 - u_0, \; u_2 - u_0] \cdot [v_1 - v_0, \; v_2 - v_0]^{-1}$$

![image-20240912195652261](..\..\..\..\imgs\image-20240912195652261.png)

其中 $v_0, v_1, v_2$ 是源三角形 $f_j$ 的三个顶点，$u_0, u_1, u_2$ 是映射后的目标顶点。

那样映射就可以表达成如下形式：

$$u_i - u_0 = A_j (v_i - v_0), \quad i = 1, 2$$

![image-20240912205200380](..\..\..\..\imgs\image-20240912205200380.png)

#### 复数域表示

在复数域上表达更为简洁。将仿射映射 $A_j$ 用复数表示为：

$$A_j(z) = \alpha z + \beta \bar{z} + \gamma$$

![image-20251016094836797](..\..\..\..\imgs\image-20251016094836797.png)

其中 $\alpha, \beta, \gamma \in \mathbb{C}$，而 $\gamma$ 是平移项（不影响 Jacobian 分析，通常忽略）。

可以求得矩阵 $A_j$ 与复数系数的关系：

$$\alpha = \frac{1}{2}\left(a + d + i(b - c)\right), \quad \beta = \frac{1}{2}\left(a - d + i(b + c)\right)$$

![image-20251016094847914](..\..\..\..\imgs\image-20251016094847914.png)

反过来：

$$a = \text{Re}(\alpha + \beta), \quad b = \text{Im}(\alpha + \beta), \quad c = \text{Im}(\alpha - \beta), \quad d = \text{Re}(\alpha - \beta)$$

![image-20251016094853613](..\..\..\..\imgs\image-20251016094853613.png)

#### 奇异值与共形扭曲

可以求得矩阵 $A_j(p)$ 的奇异值。由 $\alpha, \beta$ 的复数表示，$A_j$ 的 Jacobian 矩阵的奇异值为：

$$\sigma_1 = |\alpha| + |\beta|, \quad \sigma_2 = |\alpha| - |\beta|$$

![image-20251016062833737](..\..\..\..\imgs\image-20251016062833737.png)

（假设 $|\alpha| \geq |\beta|$，即无翻转。）

我们知道分片线性映射的扭曲 $\sigma$ 可以用其矩阵的奇异值表达：

$$\sigma(A_j) = \frac{\sigma_1}{\sigma_2} = \frac{|\alpha| + |\beta|}{|\alpha| - |\beta|}$$

![image-20251016062847174](..\..\..\..\imgs\image-20251016062847174.png)

#### 约束条件的转化

那么受限条件 (4.2)-(4.3) 就可以转化为如下形式：

$$|\alpha| - |\beta| \geq 0 \quad \text{(无翻转)} \tag{4.2'}$$

$$\frac{|\alpha| + |\beta|}{|\alpha| - |\beta|} \leq C \quad \text{(共形扭曲有界)} \tag{4.3'}$$

![image-20251016062528823](..\..\..\..\imgs\image-20251016062528823.png)

引入一个中间变量 $r_j \in \mathbb{R}$，令 $r_j = |\alpha|^2 - |\beta|^2 = \det(A_j)$，那么上式转为：

$$|\alpha|^2 - |\beta|^2 \geq r_j > 0$$

$$|\beta| \leq \frac{C-1}{C+1} |\alpha|$$

![image-20251016062721441](..\..\..\..\imgs\image-20251016062721441.png)

满足上面条件的三元组 $(\alpha, \beta, r) \in \mathbb{C} \times \mathbb{C} \times \mathbb{R}$ 构成的空间即为 $\mathcal{A}_C(f_j)$。

并注意到其最大凸子空间 $\mathcal{A}^{\oplus_j}_C(f_j) \subset \mathcal{A}_C(f_j)$：

$$\mathcal{A}^{\oplus_j}_C(f_j) = \left\{ (\alpha, \beta, r) : \; |\alpha|^2 - |\beta|^2 \geq r > 0, \; |\beta|^2 \leq \frac{(C-1)^2}{(C+1)^2} \cdot r \right\}$$

![image-20251016094749664](..\..\..\..\imgs\image-20251016094749664.png)

也就是如下图所示的（蓝色内圆与灰色半平面是凸的，但是黄色锥的补区域却是非凸的，我们就是用灰色区域代替黄色锥的补区域的）：

![image-20251107101000576](..\..\..\..\imgs\image-20251107101000576.png)

#### 凸子空间的元素

$\mathcal{A}_C^{\oplus_j}$ 是 $\mathcal{A}_C$ 的子空间，下面来看下具体 $A_C^{\oplus_j}$ 包含什么样的元素：

$$\mathcal{A}_C^{\oplus_j}(f_j) = \left\{ A_j = \begin{pmatrix} \text{Re}(\alpha+\beta) & \text{Im}(\alpha+\beta) \\ \text{Im}(\alpha-\beta) & \text{Re}(\alpha-\beta) \end{pmatrix} : (\alpha, \beta, r) \in \mathcal{A}_C^{\oplus_j} \right\}$$

![image-20240912192008382](..\..\..\..\imgs\image-20240912192008382.png)

#### 映射空间构造

通过在所有面上取 Union 从而构造出 $\mathcal{F}^{M,\oplus}_C \subset \mathcal{F}^M$：

$$\mathcal{F}^{M,\oplus}_C = \left\{ f \in \mathcal{F}^M : \; A_j(f) \in \mathcal{A}_C^{\oplus_j}(f_j), \; \forall f_j \in F \right\}$$

![image-20240912193217416](..\..\..\..\imgs\image-20240912193217416.png)

#### 双射性

可以定义 $C \geq 1$ 的保向空间 $F^+_M$：

$$F^+_M = \left\{ f \in F^M : \; \det(A_j) > 0, \; \forall f_j \in F \right\}$$

![image-20251107112805188](..\..\..\..\imgs\image-20251107112805188.png)

可以证明在保向空间中映射是双射的：

$$\text{若 } f \in F^+_M \cap \mathcal{F}^{M,\oplus}_C, \text{ 则 } f \text{ 是局部双射的。}$$

![image-20251107112556622](..\..\..\..\imgs\image-20251107112556622.png)

同时可以对上面的结论推广到多联通区域中：

$$\text{对多联通区域 } \Omega, \text{ 若 } f \in F^+_M \cap \mathcal{F}^{M,\oplus}_C, \text{ 则 } f: \Omega \to \mathbb{R}^2 \text{ 是全局双射。}$$

![image-20251107112401804](..\..\..\..\imgs\image-20251107112401804.png)

### 算法流程

![image-20251107112032660](..\..\..\..\imgs\image-20251107112032660.png)

可以用于优化平面变形（planar Morphing）和网格参数化（Parameterization）。

根据不同能量构造不同的优化式：

#### LSCM 能量

LSCM（Least Squares Conformal Maps）的离散能量为：

$$E_{LSCM}(f) = \sum_{f_j \in F} |\beta_j|^2 \cdot \text{area}(f_j)$$

![image-20251107112108353](..\..\..\..\imgs\image-20251107112108353.png)

即最小化每个面上的"反共形"部分 $\beta_j$。结合 Lipman 约束的优化问题为：

$$\min_{f} \; E_{LSCM}(f) \quad \text{s.t.} \quad (\alpha_j, \beta_j, r_j) \in \mathcal{A}_C^{\oplus_j}(f_j), \; \forall j$$

![image-20251107112137480](..\..\..\..\imgs\image-20251107112137480.png)

#### ARAP 能量

ARAP（As Rigid As Possible）的离散能量为：

$$E_{ARAP}(f) = \sum_{f_j \in F} \|A_j - R_j\|_F^2 \cdot \text{area}(f_j)$$

![image-20251107112331905](..\..\..\..\imgs\image-20251107112331905.png)

其中 $R_j$ 是 $A_j$ 的最近旋转矩阵（通过 SVD 或极分解求得）。结合 Lipman 约束的优化问题为：

$$\min_{f} \; E_{ARAP}(f) \quad \text{s.t.} \quad (\alpha_j, \beta_j, r_j) \in \mathcal{A}_C^{\oplus_j}(f_j), \; \forall j$$

![image-20251107112315320](..\..\..\..\imgs\image-20251107112315320.png)

#### 曲面展平

对于曲面展平问题，优化目标为：

$$\min_{f} \; E_{ARAP}(f) \quad \text{s.t.} \quad \sigma(A_j) \leq C, \; \forall f_j \in F$$

![image-20251107112927267](..\..\..\..\imgs\image-20251107112927267.png)
