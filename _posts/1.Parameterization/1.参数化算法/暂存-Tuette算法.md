---
layout: post
title: "曲面参数化2-Tutte参数化"
category: Parameterization
---

### 三角网格

计算机中所有3D物体的表面都是由许多小三角形拼在一起表示的，这样的三角形组成的网格称为**三角网格(Mesh)** 记作$M=\{V,E,F |V,E,F为网格的顶点,边,面\}$

![image-20250311193102749](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250311193102749.png)

**拓扑圆盘**：具有单个边界"开口网格曲面"，我们下面用这个简化版("抽象")的人物头像来做实验

![image-20250306112054639](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306112054639.png)

**Tutte算法**

假设三角网格M是有弹性的即每一条边都视为是一个弹簧的话，网格的边界是一个橡皮筋。那么我们可以在外部施加力将边界固定下来, 由于三角网格的边会对力进行传导，那内部的点也会跟着改变。

假设我们把三角网格的边界固定到一个圆周上

![image-20250311194454982](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250311194454982.png)

为了简化处理，假设对于内部某个顶点$v \in V_{int}$作用在它身上的力是均衡的，那它将会位于其邻居顶点所构成区域的质心位置，这样自然就形成了一个方程了。

![image-20250306105030177](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306105030177.png)

1. 将$M$中的顶点集$V$进行编号(用数字代表顶点) $V=\{1,2,3,...n\}$,并划分为内点集和边界点集即 $V = V_{int} \cup V_{bnd}$
2. 对内部顶点$v \in V_{int}$,设$N_v$为其邻居顶点集，则由于$v$位于质心位置则有$x_v = \frac 1 {|N_v|} \Sigma_{u \in N_v}x_u$
3. 对边界顶点$v \in V_{bnd}$,将边界点也进行排序并且$v$的序号$i_v$，由于边界点定在圆周上那么$x_{i_v}=(rcos({\theta_{i_v}}),rsin({\theta_{i_v}}))\\$

上面的式子实际上可以表示成实**稀疏线性系统**$Ax=b,A=\{a_{ij}\}_{n*n}\\$(u,v两个坐标)

1. 对任意的$v \in V_{int}$ , $A(v,u) = \begin{cases}  1 &，  u=v \\ -\frac 1 {|N_v|}&， u \in N_v \\ 0 &，其它\end{cases} $
2. 对任意的$v \in V_{bnd}$, $A(v,u) = \begin{cases}  1 &，  u=v \\  0 &，其它\end{cases} $，其边界序号为$i_v$ ,则$b_{i_v} = (rcos({\theta_{i_v}})，rsin({\theta_{i_v}}) )$

对上述线性方程的求解，如果矩阵$A$的规模不是很大，可以直接$Gauss-Seidal$方法迭代求解，如果$A$的规模很大的话要对$A$进行分解(如Cholesky分解)后求解，在后面文章中我们将会详细讨论这个线性方程数值求解问题。


最后可以得到如下图的展平结果

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306143314990.png" alt="image-20250306143314990" style="zoom:67%;" />

在展平的表面上贴上一层棋盘格，可以直观地观察到扭曲的大小。

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306144819046.png" alt="image-20250306144819046" style="zoom:67%;" />

**理论依据**

事实上，虽然上面的算法我们做了一系列的假设，但是算法的正确性还是有严格的数学保证(解是存在的，并且是有良好性质的)，这个正确性保证来自于图论(Graph Theory)中的**Tutte嵌入定理**(参考文献[1])。

![image-20251027160427694](..\..\..\..\imgs\image-20251027160427694.png)

将三角网格(Mesh)看成是一个图(graph)的话，定理说明只要将边界点固定在一个凸多边形上，并且内部的点是其邻居的凸组合(上面算法设置内点位于邻居质心)就能形成一个符合约束的参数化（无自交，全局单射）。



**算法的不足与改进**

上面的算法虽然正确性是有保证的，但是缺陷也是很明显的就是扭曲太大了(同时角度和面积的变形都很大)。

由于我们的平均权重只考虑到网格的组合性质(没有使用到关于坐标位置等几何信息),所以对于几何上比较复杂的网格模型不可避免会有比较大的扭曲,[2]中优化了权重将几何信息引入从而缓解了这部分造成的扭曲。

这个方法需要我们先固定一个凸多边形边界，那么如果原来的3D模型边界与我们所指定边界如果差别比较大的话（比如“非凸”的边界），那就不可避免的会有比较大的扭曲变形，比较好的当然是算法根据3D模型的特征自动寻找一个比较符合的边界,后面介绍的算法只需要固定两个顶点就会找到一个比较好的边界,并且尽可能减少角度的变形)

![image-20250311204032486](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250311204032486.png)



**参考文献**

[1] Tutte, W. T. (1963). *How to draw a graph*. Proceedings of the London Mathematical Society.

[2] Floater, M. S. (1997). *Parametrization and smooth approximation of surface triangulations*. CAGD.