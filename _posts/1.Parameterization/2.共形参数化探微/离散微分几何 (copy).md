

### 曲率的物理

在《三体III·死神永生》中，人类面临二向箔降维打击的绝境时，曾寄望于一种理论上的终极推进方式——**曲率驱动引擎（Curvature Drive）**。其原理是：通过局部改变时空的曲率，使飞船前方空间收缩、后方空间膨胀，从而以"空间波"的形式实现光速航行。飞船本身并不在空间中"运动"，而是乘坐在被弯曲的时空之上——这本质上是对广义相对论场方程

$$
R_{\mu\nu} - \frac{1}{2}Rg_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}
$$

的极端工程想象：质量-能量分布 $T_{\mu\nu}$ 弯曲时空（左边 Ricci 曲率项），而弯曲的时空又告诉物质如何运动。引力，就是时空曲率的直接体现。

曲率驱动引擎的概念并非纯粹的科幻狂想。1994 年，墨西哥物理学家 Miguel Alcubierre 提出了**阿库别瑞度规（Alcubierre metric）**——广义相对论的一个严格解，描述了一个"曲率泡"包裹飞船以超光速移动的时空几何。尽管目前它需要负能量（奇异物质）而无法工程实现，但它表明：**曲率不仅是数学上的抽象概念，更是物理学中最深刻的结构描述符**。

曲率在物理世界中无处不在：

| 领域 | 曲率描述的现象 | 核心方程 |
|:---|:---|:---|
| **广义相对论** | 引力 = 时空弯曲 | Einstein 场方程 $G_{\mu\nu} = 8\pi G\,T_{\mu\nu}$ |
| **弹性力学** | 薄板弯曲的弹性能 | 弯曲能 $\propto \int \kappa^2\,dA$ |
| **流体力学** | 液滴表面张力 | Laplace-Young 方程 $\Delta p = \gamma(\kappa_1+\kappa_2)$ |
| **生物膜物理** | 细胞膜形态 | Helfrich 自由能：依赖于平均曲率与高斯曲率 |
| **材料科学** | 晶体缺陷、位错 | 曲率驱动晶界迁移 |
| **计算机图形学** | 曲面光滑、网格变形 | 平均曲率流 (MCF)、Willmore 流 |

这些应用的共同数学语言正是下面要展开的**曲面的曲率理论**：从曲线的密切圆、到曲面的高斯曲率与 Gauss-Bonnet 定理、再到离散三角网格上的角亏公式——它们构成了从连续到离散、从物理到计算的完整知识链。

## 高斯曲率

如果要定义曲面的曲率首先就要先了解**曲线的曲率**。设曲线参数方程为 $ \mathbf{r}(s) $（$s$ 为弧长参数），则曲线在一点处的曲率 $ \kappa $ 定义为切向量 $ \mathbf{T} = \mathbf{r}'(s) $ 的转动速率：
$$
\kappa = \left\| \frac{d\mathbf{T}}{ds} \right\| = \|\mathbf{r}''(s)\|
$$

![image-20260617115734728](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260617115734728.png)

![image-20260617115832246](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260617115832246.png)

若曲线以任意参数 $t$ 给出 $ \mathbf{r}(t) $，则曲率公式为：
$$
\kappa = \frac{\|\mathbf{r}' \times \mathbf{r}''\|}{\|\mathbf{r}'\|^3}
$$

曲率半径 $ \rho = 1/\kappa $ 即为密切圆的半径。曲率越大，曲线弯曲越剧烈。

对于空间曲线，在每一点可定义由三个互相正交的单位向量构成的 **Frenet 标架**：

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251124200526683.png)

- $ \mathbf{T} $：单位切向量 (unit tangent)
- $ \mathbf{N} $：主法向量 (principal normal)，指向曲线弯曲方向
- $ \mathbf{B} = \mathbf{T} \times \mathbf{N} $：副法向量 (binormal)

三者满足 **Frenet-Serret 公式**：

$$
\begin{aligned}
\mathbf{T}' &= \kappa \mathbf{N} \\
\mathbf{N}' &= -\kappa \mathbf{T} + \tau \mathbf{B} \\
\mathbf{B}' &= -\tau \mathbf{N}
\end{aligned}
$$

## 法曲率与测地曲率

曲面上一条曲线 $\gamma(s)\subset M$（以弧长 $s$ 参数化）的加速度向量 $\gamma''(s)$ 可分解为两个正交分量：

