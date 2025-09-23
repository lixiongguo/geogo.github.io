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



**半边结构**

适用于三角网格(Mesh)的半边结构(half-edge)

