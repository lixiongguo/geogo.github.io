---
layout: post
title: "计算共形几何-holonomy与度量四边形网格化"
category: Parameterization
categories: ["Parameterization", "Parameterization-ComputationalConformalGeometry"]
---


![image-20260526173124605](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260526173124605.png)



## 与 N-symmetric Design 的关系

![image-20251127095738973](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251127095738973.png)

在向量场引导四边形网格化中，常用的对象不是普通向量场，而是 \(N\)-symmetric direction field。对四边形网格，最重要的是 \(N=4\) 的 cross field：一个方向旋转 \(k\frac{\pi}{2}\) 后仍然表示同一个局部坐标轴集合。

这时 holonomy 不再必须严格为零，而是允许落在离散旋转群中：

$$
\operatorname{Hol}_{\gamma}\in \frac{2\pi}{N}\mathbb{Z}.
$$

对 cross field 而言就是：

$$
\operatorname{Hol}_{\gamma}\in \frac{\pi}{2}\mathbb{Z}.
$$

如果绕某个顶点一圈后 cross field 跳到了另一个等价分支，这个跳变可以用 matching、period jump 或 layer shift 来记录。QuadCover 中的分支覆盖正是把这些非零 holonomy 展开到不同 sheet 上，使原本多值的 cross field 在覆盖空间中变成单值对象。

可以把这条关系写成：

$$
\text{matching} \rightarrow \text{covering} \rightarrow \text{holonomy elimination} \rightarrow \text{single-valued field}.
$$

其中 matching 记录跨边时需要补偿几个 quarter-turn；绕闭环累计 matching，就得到该环路上的离散 holonomy。









如果绕一圈后完全回到原状态，holonomy 为零，对应路径无关；如果绕一圈后多出一个旋转、平移或 sheet 跳变，那么这个差值就是 holonomy。

rotation compensation 可以理解为：**跨边传播方向或局部坐标系时，除了曲面本身的平行移动，还额外加入一个离散旋转，用来补偿累计 holonomy。**

![image-20251127095713763](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251127095713763.png)



在普通 Levi-Civita transport 中，向量沿曲面传播会受到曲率影响；绕闭环回来时，方向可能因为角度亏缺而偏转。如果希望得到一个 cross field 或 seamless UV，就不能任由这种偏转连续变化，而要把它调整到四边形网格允许的离散旋转上。

因此，跨边时可以把传播过程理解为两步：

1. 先用曲面的几何联络把相邻切空间对齐。
2. 再施加一个 \(k\frac{\pi}{2}\) 的离散 rotation compensation，使两个局部 frame 按 cross field 的等价关系对齐。

这个补偿量在向量场路线中表现为 matching 或 period jump；在度量路线中表现为锥点 holonomy rounding。它们的目标相同：让绕闭环后的累计误差落在四边形网格允许的离散结构中。

