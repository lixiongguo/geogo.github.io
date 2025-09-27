论文笔记 Instant Transport Maps on 2D Grids

![image-20250914152526557](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250914152526557.png)

本文针对2D平整网格(2D uniform grid)域上计算$L^2$最优传输,提出了一个高效算法，不用计算导数(derivative-free)求最优化

一般来说一个最优传输问题如下表达

![image-20250914153534040](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250914153534040.png)

如果直接按照上式进行计算是难以进行计算的。（主要来自于三处的非线性，det，u/v, v与未知h函数T的复合）

下面来看采取什么方法来求解这个高度非线性

首先对于焦散设计问题，不失一般地，v可以是一个均匀分布设v=1，那么

![image-20250914160945809](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250914160945809.png)

给定密度u是一个分段常数u=(u1,u2,...,un)T, n=hxh, 对![image-20250914161616434](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250914161616434.png)

进行积分

![image-20250914160703954](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250914160703954.png)

![image-20250914161806028](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250914161806028.png)

psi称为Kantorvich势能，与初始的凸势能的关系，并且他们的Hessian有如下关系

![image-20250914175927631](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250914175927631.png)

从而得到下式

![image-20250914180428065](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250914180428065.png)

一个insight是delta phsi比detHpsi要大很多

![image-20250914180450797](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250914180450797.png)

结合（11）和（13）得到离散化后

![image-20250914180739920](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250914180739920.png)

对(15)式求解可以通过Newton法进行求解。



进一步整理也即

![image-20250914181006163](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250914181006163.png)

其中q的定义

![image-20250914180920174](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250914180920174.png)