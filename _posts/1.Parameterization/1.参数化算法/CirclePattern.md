Circle Pattern:

共形映射保持曲面上每个点周边的圆域，所以圆形是共形几何中的基础构建单元。可以想象对于一个曲面，假设一个映射将它上面所有的圆都映射同样的圆形，那么这个映射也一定是一个共形映射。有了这样一个念头就可以构建这样对共形映射的数值逼近算法，通过大量的圆来对曲面进行填充（CirclePacking)，然后求一个映射对这些大量的圆都保持圆形的话，那这个映射就具有很好的共形性了。

【圆填充示意】

对于三角网格来说，所有三角形的外接圆可以认为是对它的一个圆填充，由于圆之间彼此是相交的我们要映射保持它们彼此之间的交角不变。假设映射后的角度是 。那么就要满足如下要求。

![image-20241129203251062](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20241129203251062.png)

满足这样角度的配置称为是一个Coherent Angle System

![image-20241201134719394](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20241201134719394.png)

满足了基本的配置之后，我们当然最好是要使得小三角形的角度变化不会很大，同之前讲的基于角度的ABF算法一样

![image-20241201132302957](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20241201132302957.png)

然后有了角度后，我们再定义如下能量S,通过对它进行优化从而求解（S(1o)是半径的对数值）

![image-20241201134811707](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20241201134811707.png)

相关工作：

![image-20241129203043390](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20241129203043390.png)

Bokeko等人最近也将其转化为求一个凸能量的最小值

![image-20241129202001225](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20241129202001225.png)

![image-20241129202409478](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20241129202409478.png)

这个工作也主要是基于Bokeno的

![image-20241129205735996](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20241129205735996.png)

圆填充(Circle Packing)这个概念最早是由Thurston提出的。