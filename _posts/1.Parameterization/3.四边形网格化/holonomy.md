基于度量生成四边形网格

![image-20251111211253923](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/_posts/1.Parameterization/2.全局参数化与四边形网格化/../../../imgs/image-20251111211253923.png)

四边形网格自然诱导黎曼度量

![image-20251127200348539](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/_posts/1.Parameterization/2.全局参数化与四边形网格化/../../../imgs/image-20251127200348539.png)

与Ray Nsymmetric Design关系？

![image-20251127095738973](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs/image-20251127095738973.png)

关键是设计一个锥奇异点度量（flat cone metric）类似于Ben-Chen的方法

![image-20251115103456876](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs/image-20251115103456876.png)

rotation补偿如何理解？

![image-20251127095713763](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/_posts/1.Parameterization/2.全局参数化与四边形网格化/../../../imgs/image-20251127095713763.png)

### 如何生成四边形网格

全局参数化诱导出映射的度量

![image-20251107154351591](../../../imgs/image-20251107154351591.png)

并且这个度量除了接缝的两端外也都是flat，这要求接缝在参数域种的两条像曲线是一个刚性变换(rigid transform)。反过来说，一个平展度量(flat metric)也能唯一确定参数化f

无缝全局参数化的要求

![image-20251107170622714](../../../imgs/image-20251107170622714.png)

$J_j e_{ij} = r_{ij} J_ie_{ij}$,满足$\frac {\pi} 2$的整数倍旋转

,如图两个三角形Ti，Tj

![image-20251107170756014](../../../imgs/image-20251107170756014.png)

如果是需要四边形网格化，还需要$t_{ij}$是整数

![image-20251107170834395](../../../imgs/image-20251107170834395.png)
