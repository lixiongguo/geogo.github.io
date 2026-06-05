

# 第1章  前言与目录

![Lucy](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\7b9141057840.png)



## 写在前面

在刘慈欣的科幻巨著《三体III·死神永生》中，歌者文明使用了一种终极武器——**二向箔**。它一经展开，便将三维空间强制"压扁"为二维平面，整个太阳系——行星、恒星、文明——在瞬间坍缩为一幅没有厚度的巨画。这或许是科幻史上最令人绝望的画面之一：**降维打击**——高维空间被不可逆地映射到低维。

有趣的是，在数学和计算机图形学中，我们也在做一件看似相似的事情：将三维曲面**展开**到二维平面上。但与二向箔不同的是——

- 我们**不摧毁**曲面结构，而是寻找最优的二维**表示**；
- 我们**不甘于**暴力降维，而是追求**尽可能小地扭曲**角度与面积。

那么，如何将三维曲面摊平到二维平面上？这个看似不起眼的问题——就像绘制世界地图时把地球仪展开那样——却蕴含着无尽的几何与拓扑奥秘。本书将带你从最朴素的直觉出发，逐步深入复分析、微分几何、拓扑学与凸优化的殿堂，探索**将三维世界优雅地映射到二维平面**的数学艺术。

### 本书特色

本书以直观、可动手的方式组织内容。通过可视化工具观察几何现象、亲手推导公式、编写代码验证结论，让抽象的数学变得可触摸、可玩味。代码与公式相互印证，使理论不再悬浮于纸面。

内容上追求**少而深刻**——不求面面俱到，而是精选核心数学概念，串联起微积分、线性代数、复分析、微分几何、拓扑学、凸优化等多个分支。读者可以在"玩"中获得对这些领域的高层次直觉。学完本书后，若想继续深入，顾险峰老师的计算共形几何与最优传输理论会是通往时代前沿的下一步阶梯。

### 主要数学理论

曲面展开的理论根植于三个数学分支的交汇。**复分析**提供了共形映射的基本语言——柯西-黎曼方程刻画角度保持的微分条件，黎曼映射定理保证单连通区域到单位圆盘的共形映射存在性。**微分几何**将曲面展开为内蕴几何问题：第一基本形式携带度量信息，等温坐标（局部坐标下度量为对角形式）是共形参数化的直接目标，高斯曲率决定曲面能否无扭曲展开，而单值化定理断言任意曲面可赋予常曲率度量，为 Ricci 流等方法提供了理论保证。**凸优化**则充当计算桥梁——多数参数化能量（如 LSCM 的二次型、Circle Patterns 的凸能量、ARAP 的交替优化）最终都归结为凸优化或可高效求解的变分问题，拉格朗日乘子法和交替方向乘子法（ADMM）是处理约束的常用工具。

我们将在本系列中多次遇到同一概念（如共形映射、高斯曲率），每次都从不同角度加深理解。同一主题，在不同阶段以不同深度反复出现，最终达成深刻理解。这正是教育中"螺旋式上升"的典范。

### 章节导读

全书共六章，按"方法 → 应用 → 理论"的逻辑递进：

- **第1章（曲面展开介绍）** 从最基础的 Tutte 嵌入和分段线性映射出发，建立 Laplace 算子和 Jacobian 矩阵等基本工具，并介绍 ARAP 能量优化。
- **第2章（共形映射方法）** 聚焦共形参数化的核心算法：LSCM、Circle Patterns（分算法与理论两篇）和 Ricci 流，展示从柯西-黎曼方程到凸变分问题的完整路径。
- **第3章（四边形网格化）** 将参数化能力从三角形网格提升到四边形网格：MIQ 混合整数规划、QuadCover 覆盖空间方法、向量场平行移动，是参数化技术在前沿几何处理中的直接应用。
- **第4章（计算共形几何）** 在具体方法与应用的感性认识之后，系统补全理论基础——代数拓扑、微分形式、Hodge 分解、全局调和与共形参数化、Abel–Jacobi 映射与 Holonomy。
- **第5章（最优传输）** 打通保面积映射与最优传输之间的等价关系，介绍 Monge-Kantorovich 理论、Semi-Discrete 解法、Monge-Ampère 方程求解以及在焦散透镜设计中的应用。
- **第6章（附录）** 提供线性方程组求解、非线性优化、离散曲率、双曲几何等预备知识。

建议阅读路线：初学者顺序阅读第1–2章建立直觉和方法论，第3章体验参数化在四边形网格化中的应用，再学习第4章补全理论基础，最后进入第5章的最优传输前沿。有微分几何基础的读者可跳过第4章前半部分。

### 与其他资源的对比

在曲面展开与几何处理领域，已有诸多优秀的参考资源：经典教材如 Botsch 等的《Polygon Mesh Processing》是很好的入门读物，但部分内容略显陈旧；顾险峰老师的《计算共形几何》与《最优传输》理论深度极高，适合进阶但门槛不低；Tristan Needham 的《可视化复分析》与《可视化微分形式》以极富直觉的方式呈现抽象概念，强烈推荐；Kenneth Stephenson 的《Introduction to Circle Packing》则是圆填充方向的不二之选。网课方面，GAMES 的 Games301 和 Games102、中科大的数字几何处理、MIT 的 Shape Analysis 以及 CMU 的 Digital Geometry Processing 各有所长，但普遍假设较多前置知识或覆盖面有限。理论补充上，梅加强的《Riemann 曲面导论》提供了严格的数学基础，顾险峰老师的"老顾谈几何"博客兼具前沿性与直观性，Bobenko 等人的《Discrete Differential Geometry》也是离散微分几何的重要教材。与上述资源相比，本系列的特点在于：从基础出发、注重实践与细致推导，不假设过多前置知识；追根溯源，剖析数学思维脉络而非仅呈现算法结论；覆盖主流参数化方法并揭示其内在联系；同时配有完整的代码与可视化，力求让理论可触摸、可验证。

### 作者

本科数学，硕士软件工程，多年图形算法工程师经验。参与过游戏引擎、WebAR、三维重建等多个从研发到落地的项目，热衷于数学与计算机图形学的交叉领域。


## 目录

### 第1章　曲面展开介绍

- 1.1 介绍
- 1.2 一个简单的展开算法
- 1.3 分段线性映射的 Laplace 算子
- 1.4 分段线性映射的 Jacobian 矩阵与 ARAP 方法
- 1.5 共形映射初步认识
- 1.6 网格的谱处理 SCP

### 第2章　共形映射方法

- 2.1 基于柯西-黎曼方程的 LSCM 方法
- 2.2 圆填充（Circle Patterns）方法——算法流程
- 2.3 圆填充方法——理论证明（KAT 定理、Rivin 定理与 Bobenko 变分原理）
- 2.3 共形因子方法
- 2.4 Ricci 流方法
- 2.5 几何变形的目标凸化

### 第3章　四边形网格化

- 3.1 介绍：从三角形参数化到四边形网格化
- 3.2 MIQ（Mixed-Integer Quadrangulation）算法
- 3.3 QuadCover 算法
- 3.4 向量场的平行移动

### 第4章　计算共形几何

- 4.1 代数拓扑基础
- 4.2.1 微分形式与参数化——介绍
- 4.2.2 Tutte 嵌入的推广
- 4.2.3 全局调和参数化（HGP）
- 4.2.4 四边形网格化（Tong06）
- 4.3 全局共形参数化
- 4.4 Abel–Jacobi 映射
- 4.5 Holonomy

### 第5章　最优传输

- 5.1 Monge 问题与 Kantorovich 问题
- 5.2 顾老师的 Semi-Discrete 解法
- 5.3 Mérigot 的 Semi-Discrete 解法
- 5.4 针对网格的 Monge-Ampère 方程求解
- 5.5 最优传输计算焦散透镜
- 5.6 流体力学观点与图像配准

