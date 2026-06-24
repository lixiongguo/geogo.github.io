## 交替优化方法用于几何变形

**几何变形（Geometric Deformation）**是计算机图形学中的核心问题之一：给定一个物体的几何表示（通常是三角网格），在用户拖拽控制点时，让物体表面发生自然、平滑的形变，同时尽量保持局部细节（如角度、面积）的刚性。

对于几何变形，我们希望变形的过程中尽可能保持刚性即只有旋转平移没有其他形变。那么我们同样可以分阶段求解：**local** 阶段固定顶点位置求最优旋转，**global** 阶段固定旋转求最优顶点位置，交替迭代。

#### 固定顶点位置求最优旋转 

记边向量 $e_{ij} = p_i - p_j$，变形后 $e'_{ij} = p'_i - p'_j$。

尽可能保持刚性：对于顶点 i，如果变形是刚性的，存在旋转矩阵 $R_i$ 使得

$$
p'_i - p'_j = R_i \, (p_i - p_j), \quad \forall j \in N(i)
$$

当变形非刚性时，可以用加权最小二乘找到最佳近似旋转 $R_i$，即最小化：

$$
E = \sum_{j \in N(i)} w_{ij} \, \| (p'_i - p'_j) - R_i (p_i - p_j) \|^2 
$$

式子展开后去掉与$R_i $无关的常数项：

$$
\arg\min_{R_i} \sum_j -2 w_{ij} \, e'^T_{ij} R_i e_{ij} = \arg\max_{R_i} \sum_j w_{ij} \, e'^T_{ij} R_i e_{ij} = \arg\max_{R_i} \operatorname{Tr}\!\left( R_i \sum_j w_{ij} \, e_{ij} e'^T_{ij} \right) 
$$

定义协方差矩阵$S_i$：

$$
S_i = \sum_{j \in N(i)} w_{ij} \, e_{ij} e'^T_{ij} = P_i D_i P'^T_i 
$$

其中 $D_i$ 是对角矩阵包含权重 $w_{ij}$，$P_i$ 是 $3 \times |N(i)|$ 矩阵列向量为 $e_{ij}$。

所以我们的优化目标就是

$$
\arg\min_{R_i} \operatorname{Tr}(R_i S_i)
$$

对 $S_i$ 做**带符号的SVD分解**（需要调整 $U_i$ 最后一列的符号）：

$$
S_i = U_i \Sigma_i V_i^T
$$

满足上面优化目标的旋转矩阵 $R_i$ 

$$
R_i = V_i U_i^T
$$

对于每一条半边，可以使用 **cot权重**,保持离散曲面的几何特征。

$$
w_{ij} = \frac{1}{2} (\cot \alpha_{ij} + \cot \beta_{ij})
$$

其中 $\alpha_{ij}$ 和 $\beta_{ij}$ 是边 $e_{ij}$ 所对的两个角。

#### 固定旋转求最优顶点位置

固定 $R_i$，对能量关于 $p'_i$ 求偏导：

$$
\frac{\partial E}{\partial p'_i} = \sum_{j \in N(i)} 2 w_{ij} \bigl((p'_i - p'_j) - R_i (p_i - p_j)\bigr) - \sum_{j \in N(i)} 2 w_{ji} \bigl((p'_j - p'_i) - R_j (p_j - p_i)\bigr) = 0
$$

令偏导为零，利用 $w_{ij} = w_{ji}$，整理得：

$$
\sum_{j \in N(i)} w_{ij} (p'_i - p'_j) = \sum_{j \in N(i)} \frac{w_{ij}}{2} (R_i + R_j) (p_i - p_j)
$$

左边正是**离散 Laplace-Beltrami 算子**作用于 $p'$，可紧凑写为稀疏线性系统：

$$
L \, p' = b
$$

其中 **L 是 cotangent Laplacian 矩阵**，b 由当前旋转矩阵决定。求解该线性系统即得更新后的顶点位置。