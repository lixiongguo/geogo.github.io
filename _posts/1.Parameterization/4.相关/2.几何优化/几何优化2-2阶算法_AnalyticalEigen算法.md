

现有许多的方法都是优化各向同性扭曲能量，但是要实现牛顿方法(二阶)的收敛速度还是比较困难的。

这篇文章介绍的方法就是通过对变化的EIgen System进行解析从而使得Hess可以投影到正的(BA优化也有这样的一个步骤)，从而实现牛顿方法的迭代优化。对于一些复杂的网格(如Beetle.obj)用ARAP等一阶方法，收敛速度速度是比较慢的，所以探索能否使用二阶的牛顿方法来求最优化。

主要是将各向同性扭曲能量（**isotropic distortion energies**）的Hess投影到半正定空间中，从而可以用牛顿方法来进行求解

三角网格整体的扭曲能量等于组成三角面扭曲能量的聚合

![image-20250110130415509](..\..\..\..\imgs\image-20250110130415509.png)

**变形梯度(deformation gradient)**

F =RS 由于R是一个旋转矩阵，所以F的扭曲都是由S产生的

主要是通过极分解F=RS 变形梯度(deformation gradient)得到stretch tensor的不变量并将eigenvalues 与eigenVectors表示为这些不变量



从而求解出各向同性能量的eigen structure



为方便表达采用的**Tensor表示法**



对每个quadrature point的能量进行累加得到总体能量



利用链式求导法对上式能量求导后



**定义不变量**



从而能量可以表达成如下形式，不变量I1,I2,I3可以用于解析Hessian的eigen stucture



先对I1的**Eigen Stucture**进行分析



I2的Stucture



I3的Structure



有了特征值后我们来求解特征向量

对于2d的情况



**接下来对不同能量进行解析**

ARAP能量

![image-20250111134212121](..\..\..\..\imgs\image-20250111134212121.png)



MIPS能量

### 算法流程