### 附录　（第6章）

- 6.1.1 线性方程组 Ax = b
- 6.1.2 非线性优化
- 6.2 离散曲面的高斯曲率
- 6.3.1 双曲平面
- 6.3.2 圆填充与极小曲面
- 6.4 一些简单情况的最优传输

### 参考文献



# 第2章  曲面展开-介绍

## 1.1 介绍

### 1.1.1 曲面展开(参数化)定义

**曲面展开（参数化 / Parameterization）**是指建立三维曲面与二维平面区域之间的一一对应映射。用数学语言描述：设 $S \subset \mathbb{R}^3$ 是一张三维曲面，$\Omega \subset \mathbb{R}^2$ 是平面区域（称为曲面的**参数域**），参数化即寻找**双射（一一对应）**：
$$
f: S \to \Omega
$$

### 1.1.2 一个生活中的例子

下面我们看一个生活中常见的曲面展开例子—我们的世界地图。我们知道地球是球形的，为方便观察，我们要将地球表面的球面铺展到平面上也即将**球面上的点转换为平面上的点**，这就要用到曲面展开的方法了。

一般常见的地图展开方法使用的是**墨卡托投影法(Mercator Projection)**：假设球面内部有一个光源，球面外包围着一个圆柱面，光线将球面上的点投射到圆柱面上，再将圆柱面展开，就得到了我们熟悉的世界地图。

![墨卡托投影示意图](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\9c1601930278.png)

然而，墨卡托投影**必然引入扭曲**。比如我们在地图上看到的俄罗斯面积远大于非洲，但事实上俄罗斯的陆地面积只有非洲的一半左右。产生这种错觉的原因在于：墨卡托投影牺牲了面积精度以换取角度保持（即"共形映射"）。赤道附近的区域扭曲极小，越靠近两极面积膨胀越严重。

![地图面积对比](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\b44f941e298c.png)



除了墨卡托投影还有许多其他投影方法，由于投影方式的不同，所形成的世界地图"长相"也大相径庭。

![2](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\imgs\23333.png)

球面是很简单的曲面，对于复杂的肠道模型需要建立地图就要复杂得多了：通过CT扫描获取到腹部断层图像，然后用多视角几何的方法重建三维直肠曲面后，为了方便医生的观察，最后将这个直肠曲面平展到平面上，像看地球仪一样观察曲折的肠道。使用这种方法，设备和病患没有接触，不需要麻醉，不会诱导并发症。

![image-20250227101914414](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\1f3c35574d83.png)

### 1.1.3 其他应用

游戏或动漫影视工业中3D模型的**纹理贴图(Texture Mapping)**：纹理贴图经常被用来对3D场景和对象进行上色及纹理填充等。设计师可以在二维空间进行模拟物体的表面纹理与细节信息的设计，再通过计算机手段将其投影到3D模型表面。

![Screenshot 2026-05-21 at 13.47.41](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\imgs\Screenshot 2026-05-21 at 13.47.41.png)

法线贴图(Normal Mapping)将细节信息存储到贴图上，从而简化面数

衣物制版将衣物拆分成不同部分并逐个摊平，然后确定每个部位的具体规格尺寸

![img](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\imgs\GarmentPattern.jpg)

![img](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\imgs\MD.jpg)

**尽可能减小扭曲**是我们寻找更优展开(参数化)方法的重要目标。我们将这个问题用数学语言进行形式化：定义一个能量 $E(f)$ 来度量映射 $f$ 的扭曲程度，从而将参数化建模为几何最优化问题——之后的工作就是找到"好"的能量以及更快更稳定的数值求解方法。
$$
\min_{f \in PL}\, E(f),\quad f\text{ \text{满足约束条件}}
$$
接下来我们会看到具体该如何定义这个能量，以及如何对这些能量进行数值优化。

并且要求 $f$ 具有某种"良好"性质（如保持角度、面积等）。并非任意映射都是合法的参数化，并且最好满足以下**约束**：

1. 映射 $f$ 是**局部单射的（Locally Injective）**，即映射后内部三角形的边不能自交；



2. 映射 $f$ 是无翻转的(flip free)，映射后三角形的定向是不能翻转的，否则也会有错乱的情况



3.映射 $f$ 是双射的(Bijecive), 映射后的边界是不能相交的








# 第3章  曲面展开-一个简单的展开算法

## 1.2 一个简单的展开算法

计算机中所有3D物体的表面都是由许多小三角形拼在一起表示的，这样的三角形组成的网格称为**三角形网格(Mesh)** 记作
$$
M=\{V,E,F \mid V,E,F \text{\text{为网格的顶点、边、面}}\}
$$




### 1.2.1 一个简单的展开算法-Tutte参数化方法

在开始我们的探索之前，先根据直觉构想一个简单的算法。想想我们生活中带弹性头套的场景，把要展开的曲面看作一张弹性膜，我们假想用手将这个弹性膜的边界固定住，之后弹性膜的内部力会将膜的内部伸展到合适的位置上。

我们后面的3D模型主要是最简单拓扑的模型即**拓扑圆盘(Topological Disk)**—是指具有单条边界环的"开口网格曲面"，比如这个简化的（"抽象"的）大卫头像：
![image-20250306112054639](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\a2220f7bbe4d.png)

现在我们将三角网格的边界固定到一个圆周上，上面这个过程用三角网格 $M$ 来进行建模就是，三角网格上面每条边我们认为是一个弹簧

![image-20250311194454982](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\4464fd1db0b6.png)

假设内部顶点 $v \in V_{int}$ 所受的力是均衡的，那么它自然位于邻居顶点所围成区域的质心位置，从而形成一个线性方程

![vertex to centroid](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\34421a57ec42.png)

1. 将 $M$ 的顶点集编号为 $V=\{1,2,3,\dots,n\}$，并划分为内部点集 $V_{int}$ 和边界点集 $V_{bnd}$；
2. 对内部顶点 $v \in V_{int}$，设 $N_v$ 为其邻居集，则平衡状态下 $x_v = \frac{1}{\vert N_v\vert}\sum_{u \in N_v} x_u$；
3. 对边界顶点 $v \in V_{bnd}$，按顺序排列并赋予序号 $i_v$，将其固定在圆周上：$x_{i_v}= \bigl(r\cos\theta_{i_v},\; r\sin\theta_{i_v}\bigr)$。

上式可整理成**稀疏线性系统** $Ax = b$，其中 $A = \{a_{ij}\}_{n\times n}$（$u, v$ 两个坐标各需一组）：

1. 对任意的 $v \in V_{int}$ ，有
$$
A(v,u) = \begin{cases}  1 &,  u=v \\ -\frac 1 {|N_v|}&, u \in N_v \\ 0 &,\text{\text{其它}}\end{cases}
$$
2. 对任意的 $v \in V_{bnd}$ ，有
$$
A(v,u) = \begin{cases}  1 &,  u=v \\  0 &,\text{\text{其它}}\end{cases}
$$
其边界序号为 $i_v$ ，则 $b_{i_v} = (r\cos({\theta_{i_v}}), r\sin({\theta_{i_v}}))$

对上述线性系统，当 $A$ 规模不大时可直接用 **Gauss-Seidel** 方法迭代求解；当规模较大时则需对 $A$ 进行**矩阵分解**（如 **Cholesky 分解**）后求解，对线性方程组求解这方面的讨论可参见附录1。


最后可得到如下展开结果：



我们在展开的表面上贴上一层棋盘格纹理，可以直观地观察到扭曲的大小。





### 1.2.2 理论保证—Tutte 嵌入定理

虽然上述算法充满感性的估计和直觉，但它的正确性有严格的数学保证—**Tutte 嵌入定理**

设 $G = (V, E)$ 是 **3-连通平面图**，将顶点集划分为边界顶点 $V_{\text{bnd}}$ 和内部顶点 $V_{\text{int}}$。若满足：

