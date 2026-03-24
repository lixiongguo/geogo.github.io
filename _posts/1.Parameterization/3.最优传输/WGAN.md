0.原始GAN回顾

![image-20260209163800811](D:\MyDocs\geogo.github.io\imgs\image-20260209163800811.png)

![image-20260209163848410](D:\MyDocs\geogo.github.io\imgs\image-20260209163848410.png)

原始GAN的优化目标

![image-20260209163918279](D:\MyDocs\geogo.github.io\imgs\image-20260209163918279.png)

原始GAN就是在求JS度量的最小化

1.原始GAN的问题

![image-20260209162948709](D:\MyDocs\geogo.github.io\imgs\image-20260209162948709.png)

WGAN（Wasserstein GAN）**在一定程度上缓解了原始 GAN 的模式坍塌**（mode collapse），但它**主要解决的核心问题是训练不稳定和梯度消失/无意义的问题**。模式坍塌的改善是其带来的**间接好处之一**，而非直接设计目标。

2.Wasserstein距离，EM距离

![image-20260209162413239](D:\MyDocs\geogo.github.io\imgs\image-20260209162413239.png)

2.EM距离相比于KL和JS Divergence的好处，能为网络提供平稳的梯度

![image-20260209163519850](D:\MyDocs\geogo.github.io\imgs\image-20260209163519850.png)

![image-20260209163549080](D:\MyDocs\geogo.github.io\imgs\image-20260209163549080.png)



3.核心计算原理，**Kantorovich-Rubinstein对偶**

![image-20260209162539581](D:\MyDocs\geogo.github.io\imgs\image-20260209162539581.png)

WGAN对于Loss的更改

![image-20260209163242598](D:\MyDocs\geogo.github.io\imgs\image-20260209163242598.png)