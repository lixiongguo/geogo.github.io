 这篇文章中, 作者给出了一个对任意亏格曲面进行全局无缝参数化的方法, 并且这一方法可以保证局部是单射的.

本文的主要目标是为了实现局部单射（local injectivity）

参数化的一个重要要求就是局部单射，而调和方法天然具有比较好的特性，最简单的调和方法就是Tutte

![image-20250702192805028](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702192805028.png)

但是对于更通用的非凸边界，以及更加复杂的拓扑就需要Gortler的这篇文章了。

![image-20250924183558400](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250924183558400.png)

![image-20250924183707551](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250924183707551.png)

![image-20250924183742615](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250924183742615.png)

核心定理：

![image-20250924183901573](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250924183901573.png)

Gortler的文章利用指标定理证明和推广Tutte参数化

![image-20250702193600893](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702193600893.png)

![image-20250702193508153](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702193508153.png)

HGP方法的速度快

![image-20250702194441005](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702194441005.png)

利用HGP方法生成的六边形参数化(q=6)

![image-20250702211005114](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702211005114.png)

中心定理

![image-20250702193757258](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702193757258.png)

局部单射与网格的离散测度具有一定的联系

![image-20250702195851780](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702195851780.png)

Tutte的权重是uniform权重，Floater对Tutte的推广，Floater允许了凸权重

![image-20250702201727555](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702201727555.png)

Tong引入了Singularity Graph以此将曲面分解为一个个Patch，然后进行参数化。与这个方法比，这个方法更多是进行了推广，从$\pi /2$拓展到任意的有理的holonomy

![image-20250702202322059](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702202322059.png)

Orbifold方法，不太清楚

![image-20250702202859340](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702202859340.png)

这个方法也是用到了Lippman的凸化方法

![image-20250702203015403](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702203015403.png)

**3.全局参数化**

harmonicity conditions

对于seam edge

![image-20250702205359832](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702205359832.png)

对于 non-seam vertices

![image-20250702205418255](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702205418255.png)

![image-20250702205703566](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250702205703566.png)

**Q-FOLD BRANCHED COVER**

![image-20250924184009210](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250924184009210.png)

![image-20250924184052390](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250924184052390.png)