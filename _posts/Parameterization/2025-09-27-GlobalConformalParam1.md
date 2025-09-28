---
layout: post
title: "全局参数化"
author: David Lee
date: 2025-09-27
category: Parameterization
---
#### 全局参数化

对于如下的一个模型，不是拓扑圆盘。按照之前的参数化方法需要先切割成若干个拓扑圆盘，然后对每个圆盘进行参数化后，将展平后的网格填充到一个图卡(Atlas)中,而全局参数化的方法就是算法自动找到割线将整个网格模型展开

![image-20250927170616468](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250927170616468.png)

如图，将网格拆开后两个部分交界处的一致性是难以保证的

![image-20250927205710412](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250927205710412.png)

全局参数化可以认为是与四边形网格化是等价的问题