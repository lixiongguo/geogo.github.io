---

layout: post
title: "曲面参数化8-CirclePattern算法"
category: Parameterization
---

### 直观求解保角映射的算法-ABF算法

三角网格是由成千上万的三角形组合而成的，那么如果两个三角网格的每对三角形都尽可能相似的话，那么两个三角网格也可以认为是“相似”的，所以我们尝试着让每个小三角形都尽可能保持相似的从而保持整体的形状 ，这种从三角形角度考虑出发的方法称为**ABF（Angle Based Flattening）**算法

设$\alpha_i^0$，$\alpha_i$分别为三角网格展开前后的某个内角值，那它们的映射前后的差值就是$(\alpha_i - \alpha_i^0)^2$，对所有的角度累加，从而得到一个能量值$E=min\Sigma(\alpha_i - \alpha_i^0)^2$，![image-20251015090401255](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251015090401255.png)而我们要让这个能量值尽可能小。

由于角度发生改变了，所以对于每个三角形我们要让内角和保持为$\pi$, 即$\Sigma_{\alpha_i\in t}{\alpha_i}=\pi$ 

另外由于是展平到了平面上，所以对于内部每个顶点v，与它连接角度的角度和为$2\pi$,即$\Sigma_{\alpha_i\in v}=2\pi$

![image-20251113093156112](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251113093156112.png)

(3)对于每个顶点v,其1-邻域两个对角$\beta_i与\gamma_i$满足如下关系$\prod \frac {sin_{\beta_i}} {sin\gamma_i}=1$、



![image-20250721143632617](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250721143632617.png)

**求解**

上面约束优化问题虽然可以通过Lagrange乘子法转化为无约束优化问题进行求解，但是由于约束(3)中含有非线性条件所以是不容易求解的，一种思路是将约束(3)进行**线性化**后再求解。



实际上保角映射并不是说保三角网格的内角，而是保持的是曲面内两条相交线夹角的不变，所以上面方法并没有很好的保角性质。

![image-20250312183649382](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250312183649382.png)

**CirclePatterns算法**

圆形是共形几何中的基础构建单元，共形映射将圆映射为圆并且两个圆之间的交角不变。有了这样一个念头就可以构建这样对共形映射的数值逼近算法，通过大量的圆来对曲面进行填充，然后求一个映射对这些大量的圆都保持圆形的话，那这个映射就具有很好的共形性了。

![image-20251107104108134](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251107104108134.png)



对于Delaunay三角网格来说，所有三角形的**外接圆**可以认为是对它的一个**圆填充(CirclePattern)**,我们的目的就是求这个圆填充，即求出其中填充圆之间的相交角度（称为**边权值(edge weight)**$\theta_e$),以及填充圆的半径

显然CirclePatterns是要求满足Delaunay三角剖分的空圆条件的，否则就会有某个顶点位于另一个三角形的外接圆内，与CirclePatterns定义是违背的。

![image-20251107105925485](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251107105925485.png)

![image-20251112191400533](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251112191400533.png)

**抽象三角网格**（Abstract Triangulation），只定义了连接关系是一个**纯组合对象**，也叫做**单纯复形**（simplicial complex），**仅从组合结构**（即顶点、边、面之间的关联关系），而不依赖于具体的几何嵌入（如坐标、距离、角度等）。，展平前后的三角网格的抽象三角网格是一致的。

### Circle Patterns问题

对于**给定边权值$\theta_e$** (共形变换下是保持不变的)和一个**抽象三角网格**，**其CirclePattern存在当且仅当Coherent angle system存在的**，实际上抽象三角网格的CirclePatterns即是该三角网格的几何嵌入。

**Coherent angle system**是一种对抽象三角网格赋予一组满足如下条件的角度值$ \hat\alpha_{ij}^k$

大于0

![image-20251015085845727](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251015085845727.png)

对于每个三角形，相加等于$\pi$

![](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251015090132394.png)

并且满足下式（注意是 $\hat \alpha_{ij}^k$替代$\alpha_{ij}^k$）

![image-20251112191400533](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251112191400533.png)

从而求Coherent angle system 相当于 3|F|个变量；3|F|个不等式约束，|F|+|E|个等式约束的线性可解区域。

### 变分法求半径

假设$\rho_{ijk} = logc_{ijk}$

![image-20251107104253558](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251107104253558.png)

![image-20251112193409629](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251112193409629.png)

我们再通过变分的方法求解圆的半径，从而得到整个圆配置



![image-20241201134811707](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20241201134811707.png)

### 空间中曲面的三角网格

原始网格的$\theta_e$可能会导致我们无法找到合适的Coherent Angle System。我们尽可能趋近于原来的角度值,并且能获取到可行$\theta_e$的角度配置，所以就有了如下的一个二次优化

![image-20251015090401255](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251015090401255.png)

约束条件

![image-20251015090458352](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251015090458352.png)

对每条内部的边$e$需要满足局部Delaunay(local delaunay)条件

![image-20251112180201085](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251112180201085.png)

局部Delaunay是Dalaunay三角剖分空圆性质的等价条件，所以优化后得到的三角形配置自然是Delaunay三角剖分。



边界情况的指定,自由边界与指定边界

![image-20251112174426460](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251112174426460.png)

![image-20251112174435772](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251112174435772.png)

![image-20251107105336742](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251107105336742.png)

### 



**intrinsic local delaunay预处理**

![image-20251112211124525](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251112211124525.png)

可以先对原始的三维三角网格进行**intrinsic local delaunay**的处理，从而计算得到的扭曲更小



### 全局参数化与锥奇异点

上面方法仅适用于拓扑圆盘，但是对于拓扑更加复杂的模型来说需要通过分割线将网格切开，需要找到合适的割线。而有了锥奇异点，这个过程能自动的进行。

对于一个球状模型需要先切割成若干个分片(拓扑圆盘)，然后对每个分片分别进行平后的网格填充到一个图卡(Atlas)中

![image-20250927205710412](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250927205710412.png)

而全局参数化的方法就是算法自动找到割线将整个网格模型展开，不再通过分割进行展开

锥奇异点，展平后曲面上点的高斯曲率几乎处处为0，而锥奇异点的高斯曲率为给定数值不为0的点



![image-20250924183558400](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250924183558400.png)

通过引入锥奇异点可以极大地减少扭曲

![image-20251112194941344](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251112194941344.png)



高斯博内定理



在算法中加入锥奇异点

![image-20251113091148098](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251113091148098.png)



与ABF算法的对比

使用的是quasi-conformal来度量扭曲（Sander那篇文章）。都是使用了角度优化的，明显看到右边的扭曲要小很多

![image-20251113091722848](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251113091722848.png)

Stephenson实现了三角网格的CirclePacking算法，但是Circle Packing的问题是只考虑了三角网格的连接性质，却没有考虑到其几何性质。