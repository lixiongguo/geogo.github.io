## ARAP变形

尽可能保持刚性：对于顶点 i，如果变形是刚性的，存在旋转矩阵 R_i 使得

$$p'_i - p'_j = R_i \, (p_i - p_j), \quad \forall j \in N(i). \tag{1}$$

当变形非刚性时，可以用加权最小二乘找到最佳近似旋转 R_i，即最小化：

$$E(C') = \sum_{j \in N(i)} w_{ij} \, \| (p'_i - p'_j) - R_i (p_i - p_j) \|^2 \tag{2}$$

分阶段求解：**local** 阶段固定顶点位置求最优旋转，**global** 阶段固定旋转求最优顶点位置，交替迭代。

### local —— 求最优旋转

记边向量 $e_{ij} = p_i - p_j$，变形后 $e'_{ij} = p'_i - p'_j$。展开 (2)：

$$\sum_j w_{ij} \, (e'_{ij} - R_i e_{ij})^T (e'_{ij} - R_i e_{ij}) \tag{3}$$

去掉与 R_i 无关的常数项：

$$\arg\min_{R_i} \sum_j -2 w_{ij} \, e'^T_{ij} R_i e_{ij} = \arg\max_{R_i} \sum_j w_{ij} \, e'^T_{ij} R_i e_{ij} = \arg\max_{R_i} \operatorname{Tr}\!\left( R_i \sum_j w_{ij} \, e_{ij} e'^T_{ij} \right) \tag{4}$$

定义协方差矩阵 S_i：

$$S_i = \sum_{j \in N(i)} w_{ij} \, e_{ij} e'^T_{ij} = P_i D_i P'^T_i \tag{5}$$

其中 $D_i$ 是对角矩阵包含权重 $w_{ij}$，$P_i$ 是 $3 \times |N(i)|$ 矩阵列向量为 $e_{ij}$。

使 $\operatorname{Tr}(R_i S_i)$ 最大化的旋转矩阵 $R_i$ 满足 $R_i S_i$ 为对称半正定。对 $S_i$ 做 SVD：$S_i = U_i \Sigma_i V_i^T$，则：

$$R_i = V_i U_i^T \tag{6}$$

（需要调整 $U_i$ 最后一列的符号使得 $\det(R_i) > 0$。）

### 权重

对于每一条半边，可以设置如下权重来表征三角网格的特征，使用 cotangent 权重公式避免离散化偏差：

$$w_{ij} = \frac{1}{2} (\cot \alpha_{ij} + \cot \beta_{ij})$$

其中 $\alpha_{ij}$ 和 $\beta_{ij}$ 是边 ij 所对的两个角。

### global —— 更新顶点位置

固定 R_i，对能量关于 $p'_i$ 求偏导：

$$\frac{\partial E}{\partial p'_i} = \sum_{j \in N(i)} 2 w_{ij} \bigl((p'_i - p'_j) - R_i (p_i - p_j)\bigr) - \sum_{j \in N(i)} 2 w_{ji} \bigl((p'_j - p'_i) - R_j (p_j - p_i)\bigr) = 0$$

令偏导为零，利用 $w_{ij} = w_{ji}$，整理得：

$$\sum_{j \in N(i)} w_{ij} (p'_i - p'_j) = \sum_{j \in N(i)} \frac{w_{ij}}{2} (R_i + R_j) (p_i - p_j) \tag{7}$$

左边正是离散 Laplace-Beltrami 算子作用于 $p'$，可紧凑写为稀疏线性系统：

$$L \, p' = b \tag{8}$$

其中 L 是 cotangent Laplacian 矩阵，b 由当前旋转矩阵决定。求解该线性系统即得更新后的顶点位置。

重复 local-global 迭代直到收敛，即得到尽可能保持刚性（As-Rigid-As-Possible）的变形结果。
