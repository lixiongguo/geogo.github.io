基于流的生成模型(Normalizing Flow)通过流的作用将一个概率分布转化到另一个概率分布，比如GLOW和NICE，REALNVP等，这些方法是通过逐层神经网络堆叠来实现流的作用的，是离散的，这里我们考虑连续的即Continous Normalizing Flows(CNFs)

![image-20250731091244588](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250731091244588.png)

![image-20250731091346094](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250731091346094.png)

Flow Matching是一个simulation-free的，训练CNF(continous normalizing flow)方法，基于对固定的(fixed)条件概率路径（conditional probability paths）的向量场的回归。

![image-20250709194547360](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709194547360.png)

非diffusion probability paths实现的CNF训练实现的可能

![image-20250709195019956](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709195019956.png)

OT Displacement path比diffusion path要更加高效的

![image-20250709195115193](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709195115193.png)

我们的目的是训练一个能回归出一个能生成目标向量场

![image-20250709200244714](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709200244714.png)

事实上，我们可以通过FM构造OT路径

![image-20250709200515486](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709200515486.png)



向量场的定义

![image-20250709201223238](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709201223238.png)

（phi_t(x)是R^d的点，而v_t是R ^d的向量）

CNF就是用Flow将一个简单分布p0转化为一个复杂分布p1(Push Forward)

![image-20250709201922658](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709201922658.png)

![image-20250709201954876](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709201954876.png)

用神经网络建模向量场v_t

![image-20250709202054578](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709202054578.png)

对应的Flow Matching的训练目标如下，就是匹配一个向量场u_t(x)

![image-20250709201535903](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709201535903.png)

直接进行训练的问题

![image-20250709202537312](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709202537312.png)

我们通过对所有的点进行建模条件概率路径(基于指定点的高斯分布)并进行混合，从而建模复杂的概率路径

![image-20250709202710341](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709202710341.png)

然后通过对条件路径进行边缘化就能得到目标概率路径p_t(x)

![image-20250709203550588](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709203550588.png)

由于混合高斯的特性![image-20250709203625191](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709203625191.png)

我们对向量场进行边缘化

![image-20250709203747251](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709203747251.png)

![image-20250709203813451](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709203813451.png)

中心定理

经过边缘化的向量场u_t可以边缘化p_t

![image-20250709203849550](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709203849550.png)

通过将边缘概率分解为一系列条件概率从而求解

![image-20250709210033692](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709210033692.png)



CFM

![image-20250709210142893](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709210142893.png)

u_t还是不可求解的，所以如果作为目标的话还是没办法进行训练，所以我们只匹配条件u_t，并且可以证明的是这两者是等价的

![image-20250709204023733](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709204023733.png)

两个损失的梯度是一致的

![image-20250709204540895](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709204540895.png)



用高斯条件概率路径来表征基础的条件概率

![image-20250709204311551](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709204311551.png)

并进一步有

![image-20250709210405474](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709210405474.png)



从而对于简单的高斯概率路径能证明

![image-20250709204342873](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250709204342873.png)