$$
\gamma'' = \kappa_n \,\mathbf{n} + \kappa_g \,(\mathbf{n}\times\gamma'),
$$

其中 $\mathbf{n}$ 为曲面单位法向量。$\kappa_n$ 为**法曲率**，$\kappa_g$ 为**测地曲率**。

- **法曲率（Normal Curvature）** $\kappa_n = \gamma''\cdot\mathbf{n}$：曲线在曲面法方向上的弯曲——即曲面"硬掰"曲线离开切平面的程度。它完全由第二基本形式决定：
  $$
  \kappa_n = I\!I(\gamma',\gamma') = L(du)^2 + 2M\,du\,dv + N(dv)^2.
  $$
  对给定方向，$\kappa_n$ 不依赖于曲线的具体形状，只取决于该方向的切向量——这是 **Meusnier 定理**。

- **测地曲率（Geodesic Curvature）** $\kappa_g$：曲线在切平面内的弯曲分量。它是内蕴量——仅取决于曲面的度量（第一基本形式），与嵌入方式无关。测地线正是测地曲率处处为零的曲线（$\kappa_g\equiv 0$）：
  $$
  \int_{\partial M} \kappa_g\,ds \quad\text{出现在 Gauss-Bonnet 定理的边界项中}.
  $$

**分量关系**。由正交分解得：
$$
\kappa^2 = \kappa_n^2 + \kappa_g^2,
$$
即曲线的 Frenet 曲率 $ \kappa $ 是法曲率与测地曲率的平方和。

![image-20260617121817778](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260617121817778.png)

**开车类比**。想象你在山路上开车：

- **测地曲率** = 方向盘左右转——路在路面平面内左弯右弯。即使路完全平坦（法曲率为零），你依然需要打方向盘。蚂蚁在路面上爬，仅靠路边画线就能感知测地曲率——它是**内蕴**的。
- **法曲率** = 路面上下坡——山路爬升或俯冲，把你挤出路面切平面。这是山体形状（嵌入 $\mathbb R^3$）强加给你的纵向加速度。同样的路网若被摊平到桌面，法曲率消失，但测地曲率依然存在。

你身体感受到的总加速度满足 $\kappa^2 = \kappa_n^2 + \kappa_g^2$：最刺激的"发卡弯 + 盘山路"就是大 $\kappa_g$ 叠加大 $\kappa_n$——曲面的弯曲方式决定了加速度向"出曲面"（法曲率）和"在曲面内"（测地曲率）两个方向的分量分配。这正是 Weingarten 映射（$W = I^{-1} \cdot I\!I$）刻画的：形状算子 $W$ 编码了每个切方向上曲面偏离平面的法向加速度，而测地曲率则由度量 $g$ 单独给出。

![image-20260617120550663](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260617120550663.png)

### 高斯映射（Gauss map）

曲面上每个点 $p \in S$ 存在唯一的单位法向量 $N(p)$，垂直于其切平面。将 $N(p)$ 平移到单位球面 $S^2$ 的对应位置，就得到了**高斯映射** 

$$
\varphi: p \to N(p)
$$

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251124184622415.png)

**高斯映射的微分（Weingarten 映射）**：$\mathrm{d}N(X)$ 称为 **Weingarten 映射**（形状算子），它量化了法向量随曲面弯曲的变化速率：
$$
\mathrm{d}g_p(v) = \frac{\partial N}{\partial v} = -W_p(v)
$$


![image-20260617121044362](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260617121044362.png)

![image-20260617121329525](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260617121329525.png)

![image-20260617122126496](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260617122126496.png)

在局部坐标下，Weingarten 映射的矩阵表示为 $W = I^{-1} \cdot II$，其中 $I$ 是第一基本形式矩阵，$II$ 是第二基本形式矩阵。

**Gauss 曲率与 Gauss 映照的关系**：

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251125150744255.png)

曲面上一点$p$高思曲率$K(p)$定义为该点高思映射面积放大率

$$
K(p) = \lim_{A \to 0} \frac{\text{Area}(\varphi(A))}{\text{Area}(A)}
$$


显然这等价于Weingarten 映射的行列式

$$
K = \frac{LN-M^2}{EG-F^2} = \det(W)
$$



## 主曲率

![image-20260617121246998](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260617121246998.png)



![image-20260617123130700](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260617123130700.png)

![image-20260617123316665](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260617123316665.png)

## 离散高斯曲率

对于三角网格上的内部顶点 $v_i$，其离散高斯曲率定义为**角亏**即 $2\pi$ 减去该顶点周围所有三角形的内角之和：

$$
K(v_i) = 2\pi - \sum_{v_j \in N_1(v_i)} \theta_j
$$

其中 $\theta_j$ 为顶点 $v_i$ 处各相邻三角形的内角（angle defect / 角度亏量）。

对于带边界的离散曲面，**边界点测地曲率**：
$$
\kappa_g(v_i) = \pi - \sum \theta_j
$$

## Gauss-Bonnet 定理

**曲率的总和只与曲面的"洞数"有关，与具体的弯曲方式无关。**

Gauss-Bonnet 定理的完整形式为：
$$
\int_M K\,dA + \int_{\partial M} \kappa_g\,ds = 2\pi\chi(M)
$$


直接离散化可推导出三角网格的Gauss-Bonnet 定理：

$$
\sum_{v_i \in V} K(v_i) = 2\pi\chi(M) = 2\pi(V - E + F)
$$

其中 $ \chi = V - E + F $ 由 **Euler 多面体公式** 给出（$V$ 为顶点数，$E$ 为边数，$F$ 为面数）

如下图，环面的总角度亏量趋近于 0（欧拉示性数$ \chi = 2 - 2g $（$g$ 为亏格）=0）。甜甜圈内部是负曲率、外部是正曲率，根据 Gauss-Bonnet 定理，两者之和为零。

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251028134522912.png)



## **高斯绝妙定理（Theorema Egregium）**

高斯曲率完全由第一基本形式决定——曲率是内蕴的，与外部观察者视角无关

直观理解：篮球表面处处"向外鼓"，高斯曲率为正；马鞍中间"向内凹"，曲率为负；桌面曲率为 0。高斯曲率最神奇之处在于它是**内禀的**——蚂蚁在球面上爬，不用抬头看天空，光靠测量周围三角形内角和就能知道自己在正曲率世界（内角和 >180°）。

根据 **Theorema Egregium（绝妙定理）**，高斯曲率是内蕴量，不能通过等距变换改变。因此：

- **高斯曲率为零**的曲面（如柱面、锥面）可以无扭曲地展开
- **高斯曲率非零**的曲面（如球面）**不可能**无扭曲地展开

这意味着，对于一般曲面，参数化必然引入**扭曲**。算法设计的目标就是：**在满足约束的前提下，最小化扭曲**。