1. **边界固定**：将 $V_{\text{bnd}}$ 按顺序固定到平面上一个**严格凸多边形**的顶点位置；
2. **内部为邻居凸组合**：对每个 $v_i \in V_{\text{int}}$，存在权重 $w_{ij} > 0$（$\sum_j w_{ij} = 1$），使得：

$$
v_i = \sum_{v_j \in N(v_i)} w_{ij} \cdot v_j
$$

**则**：由此得到的平面嵌入**无自交**（全局单射），所有面具有正面积，是一个合法的直线平面嵌入（straight-line planar embedding）。

我们这里使用的是最简单的均匀权重特例
$$
w_{ij} = \frac{1}{\vert N(v_i)\vert}
$$
即每个内部顶点位于其邻居的重心位置。

![image-20260522151857590](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\imgs\image-20260522151857590.png)



### 1.2.3 算法缺陷分析

我们**扭曲过大**（角度和面积都严重变形）。其中一个问题在于均匀权重只利用了网格的连接信息，完全**忽略了网格的几何属性**。

另一个问题在于**固定边界指定**：这个方法需要人为指定一个凸多边形边界，当三维模型本身的轮廓距离凸边形较远（比如非凸边界）时，大量扭曲不可避免。

后面介绍的**自由边界方法**是会3D模型的几何特征解算出更好的边界。

![自由边界 vs 固定边界](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\8f29f01ec492.png)




# 第4章  曲面展开-离散微分几何-Laplace算子

## 1.3 分段线性映射的 Laplace 算子

### 1.3.1 分片线性映射

在三角网格的设定下，我们所求的映射 $f: M \to \mathbb{R}^2$ 将三维网格 $M \subset \mathbb{R}^3$ 映射到平面。只需为每个顶点 $v \in V$ 找到一组 $\mathbb{R}^2$ 坐标（常称为 **UV 坐标**），映射 $f$ 便完全确定。



首先看下三角形**重心坐标（Barycentric Coordinate）**的概念：

![image-20250317142741458](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\d9c70116a558.png)

重心坐标 $\alpha$ 可以认为是小三角形与大三角形之间的**面积比**
$$
\alpha = \frac{A_i}{A_T} = \frac{\left( (\mathbf{x} - \mathbf{x}_j) \cdot \frac{(\mathbf{x}_k - \mathbf{x}_j)^\perp}{\|\mathbf{x}_k - \mathbf{x}_j\|} \right) \|\mathbf{x}_k - \mathbf{x}_j\|}{2 A_T} = \frac{(\mathbf{x} - \mathbf{x}_j) \cdot (\mathbf{x}_k - \mathbf{x}_j)^\perp}{2 A_T}
$$

其中 $A_t$ 是三角形有向面积，$2A_t = (x_iy_j - y_ix_j) + (x_jy_k - y_jx_k) + (x_ky_i - y_kx_i)$。有了 $u, v$ 两方向的梯度后便可组合成 Jacobian 矩阵（见下一节）。

以重心坐标作为插值权重，分段线性映射可以表达为各顶点函数值关于重心坐标的线性组合：
$$
f(x) = \alpha f_i + \beta f_j + \gamma f_k
$$

### 1.3.2 映射的 Laplace 算子

将**梯度算子 $\nabla$**作用于式(2)可得
$$
\nabla f(\mathbf{x}) = f_i \nabla \alpha + f_j \nabla \beta + f_k \nabla \gamma
\\\nabla \alpha = \frac{(\mathbf{x}_k - \mathbf{x}_j)^\perp}{2A_T},\quad \nabla \beta = \frac{(\mathbf{x}_i - \mathbf{x}_k)^\perp}{2A_T},\quad \nabla \gamma = \frac{(\mathbf{x}_j - \mathbf{x}_i)^\perp}{2A_T}
$$

因此
$$
\nabla f(\mathbf{x}) = f_i \frac{(\mathbf{x}_k - \mathbf{x}_j)^\perp}{2A_T} + f_j \frac{(\mathbf{x}_i - \mathbf{x}_k)^\perp}{2A_T} + f_k \frac{(\mathbf{x}_j - \mathbf{x}_i)^\perp}{2A_T}
$$



**Laplace算子**定义为其**梯度的散度** 
$$
\Delta f = \operatorname{div}\,\nabla f
$$
 Laplace 算子度量了函数的"不规则程度"，$\Delta f = 0$ 称为调和映射(Harmonic Mapping)。在我们熟悉的 $\mathbb{R}^2$ 中，上式简化为 $\Delta f = f_{xx} + f_{yy}$。在流形上定义的Laplace算子称为**Laplace-Beltrami算子**。那么在三角形网格上如何定义和计算呢？其关键就在于如何定义离散(三角网格上)**散度(Divergence)**。

如果将网格看成是图(Graph)，从而图的Laplace算子也能用来定义网格的Laplace算子(Uniform Laplacian)
$$
\Delta f(v_i) = \frac{1}{|\mathcal{N}_1(v_i)|} \sum_{v_j \in \mathcal{N}_1(v_i)} (f_j - f_i)
$$

但是图仅考虑网格的连接属性(或组合属性),没有考虑顶点的几何属性，所以使用起来会丢失许多几何信息。

根据**散度定理(Divergence Theorem,又称高斯定理)**
$$
\int_{A_i} \operatorname{div} \mathbf{F}(\mathbf{u})\,\mathrm{d}A = \int_{\partial A_i} \mathbf{F}(\mathbf{u}) \cdot \mathbf{n}(\mathbf{u})\,\mathrm{d}s
$$
对于下面的顶点的小领域 $A_i$ 采用Mixed Voronoi Cell

![image-20250318142418809](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\026a37e73051.png)



那么对于Laplace算子则有
$$
\int_{A_i} \Delta f(\mathbf{u}) \,\mathrm{d}A = \int_{A_i} \operatorname{div} \nabla f(\mathbf{u}) \,\mathrm{d}A = \int_{\partial A_i} \nabla f(\mathbf{u}) \cdot \mathbf{n}(\mathbf{u}) \,\mathrm{d}s
$$


$\mathbf{n}$ 的朝向向外。下图为三角形 $T$ 上与边 $(\mathbf{x}_i,\mathbf{x}_j)$、$(\mathbf{x}_i,\mathbf{x}_k)$ 相关的局部记号（点 $\mathbf{a},\mathbf{b}$ 及法向等）。

![image-20250318142917334](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\94e6ab891cbe.png)

对每一个部分分别进行计算
$$
\begin{aligned}
\int_{\partial A_i \cap T} \nabla f(\mathbf{u}) \cdot \mathbf{n}(\mathbf{u})\,\mathrm{d}s
&= \nabla f(\mathbf{u}) \cdot (\mathbf{a} - \mathbf{b})^\perp
=\frac{1}{2}\, \nabla f(\mathbf{u}) \cdot (\mathbf{x}_j -\mathbf{x}_k)^\perp
\end{aligned}
$$

将之前计算的导数代入进去则有
$$
\begin{aligned}
\int_{\partial A_i \cap T} \nabla f(\mathbf{u}) \cdot \mathbf{n}(\mathbf{u})\,\mathrm{d}s
={} & (f_j - f_i)\,\frac{(\mathbf{x}_i - \mathbf{x}_k)^\perp \cdot (\mathbf{x}_j - \mathbf{x}_k)^\perp}{4A_T}  + (f_k - f_i)\,\frac{(\mathbf{x}_j - \mathbf{x}_i)^\perp \cdot (\mathbf{x}_j - \mathbf{x}_k)^\perp}{4A_T}
\end{aligned}
$$

