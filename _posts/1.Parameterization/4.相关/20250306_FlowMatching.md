---
layout: post
title: "FlowMatching"
author: David Lee
date: 2025-03-06
categories: [Diffusion]

---

传统的标准化流是由一系列离散的变换组成，下面我们将流这个概念像连续上拓展，即连续正则化流

![image-20251217103053246](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251217103053246.png)

FlowMatching也有更好的生成路径

![image-20251217103251574](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251217103251574.png)

一个流将Rn上的一个分布进行变换，如图圆环的分布转化为一个螺线的分布

![image-20251217102452763](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251217102452763.png)

流的更加准确的表述实际上就是一个随时间变换的向量场(Rn上的)

![image-20251217100141128](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251217100141128.png)



而连续变换的过程可以用如下的ODE来描述

![image-20251217102139890](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251217102139890.png)

初始条件(边界条件)![image-20251217102207190](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251217102207190.png)

从离散的视角看就是

![image-20251217102523027](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251217102523027.png)

用如下方式表达

![image-20251217102248048](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251217102248048.png)

![image-20251217104100624](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251217104100624.png)

下面要做的是用神经网络来拟合这一系列变换的过程





将目标分数参数化为p1(x,theta),求其到

![image-20250928084055471](D:\MyDocs\geogo.github.io\imgs\image-20250928084055471.png)

这种离散的组合一系列变换的方式需要每个组合函数都满足可逆，可微分的性质，要构造这样条件的神经网络需要很高的技巧。

在连续标准化流(CNF)中，我们规避了求解单个映射的复杂条件，转而用一个常微分方程（ODE）

来描述流的变换过程

![image-20250928085821137](D:\MyDocs\geogo.github.io\imgs\image-20250928085821137.png)

![image-20250928085916614](D:\MyDocs\geogo.github.io\imgs\image-20250928085916614.png)

从连续性方程出发

![image-20250928090654212](D:\MyDocs\geogo.github.io\imgs\image-20250928090654212.png)

得到如下公式

![image-20250928090710933](D:\MyDocs\geogo.github.io\imgs\image-20250928090710933.png)

