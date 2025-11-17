### 映射的Jacobian矩阵

对于每一个三角面片，我们可以首先建立一个如下的局部坐标系，二维坐标来表示其中的点那就是说如何在每个三角形上建立起局部·坐标系。如下图所示，假设我们选取三角形$T=[x_i,x_j,x_k]$,那么我们以某个顶点$x_i$为原点以某个边$[x_i,x_j]$为$X$轴，然后按照右手定则建立坐标系。

![image-20251028101202481](C:\Users\LGX_MATE_BOOK\AppData\Roaming\Typora\typora-user-images\image-20251028101202481.png)

对于每一个三角面片$t$我们可以合理地假设映射$f$在其上的作用可以是一个简单的线性函数$f_t$,可以设$f_t(x) = J_tx + b_t$。

其中$J_t$是Jacobian矩阵，是对映射局部形变情况的描述，在后面我们在对其进行仔细的研究。$b_t$平移量对于参数化映射来说并没有影响，直接设为0

分片线性映射$f$的Jacobian矩阵如下

$$J_t ={\begin{pmatrix}{{\partial u}/{\partial x}}&{{\partial u}/{\partial y}}\\{{\partial v}/{\partial x}}&{{\partial v}/{\partial y}}\end{pmatrix} }= {\begin{pmatrix}{u_j-u_i}&{u_k-u_i}\\{v_j-u_i}&{v_k-v_i}\end{pmatrix} }{\begin{pmatrix}{x_j-x_i}&{x_k-x_i}\\{y_j-y_i}&{y_k-y_i}\end{pmatrix}^{-1}}\tag{1} $$

2阶矩阵可以直接求逆
$$
A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}, \quad
A^{-1} = \frac{1}{ad - bc} \begin{pmatrix} d & -b \\ -c & a \end{pmatrix}
\quad \text{（当 } ad - bc \ne 0 \text{）}
$$
对公式(1)代数变形可以得到下面的展开形式
$$
\begin{aligned}
{\begin{pmatrix}{{\partial u}/{\partial x}}\\{{\partial u}/{\partial y}}\end{pmatrix} }=\frac{1}{2A_t}{\begin{pmatrix}{y_j-y_k}&{y_k-y_i}&{y_i-y_j}\\{x_k-x_j}&{x_i-x_k}&{x_j-x_i}\end{pmatrix} }
{\begin{pmatrix}u_i\\u_j\\u_k\end{pmatrix} }\\
{\begin{pmatrix}{{\partial v}/{\partial x}}\\{{\partial v}/{\partial y}}\end{pmatrix} }=\frac{1}{2A_t}{\begin{pmatrix}{y_j-y_k}&{y_k-y_i}&{y_i-y_j}\\{x_k-x_j}&{x_i-x_k}&{x_j-x_i}\end{pmatrix} }
{\begin{pmatrix}v_i\\v_j\\v_k\end{pmatrix} }
\end{aligned}
\tag{2}
$$
其中$A_t$是三角形面积，可以通过叉积求得$2A_t=(x_iy_j-y_ix_j)+(x_jy_k-y_jx_k)+(x_ky_i-y_kx_i)$



**分段线性映射的奇异值**

对分段线性映射$f$的Jacobian矩阵$J_t$进行SVD分解 ,$$J_t=U\Sigma V^T,\Sigma={\begin{pmatrix}{\sigma_1}&{0}\\{0}&{\sigma_2}\end{pmatrix} } $$,奇异值$\sigma1 , \sigma2$分别描述映射在正交两个方向上的拉伸程度，如下图所示

![img](D:\MyDocs\geogo.github.io\imgs\image-20250318111321305.png)

根据分解后的奇异值$\sigma1 , \sigma2$，对映射扭曲进行度量

（1）若$\sigma1 = \sigma2$ 则这两个三角形是相似三角形，则映射是保角映射

（2）进一步若$\sigma1 = \sigma2 =1$ 则这两个三角形只是发生了旋转