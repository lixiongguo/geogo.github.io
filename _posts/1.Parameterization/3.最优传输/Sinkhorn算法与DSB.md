Sinkhorn 算法与薛定谔桥

Sinkhorn 算法和薛定谔桥（Schrodinger Bridge, SB）可以看成同一条思想链上的两个层次：

- Sinkhorn 是**熵正则最优传输**的高效离散算法；
- 薛定谔桥是**带噪随机动力系统**上的熵最优控制问题；
- 当噪声趋于 0 时，薛定谔桥会逼近经典最优传输；
- 在现代机器学习中，Diffusion Schrodinger Bridge（DSB）可以看成 SB 与扩散模型结合后的可学习版本。

## 1. 为什么需要 Sinkhorn

经典离散 OT 需要求解线性规划：

$$
\min_{P\in U(a,b)} \langle C,P\rangle,
$$

其中

$$
U(a,b)=\{P\ge 0\mid P\mathbf{1}=a,\ P^\top \mathbf{1}=b\}.
$$

这里 $a,b$ 是源和目标边缘分布，$C$ 是代价矩阵。  
问题在于：当样本规模较大时，线性规划计算代价高，而且数值上不够平滑。

因此引入熵正则项：

$$
\min_{P\in U(a,b)} \langle C,P\rangle
+\varepsilon \sum_{i,j} P_{ij}(\log P_{ij}-1).
$$

其中 $\varepsilon>0$ 控制“运输成本最优”和“耦合平滑程度”之间的平衡。

## 2. 熵正则 OT 的结构

加入熵项后，最优耦合有显式结构：

$$
P^\*=\operatorname{diag}(u)\,K\,\operatorname{diag}(v),
$$

其中

$$
K_{ij}=\exp\left(-\frac{C_{ij}}{\varepsilon}\right).
$$

问题就变成：寻找两个缩放向量 $u,v$，使得 $P^\*$ 满足边缘约束。

这一步之所以重要，是因为它把原本的大规模约束优化，转成了矩阵缩放问题。

## 3. Sinkhorn 迭代

由边缘约束

$$
P\mathbf{1}=a,\qquad P^\top \mathbf{1}=b
$$

可推出经典 Sinkhorn 更新：

$$
u^{(k+1)}=\frac{a}{Kv^{(k)}},\qquad
v^{(k+1)}=\frac{b}{K^\top u^{(k+1)}},
$$

这里除法按元素进行。

算法流程非常简单：

1. 构造 Gibbs kernel
   $$
   K_{ij}=\exp(-C_{ij}/\varepsilon);
   $$
2. 初始化 $u=\mathbf{1},v=\mathbf{1}$；
3. 交替归一化行与列；
4. 收敛后恢复耦合
   $$
   P^\*=\operatorname{diag}(u)K\operatorname{diag}(v).
   $$

## 4. Sinkhorn 的优缺点

优点：

- 实现简单，GPU 友好；
- 可微，适合深度学习训练；
- 熵正则让问题更稳定，也更容易并行。

缺点：

- $\varepsilon$ 太大时，解会过度平滑，偏离真实 OT；
- $\varepsilon$ 太小时，会出现数值下溢，需要 log-domain 技巧；
- 它求得的是正则化 OT，不是严格原始 OT。

因此实际使用中常配合：

- log-Sinkhorn；
- epsilon scaling；
- 截断 kernel 或多尺度近似。

## 5. Sinkhorn 距离

直接使用熵正则 OT 值会带有 entropy bias，因此常用 Sinkhorn divergence：

$$
S_\varepsilon(\mu,\nu)
=
OT_\varepsilon(\mu,\nu)
-\frac12 OT_\varepsilon(\mu,\mu)
-\frac12 OT_\varepsilon(\nu,\nu).
$$

它兼具两点：

- 保留 Wasserstein 类几何信息；
- 降低熵正则带来的自匹配偏差。

这也是现代生成模型与配准任务里更常用的版本。

## 6. 从 Sinkhorn 到薛定谔桥

Sinkhorn 看上去像静态离散算法，但它背后其实对应一个更深的概率解释：

> 在所有满足给定起终边缘分布的随机路径分布中，寻找与某个参考扩散过程最接近的那一个。

这就是薛定谔桥问题。

设参考过程 $R$ 通常是布朗运动或扩散过程。  
薛定谔桥要求寻找路径测度 $Q$，使得

$$
\min_Q \operatorname{KL}(Q\|R),
$$

subject to

$$
Q_0=\mu,\qquad Q_1=\nu.
$$

也就是说：  
不是在所有确定性映射中找最短搬运，而是在所有随机过程里找“相对参考扩散最不意外”的那条路径。

## 7. 动态形式与连续性方程的关系

如果把经典 OT 看作“无噪声最小动能流”，那么薛定谔桥就是“带扩散项的最小控制能流”。

它的连续形式可写成一类随机控制问题：

