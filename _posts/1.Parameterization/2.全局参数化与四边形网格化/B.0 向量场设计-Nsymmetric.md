![image-20251111163816759](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111163816759.png)

如何计算的**Singularity of index？**

通过turning number来研究N-symetry 方向场的拓扑

![image-20251111164006268](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111164006268.png)

vector filed的同伦等价

![image-20251111164118941](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111164118941.png)

vector fields的Turnnning number定义

先定义 curvature

![image-20251111164530207](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111164530207.png)

再定义Turning number

![image-20251111164356051](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111164356051.png)

定理：vector-fields的同伦等价与turnning number的关系

![image-20251111164424288](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111164424288.png)

指标以及根据指标确定奇异点

![image-20251111164629687](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111164629687.png)

定理：奇异点指标之和等于Euler示性数

![image-20251111164729785](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111164729785.png)

Turning number的数据结构由如下的Period jumps来表达

![image-20251111165518808](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111165518808.png)

Period jumps定义

![image-20251111164825645](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111164825645.png)

所以只要这三样东西可以定义一个方量场：（1）每个面上的局部坐标（2）关于角度的标量场 （3）用于表征向量场在不同点跳变得period jumps

![image-20251111164844596](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111164844596.png)

### 算法：

zipper 算法，

解决如下问题

![image-20251111165152292](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111165152292.png)

算法流程

![image-20251111165215004](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111165215004.png)

对于向量场设计的问题

![image-20251111165259490](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111165259490.png)

算法如下

![image-20251111165315826](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251111165315826.png)