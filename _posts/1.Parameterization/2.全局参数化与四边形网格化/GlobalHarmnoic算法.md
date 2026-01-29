### 介绍

 这篇文章出了一个对**任意亏格(arbitrary genus)**曲面进行参数化的方法, 并且这一方法可以保证是**局部单射（local injectivity）**且**无缝(seamless)**，并且速度上是比较好的。

定义了**q-CCM(q-convex combinatorial map)**凸组合映射,是**对Tutte和Gortler方法的泛化![image-20260129091732646](C:\Users\lixio\OneDrive\Desktop\MyDoc\lixiongguo.github.io\imgs\image-20260129091732646.png)**

q可以是4或者6，比如q=6对应的六边形参数化形的参数化

![image-20250702211005114](..\..\..\imgs\image-20250702211005114.png)

#### 相关方法与思路

**利用分支覆盖，将求q-CCM转化到求覆盖空间的一个凸映射**

局部单射与网格的离散测度具有一定的联系

![image-20250702195851780](..\..\..\imgs\image-20250702195851780.png)



Tong引入了Singularity Graph以此将曲面分解为一个个Patch，然后进行参数化。与这个方法比，这个方法更多是进行了推广，从$\pi /2$拓展到任意的有理的holonomy

![image-20250702202322059](..\..\..\imgs\image-20250702202322059.png)

### Gortler的凸组合参数化

#### Poincare-Hopf 指标定理

指标定义

![image-20250702193600893](..\..\..\imgs\image-20250702193600893.png)

指标定理

![image-20250702193508153](..\..\..\imgs\image-20250702193508153.png)

下面通过指标定理证明和离散1-形式（discrete one form）证明了Tutte定理，这个基本结论进行推广到多连通非凸边界的情况。

1-形式的closed和co-closed

![image-20250323162445529](..\..\..\imgs\image-20250323162445529.png)

要证明映射是单射的，关键是分析顶点的doubly-wheel性质

### 定理

注意到我们是要在覆盖空间中寻找映射

#### 分支覆盖

![image-20250924184009210](..\..\..\imgs\image-20250924184009210.png)

#### Riemann-Huritz公式

![image-20250924184052390](..\..\..\imgs\image-20250924184052390.png)

Gauss-Bonet定理证明如下引理

![image-20260129091341379](..\..\..\imgs\image-20260129091341379GB.png)

#### 中心定理

![image-20250924183901573](..\..\..\imgs\image-20250924183901573.png)

利用上面的引理，以及Riemann Huritz公式，上述的1-形式求

### 算法

#### 无缝参数化条件

**harmonicity conditions**

对于seam edge

![image-20250702205359832](..\..\..\imgs\image-20250702205359832.png)

对于 non-seam vertices

![image-20250702205418255](..\..\..\imgs\image-20250702205418255.png)

![image-20250702205703566](..\..\..\imgs\image-20250702205703566.png)

公式(8)被转为附录中的公式(14)

算法综合了上述的条件

![image-20250924183742615](..\..\..\imgs\image-20250924183742615.png)**求解这个最优化问题也要用到Lippman的凸化方法**