记 $\gamma_j,\gamma_k$ 分别为顶点 $v_j,v_k$ 处的内角。由
$$
A_T = \tfrac{1}{2}\sin\gamma_j \,\|\mathbf{x}_j - \mathbf{x}_i\|\,\|\mathbf{x}_j - \mathbf{x}_k\| = \tfrac{1}{2}\sin\gamma_k \,\|\mathbf{x}_i - \mathbf{x}_k\|\,\|\mathbf{x}_j - \mathbf{x}_k\|
$$

以及
$$
\cos\gamma_j = \frac{(\mathbf{x}_j - \mathbf{x}_i)\cdot(\mathbf{x}_j - \mathbf{x}_k)}{\|\mathbf{x}_j - \mathbf{x}_i\|\,\|\mathbf{x}_j - \mathbf{x}_k\|},\qquad \cos\gamma_k = \frac{(\mathbf{x}_i - \mathbf{x}_k)\cdot(\mathbf{x}_j - \mathbf{x}_k)}{\|\mathbf{x}_i - \mathbf{x}_k\|\,\|\mathbf{x}_j - \mathbf{x}_k\|}
$$
可得
$$
\int_{A_i} \Delta f(\mathbf{u})\,\mathrm{d}A = \frac{1}{2} \sum_{v_j \in \mathcal{N}_1(v_i)} (\cot \alpha_{ij} + \cot \beta_{ij})(f_j - f_i)
$$

从而对 Laplace–Beltrami 算子在三角网格上的离散化为
$$
\Delta f(v_i) := \frac{1}{2A_i} \sum_{v_j \in \mathcal{N}_1(v_i)} (\cot \alpha_{ij} + \cot \beta_{ij})(f_j - f_i)
$$

### 1.3.3 调和映射与 Dirichlet 能量

**映射的 Dirichlet 能量**定义为映射梯度的 $L^2$ 范数：
$$
E_D(f) = \frac{1}{2}\int_S \|\nabla f\|^2 \,dA
$$

对于从曲面 $S$ 到平面 $\Omega$ 的映射 $f = (u,v)$，总 Dirichlet 能量为两分量之和：

$$
E_D = \frac{1}{2}\int_S \left(\|\nabla u\|^2 + \|\nabla v\|^2\right) dA
$$

极小化 Dirichlet 能量等价于求解 Laplace 方程 $\Delta u = 0, \Delta v = 0$——这正是**调和映射(Harmonic Mapping)**的定义。

将上一节推导的离散 Laplace-Beltrami 算子代入，可以写出三角网格上 Dirichlet 能量的**离散形式**：

$$
E_D(\mathbf{u}) = \frac{1}{2} \sum_{e_{ij} \in E} w_{ij} \|\mathbf{u}_i - \mathbf{u}_j\|^2
$$

其中权重 $w_{ij} = \cot\alpha_{ij} + \cot\beta_{ij}$ 正是 **cot-Laplace 矩阵中的边权重**，$\alpha_{ij}, \beta_{ij}$ 为共享边 $e_{ij}$ 的两个三角形中该边的对角。

DCP内部点同样权重。但是**自由边界**

1. **内部点**：满足调和方程 $\Delta u = 0$，即 $u_i$ 为其邻域顶点的 cot 加权平均：
   $$
   \sum_{v_j \in N(v_i)} w_{ij} (\mathbf{u}_j - \mathbf{u}_i) = 0, \quad w_{ij} = \cot\alpha_{ij} + \cot\beta_{ij}
   $$

2. **边界点**：具体做法是将边界点以弧长比例映射到凸多边形（如圆或矩形）上并固定。这种边界处理保证了映射的全局一一对应性。

3. **求解**：将内部点方程与固定边界组合为一个稀疏线性系统：
   $$
   \mathbf{L} \mathbf{U} = \mathbf{0}, \quad \text{\text{边界点坐标作为} Dirichlet \text{边界条件}}
   $$
   其中 $\mathbf{L}$ 为 $|V|\times|V|$ 的 **cot-Laplace 矩阵**，$\mathbf{U}$ 为所有顶点的 $(u,v)$ 坐标。由于 $\mathbf{L}$ 是对称半正定的（在固定边界后变为正定），可用 Cholesky 分解或共轭梯度法高效求解。

- **Tutte (Cot-Laplace)**：强制所有边界点映射到一个完美的圆或正方形上。结果内部网格会被拉伸，以匹配这个强加的边界形状。角度会被扭曲。
- **DCP**：边界点会"自由"地找到一个位置，使得整体 Dirichlet 能量最小。结果可能是边界变成一个不规则的形状，但内部三角形的角度扭曲被最小化了。

### Tutte 与 DCP 辨析

#### 本质统一：都是调和映射

Tutte 参数化（含 cot-Laplace 权重变体）与 DCP（Desbrun 离散共形参数化）在数学本质上**是同一类问题**——都是求解调和映射（Harmonic Mapping），即极小化 Dirichlet 能量：

$$
\min \quad E_D = \frac{1}{2} \sum_{e_{ij}} w_{ij} \|\mathbf{u}_i - \mathbf{u}_j\|^2
$$

内部顶点均满足 $\Delta u = 0, \Delta v = 0$，用 cotan 权重构建 Laplace 矩阵。两者的**唯一区别在于边界条件的强加方式**。

#### 边界条件差异：满秩约束 vs 最小约束

- **Tutte**：将所有边界顶点按弧长比例映射到凸多边形（圆/矩形）上并固定，作为 Dirichlet 边界条件。这保证了线性系统满秩（正定），但也引入了**人为的边界形变**——内部点被迫适应这个"外挂"的边界形状，局部角度保真性遭到破坏。

- **DCP**：不固定任何边界顶点，而是利用系统本身的零空间结构。cot-Laplace 矩阵 $\mathbf{L}$（未经边界约束时）是半正定的，其零空间仅包含常数向量——对应 u、v 各自的平移自由度。在 $\mathbb{R}^2$ 映射中，零空间为 **3 维**（2 平移 + 1 旋转）。只需**固定任意 2 个顶点的 UV 坐标**即可消除这三个自由度，使系统满秩。其余所有顶点（包括边界）都是自由的，由能量极小化自然决定位置。

#### 为什么 2 个 pin 点就够？

这是 DCP 最优雅的性质：在 $n$ 个顶点的系统中，$\mathbf{L}$ 的秩为 $n - 1$（单连通网格）。对于二维映射 $f = (u, v)$，联立系统的秩为 $2n - 2$，零空间维数为 3：

| 自由度 | 物理含义 | 消去方式 |
|--------|---------|---------|
| 平移 u | 常数偏移 | `pin[0]` → u=0 |
| 平移 v | 常数偏移 | `pin[0]` → v=0 |
| 旋转 | 整体刚体转动 | `pin[1]` → v=0（固定两点连线方向）|

因此 2 个 pin 点恰好提供所需的 3 个标量约束，无需固定整条边界。这与 LSCM（最小二乘共形映射）的秩分析完全一致。

#### 各自的优劣

|  | Tutte（固定边界） | DCP（自由边界） |
|--|--|--|
| **角度保真** | 较差——边界约束强制拉伸 | 较好——边界由能量极小化自然决定 |
| **边界形状** | 规则（圆/矩形等） | 不规则（可能弯曲、自交） |
| **理论保证** | 凸边界 → 保证无翻转 | 无全局一一映射保证，可能出现局部翻转 |
| **求解复杂度** | 解一次线性系统（正定，收敛快） | 解一次线性系统（2 pin 约束，收敛快） |
| **翻转风险** | 仅在退化网格出现 | 高曲率区域可能翻转（类似 LSCM） |
| **适用场景** | 可视化、纹理映射（边界可控） | 几何处理、曲面拟合（需要角度保真） |

#### 从能量角度看统一性

Tutte 和 DCP 本质上都是求解同一族能量极小化问题的不同边界条件下的特例：

$$
\mathbf{L}\mathbf{u} = \mathbf{0}, \quad \mathbf{u}|_{\partial_0} = \mathbf{g}
$$

