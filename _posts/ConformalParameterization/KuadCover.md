

QuadCover的效果：

![image-20250923100901371](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923100901371.png)

高质量的全局参数化，对网格噪声不敏感

![image-20250923092844643](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250923092844643.png)



光滑流形的全局参数化定义，

![image-20250708190400214](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708190400214.png)

对于每个chart是容易定义局部参数化的，但是要满足全局一致性不是件容易的事

需要满足两个条件

![image-20250708185334516](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708185334516.png)

![image-20250708185346432](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708185346432.png)

这里定义r_ij为matchings

![image-20250708190812738](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708190812738.png)

参数值只能相隔整数

![image-20250708185409588](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708185409588.png)

本文的核心思想是借助Riemann面中分支覆盖(branch cover)的概念，将一个Frame field拆解为4个支集面上的Vector Field来求解

分支覆盖的概念（）

![image-20250708191705280](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708191705280.png)

对于黎曼面M其覆盖M',M的局部坐标表征z,M'的局部坐标表征z',局部满足z =(z')_np,那么p就认为是M'（covering）的分支点。

![image-20250708191714633](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708191714633.png)

covering是分层的

![image-20250708195159461](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708195159461.png)

![image-20250708195800221](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708195800221.png)

通过将流形M的相邻两个patch粘合在一起(glue together)从而构造M的覆盖

由matching引导的covering

![image-20250708192932179](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708192932179.png)

![image-20250708195814043](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708195814043.png)

顶点的layer shift，如下定义。对于一个顶点v，设其相邻三角形为T0,T1...Tn,对于边的matching有rij



![image-20250923095716872](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923095716872.png)

显然ls=0就意味着一个普通的四边形点，而对于非零的情况

![image-20250708201420247](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250708201420247.png)

Frame Field的定义

![image-20250923100231939](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923100231939.png)

如何通过Frame Field求出全局参数化

![image-20250923100426168](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923100426168.png)

### 参数化函数 �=(�,�)\*ϕ\*=(\*u\*,\*v\*)

- 在每个三角形上，�*ϕ* 是一个从三角形顶点坐标到 �2R2 的线性映射。
- 它由梯度场（或 frame field）积分得到 —— 但积分常数未定，所以不同三角形的 �*ϕ* 值可能不匹配





在covering spaces中的标量函数

![image-20250923101853458](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923101853458.png)

下面对这个空间进行研究，求得这个空间的基

![image-20250923102915420](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923102915420.png)

核心定理

![image-20250923102434299](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923102434299.png)

算法输入

![image-20250923103242130](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923103242130.png)