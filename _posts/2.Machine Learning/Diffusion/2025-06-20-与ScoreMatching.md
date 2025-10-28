Liklihood-based类型生成模型包括自回归(autoregressive model)和正规流(Normalize flow)

他们有良好的生成效果，但还是具有一些内在的缺陷

![image-20250727165813748](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250727165813748.png)

GAN避免了一些限制，但是GAN的对抗训练过程还是不稳定的，并且有模式坍塌等问题的存在

本文通过对Stein分数的研究探讨一种新的生成模型，Stein分数是对数概率密度值的梯度，所以是一个向量场，指向对数概率密度增长最快的方向。通过神经网络对数据训练从而回归出向量场

要实现这样的想法需要攻克两个难题

![image-20250727170854035](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250727170854035.png)

第一，根据数据流形假设，数据是嵌入在高维空间中的低维流形，那么在其他广大的数据空间中，分数是无法定义的，所以无法有效的进行score计算与匹配。

其次，对于某些低概率密度的数据空间缺少有效的训练数据使得score估计的准确度大大降低。Langevein动力学从低密度区域进行初始化，不准确的分数估计也将对采样过程造成不好的影响。

为解决上面说的两个问题，我们提出可以对数据施加不同量级的随机高斯噪声，通过增加噪声从而确保获得的分布避免塌陷到(collapse)低维数据流形中。大噪声可以使低密度数据区域增加数据量，从而有效提高分数估计。

我们使用基于模拟退火方式的Langevein 动力学，渐进地减小噪声级别。





DDPM方程

如图，一滴液体在水中扩散，就像在一张干净的图上不断加噪



而上面一张图不断加噪的扩散过程可以看做是一个如下伊藤(Ito)随机偏微分方程(SDE)的解

![image-20250727160654637](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250727160654637.png)

w是一个标准维纳过程(Wiener Process)，f是一个向量函数，称为漂移系数。g是一个标量函数称为扩散系数。

Anderson于1982年给出了以上过程的逆过程，这里w_bar也是一个标准的维纳过程

![image-20250727162645168](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250727162645168.png)

一个分布的score可以通过神经网络进行估计

