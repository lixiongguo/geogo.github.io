**匹配(matching)**

设光滑的2维流形$M$,有图集(charts,或者atlas)$\phi_i:U_i \sub M \to \Omega_i \sub \mathbb{R}^2$,$M$的参数化栅格定义单位栅格线$\mathbb{Z} \times \mathbb{R}$以及$\mathbb{R} \times \mathbb{X}$在$\phi_i$作用下的原像。

在单个图卡下(chart)容易定义局部的参数化，但是如何将不同图卡下的参数曲线保持全局连续性不容易。

全局连续的参数化，即找到这样连续一致的图集$\{U_i,\phi_i\}$,相邻两个区域$U_i$与$U_j$重合的地方，有如下的转移函数

![image-20251027112216977](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027112216977.png)



这里$r_{ij} \in \{0,1,2,3\}$定义为两个区域间的匹配(matching)

如图,两个chart之间的匹配$r_{ij}$ = 3

![image-20251027112932703](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027112932703.png)

对于如下的正方体展开,$r_{01}=r12 = 0,r_{20} = 1$

![image-20251027112941971](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027112941971.png)

对于离散三角网格,我们定义所有局部的图卡(chart)是三角面片,区域重合的地方就是三角面片的公共边，所以匹配是定义在边$E$上的。

![image-20251027125903959](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027125903959.png)

对于四边形网格化

并且参数值u，v之间只能相隔整数

网格自同构

![image-20251027153845109](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027153845109.png)

在构造**无缝参数化**时，要求：

> 相邻面之间的参数变换必须是一个 **grid automorphism**。

这意味着：

- 跨过一条边时，UV 坐标的变化不能是任意的；
- 必须是**整数平移**（可能加上 90° 旋转等对称操作）；
- 这样才能保证纹理或网格在拼接时**无缝**（seamless）且**结构一致**。

**分支覆盖(branch cover)**

设$M$是一个Riemann曲面(一维复流形),我们定义$M$的一个**分支覆盖(branch cover)$M'$**是一个这样的黎曼面:

其与$M$存在局部存在同胚映射$\pi:M' \to M$，对任意一个$M'$上的点$p' \in M'$,存在一个$p'$的领域$U'$,在其上可以定义局部坐标$z':U' \to \mathbb{C}$,并且以点$p'$为坐标架的中心,即$z'(p') = 0$。同样也可以在像点的领域$U(\pi(p') \in U)$,定义局部坐标$z: U \to \mathbb{C},z(\pi(p'))=0$,存在一个整数$n_p > 0$,在$p$的局部有如下坐标变换关系成立$z = (z')^{n_p}$，如果$n_p > 1$,那么$p$点即为$M$的一个分支点。

如果$p$不是一个分支点，那么存在一个$p$的邻域$V$,其原像$\pi^{-1}(V)$的每一个连通分量都将被$\pi$同胚地映射到$V$上。

分支点

![image-20251027130358889](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027130358889.png)

对$M$子集U的平凡覆盖

![image-20250708195159461](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708195159461.png)

 ![image-20251027120734402](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027120734402.png)

通过定义一致的转移函数$\rho$，将流形M的相邻两个patch$U_i,U_j(U_i and U_j)$粘合在一起(glue together)

![image-20251027203739496](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027203739496.png)



![image-20250708195814043](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708195814043.png)

给定了三角网格的匹配M后可以**由匹配(matching)诱导的覆盖(cover)**

![image-20250708192932179](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708192932179.png)



**Frame Field**

![image-20251027134959153](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027134959153.png)

![image-20250923100231939](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923100231939.png)

![image-20250923100426168](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923100426168.png)



Frame filed可以在covering space中为vector field，称为曲面的covering field



通过标架场(cross-field)诱导全局参数化，将一个Frame field拆解为4个支集面上的Vector Field来求解

![image-20251022105655704](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251022105655704.png)

顶点的层偏移layer shift，如下定义。对于一个顶点v，设其相邻三角形为T0,T1...Tn,Tn=T0对于边的matching有rij

![image-20250923095716872](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923095716872.png)

显然ls=0就意味着一个普通的四边形点，而对于非零的情况

![image-20250708201420247](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708201420247.png)

在covering spaces中的标量函数空间

nabla Sr(M')是无璇的，为什么这个性质这么重要

![image-20251027141650460](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027141650460.png)

从对称covering函数中可以引导出二维参数化

![image-20251027204833753](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027204833753.png)

transition 必须是grid automorphism

![image-20251028090459245](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251028090459245.png)

![image-20251028090536003](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251028090536003.png)

covering space 是从matchings中计算得来的，对称标量函数的表达如式(6)

![image-20251027204948045](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027204948045.png)

下面对这个空间进行研究，求得这个空间的基

![image-20250923102915420](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923102915420.png)

核心定理

![image-20251028090604308](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251028090604308.png)





**算法输入**

r与symmetric frame field或者等价为一个symmetric covering field

算法输入是可以是主曲率场(principal curvature directions)

如何计算主曲率场？

$r_{ij}$是如何给定的？

**算法预处理**

![image-20251027205419567](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027205419567.png)



脐点(umbilic)区域？没有主曲率，又是为什么要在其上进行平滑



**主要流程**

![image-20251027141901004](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027141901004.png)

1.求最优化

![image-20251027141927915](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027141927915.png)

通过对K进行Hodge分解可以解上面的最优化。

$K = P_K + C_K+ H_K$

由于$\nabla \phi$是标量场的梯度，所以一定是无璇的，所以$\hat X = P_K + H_K$是（9）式积分的最小化



2.全局连续性处理

![image-20251027142441224](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027142441224.png)

关键是miuj(phi)是整数（基底下的第二个分量）

![image-20251027210409655](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027210409655.png)

为什么是2Z?

![image-20251027210706934](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251027210706934.png)