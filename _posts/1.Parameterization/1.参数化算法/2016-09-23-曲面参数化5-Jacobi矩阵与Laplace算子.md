---
layout: post
title: "曲面参数化5-映射的Jacobi矩阵与Laplace算子"
category: Parameterization
---

### 映射的Jacobi矩阵

经典微分几何理论是建立在对曲面的局部性质的研究基础上的，而如果研究曲面的局部性质的那就需建立局部坐标系。对于三角网格来说，“局部”的定义倒是容易的，我们可以直接将一个三角形就视为一个局部，也可以以每个点的周遭作为一个局部。

我们知道计算机中的曲面是由三角网格(Mesh)来表示的，对于真实物理世界的曲面我们可以使用微分几何的方法来研究曲面的性质。那我们该如何将经典的微分几何工具应用到三角网格的曲面性质(包括变形和展平等)的研究中呢？

对于一般的映射，其Jacobian矩阵是其局部形变情况的描述

![ ](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250318111007319.png)

映射$f$是一个多元函数，根据多元微积分的知识，其Jacobi矩阵$J_t$是一个2*2矩阵，定义如下$J_t = {\begin{pmatrix}{{\partial u}/{\partial x}}&{{\partial u}/{\partial y}}\\{{\partial v}/{\partial x}}&{{\partial v}/{\partial y}}\end{pmatrix} }$



通过矩阵运算可以得到$J_t = {\begin{pmatrix}{u_j-u_i}&{u_k-u_i}\\{v_j-u_i}&{v_k-v_i}\end{pmatrix} }{\begin{pmatrix}{x_j-x_i}&{x_k-x_i}\\{y_j-y_i}&{y_k-y_i}\end{pmatrix}^{-1}}$



映射Jacobi矩阵SVD分解后的奇异值$\sigma1 , \sigma2$分别描述映射在正交两个方向上的拉伸程度，如下图所示

![image-20250318111321305](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250318111321305.png)

根据分解后的奇异值$\sigma1 , \sigma2$，对映射扭曲进行度量

![image-20250306153752988](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250306153752988.png)



如何定义扭曲的大小

![image-20250111143503909](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250111143503909.png)