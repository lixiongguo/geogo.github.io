

算法的主要思想是：**四边形网格等价于一个具有封闭轨迹的亚纯四次微分，其奇点满足Abel-Jacobi条件**。算法的生成流程可概括为以下步骤：

1. **计算同调群**：确定曲面的拓扑结构。
2. **计算全纯微分群**：为基础计算做准备。
3. **构造周期矩阵和Jacobi簇**：建立曲面与复平面之间的桥梁。
4. **计算给定除子的Abel-Jacobi映射**。
5. **通过整数规划优化除子以满足Abel-Jacobi条件**：这是关键步骤，确保奇点配置的合理性。
6. **通过Ricci流计算在除子处具有锥奇异点的平坦黎曼度量**。
7. **将除子处穿刺的曲面等距浸入复平面**，并拉回典范全纯微分到曲面上以获得亚纯四次微分。
8. **构造摩托图以生成T网格**，进而可生成四边形网格



共形结构与Riemann Surface的定义

![image-20250721193808999](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250721193808999.png)

![image-20250721193843582](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250721193843582.png)

亚纯函数(meromorphic)的除子(divisor)

![image-20250721194208550](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250721194208550.png)

Riemann面的正规基础群生成子a_1...a_g与b_1...b_g，可以通过求tunnel和handle的方法获取到

另外设正规基

![image-20250721195235753](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250721195235753.png)

对于每一条曲线可以进行积分，从而得到g-维的lattice

![image-20250721195342300](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250721195342300.png)

定义Jacobian Variety  J(S)
![image-20250721195837939](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250721195837939.png)

以某个固定点p0为原点可以构建Abel-Jacobian映射

![image-20250721200035170](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250721200035170.png)

Abel-Jacobi定理

![image-20250721200125101](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250721200125101.png)

一个QuadMesh可以引导出共形结构

![image-20250721204457644](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250721204457644.png)

不存在只有一个度为5的奇异点和一个度为7奇异点的三角化

![image-20250722152933804](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250722152933804.png)

![image-20250722153101451](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20250722153101451.png)