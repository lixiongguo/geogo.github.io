SB实际上是一个熵正则最优传输（entropy-regularized optimal transport）

![image-20251013204038462](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251013204038462.png)

薛定谔桥问题的定义

![image-20251013192504630](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251013192504630.png)

前后向的定义

![image-20251013205646061](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251013205646061.png)

定理

![image-20251013205251119](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251013205251119.png)

通过薛定谔桥实现生成模型

![image-20251013192655633](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251013192655633.png)

通过IPF方法进行迭代求解

![image-20251013193650843](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251013193650843.png)



IPF方法与原问题的等价性

![image-20251013194053850](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251013194053850.png)

本文提出的方法实际是对IPF方法的一个近似。

分别用神经网络来拟合前向与后向过程

![image-20251013194138454](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251013194138454.png)

![image-20251013194156449](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251013194156449.png)

算法

![image-20251013193907404](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251013193907404.png)

证明该过程的收敛性

![image-20251013194002903](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251013194002903.png)

![image-20251013194014601](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251013194014601.png)