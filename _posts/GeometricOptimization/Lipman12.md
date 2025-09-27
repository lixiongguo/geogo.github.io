本文主要讲解的是如何控制三角网格映射的conformal distortion记为$\sigma$并且同时确保三角网格的单射性质，

三角网格上M = (V,F,E)定义的映射可以认为是分片连续线性的（CPL continous Piecewise Linear ，每个三角面线性的同时，相邻两个三角面在边界保持连续）将所有这样的映射的空间定义为$F^M$ ,而我们需要的是$\sigma$有限的子空间

我们这样定义空间$F^M_C \subset F^M,常数C >=1,\sigma<=C$，不过麻烦的是$F^M_C $是非凸的，而我们要做的就是找一个比较好的一个替代。我们通过在每个面上定义一个坐标加$\oplus$，从而可以简易表达出的映射空间$F^{M,\oplus}_C \subset F^M_C$

具体做法如下

1）研究使仿射变换无翻转的并且其conformal distortion不大于一个常数C(C>=1)的空间$\mathcal A_C(f_j) $

2）对其中最大子空间的描述 $\mathcal A^{\oplus_j}_C(f_j) \subset \mathcal A_C(f_j)$ ，其是由在每个面$f_j$上定义一个坐标架$\oplus_j$

3）对所有面$f_j \in F$ 考虑$\mathcal A^{\oplus_j}_C(f_j)$并且考虑边上的连续性的约束,从而得到映射空间$F^{M,\oplus}_C \subset F^M_C$

4）对得到的映射空间$F^{M,\oplus}_C$进行优化

对每个三角面定义f_j \in F 定义其上的一个本地坐标系 $\oplus_j := [0_j,e_1^j,e_2^j]$,那么对于f_j上的一点p

可以表示成 p = 0j+e1p+e2p,我们可以定义在f_j上的仿射映射A_j:f_j ->R2  A_j(p) =(abcd)(p)+t = A[p] +T

![image-20240912204220610](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912204220610.png)

将上面的仿射映射用矩阵来进行表达从而就可以表达为如下的限制条件

![image-20240912204938422](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912204938422.png)

为方便表达我们写成如下的矩阵形式

![image-20240912195652261](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912195652261.png)

那样映射就可以表达成如下

![image-20240912205200380](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912205200380.png)

通过定义alphaj与betaj等可以转化为求下式

![image-20240912205349059](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912205349059.png)

并且扭曲 $\sigma\$可以表达成  

![image-20240912205426765](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912205426765.png)

那么受限条件就可以转化为如下形式

![image-20240912205621038](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912205621038.png)

引入一个中间变量gammaj in R ,那么上式转为

![image-20240912190926291](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912190926291.png)

这样只要三元组（alpha,beta,gamma） C,C,R满足上面的条件，那么对应的面片上的映射 $\mathcal A_C(f_j)$也就是符合条件的

并用如下方式进行凸化

![image-20240830211740284](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240830211740284.png)

也就是如下图所示的（蓝色内圆与灰色半平面是凸的，但是黄色锥的补区域却是非凸的，我们就是用灰色区域代替黄色锥的补区域的）

![image-20240912190810313](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912190810313.png)

$\mathcal A_C^{\oplus_j}$是$A_C$的子空间，下面来看下具体$A_C^{\oplus_j}$包含什么样的元素

![image-20240912191656882](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912191656882.png)

![image-20240912192008382](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912192008382.png)

![image-20240912192635381](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912192635381.png)

通过在所有面上取Union从而构造出$\mathcal F^{M,\oplus}_C \subset \mathcal F^M$

![image-20240912193217416](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20240912193217416.png)