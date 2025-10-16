### “剑宗”强算，强推，大剑无锋



”气宗“主打一个高观点，简洁，深刻，本质



现有许多的方法都是优化各向同性扭曲能量，但是要实现牛顿方法(二阶)的收敛速度还是比较困难的。

这篇文章介绍的方法就是通过对变化的EIgen System进行解析从而使得Hess可以投影到正的(BA优化也有这样的一个步骤)，从而实现牛顿方法的迭代优化。对于一些复杂的网格(如Beetle.obj)用ARAP等一阶方法，收敛速度速度是比较慢的，所以探索能否使用二阶的牛顿方法来求最优化。

主要是将各向同性扭曲能量（**isotropic distortion energies**）的Hess投影到半正定空间中，从而可以用牛顿方法来进行求解

三角网格整体的扭曲能量等于组成三角面扭曲能量的聚合

![image-20250110130415509](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250110130415509.png)

变形梯度(deformation gradient)

F =RS 由于R是一个旋转矩阵，所以F的扭曲都是由S产生的

主要是通过极分解F=RS 变形梯度(deformation gradient)得到stretch tensor的不变量并将eigenvalues 与eigenVectors表示为这些不变量

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\775b1522f9f47bd03d7b8abbb63c0b55.png)

从而求解出各向同性能量的eigen structure

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\488b1e54f3fe9cb3bc4ea89fb2d8dbc3.png)

为方便表达采用的Tensor表示法

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\df51097ecf1a1bb4c9df956cf0675c28.png)

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\eaa6cb18b09499b13efc3550d4d02910.png)



对每个quadrature point的能量进行累加得到总体能量![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\723df298163a0815e45039e42eac7a90.png)



![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\25e0fc27601a48486e0ca22ce2d6c02e.png)

利用链式求导法对上式能量求导后

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\5fa0a61373acd46970007ad2ab8ee0d5.png)

定义不变量

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\4f07857f21fc57bab669579fa88405a3.png)

从而能量可以表达成如下形式，不变量I1,I2,I3可以用于解析Hessian的eigen stucture

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\4abfc3f58f0e88f7a9ae86bbd4d1305f.png)

先对I1的Eigen Stucture进行分析

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\4d2cab2070ea77c0fdc7ae36ca8f938e.png)

I2的Stucture

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\141e2151667a90c31098302ca52f75c1.png)

I3的Structure

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\14ce96208f65af22a12388111e56de38.png)

有了特征值后我们来求解特征向量

对于2d的情况

![![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\a222fed0becdd9abf09c27b710b91177.png)](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\a2b78220285fa4ff86fcf2e6a57e054e.png)



接下来对不同能量进行解析

ARAP能量

![image-20250111134212121](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250111134212121.png)

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\4008ca793bccbd847dd5b2b3ef017271.png)

![](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\fb432b86d478dee45ebe737dcabdadfa.png)

MIPS能量![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\52435b5efcf001d6bf85238f3f4f7a4a.png)

算法流程

![img](file:///C:\Users\LGX_MATE_BOOK\Documents\Tencent Files\474015788\nt_qq\nt_data\Pic\2024-07\Ori\28664d8f179241e36b59e3a651ed871a.png)

