DDPM方程

如图，一滴液体在水中扩散，就像在一张干净的图上不断加噪



而上面一张图不断加噪的扩散过程可以看做是一个如下伊藤(Ito)随机偏微分方程(SDE)的解

![image-20250727160654637](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250727160654637.png)

w是一个标准维纳过程(Wiener Process)，f是一个向量函数，称为漂移系数。g是一个标量函数称为扩散系数。

Anderson于1982年给出了以上过程的逆过程，这里w_bar也是一个标准的维纳过程

![image-20250727162645168](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250727162645168.png)

一个分布的score可以通过神经网络进行估计