- 当 $\partial_0$ 取为整个边界环 → Tutte
- 当 $\partial_0$ 取为仅 2 个任意顶点 → DCP

理解这一点后，便可将 Tutte、DCP（以及 ABF、LSCM 等更多共形方法）统一纳入"离散调和能量 + Dirichlet 边界约束"的框架之中。



# 第5章  曲面展开-离散微分几何-Jacobian矩阵

## 1.4 分段线性映射的 Jacobian 矩阵

### 1.4.1 映射的 Jacobian 矩阵

对于每一个三角面片，先建立局部坐标系以简化计算。如下图所示，选取三角形 $$T = [x_i, x_j, x_k]$$，以某顶点 $$x_i$$ 为原点、边 $$[x_i, x_j]$$ 为 $$X$$ 轴方向，按右手定则建立坐标系。

![局部坐标系](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\ea1f5f955905.png)

在每个三角面片 $$t$$ 上，假设映射 $$f$$ 退化为线性函数 $$f_t(x) = J_t x + b_t$$——其中 $$J_t$$ 是 Jacobian 矩阵，刻画了该三角形局部的缩放与旋转；平移量 $$b_t$$ 对参数化无影响，可直接设为零。

分片线性映射$$f$$的Jacobian矩阵如下

$$
J_t =
\begin{pmatrix}
\frac{\partial u}{\partial x} & \frac{\partial u}{\partial y} \\[4pt]
\frac{\partial v}{\partial x} & \frac{\partial v}{\partial y}
\end{pmatrix}
:=
\begin{pmatrix}
u_j-u_i & u_k-u_i \\[4pt]
v_j-v_i & v_k-v_i
\end{pmatrix}
\begin{pmatrix}
x_j-x_i & x_k-x_i \\[4pt]
y_j-y_i & y_k-y_i
\end{pmatrix}^{-1}
\tag{1}
$$

二阶矩阵可以直接求逆：
$$
A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}, \quad
A^{-1} = \frac{1}{ad - bc} \begin{pmatrix} d & -b \\ -c & a \end{pmatrix}
\quad \text{\text{（当} } ad - bc \ne 0 \text{\text{）}}
$$
对公式(1)代数变形可以得到下面的展开形式

$$
\begin{aligned}
{\begin{pmatrix}{\frac{\partial u}{\partial x}}\\{\frac{\partial u}{\partial y}}\end{pmatrix} }=\frac{1}{2A_t}{\begin{pmatrix}{y_j-y_k}&{y_k-y_i}&{y_i-y_j}\\{x_k-x_j}&{x_i-x_k}&{x_j-x_i}\end{pmatrix} }
{\begin{pmatrix}u_i\\u_j\\u_k\end{pmatrix} }\\
{\begin{pmatrix}{\frac{\partial v}{\partial x}}\\{\frac{\partial v}{\partial y}}\end{pmatrix} }=\frac{1}{2A_t}{\begin{pmatrix}{y_j-y_k}&{y_k-y_i}&{y_i-y_j}\\{x_k-x_j}&{x_i-x_k}&{x_j-x_i}\end{pmatrix} }
{\begin{pmatrix}v_i\\v_j\\v_k\end{pmatrix} }
\end{aligned}
\tag{2}
$$

### 1.4.2 Jacobian 矩阵的奇异值

对分段线性映射$$f$$的Jacobian矩阵$$J_t$$可以进行SVD分解 ,$$J_t=U\Sigma V^T,\Sigma={\begin{pmatrix}{\sigma_1}&{0}\\{0}&{\sigma_2}\end{pmatrix} } $$,奇异值$$\sigma_1 , \sigma_2$$分别描述映射在正交两个方向上的拉伸程度，如下图所示

![img](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\b396a6f48867.png)

根据分解后的奇异值$$\sigma_1 , \sigma_2$$，对映射扭曲进行度量

（1）若$$\sigma_1 = \sigma_2$$ 则这两个三角形是相似三角形，则映射是保角映射

（2）进一步若$$\sigma_1 = \sigma_2 =1$$ 则这两个三角形只是发生了旋转

映射$$f$$ 是无翻转的(flip free)，映射后三角形的定向是不能翻转的，否则也会有错乱的情况，有翻转即两个奇异值是异号的
$$
\sigma_1 * \sigma_2 < 0
$$



### 1.4.3 通过奇异值来定义变形能量

Jacobian 矩阵的奇异值 $$\sigma_1, \sigma_2$$ 完整地刻画了局部映射的拉伸行为。基于这两个奇异值，我们可以系统性地定义各类变形能量，每种能量对应不同的几何约束目标。下表汇总了常见的基于奇异值的变形能量。

#### 1.4.3.1 能量函数族

| 能量名称 | 公式 | 含义 |
|---------|------|------|
| **Dirichlet 能量** | $$E_D = \sigma_1^2 + \sigma_2^2$$ | 膜能量，惩罚所有拉伸。极小化时得到调和映射 |
| **共形能量 (LSCM)** | $$E_C = (\sigma_1 - \sigma_2)^2$$ | 惩罚各向异性拉伸，极小化时 $$\sigma_1=\sigma_2$$ |
| **等距能量 (isometric)** | $$E_I = (\sigma_1-1)^2 + (\sigma_2-1)^2$$ | 惩罚偏离恒等映射，极小化时 $$\sigma_1=\sigma_2=1$$ |
| **ARAP 能量** | $$E_{\text{ARAP}} = (\sigma_1-1)^2 + (\sigma_2-1)^2$$ | 与等距能量同形，但配合旋转最优匹配 |
| **面积保持能量** | $$E_A = (\sigma_1\sigma_2 - 1)^2$$ | 惩罚面积改变，极小化时 $$\det J = 1$$ |
| **对称 Dirichlet** | $$E_{SD} = \sigma_1^2 + \sigma_2^2 + \sigma_1^{-2} + \sigma_2^{-2}$$ | 双向惩罚拉伸和压缩，防止翻转 |
| **MIPS 能量** | $$E_{\text{MIPS}} = \frac{\sigma_1}{\sigma_2} + \frac{\sigma_2}{\sigma_1}$$ | 最大/最小奇异值比，纯共形度量 |
| **有界共形扭曲** | $$E_{\text{BD}} = \begin{cases} 0, & \sigma_1 \leq c\sigma_2 \\ \infty, & \text{\text{否则}} \end{cases}$$ | 硬约束 $$\sigma_1/\sigma_2 \leq c$$ |




#### 1.4.3.2 ARAP 能量重新推导

利用 SVD 框架可以更优雅地重新推导 ARAP 的 Local-Global 求解公式。

**Local 步**：对每个三角形寻找最近旋转（或最近相似变换）$$R_t$$。由 SVD 理论，$$J_t = U\Sigma V^T$$ 的最优旋转为 $$R_t^* = UV^T$$（带符号 SVD 保证 $$U,V$$ 为旋转矩阵）。经此旋转后：

$$
\|J_t - R_t^*\|_F^2 = (\sigma_1-1)^2 + (\sigma_2-1)^2
\tag{5}
$$

**Global 步**：固定旋转 $$R_t$$，极小化
$$
\min_{\mathbf{u}} \sum_{t} A_t \|J_t(\mathbf{u}) - R_t\|_F^2
$$
此二次型的 Hessian 矩阵正是 **cot-Laplacian**，因为每个 $$J_t$$ 可写为三角形三顶点的线性函数（式(2)）。





### 1.4.4 基于奇异值优化的展开方法 — ARAP

**ARAP(As Rigid As Possible)**采用**迭代**优化的策略：先从一个简单算法（如 Tutte）初始化，然后交替进行如下两步——首先为每个三角形寻找一个尽量保持原形状的局部近似（**Local 优化**），再回头调整 Jacobian 矩阵使网格整体保持连接（**Global 优化**）。

