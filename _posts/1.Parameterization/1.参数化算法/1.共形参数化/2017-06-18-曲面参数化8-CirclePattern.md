---
layout: post
title: "曲面参数化8-CirclePattern算法"
category: Parameterization
---

### 直观求解保角映射的算法-ABF算法

三角网格是由成千上万的三角形组合而成的，那么如果两个三角网格的每对三角形都尽可能相似的话，那么两个三角网格也可以认为是“相似”的，所以我们尝试着让每个小三角形都尽可能保持相似的从而保持整体的形状 ，这种从三角形角度考虑出发的方法称为**ABF（Angle Based Flattening）**算法

设$\alpha_i^0$，$\alpha_i$分别为三角网格展开前后的某个内角值，那它们的映射前后的差值就是$(\alpha_i - \alpha_i^0)^2$，对所有的角度累加，从而得到一个能量值$E=min\Sigma(\alpha_i - \alpha_i^0)^2$，而我们要让这个能量值尽可能小。

由于角度发生改变了，所以对于每个三角形我们要让内角和保持为$\pi$, 即$\Sigma_{\alpha_i\in t}{\alpha_i}=\pi$ 

另外由于是展平到了平面上，所以对于内部每个顶点v，与它连接角度的角度和为$2\pi$,即$\Sigma_{\alpha_i\in v}=2\pi$

(3)对于每个顶点v,其1-邻域两个对角$\beta_i与\gamma_i$满足如下关系$\prod \frac {sin_{\beta_i}} {sin\gamma_i}=1$、

上面约束优化问题虽然可以通过Lagrange乘子法转化为无约束优化问题进行求解，但是由于约束(3)中含有非线性条件所以是不容易求解的，一种思路是将约束(3)进行**线性化**后再求解。

![image-20250721143632617](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250721143632617.png)



**CirclePatterns算法**

Stephenson实现了三角网格的CirclePacking算法，但是Circle Packing的问题是只考虑了三角网格的连接性质，却没有考虑到其几何性质。

共形映射保持曲面上每个点周边的圆域，所以圆形是共形几何中的基础构建单元。可以想象对于一个曲面，假设一个映射将它上面所有的圆都映射同样的圆形，那么这个映射也一定是一个共形映射。有了这样一个念头就可以构建这样对共形映射的数值逼近算法，通过大量的圆来对曲面进行填充（CirclePacking)，然后求一个映射对这些大量的圆都保持圆形的话，那这个映射就具有很好的共形性了。

![image-20251107104108134](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251107104108134.png)

对于三角网格来说，所有三角形的外接圆可以认为是对它的一个圆填充,我们的目的就是求这个圆填充，即求出其中填充圆的半径与相交角度，其中相交角度称为**边权重(edge weight)**$\theta_e$

![image-20251107105925485](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251107105925485.png)

### Coherent angle system

对于给定映射后的角度是$\theta_e$ (共形变换下是保持不变的)和一个抽象三角网格（Abstract Triangulation），**一个CirclePattern存在当且仅当Coherent angle system存在的**，所以要先调整角度来保证Circle Pattern的存在性

对于所有角度$ \hat\alpha_{ij}^k$

大于0

![image-20251015085845727](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251015085845727.png)

对于每个三角形，相加等于$\pi$

![](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251015090132394.png)

对每条边$e$有

![image-20241129203251062](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20241129203251062.png)

从而转化为一个线性问题，3|F|个变量，3|F|个不等式约束，|F|+|E|个等式约束
由于是展平，所以对于内部顶点角盈为0，即周角和为2pi

满足了基本的配置之后，我们当然最好是要使得小三角形的角度变化不会很大，类似之前讲的基于角度的ABF算法一样的最优化，但是不用像ABF一样考虑循环一致性。

![image-20251015090401255](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251015090401255.png)



约束条件

![image-20251015090458352](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251015090458352.png)

边界情况的指定

![image-20251107111308424](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251107111308424.png)

自由边界与指定边界

![image-20251107105336742](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251107105336742.png)

### 变分法求半径

有了边权重后，通过简单的平面几何计算就可以得到展平后三角网格中每个内角的角度值。

![image-20251107104253558](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251107104253558.png)

我们再通过变分的方法求解圆的半径，从而得到整个圆配置



![image-20241201134811707](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20241201134811707.png)

**intrinsic local delaunay**

可以先对原始的三维三角网格进行**intrinsic local delaunay**的处理，从而计算得到的扭曲更小

### 锥奇异点

锥奇异点，展平后曲面上点的高斯曲率几乎处处为0，而锥奇异点的高斯曲率为给定数值不为0的点

![image-20250924183558400](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250924183558400.png)