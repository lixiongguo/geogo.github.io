BDHM那篇文章是通过求带约束凸优化的方法，而这里(GLID)通过将Hessian矩阵凸化，用求解无约束优化问题的牛顿法来做优化

1）引用BDHM中的结果，Bounded的约束是

这里将从单连通拓展到多连通

![image-20250326201834471](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326201834471.png)‘

注意这里并不是同BDHM的优化方式，而是做牛顿法做全局优化

2）我们优化的能量是各向同性(Isometric Energy)

![image-20250326202125560](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326202125560.png)