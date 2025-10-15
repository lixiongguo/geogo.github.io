---

layout: post
title: "最优传输1-Monge问题与Kantorivch问题"
categories  : OptimalTransport
---

y引子：

保面积映射与最优传输映射



Monge问题

![](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928203504345.png)Kantorvich问题

![image-20250928203252541](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928203252541.png)

Kantorvich对偶 

对偶问题等价性 min(KP) = max(DP)

![image-20250928203211180](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928203211180.png)

其中满足等式约束的函数对$(\phi,\psi)$称为Kantorvich Potential，其中$\psi$是$\phi$的凸共轭。凸共轭用如下$c$变换进行定义。

![image-20250928210211753](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928210211753.png)

当代价函数是内积形式时$c(x,y)=<x,y>$

![image-20250928201458627](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928201458627.png)

![image-20250928213017899](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928213017899.png)

Brenier Potential

针对二次代价$c(x,y) = \frac{1}{2}||x-y||^2$，则存在唯一的最优传输映射$T$，且$T$是某个凸函数$\phi$的梯度$T = \nabla \phi$,这个凸函数$\phi$称为是Brenier Potential



![image-20250928210635343](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928210635343.png)

![image-20250928212234034](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928212234034.png)

所以

![image-20250928212316955](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928212316955.png)

![image-20250928212149743](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928212149743.png)

![image-20250928212412091](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928212412091.png)



如果代价c满足扭曲条件(twist condition)

![image-20250928212430066](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928212430066.png)

![image-20250928212605275](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928212605275.png)

​	其中$\phi$是Kantorvich potential

![image-20250928212705825](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928212705825.png)

Kantorvich potential是“价格函数”

![image-20250928211016803](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250928211016803.png)

**传输方向由势函数的梯度（或广义梯度）决定** —— 类似于物理中的“力是势能的负梯度