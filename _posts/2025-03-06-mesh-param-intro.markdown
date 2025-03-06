---
layout: post
title: "曲面展平与网格参数化算法"
author: David Lee
date: 2025-03-06
category: 几何与拓扑
---
本文主要介绍曲面展平与网格参数化算法
<!--more-->
#### 曲面展平映射

如何将一个三维空间中的曲面摊平到二维的平面上？有时为了方便观察研究人们会将地球仪的表面展平。这在生活经验中看起来似乎不太起眼的问题，但是却蕴含着无限的几何与拓扑的奥秘。想象一下如果有一个曲面我们想要设计程序让计算机来做这个“展平”的话,似乎就不是一件容易的事了。

比如通过CT扫描获取到腹部断层图像，然后用多视角几何的方法重建三维直肠曲面后，为了方便医生的观察，最后将这个直肠曲面平展到平面上。（使用这种方法，设备和病患没有接触，不需要麻醉，不会诱导并发症）

![image-20250227101914414](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250227101914414.png)

为了解决这个问题我们要从数学上找到一个**展平映射**$f:R^3\rightarrow R^{2}$，使得三维空间中曲面的点与二维空间中的点是相对应。

为了先对这个问题有一个初步的了解，考虑最简单的情况，即最简单的二维曲面—球面。如下图所示这种绘制世界地图的“墨卡托投影法”。基本方法是假想在球面内部有一个光源，而球面外部包围着一个圆柱面,光线将球面的点投射到圆柱面上,再将圆柱面展开。

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306100413501.png" alt="image-20250306100413501" style="zoom: 67%;" />

**映射是有扭曲的**,可以看到图中格陵兰岛面积跟非洲差不多大，但是真实相差很远。这种方法牺牲面积大小，保留角度和形状(也称为共形映射)沿着赤道不会发生扭曲，越靠近极点的地方面积扭曲就越大。

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250228102623615.png" alt="image-20250228102623615" style="zoom:67%;" />

对于更加复杂的曲面，又该如何计算呢？比如下图所示的大卫头像，我们限定后面要研究的对象都是”拓扑圆盘“的曲面（有一条简单曲线作为边界) 。

#### 三角网格参数化

如图，计算机中的曲面是由许多小三角形构成的,整体称为**三角网格(Mesh)** 记作$M=\{V,E,F |V,E,F为网格的顶点,边,面\}$

![image-20250306112054639](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306112054639.png)

在这样的设定下，那么我们要求的映射$f$又可以写成这样$f:M \rightarrow R^{2},\text M{是R^{3}中的三角网格}$ ,而将网格进行展平的算法称为”**网格参数化算法**“(Mesh Parameterization)，而要构造这样映射$f$只要对顶点集$V$找到一组$R^2$的坐标(一般称为”**UV坐标**“如下图所示）即可。

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306113753650.png" alt="image-20250306113753650" style="zoom: 80%;" />

注意到有一些约束条件是需要满足的

1.映射之后内部的三角形的边是不能相交的

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250227112126656.png" alt="image-20250227112126656" style="zoom:50%;" />

2.映射后三角形的定向是不能翻转的，否则也会有错乱的情况

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250227120632868.png" alt="image-20250227120632868" style="zoom: 50%;" />

3.映射后的边界也是不能相交的

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306151844519.png" alt="image-20250306151844519" style="zoom:50%;" />

#### 正确但并不好的简单算法

类似上面的”墨卡托投影“的过程，我们可以先进行直觉性的假想实验。假设三角网格M是有弹性的，那么我们可以先外部施加力将边界固定下来，比如把它们固定到一个圆周上, 三角网格的边对力进行传导，那内部的点也会跟着改变。

为了简化处理，假设对于内部某个顶点$v \in V_{int}$作用在它身上的力是均衡的，那它将会位于其邻居顶点所构成区域的质心位置，这样自然就形成了一个方程了。而整个过程是线性的，所以应该是容易解的。

![image-20250306105030177](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306105030177.png)

1. 将$M$中的顶点集$V$进行编号(用数字代表顶点) $V=\{1,2,3,...n\}$,并划分为内点集和边界点集即 $V = V_{int} \cup V_{bnd}$
2. 对内部顶点$v \in V_{int}$,设$N_v$为其邻居顶点集，则由于$v$位于质心位置则有$x_v = \frac 1 {|N_v|} \Sigma_{u \in N_v}x_u$
3. 对边界顶点$v \in V_{bnd}$,将边界点也进行排序并且$v$的序号$i_v$，由于边界点定在圆周上那么$x_{i_v}=(rcos({\theta_{i_v}}),rsin({\theta_{i_v}}))\\$

上面的过程实际上可以表示成两个实稀疏线性方程$Ax=b,A=\{a_{ij}\}_{n*n}\\$(u,v两个坐标),下面以其中一个坐标为例

1. 对任意的$v \in V_{int}$ , $A(v,u) = \begin{cases}  1 &，  u=v \\ -\frac 1 {|N_v|}&， u \in N_v \\ 0 &，其它\end{cases} $
2. 对任意的$v \in V_{bnd}$, $A(v,u) = \begin{cases}  1 &，  u=v \\  0 &，其它\end{cases} $，其边界序号为$i_v$ ,则$b_{i_v} = rcos({\theta_{i_v}})$


C++中可以通过Eigen库来解这个稀疏线性方程组最后可以得到如下图结果

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306143314990.png" alt="image-20250306143314990" style="zoom:67%;" />

如果在表面贴上一层棋盘格，可以直观地观察到扭曲的大小

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306144819046.png" alt="image-20250306144819046" style="zoom:67%;" />

上面算法的正确性(解是存在的，并且符合约束条件)是有严格的数学保证，如果将三角网格(Mesh)看成是一个图(graph)的话，那么根据图论平面图理论中的**Tutte定理**

![image-20250303203607936](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250303203607936.png)

对于”拓扑圆盘“的三角网格，只要将边界点固定在一个凸多边形上，并且内部的点是其邻居的凸组合(上面算法设置内点位于邻居质心)就能形成一个合法的参数化。

上面算法虽然是正确的，但是并不好，对于稍微复杂一些的曲面就会有很严重的扭曲。比如图中的兔头，耳朵部分的面积拉伸非常大。而对于如何尽可能减小扭曲，如何尽可能提高算法的效率是相关领域科研技术人员努力的目标

![image-20250306152433544](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306152433544.png)

最后介绍一下”伪3D" : 对于一部分3D模型如果我们能够找到某个方向，在这个方向上曲面上的点之间不存在遮挡的话，那这样的话展平映射只要直接在这个方向上做投影就可以。比如对于平整的芯片来说就是这样的”伪3D“的场景。

![image-20250227110050467](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250227110050467.png)