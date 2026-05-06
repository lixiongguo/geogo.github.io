### SCP

SCP相比于LSCM的优点就是不用指定两个固定点。这是其核心优势，算法本身**不依赖任何顶点位置约束**即可自动生成参数化，从而避免了因固定顶点造成的扭曲。

![image-20251203151719056](C:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/imgs/image-20251203151719056.png)




共形能量

![image-20250318151824704](C:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/imgs/image-20250318151824704.png)

面积![image-20250318152308518](C:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/imgs/image-20250318152308518.png)



可以将能量表达成如下形式

![image-20250318152432869](C:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/imgs/image-20250318152432869.png)

即是求

![image-20251014214658893](C:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/imgs/image-20251014214658893.png)

![image-20251028140228283](C:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/imgs/image-20251028140228283.png)

求此能量的最小值即相当于求矩阵的最小特征值与其对应的特征向量$Lu^* = \lambda u^*$,其中$\lambda$是最小的特征值,$u^*$也称为$Fiedler向量$

可以采用**Power Iteration**进行数值求解

![image-20251028140244121](C:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/imgs/image-20251028140244121.png)

![image-20251028140327972](C:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/imgs/image-20251028140327972.png)

![image-20251028140338217](C:/Users/lixio/OneDrive/Desktop/MyDoc/lixiongguo.github.io/imgs/image-20251028140338217.png)



![image-20251028140407733](../../../imgs/image-20251028140407733.png)