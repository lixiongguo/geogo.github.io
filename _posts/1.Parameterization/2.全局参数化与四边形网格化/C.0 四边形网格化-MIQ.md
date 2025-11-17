## 四边形网格

相比三角形网格，四边形网格的张量积结构可以用于高阶表面建模，如用于CAD/CAM中的NURBS样条以及动画电影中的网格细分。并且四边形网格能更好地捕捉到物体的几何特征。

![image-20251016192108923](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251016192108923.png)

**如何生成四边形网格:**

最淳朴的方法自然是将三角网格中两个三角形拼在一起形成一个四边形。

**基于全局参数化的方法：**先把曲面展平到平面上，然后在平面上铺上四边形网格。全局映射化映射要满足网格自同构(grid automorphism)

![image-20251113110736577](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251113110736577.png)

**基于标架场(cross field)诱导的四边形网格化**：让四边形网格的边与方向场中的向量相贴合，从而用户通过设计向量场从而让四边形网格的边贴合曲面的表面特征。

![image-20251109163355504](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251109163355504.png)

衡量四边形网格的质量

![image-20251109170905192](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251109170905192.png)

**混合整数求解器**

方法的核心步骤是利用整数规划进行，所以算法的一个重要的是设计一个高效的混合整数求解器

**构建平滑的正交向量场(cross fileds)**



![image-20251109164807242](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251109164807242.png)

![image-20251109165317859](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251109165317859.png)

一个正交向量场可以由赋予三角网格中每个三角面片一个角度值$\theta$,另外图中红色箭头的变动也是直观表示出了正交向量场的**period jumps**

可以将正交向量场的平滑度简单定义为相邻两个三角面的角度差值的平方和

![image-20251109165559730](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251109165559730.png)

展开可以得到

![image-20251109165727557](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251109165727557.png)

对上面的整数求导后，用前面介绍的混合整数求解器计算得到正交向量场的$\theta$以及$p_{ij}$

![image-20251109165810573](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251109165810573.png)

**有了向量场之后求解全局参数化**

通过这样一个能量来拟合之前计算的那个向量场

![image-20251109170058452](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251109170058452.png)