##  交替优化方法(Local/Global)求解能量优化

**(As Rigid As Possible)**采用**迭代**优化的策略：先从一个简单算法（如 Tutte）初始化，然后交替进行如下两步——首先为每个三角形寻找一个尽量保持原形状的局部近似（**Local 优化**），再回头调整 Jacobian 矩阵使网格整体保持连接（**Global 优化**）。

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251023215121312-1778207385711-1.png)

若矩阵 SVD 分解后两奇异值相等（$\sigma_1 = \sigma_2$），则该变换是相似变换（仅旋转+均匀缩放），由此构成的相似变换族记为 $\Omega_s$。用 Frobenius 范数量化当前 Jacobian $J_t$ 到 $\Omega_s$ 的距离：

$$
d(J_t,L_t)=||J_t-L_t||_F^2
$$

对于整个三角网格，累加所有三角形的差异得到一个如下的能量函数，这个就是我们要优化的能量函数

$$
E_{ARAP}=\sum_{t}A_t\|J_t-L_t\|_F^2,\quad L_t\in\Omega_s
$$

这个优化能量有两部分是要优化的对象，其一是映射 Jacobian 矩阵 $J_t$，其二是局部优化目标 $L_t$。考虑先固定其中一个再优化另外一个，交替进行。

#### Local 优化

固定当前映射的 $J_t$，对每个三角形独立寻找最优的相似变换近似 $L_t^*$：

$$
L_t^* = \min_{L_t}\{d(J_t,M_t)\},\quad M_t\in\Omega_s
$$

注意到

$$
||J_t-L_t||_F^2=tr((J_t-L_t)^T(J_t-L_t))
$$

根据**Procrustes分析**，通过对 $J_t$ 的**带符号的SVD分解(Signed SVD)**可以解得 $L_t^*$

对 $J_t$ 进行 SSVD 分解保证 $U,V$ 是**旋转矩阵**，可以令 $\sigma_2$ 是负的(一般的SVD分解中U,V是正交矩阵不一定是旋转矩阵)

$$
J_t=U\Sigma V^T,\Sigma={\begin{pmatrix}{\sigma_1}&{0}\\{0}&{\sigma_2}\end{pmatrix} }
$$
然后重新组合上面分解的矩阵得到 $L_t$

$$
L_t= U {\begin{pmatrix}{s}&{0}\\{0}&{s}\end{pmatrix}} V^T,s = \frac{\sigma_1+\sigma_2}{2}
$$

这个局部优化的效果可参看下图，其中右边黑色三角形是优化的目标三角形，红色三角形为最优的共形三角形

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251023215506894-1778207385711-3.png)

#### Global 优化

若直接令 $J_t = L_t$，各三角形独立优化后会破坏网格顶点间的连接关系——相邻三角形共用的顶点将不再重合。

![](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250317141120034-1778207385711-2.png)

因此需要**Global 优化**：固定 $L_t$，在全局顶点位置 $\{u_t\}$ 上优化 $E_{ARAP}$。将上节推导的 $J_t$ 表达式代入（每个 $J_t$ 可写为该三角形三个顶点 $\{u_i, u_j, u_k\}$ 的线性函数）：

$$
\begin{aligned}
{\begin{pmatrix}{\frac{\partial u}{\partial x}}\\{\frac{\partial u}{\partial y}}\end{pmatrix} }=\frac{1}{2A_t}{\begin{pmatrix}{y_j-y_k}&{y_k-y_i}&{y_i-y_j}\\{x_k-x_j}&{x_i-x_k}&{x_j-x_i}\end{pmatrix} }
{\begin{pmatrix}u_i\\u_j\\u_k\end{pmatrix} }\\
{\begin{pmatrix}{\frac{\partial v}{\partial x}}\\{\frac{\partial v}{\partial y}}\end{pmatrix} }=\frac{1}{2A_t}{\begin{pmatrix}{y_j-y_k}&{y_k-y_i}&{y_i-y_j}\\{x_k-x_j}&{x_i-x_k}&{x_j-x_i}\end{pmatrix} }
{\begin{pmatrix}v_i\\v_j\\v_k\end{pmatrix} }
\end{aligned}
$$

 可以将(2)式的能量转化为如下形式，我们优化的变量是向量 $\{u_t\}$

$$
\begin{aligned}
E_{\text{ARAP}}(u,L) = \frac{1}{2}\sum_{t=1}^T\sum_{i=0}^2\cot(\theta_t^i)\|(u_t^i-u_t^{i+1})-L_t(x_t^i-x_t^{i+1})\|^2\\
=\frac{1}{2} \sum_{he_{ij}}\cot(\theta_{ij})\|(u^i-u^j)-L_t(x^i-x^j)\|^2\\
\end{aligned}
$$

对向量 $\{u_t\}$ 求导并令其为零（寻找能量极小值的临界点），得到稀疏线性系统：

$$
\sum_{j\in N(i)}[\cot(\theta_{ij}) +\cot(\theta_{ji})](u^i-u^{j}) 
=\sum_{j\in N(i)}[\cot(\theta_{ij})L_{t(i,j)} +\cot(\theta_{ji})L_{t(j,i)}](x^i-x^{j}) 
$$

最后可以求解上面的**稀疏线性方程组（Sparse Linear System）**来求得 $\{u_t\}$

