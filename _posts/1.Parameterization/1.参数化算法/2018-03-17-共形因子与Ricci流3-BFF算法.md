#### 参数域形状可控性的研究

根据**Riemman映照**定理存在变形的可能。

本篇文章就是从如何**改变参数域形状**的角度入手，实现了一种可**实时交互**的高效共形参数化算法

![image-20250108195307527](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250108195307527.png)

可不可以展平后通过变形的方法(Planer shape deformation)来对形状进行编辑呢？(破坏了pipeline的一致性)



到底能对形状做出什么程度的变形呢？

![image-20241115185037947](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20241115185037947.png)

到底能对形状做出什么程度的变形呢？限制肯定是有的，毕竟需要满足（2）中的约束黎曼映射定理是说任意两个拓扑圆盘之间存在共形映射，但并不是说能从一个形状进行任意变形并且还能保持共形性

**复数域上映射的研究**

**Cauchy-Riemann 方程**

共形映射在每个点的局部区域的所有方向的向量都是统一(uniform)的放缩，这个统一的放缩系数就是共形因子

![image-20250108194219541](C:\Users\LGX_MATE_BOOK\Desktop\我的文档\GeoNotes\imgs\image-20250108194219541.png)

![image-20250108194600110](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250108194600110.png)

**再看共形映射与调和映射**

共形映射是共轭调和映射对组成（conjugate  harmonic pair）,所以求解共形映射就是求解这样一对调和映射对

![image-20250108203251309](C:\Users\LGX_MATE_BOOK\Desktop\我的文档\GeoNotes\imgs\image-20250108203251309.png)









**Cherrier Formula**

考虑边界条件的Yamabe方程称为Cherrier Formula

$$ \begin{array} { r c l c l } { { \Delta u } } & { { = } } & { { K - e ^ { 2 u } \widetilde { K } } } & { { \mathrm { o n } } } & { { M } } \\ { { \frac { \partial u } { \partial n } } } & { { = } } & { { \kappa - e ^ { u } \widetilde { \kappa } } } & { { \mathrm { o n } } } & { { \partial M } } \end{array} $$

对上面的式子离散化再积分

![image-20250318172535453](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250318172535453.png)

所以边界变形的关键就是求解h

#### Poincaré-Steklov operator

根据poisson方程的两种边界条件Dirichlet条件和Neumann边界条件

我们看到上面给出的是针对Neumann条件的，如果给的是Dirichlet条件的话该如何转换为Neumann条件呢？

如果给定的是dirichlet条件

![image-20250108213509798](C:\Users\LGX_MATE_BOOK\Desktop\我的文档\GeoNotes\imgs\image-20250108213509798.png)

如果给定的是Neumann条件

![image-20250108214927004](C:\Users\LGX_MATE_BOOK\Desktop\我的文档\GeoNotes\imgs\image-20250108214927004.png)

Hilbert 变换：

![image-20250108215023689](C:\Users\LGX_MATE_BOOK\Desktop\我的文档\GeoNotes\imgs\image-20250108215023689.png)

得到了边界后可以通过解析延拓的方式拓展到区域内部

![image-20250108220237170](C:\Users\LGX_MATE_BOOK\Desktop\我的文档\GeoNotes\imgs\image-20250108220237170.png)





BFF这个算法主要是提供了一种可以对conformal flattenning进行交互编辑控制的方法

<img src="C:\Users\LGX_MATE_BOOK\Desktop\我的文档\GeoNotes\imgs\image-20241115183600163.png" alt="image-20241115183600163" style="zoom:150%;" />

![image-20250318173816762](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250318173816762.png)



**Hilbert Transform**

HilbertTransform.Onadisk-likedomain,theHilberttrans formHmapsthetangentialderivativeofaharmonicfunctiona tothenormalderivativeof itsharmonicconjugateb,providing boundarydataforaholomorphicfunctionf =a+bı (Sec.3.2.1).

**Curvature Integrate**

 AkeystepinBFFisrecoveringaclosedboundarycurve ˜ γ from givencurvatureandlengthdata.Inthesmoothsettingthisdatacan beintegrateddirectly,butinthediscretecaseasmallamountof discretizationerrorpreventsclosure—wethereforeseekaclosed curvethatapproximatesthegivendata.

**BFF算法**



算法流程

# ![image-20250318174618349](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250318174618349.png)