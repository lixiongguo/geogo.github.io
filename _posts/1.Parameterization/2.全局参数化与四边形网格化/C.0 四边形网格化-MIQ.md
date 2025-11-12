生成四边形网格分为两个步骤：

（1）确定一系列的方向，以及一些奇异点生成一个符合该方向指定的cross-field

（2）根据前一步生成的cross-field生成四边形网格

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