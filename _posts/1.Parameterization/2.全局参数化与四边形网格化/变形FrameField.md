

![image-20250923104719017](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923104719017.png)

先在曲面上顶下几个稀疏的点，然后通过插值生成一个frame field，通过变形的方法将frame field变形成cross field，通过这个cross field我们用来引导生成一个四边形网格，最后变形回原来的曲面

frame field与cross field的对应

![image-20250923105418255](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923105418255.png)

一个discrete cross field的smooth的定义

![image-20250923105930362](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923105930362.png)

通过求如下的最优化得到变形后的顶点

![image-20250923110416518](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923110416518.png)

BCD求解能量

![image-20250923110121214](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250923110121214.png)

