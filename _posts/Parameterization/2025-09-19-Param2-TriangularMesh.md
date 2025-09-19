---
layout: post
title: "三角网格"
author: David Lee
date: 2025-07-20
category: 曲面参数化算法
---



#### 三角网格参数化

比如下图所示的大卫头像，计算机中的曲面是由许多小三角形构成的网格来表示的，这样的三角形组成的网格称为**三角网格(Mesh)** 记作$M=\{V,E,F |V,E,F为网格的顶点,边,面\}$

![image-20250311193102749](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250311193102749.png)

为了简化处理我们下面用这个简化版("抽象")的头像来做实验

![image-20250306112054639](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306112054639.png)

在三角网格的设定下，那么我们要求的映射$f$又可以写成这样$f:M \rightarrow R^{2},\text M{是R^{3}中的三角网格}$ ,而将网格进行展平的算法称为”**网格参数化算法**“(Mesh Parameterization)，而要构造这样映射$f$只要对顶点集$V$找到一组$R^2$的坐标(一般称为”**UV坐标**“如下图所示）即可。

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306113753650.png" alt="image-20250306113753650" style="zoom: 80%;" />

注意到要使我们的映射的效果比较好的话，有一些约束条件是需要满足的

1.映射之后内部的三角形的边是不能相交的

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250227112126656.png" alt="image-20250227112126656" style="zoom:50%;" />

2.映射后三角形的定向是不能翻转的，否则也会有错乱的情况

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250227120632868.png" alt="image-20250227120632868" style="zoom: 50%;" />

3.映射后的边界也是不能相交的

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250306151844519.png" alt="image-20250306151844519" style="zoom:50%;" />

**半边结构**

适用于三角网格(Mesh)的半边结构(half-edge)