![Local优化示意](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\d0a502aed39b.png)

若矩阵 SVD 分解后两奇异值相等（$$\sigma_1 = \sigma_2$$），则该变换是相似变换（仅旋转+均匀缩放），由此构成的相似变换族记为 $$\Omega_s$$。用 Frobenius 范数量化当前 Jacobian $$J_t$$ 到 $$\Omega_s$$ 的距离：
$$
d(J_t,L_t)=||J_t-L_t||_F^2
$$
对于整个三角网格，累加所有三角形的差异得到一个如下的能量函数，这个就是我们要优化的能量函数
$$
E_{ARAP}=\sum_{t}A_t||J_t-L_t||_F^2,L_t\in\Omega_s \
\tag{6}
$$

这个优化能量有两部分是要优化的对象，其一是映射Jacobian矩阵$$J_t$$，其二是局部优化目标$$L_t$$。考虑先固定其中一个再优化另外一个，交替进行。

#### 1.4.4.1 Local 优化

固定当前映射的 $$J_t$$，对每个三角形独立寻找最优的相似变换近似 $$L_t^*$$：
$$
L_t^* = min_{L_t}\{d(J_t,M_t)\} ,M_t\in\Omega_s \\
$$
注意到
$$
||J_t-L_t||_F^2=tr((J_t-L_t)^T(J_t-L_t))
$$


根据**Procrustes分析**，通过对$$J_t$$的**带符号的SVD分解(Signed SVD)**可以解得$$L_t^*$$

对$$J_t$$进行SSVD分解保证 $U,V$ 是**旋转矩阵**，可以令$$\sigma_2$$是负的(一般的SVD分解中U,V是正交矩阵不一定是旋转矩阵)
$$
J_t=U\Sigma V^T,\Sigma={\begin{pmatrix}{\sigma_1}&{0}\\{0}&{\sigma_2}\end{pmatrix} }
$$
然后重新组合上面分解的矩阵得到$$L_t$$

$$
L_t= U {\begin{pmatrix}{s}&{0}\\{0}&{s}\end{pmatrix}} V^T,s = \frac{\sigma_1+\sigma_2}{2}
\tag{7}
$$
这个局部优化的效果可参看下图，其中右边黑色三角形是优化的目标三角形，红色三角形为最优的共形三角形

![image-20251023215506894](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\36c564cb3e2a.png)

#### 1.4.4.2 Global 优化

若直接令 $$J_t = L_t$$，各三角形独立优化后会破坏网格顶点间的连接关系——相邻三角形共用的顶点将不再重合。

![Global优化示意](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\a9ebf86e0e44.png)

因此需要**Global 优化**：固定 $$L_t$$，在全局顶点位置 $$\{u_t\}$$ 上优化 $$E_{ARAP}$$。将上节推导的 $$J_t$$ 表达式代入（每个 $$J_t$$ 可写为该三角形三个顶点 $$\{u_i, u_j, u_k\}$$ 的线性函数）：
$$
\begin{aligned}
{\begin{pmatrix}{\frac{\partial u}{\partial x}}\\{\frac{\partial u}{\partial y}}\end{pmatrix} }=\frac{1}{2A_t}{\begin{pmatrix}{y_j-y_k}&{y_k-y_i}&{y_i-y_j}\\{x_k-x_j}&{x_i-x_k}&{x_j-x_i}\end{pmatrix} }
{\begin{pmatrix}u_i\\u_j\\u_k\end{pmatrix} }\\
{\begin{pmatrix}{\frac{\partial v}{\partial x}}\\{\frac{\partial v}{\partial y}}\end{pmatrix} }=\frac{1}{2A_t}{\begin{pmatrix}{y_j-y_k}&{y_k-y_i}&{y_i-y_j}\\{x_k-x_j}&{x_i-x_k}&{x_j-x_i}\end{pmatrix} }
{\begin{pmatrix}v_i\\v_j\\v_k\end{pmatrix} }
\end{aligned}
$$



 可以将(2)式的能量转化为如下形式,我们优化的变量是向量$$\{u_t\}$$
$$
\begin{aligned}
E_{\text{ARAP}}(u,L) = \frac{1}{2}\sum_{t=1}^T\sum_{i=0}^2\cot(\theta_t^i)\|(u_t^i-u_t^{i+1})-L_t(x_t^i-x_t^{i+1})\|^2\\
=\frac{1}{2} \Sigma_{he_{ij}}\cot(\theta_{ij})\|(u^i-u^j)-L_t(x^i-x^j)\|^2\\
\end{aligned}
\tag{8}
$$

对向量 $$\{u_t\}$$ 求导并令其为零（寻找能量极小值的临界点），得到稀疏线性系统：
$$
\sum_{j\in N(i)}[\cot(\theta_{ij}) +\cot(\theta_{ji})](u^i-u^{j}) 
=\sum_{j\in N(i)}[\cot(\theta_{ij})L_{t(i,j)} +\cot(\theta_{ji})L_{t(j,i)}](x^i-x^{j}) 
\tag{9}
$$
最后可以求解上面的**稀疏线性方程组（Sparse Linear System）**来求得$$\{u_t\}$$

**ARAP-共形关系**：展开 ARAP 能量
$$
\begin{aligned}
E_{\text{ARAP}} &= (\sigma_1-1)^2 + (\sigma_2-1)^2 \\
&= (\sigma_1^2 + \sigma_2^2) - 2(\sigma_1+\sigma_2) + 2 \\
&= E_D - 2(\sigma_1+\sigma_2) + 2
\end{aligned}
\tag{4}
$$
其中 $$\sigma_1+\sigma_2$$ 是 Jacobian 矩阵的**核范数（nuclear norm）**，度量拉伸的总量。

**ARAP 与 LSCM 的联系**：当 $$\sigma_1 \approx \sigma_2 \approx 1$$ 时（即映射接近等距），有 $$\sigma_1+\sigma_2 \approx 2$$ 且 $$\sigma_1\sigma_2 \approx 1$$，此时：
$$
E_{\text{ARAP}} \approx E_D - 2 \approx E_C
$$
这意味着在接近理想映射的区域，ARAP 和 LSCM 优化趋向一致。



# 第6章  曲面展开-共形映射初步认识

## 1.5 共形映射初步认识

### 1.5.1 共形映射介绍

如图将一个三维人脸曲面映射到平面圆盘上。我们在人脸曲面任意画两条相交曲线，这两条曲面上的曲线被映射到平面上的两条曲线，空间曲线的交点被映成平面曲线的交点，在交点处，空间曲线的夹角等于平面曲线的夹角。这两条空间曲线任意选取，其夹角都被映射完美保持。

![image-20250312183649382](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\a1610e4050bd.png)

这种能保持局部角度的映射称为**保角映射**（Angle Preserving），在高等数学理论中称这类保持角度的映射为**共形映射(Conformal Mapping)**，它能最大程度地维持几何细节的形状不失真——因此是参数化算法中极具价值的研究方向。

![image-20251203151355902](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\3eaca1488efa.png)

回头再看墨卡托映射：各国面积虽被扭曲，但局部形状得以保持——对地图导航而言，角度保真度远比面积保真度重要，否则按地图导航将导致方向错误。



我们看到这类映射有非常良好的性质(具有直观和谐的美感，以及良好的物理属性)，事实上这类映射也具有良好的数学性质，对它们的研究归属于现代数学分支中的复分析以及黎曼几何理论。经过经年累月的研究可以说数学家们对共形映射的研究已经是颇为充分的了。首先是如下存在性的保证。

**黎曼映照定理(Riemann Mapping Theorem)**保证了数学上任意两个平面区域之间都是存在共形映射。

 设 $$\Omega \subset \mathbb{C}$$ 是单连通开集，$$\Omega \neq \mathbb{C}$$。对任意 $$z_0 \in \Omega$$，存在唯一全纯双射 $$f : \Omega \to \mathbb{D}$$ 

