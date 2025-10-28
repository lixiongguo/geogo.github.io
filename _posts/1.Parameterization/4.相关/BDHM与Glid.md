将2D平面变形视为一个复映射，那么我们知道调和映射是有比较好的性质那样也就是对应了更好的变形效果，所以本研究的主要目的就是通过数值方法寻找一个这样比较好的映射。

1）首先一个复调和映射可以分解为一个全纯函数与另一个全纯函数共轭的和

![image-20250326191459767](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326191459767.png)

1.1.1）由此得到一个推论Corollary 1

![image-20250326191727770](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326191727770.png)

通过复导数$f_z$与$f_{\tilde z}$的全纯与反全纯性质来研究f的调和性

1.1.2）f的Jacobian

![image-20250326192504209](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326192504209.png)

![image-20250326192435124](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326192435124.png)

1.1.3）f的dilation的定义,用其来度量conformal distortion

![image-20250326192719066](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326192719066.png)

1.2）我们要求尽可能扭曲小的2D变形，可以考虑给扭曲施加一个bound，我们求解可接受bound范围内的扭曲

1.2.1）定义bound映射

![image-20250326192833404](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326192833404.png)

容易证明满足上面条件的f是单射

1.2.2)对于Harmonic映射，边界值全部决定了映射的形态，那么上面bound定义可以将考察范围缩小到边界

![image-20250326193102908](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326193102908.png)



2）进一步考察边界(简单曲线)可以用一个简单多边形(Polygon)来进行离散化逼近

2.1）对于简单多边形，定义Cauchy重心坐标

![image-20250326194001555](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326194001555.png)

那么就可以将调和映射进一步分解

![image-20250326193741329](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326193741329.png)

并且对于复导数有

![image-20250326194131187](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326194131187.png)

所以现在f就完全由phi psy系数来表征了

2.2）为了做求解，需要做凸化处理，并导出最优化形式

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\38c5ca4e8f15c07a5b041a5d4cf15470.png)

各constrain条件的凸化如下

用复导数来表示

![image-20250326194610150](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326194610150.png)

![image-20250326194555045](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326194555045.png)

对于5d)

![image-20250326194702236](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326194702236.png)

用复导数表示

![image-20250326194647654](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326194647654.png)

并进一步限制在二阶凸锥中

![image-20250326195026284](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326195026284.png)

对于5b)

![image-20250326194926784](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326194926784.png)

复导数表示

![image-20250326194857851](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326194857851.png)

并限制在二阶凸锥中

![image-20250326195506007](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326195506007.png)

对于非线性**边界条件5a)的处理**比较复杂，见原文6.4）

然后要加入正则项，可以选择ARAP能量

![image-20250326195946561](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326195946561.png)

由于这个能量也是非凸的所以做如下凸化，过程参考Lipman的文章

![image-20250326200338839](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326200338839.png)

以及外界输入的约束，终于问题就变成求解如下的**最优化问题**

![image-20250326200049856](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326200049856.png)

积分形式的能量用求和表达

![image-20250326200432211](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326200432211.png)



综合上面凸化的结果，利用**Active Set**方法，则可以得到如下表达式

（注意这里采样了三个集合 M，A, B）

![image-20250326200819142](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326200819142.png)

对于conformal Mapping可以更进一步简化

![image-20250326200901879](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326200901879.png)

计算细节

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\5b46740096272510318004b9e18226da.png)

另外注意到的是这里用到了三个active set，这三个set如何添加

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\815ab12449ac6fe0bb5b94fb5d98df44.png)

上面的优化这是针对边界上的个别的点，为了能推广到整个边界上（注意利用Thereom 4的定义）

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\3d488c2281c1da5eb875c978f3bf49ea.png)

利用之前uniform采样的B集，如何计算各最值

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\0727a8e7112236a51dc4f82c385cfba1.png)

利用Lipschitz性，转化为两个端点值和Liphischitz常数的表达

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\7cfa5e20ccc6041b5476e8064e9ad597.png)

如何计算Liphsthiz常数

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\7b73ae66c1f199857e7ba022857d5e7d.png)

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\155fc608f007641a5ceb2206b9216c2a.png)

BDHM那篇文章是通过求带约束凸优化的方法，而这里(GLID)通过将Hessian矩阵凸化，用求解无约束优化问题的牛顿法来做优化

1）引用BDHM中的结果，Bounded的约束是

这里将从单连通拓展到多连通

![image-20250326201834471](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326201834471.png)‘

注意这里并不是同BDHM的优化方式，而是做牛顿法做全局优化

2）我们优化的能量是各向同性(Isometric Energy)

![image-20250326202125560](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250326202125560.png)