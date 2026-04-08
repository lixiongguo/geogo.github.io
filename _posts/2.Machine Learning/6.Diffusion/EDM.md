将FlowMatching,ScoreMatching,DDPM/DDIM等扩散模型形式进行统一，并寻求优化

## 通用加噪公式

![image-20260121205507317](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20260121205507317.png)

所以可以归纳出如下的一个通式

![image-20260121205732014](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20260121205732014.png)



对应一个随机微分方程，这个方程的解可以描述x_t分布的变化

![image-20260121210123114](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20260121210123114.png)

![image-20260121210206019](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20260121210206019.png)

下面我们就来求这个通用公式的s(t)和sigma(t).

### 2.求$s(t)$的表达式

根据加噪公式的均值和方差

![image-20260121210218577](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20260121210218577.png)

![image-20260121210347087](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20260121210347087.png)

### 3.$\sigma(t)$的表达式

![image-20260121211124471](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20260121211124471.png)

![image-20260121211133856](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20260121211133856.png)

### 通⽤推理过程：确定性采样

![image-20260121211738518](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20260121211738518.png)

## 通⽤推理过程：随机性采样

EDM框架下的随机偏微分方程

![image-20260121211244247](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20260121211244247.png)