$$
\min_{\rho_t,v_t}
\int_0^1\!\!\int
\frac12 \|v_t(x)\|^2 \rho_t(x)\,dx\,dt
$$

subject to

$$
\partial_t \rho_t+\nabla\cdot(\rho_t v_t)
-\frac{\sigma^2}{2}\Delta \rho_t = 0,
$$

并满足

$$
\rho_0=\mu,\qquad \rho_1=\nu.
$$

与 Benamou-Brenier 相比，唯一显著区别就是多了扩散项

$$
-\frac{\sigma^2}{2}\Delta \rho_t.
$$

当 $\sigma\to 0$ 时，SB 会趋近经典 OT；  
当噪声较大时，路径更平滑、更随机，也更稳定。

## 8. 薛定谔系统与迭代比例因子

薛定谔桥有一对前向/后向势函数（也常写成 Schrödinger potentials）：

$$
\varphi_t,\qquad \hat{\varphi}_t,
$$

满足密度分解

$$
\rho_t(x)=\varphi_t(x)\hat{\varphi}_t(x).
$$

这与 Sinkhorn 中的左右缩放向量 $u,v$ 在结构上是完全对应的。  
可以粗略理解为：

- 离散 Sinkhorn：对矩阵做左右缩放；
- 连续 Schrödinger bridge：对路径测度做前后向重权。

因此很多文献会说：

> Sinkhorn 是 Schrödinger bridge 在离散静态耦合问题上的迭代比例拟合（IPFP）。

## 9. DSB（Diffusion Schrodinger Bridge）的理解

现代机器学习中的 DSB，一般指把薛定谔桥和扩散/score 模型结合起来，学习从分布 $\mu$ 到分布 $\nu$ 的随机生成路径。

常见理解方式：

- 用前向扩散提供参考过程；
- 通过学习时间相关 drift 或 score，逼近桥过程；
- 同时满足起点分布与终点分布约束；
- 利用双向训练、time-reversal、score matching 等技巧求解。

如果说：

- 经典 OT 更像“确定性搬运”；
- SB 更像“带噪声的最优随机搬运”；
- DSB 则是“可学习的、适合高维数据的薛定谔桥实现”。

## 10. Sinkhorn 与 SB 的关系

二者可以从三个层面对应：

### 10.1 数学层面

- Sinkhorn 解的是熵正则化的静态耦合问题；
- SB 解的是路径空间上的 KL 投影问题；
- 两者本质上都与相对熵最小化有关。

### 10.2 算法层面

- Sinkhorn 是交替归一化；
- SB 常用 IPFP / Fortet / Sinkhorn-like 迭代；
- 连续时间下可转成前后向 PDE 或 SDE 学习问题。

### 10.3 几何层面

- OT 给出 Wasserstein 几何；
- SB 给出带噪 Wasserstein 几何；
- DSB 则把这种几何推广到高维生成建模。

## 11. 与前文 OT 路线的联系

可以把这几条路线放在一起看：

- `MA 方程`：静态 PDE 路线，追求精确势函数与映射；
- `Benamou-Brenier`：动态无噪流体路线；
- `Sinkhorn`：静态熵正则离散路线；
- `Schrodinger Bridge`：动态带噪随机路线；
- `DSB`：SB 在高维学习问题中的现代实现。

它们并不是互相竞争，而是同一问题在不同约束、不同噪声模型、不同数值需求下的表现形式。

## 12. 实践建议

如果任务是：

- **离散分布距离计算 / 配准损失**：优先用 Sinkhorn 或 Sinkhorn divergence；
- **需要路径插值且希望更稳定**：考虑 Schrödinger bridge；
- **高维生成与域间转换**：考虑 DSB 或相关 score-based bridge 方法；
- **低维高精度几何映射**：还是 MA / 半离散 OT 更直接。

## 13. 小结

Sinkhorn 的核心不是“一个巧妙的数值技巧”，而是把 OT 放入熵正则框架后出现的自然矩阵缩放结构。  
薛定谔桥则把这一思想推广到随机路径空间：不是问“怎么最省力地搬”，而是问“在参考扩散附近，怎么最合理地从起点分布走到终点分布”。

从这个角度看，Sinkhorn 与薛定谔桥是同一理论脉络在离散静态与连续动态两个层面的展开。

## 参考文献

- Villani, C. (2009). *Optimal Transport: Old and New*. Springer.
- Peyre, G., & Cuturi, M. (2019). *Computational Optimal Transport*. Foundations and Trends in Machine Learning.
- Brenier, Y. (1991). *Polar factorization and monotone rearrangement of vector-valued functions*.
- Benamou, J.-D., & Brenier, Y. (2000). *A computational fluid mechanics solution to the Monge-Kantorovich mass transfer problem*.
- Cuturi, M. (2013). *Sinkhorn distances: Lightspeed computation of optimal transport*.
