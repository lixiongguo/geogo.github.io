#### 全局参数化

对于一个球状模型需要先切割成若干个分片(拓扑圆盘)，然后对每个分片分别进行平后的网格填充到一个图卡(Atlas)中

![image-20250927205710412](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250927205710412.png)

而全局参数化的方法就是算法自动找到割线将整个网格模型展开，不再通过分割进行展开

![image-20251015173125209](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251015173125209.png)

