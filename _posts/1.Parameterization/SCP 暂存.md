---
layout: post
title: "网格的谱处理SCP"
categories: [TechRelated]
---

## SCP 方法

SCP（Spectral Conformal Parameterization，Mullen et al.）是 LSCM 的谱方法变体。LSCM 需手工指定两个 pin 点以消除平凡解；SCP **不必指定 pin 点**，从而避免 pin 点带来的额外扭曲。

LSCM 共形能量与 Dirichlet 能量、ARAP 能量在固定边界条件下的等价关系，已在前面章节讨论，此处不再展开。

### 离散共形能量

共形能量在离散情形下可写成对 **(u,v) 堆叠向量** 的二次型。加入向量面积项（vector area matrix，仅依赖边界边，与 libigl 的 `vector_area_matrix` 一致）后得到对称矩阵 \(L_C\)：

$$
L_C = -\mathrm{diag}(L,L) + 2A
$$

其中 \(L\) 为 cotan 拉普拉斯，\(A\) 为向量面积矩阵。

**注意**：不要把它与「单独对 cotan 拉普拉斯 \(L\) 求最小特征值」混为一谈——后者是另一套谱问题。

共形能量（示意）

![image-20250318151824704](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250318151824704.png)

面积项（示意）

![image-20250318152308518](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250318152308518.png)

![image-20251203151719056](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251203151719056.png)

### 谱求解

SCP 对应 \(L_C\) 在**去掉边界常数模态**（投影算子 \(P = B - EE^\top\)）后的逆幂迭代：

$$
L_C x_{k+1} = P x_k
$$

所收敛的主模式即为参数化结果。可采用 **Power / inverse 迭代** 配合线性求解器（稠密 LU 或 GMRES）数值求解。

**与 Fiedler 向量的区别**：图论中 Fiedler 向量常指**标量**拉普拉斯第二小特征值对应的特征向量；SCP 处理的是 **2|V| 维堆叠系统** \(L_C\) 的谱，二者概念相近但矩阵与约束并不相同。

![image-20251028140244121](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251028140244121.png)

![image-20251028140327972](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251028140327972.png)

![image-20251028140338217](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251028140338217.png)

![image-20251028140407733](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251028140407733.png)