满足：  $$f(z_0) = 0 , f'(z_0) > 0$$ 其中$$\mathbb{D} = \{ z \in \mathbb{C} , |z|<1 \}$$。

理论上的存在性已经由黎曼映照定理保证，接下来的任务是通过变分的方法，构造一个能量泛函 $$E(f)$$ 然后通过最优化的方法来求解，从而得到具体的映射。


### 1.5.2 基于复变函数理论的方法

LSCM(Least Square Conformal Mapping)算法基于复变函数理论中的**Cauchy-Riemann方程**，令复数$$U=u+iv,X=x+iy$$，那么显然$$U(X)$$就是一个复函数，复函数是共形的当且仅当其满足下面公式
$$
{\partial u}/{\partial x} = {\partial v}/{\partial y} \\ {\partial u}/{\partial y} = -{\partial v}/{\partial x}
\tag{1}
$$
共形映射满足 u-等值线和 v-等值线在点的切向量正交

![CR](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\imgs\Screenshot 2026-05-21 at 13.41.14.png)

所以我们可以将能量泛函定义为映射的**Cauchy-Riemann 残差**的最小二乘 $$L^2$$ 范数，即有
$$
E_{\text{LSCM}}(\mathbf{u}) = \int_X |{\nabla u}^ \perp  - \nabla v|^2 dA
\tag{2}
$$
结合上一节推导的**Jacobian矩阵**，对于三角形 $T$ 映射的偏导数有
$$
{\partial U}/{\partial x} + i{\partial U}/{\partial y} = \frac{i}{2A_T}(W_{i,T},W_{j,T},W_{k,T}){\begin{pmatrix}u_i\\u_j\\u_k\end{pmatrix}}
$$
其中
$$
\begin{cases}W_{i,T} = (x_k - x_j)+i(y_k-y_j)\\
W_{j,T} = (x_i - x_k)+i(y_i-y_k)\\
W_{k,T} = (x_j - x_i)+i(y_j-y_i)\\
\end{cases}
\tag{3}
$$

那么对于每个三角形$$T_i$$可以通过如下方法定义一个能量来衡量其不满足共形性的程度


$$
C(T_i) = {||{{\partial U}/{\partial x}}+i{{\partial U}/{\partial y}}||}^2 A_{T_j}=\frac {1} {4A_T}{|(W_{j1},W_{j2},W_{j3})(U_{j1},U_{j2},U_{j3})|}^2
$$


将所有三角形能量进行累加$$E_{\text{LSCM}}(\mathbf{u}) = \Sigma_{i=1}^{n} C(T_i)$$，可以认为是关于复数$$U=(U_1,U_2,...,U_n)^T$$的**复二次型**
$$
E_{\text{LSCM}}(\mathbf{u}) = C(U=(U_1,U_2,...,U_n)^T)=U^*CU
$$
其中 $C$ 是**Hermitee Gram矩阵**，所以可以对其进行分解
$$
C=M^*M
\\M=(m_{ij})\text{ \text{是} }|F|\times|V|\text{ \text{稀疏矩阵}}
m_{ij} = \begin{cases}W_{j,T_i}, & \text{\text{如果} } v_j \text{ \text{属于三角形} } T_i \\ 0\end{cases}
\tag{4}
$$
如果不加限制那么会得到平凡解(trivial)即$$U=0$$的常映射，所以要想得到非平凡解需要固定一部分点**(pin点)**，即固定某些$$U$$的值。

我们将$$U$$分块为$$(U_f^T,U_p^T)^T$$其中$$U_f$$是自由的点$$U_p$$是固定的点，同样的将$$M$$分解$$M =(M_f \ M_p)$$,其中$$M_f$$的形状是$$|F|*(|V|-p)$$
$$
||MU||^2=||M_fU_f+MpUp||^2
$$
上面的讨论还是基于复数的，我们要进行数值计算就要转到实数域上，进一步对**复矩阵$$M$$的实部与虚部进行分解**，$$M=M^{re}+iM^{im}$$,最终可以将上式转为求解如下的**实最小二乘**
$$
\begin{aligned}
C(x) = ||Ax-b||^2,
A={\begin{pmatrix}{M_f^{Re}}&{-M_f^{Im}}\\{M_f^{Im}}&{M_f^{Re}}\end{pmatrix} },
b=-{\begin{pmatrix}{M_p^{Re}}&{-M_p^{Im}}\\{M_p^{Im}}&{M_p^{Re}}\end{pmatrix} }{\begin{pmatrix}U_p^{Re}\\U_p^{Im}\end{pmatrix}}
\end{aligned}\tag{5}
$$
其中矩阵A的大小为$$2|F|\times 2(|V| -p)$$，并且$$b\in R^{2|F|},x\in R^{2|V|-p}$$ ，原始论文在附录处有证明当固定点个数大于等于2时($$p\geq2$$)，矩阵A满秩，方程有唯一解。


### 1.5.3 共形能量的一致性

LSCM 共形能量与前面介绍的 Dirichlet 能量具有如下关系：**LSCM 共形能量 = Dirichlet 能量 − 参数域有向面积**。这意味着最小化 LSCM 共形能量等价于**在固定边界条件下最小化 Dirichlet 能量**（面积项 $\mathcal{A}$ 在边界固定时为常数）。

Cohen-Steiner 等人在 2002 年的工作中证明：**LSCM（Least Squares Conformal Maps）与 Desbrun 的 DNCP（Discrete Natural Conformal Parameterization）在数学上完全等价**。

- **DNCP** 基于离散 Dirichlet 能量的变分原理：边界固定时，极小化 Dirichlet 能量等价于求解线性 Laplace 方程，数值骨架正是 `cot-Laplacian` 矩阵
- **LSCM** 基于 Cauchy-Riemann 残差的 $L^2$ 最小二乘：由 $E_{\text{LSCM}} = E_D - \mathcal{A}$ 可知，当参数域面积 $\mathcal{A}$ 固定时，极小化 LSCM 能量即极小化 Dirichlet 能量

两者的法方程最终都归结为同一个 `cot-Laplacian` 系统——不同出发点的方法共享同一线性骨架（见 [5] Cohen-Steiner et al. 2002）。

展开 LSCM 能量：

$$
\begin{aligned}
E_{\text{LSCM}}(\mathbf{u})
&= \int_{\chi} \frac{1}{2}\Bigl( \nabla u^{\perp} \!\cdot\! \nabla u^{\perp} + \nabla v \!\cdot\! \nabla v - 2\,\nabla u^{\perp} \!\cdot\! \nabla v \Bigr)\,dA \\[4pt]
&= \int_{\chi} \frac{1}{2}\Bigl( \nabla u \!\cdot\! \nabla u + \nabla v \!\cdot\! \nabla v - 2\,\nabla u \times \nabla v \Bigr)\,dA \\[4pt]
&= E_D(\mathbf{u}) - \mathcal{A}(\mathbf{u})
\end{aligned}
$$

其中 Dirichlet 能量为

$$
E_D(\mathbf{u}) = \frac{1}{2}\int_\Omega \bigl(|\nabla u|^2 + |\nabla v|^2\bigr) \, dA
$$

关键恒等式来自 Cauchy-Riemann 残差的展开：

$$
\begin{aligned}
\bigl|(\nabla u)^{\perp} - \nabla v\bigr|^2
&= |\nabla u|^2 + |\nabla v|^2 - 2\,\nabla u \times \nabla v
\end{aligned}
$$

因此 $E_C = E_D - \mathcal{A}$，其中 $\mathcal{A} = \displaystyle\int_D (\nabla u \times \nabla v)\,dA$ 为参数域有向面积。

Desbrun 等人 [DMA02] 进一步指出，Dirichlet 能量可分解为参数域面积与共形扭曲项：

