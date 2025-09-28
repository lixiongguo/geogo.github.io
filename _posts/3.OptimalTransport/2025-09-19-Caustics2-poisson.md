---
layout: post
title: "基于Poisson方程的焦散计算"
author: David Lee
date: 2025-03-06
categories: [Caustics]
---


焦散('caustic')是光线经过经过表面的散射和折射作用后形成的现象。

![image-20250801140209582](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250801140209582.png)

![image-20250724090825649](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250724090825649.png)

水面由于有水波(wave)的存在，使其构成了多个凹面镜与凸面镜

![image-20250724091317364](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250724091317364.png)

最简单的焦散效果—透镜聚焦

![image-20250801132821417](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250801132821417.png)

通过模拟光线的运动可以实现效果，但是需要消耗太多运算资源

直接用一个triangle mesh来做为光源波面

![image-20250801134149935](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250801134149935.png)

![image-20250801160146361](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250801160146361.png)

