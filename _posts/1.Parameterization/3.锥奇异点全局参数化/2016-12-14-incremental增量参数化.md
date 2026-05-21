---
layout: post
title: "incremental增量参数化"
categories: [TechRelated]
---

本文给出了一种**自动寻找奇异点**的方法，以减少全局参数化的扭曲。

![image-20251107134929739](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107134929739.png)

这篇工作的核心不是先固定奇异点、再去解参数化，而是直接对曲面的**度量(metric)**做优化：**不断扩大零高斯曲率区域的占比，最后把曲率压缩到少量锥奇异点上。**  



## 全局参数化

原始三角网格为 $M$，沿割缝切开后的网格记为 $M_c$。原始网格 $M$ 的割缝上的一个顶点 $p$ 会在切开后分裂成两个边界点 $p_1,p_2$，如图中的两个绿色点。

![image-20251107151137430](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107151137430.png)

一个全局参数化$f$会诱导出一个平面度量$g$：
$$
g= {\nabla f}^T\nabla f
$$
除了锥奇异点这个**度量是平整的(flat)**(高斯曲率为0)。
接缝两侧在参数域中的像不能随意错开，而必须只差一个**刚性变换(rigid transform)**。  

无缝参数化的要求跨边时两个局部 **Jacobian** 必须相差一个 $\frac{\pi}{2}$ 的整数倍旋转：

$$
J_j e_{ij} = r_{ij} J_i e_{ij} + t_{ij}
$$

也就是说，相邻两个三角形 $T_i,T_j$ 的局部参数坐标系只能发生 **quarter-turn** 对齐，同时跨边的平移量 $t_{ij}$ 也是整数。

![image-20251107170756014](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107170756014.png)



### 和乐性(holonomy)

一条环路的和乐记录的是局部坐标沿闭环平行移动一圈以后，回到起点时它相对初始状态产生的累计变化,即累计获得了多少旋转



![image-20251107171257260](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107171257260.png)

![image-20251107171701999](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107171701999.png)

![image-20251109172609603](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251109172609603.png)

对无缝参数化来说，和乐是全局一致性的核心约束：**围绕锥奇异点走一圈，累计旋转必须落在允许的 quarter-turn** 集合里。



## 算法

![image-20251107171847753](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107171847753.png)

### Flatten 和 Rounding

#### 1. Flatten

Flatten 的思想和 Ben-Chen 一类的“度量平展化”方法接近：逐步调整度量，把分散的曲率集中到少数点上。

![image-20251107172009324](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107172009324.png)

Flatten 的过程会把曲率逐渐集中：黄色正曲率区域收缩到红色正曲率点上，青色负曲率区域收缩到蓝色负曲率点上。

![image-20251107175302658](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107175302658.png)

对于离散三角网格，这一步最终会落成一个 Poisson 型方程：

![image-20251107175529244](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107175529244.png)

 尺度一旦被重新分配，原来分散的高斯曲率就会被“挤压”到少量锥点，这些点就是后续参数化中的奇异点。  
因此，这篇方法最突出的特点之一，就是**奇异点位置不是预先指定的，而是随着度量优化被自动找出来的**。

#### 2. Rounding

Rounding 主要是对 holonomy 施加离散控制，从而实现无缝参数化。它分成两部分：  
一部分是 rounding 锥奇异点，把旋转 holonomy 调整到 $\frac{\pi}{2}$ 的整数倍上：

![image-20251107172058288](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107172058288.png)

对 homology loop 的处理如下：

![image-20251107180455682](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107180455682.png)

这里控制的是拓扑环上的平移周期。  
因为局部可积还不够，参数在线性空间里闭合，不代表它在曲面拓扑上也能闭合成无缝结构。  
只有当这些非平凡环路上的周期也被 round 到兼容整数格的值时，最终的 UV 才是一个真正的 seamless parameterization。



### 从旋转场恢复参数化

最后使用 ARAP 方法将前面得到的离散 holonomy 约束转回到具体的 UV 映射。

Rotation field：

![image-20251107190904459](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107190904459.png)

cross field 可以用每个面上的一个角度 $\theta$ 来表达：

![image-20251107181215621](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107181215621.png)

求得 $\theta$ 后，就能恢复相应的旋转矩阵 $R$：

![image-20251107191121676](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107191121676.png)

最后进行 global 步：

![image-20251107191353231](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251107191353231.png)

优化过程可以理解为：  在已经满足离散拓扑约束的前提下，寻找一个尽量贴合这些旋转关系、同时扭曲更小的具体参数化。  