$$
E_D = E_A + \frac{1}{2}\int_S (\sigma_1 - \sigma_2)^2 \,dA
$$

其中 $E_A = \int_S \det(J)\,dA$ 为参数域面积，$\sigma_1, \sigma_2$ 为 Jacobian 奇异值。当且仅当 $\sigma_1 = \sigma_2$（共形映射）时 $E_D = E_A$，扭曲项消失。

> 这个关系揭示了 Dirichlet 能量在参数化中的核心地位：极小化 Dirichlet 能量 → 趋向于保角映射。

#### 1.5.4 ARAP 能量与 LSCM 能量的等价性

ARAP 的能量形式与 LSCM 在**固定边界条件**下完全等价。对单个三角形，设 Jacobian 为 $J$，SVD 为 $J = U\Sigma V^{\mathsf T}$，$\sigma_1 \geq \sigma_2 \geq 0$。

**ARAP 局部能量**（到最近旋转的 Frobenius 距离）：

$$
E_{\text{ARAP}}(T) = \min_{R \in SO(2)} \|J - R\|_F^2 = (\sigma_1 - 1)^2 + (\sigma_2 - 1)^2
$$

**LSCM 局部能量**（Cauchy-Riemann 残差，$\det J > 0$ 时）：

$$
E_{\text{LSCM}}(T) = \|J\|_F^2 + 2\det J = (\sigma_1 + \sigma_2)^2
$$

**Dirichlet 能量**：$E_D(T) = \|J\|_F^2 = \sigma_1^2 + \sigma_2^2$。

展开 ARAP 能量：

$$
E_{\text{ARAP}}(T) = \|J\|_F^2 - 2(\sigma_1 + \sigma_2) + 2
$$

其中 $\sigma_1 + \sigma_2$ 为 Jacobian 的**核范数**，度量拉伸总量。全局上 $E_{\text{LSCM}} = E_D - \mathcal{A}$；ARAP 的全局步骤求解 Poisson 方程 $\Delta \mathbf{u} = \nabla \cdot \mathbf{b}$，刚度矩阵同样是 **cot-Laplacian**，与 LSCM 法方程共享同一线性算子。

在离散网格上，ARAP 全局步骤极小化

$$
\min_{\mathbf{u}} \sum_{T \in \mathcal{F}} \sum_{(i,j) \in T} \cot\theta_{ij}^T \|\mathbf{u}_i - \mathbf{u}_j - R_T(\mathbf{x}_i - \mathbf{x}_j)\|^2
$$

对 $\mathbf{u}$ 求导得 $\mathbf{L}\mathbf{u} = \mathbf{b}$，其中 $\mathbf{L}$ 为 cot-Laplacian。LSCM 法方程导出同一个 $\mathbf{L}$；固定边界时右端项 $\mathbf{b}$ 由边界约束唯一确定，故

$$
\boxed{\mathbf{u}_{\text{ARAP}} = \mathbf{u}_{\text{LSCM}} = \mathbf{L}^{-1} \mathbf{b}}
$$

**总结**：ARAP 的 Local-Global 迭代中，Global 步骤与 LSCM 的一步求解是同一个线性系统；ARAP 通过迭代逼近最优旋转 $R_T^*$，LSCM 直接消去旋转自由度。固定边界且收敛到驻点时，两者给出相同解。



# 第7章  曲面展开-网格的谱处理SCP

## 1.6 网格的谱处理 SCP

### 1.6.1 SCP 方法

SCP（Spectral Conformal Parameterization，Mullen et al.）是 LSCM 的谱方法变体。LSCM 需手工指定两个 pin 点以消除平凡解；SCP **不必指定 pin 点**，从而避免 pin 点带来的额外扭曲。

![image-20260525110441072](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\imgs\image-20260525110441072.png)

SCP 的核心思想是：在所有**单位范数**的非平凡解中，求能量最小者，等价于求能量矩阵的**主特征向量**（Mullen et al., 2008）。

### 1.6.2 离散共形能量

SCP 所优化的正是 1.5.3 节建立的 LSCM 共形能量。连续情形下，它与 Dirichlet 能量、参数域有向面积满足：

$$
E_C(\mathbf{u}) = E_D(\mathbf{u}) - \mathcal{A}(\mathbf{u})
$$

参数域有向面积可写为边界边的求和：

$$
\mathcal{A}(\mathbf{u}) = \sum_{e_{ij} \in \partial \mathcal{U}} \frac{1}{2}(u_i v_j - u_j v_i)
$$

离散化后，共形能量成为对 **(u,v) 堆叠向量** $\mathbf{x} = (u_1,\ldots,u_n,v_1,\ldots,v_n)^{\mathsf T}$ 的二次型：

$$
E_C(\mathbf{x}) = \frac{1}{2}\mathbf{x}^{\mathsf T} L_C \mathbf{x}
$$

其中 $L_C$ 为稀疏对称矩阵。记 Dirichlet 能量的 Hessian 为 $L_D$，向量面积矩阵为 $A$，则有：

$$
L_C = L_D - A
$$

在三角网格上，$L$ 为 cotan 拉普拉斯，$L_D = \mathrm{diag}(L,L)$。向量面积矩阵 $A$ 仅由边界边贡献（与 libigl 的 `vector_area_matrix` 一致），对边界边 $(i,j)$ 有：

$$
A_{i,\,j+n} = A_{j+n,\,i} = \tfrac{1}{4}, \qquad
A_{i+n,\,j} = A_{j,\,i+n} = -\tfrac{1}{4}
$$

因此实现中常用：

$$
L_C = -\mathrm{diag}(L,L) + 2A
$$

**注意**：不要把它与「单独对 cotan 拉普拉斯 $L$ 求最小特征值」混为一谈——后者是另一套谱问题。

### 1.6.3 谱求解

SCP 等价于如下约束优化问题：

$$
\mathbf{x}^* = \underset{\substack{\mathbf{x}^{\mathsf T}\mathbf{e}=0 \\ \mathbf{x}^{\mathsf T}\mathbf{x}=1}}{\arg\min}\ \mathbf{x}^{\mathsf T} L_C \mathbf{x}
$$

其中 $\mathbf{e}$ 为常数模态向量。极小值即 $L_C$ 的最小特征值 $\lambda$，对应特征向量 $\mathbf{x}^*$ 即为参数化坐标。

在**去掉边界常数模态**（投影算子 $P = B - EE^{\mathsf T}$）后，用**逆幂迭代**求解：

$$
L_C \mathbf{x}_{k+1} = P \mathbf{x}_k
$$

**幂迭代**（正向）反复左乘矩阵，收敛到最大特征值对应的特征向量：

$$
\mathbf{y} \leftarrow A\mathbf{y}, \qquad \mathbf{y} \leftarrow \mathbf{y}/\|\mathbf{y}\|
$$

**逆幂迭代**则通过求解线性方程组，收敛到最小特征值对应的特征向量：

1. 给定初值 $\mathbf{y}_0$
2. **while** $\mathrm{Residual}(L_C, \mathbf{y}_{i-1}) > \varepsilon$ **do**
3. 解 $L_C \mathbf{y}_i = \mathbf{y}_{i-1}$
4. $\mathbf{y}_i \leftarrow \mathbf{y}_i / \|\mathbf{y}_i\|$
5. **end while**

几何上，反复左乘矩阵会把单位球沿最大特征向量方向"压扁"为细纺锤形：

![幂迭代的几何直观：单位球经反复左乘矩阵后沿主特征向量方向收缩](c:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\scripts\build_pdf\images\d9e063ceb12d.png)

**与 Fiedler 向量的区别**：图论中 Fiedler 向量常指**标量**拉普拉斯第二小特征值对应的特征向量；SCP 处理的是 **2|V| 维堆叠系统** $L_C$ 的谱，二者概念相近但矩阵与约束并不相同。

