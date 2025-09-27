RF很简单，是用学习常微分方程的方式来在两个分布间的映射

![image-20250711135433102](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250711135433102.png)

基本的思路就是学习直线路径，可以通过求解一个非线性最小二乘

![image-20250711135747825](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250711135747825.png)

由于方法生成的是直线所以只用一步Euler就能获得很好的结果

![image-20250711135930889](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250711135930889.png)



神经网络生成可以认为是一个传输映射问题（跟Monge问题是一个意思吗？）

![image-20250711140246192](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250711140246192.png)

全部就是求解如下的一个非线性最小二乘

![image-20250711140456644](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250711140456644.png)

这样计算出来的Flow有3个特性

![image-20250711160914052](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250711160914052.png)

非线性版

![image-20250711162245044](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250711162245044.png)