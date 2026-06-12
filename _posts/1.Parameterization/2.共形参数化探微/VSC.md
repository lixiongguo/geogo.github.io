
## Variational Surface Cut

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010142551440.png)

可以得到很好的分割效果

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010192434507.png)

用变分法的方式求解析优化的方式，而不再用传统的组合优化方式

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010174554855.png)

定义一个依赖于切割路径的能量函数，然后通过连续变形（演化）切割路径不断降低这个能量值

变形过程中需要共形因子时刻满足如下Yamabe方程

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010183229321.png)



![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010142836409.png)

通过连续变形一条曲线 $\gamma$,使得一方面distortion尽可能小，另外长度尽可能小

用Dirichlet能量来度量distortion

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010143206213.png)

仅要求distortion尽可能小，那么问题就是ill-posed，由于可以通过不断延展 $\gamma$ 的长度来减小distortion，所以需要对curve长度进行约束

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010143507440.png)

Cea方法

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010145117349.png)

构造Lagrangian函数

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251010192645924.png)
