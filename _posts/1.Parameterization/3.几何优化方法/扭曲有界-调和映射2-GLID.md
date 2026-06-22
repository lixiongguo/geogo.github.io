## 4. 推广到多连通域：GLID (Chen & Weber 2017)

BDHM 假设单连通域。GLID 把它推广到**带洞的多连通域**，并改用**无约束 Newton 求解 + 闭式正定 Hessian 修正**，整套流水线跑在 GPU 上。

### 4.1 多连通调和分解 (Theorem 4.1)

> 设 $\Omega$ 有 $N$ 个洞 $K_1,\dots,K_N$，每洞内取一点 $\rho_i$。任意调和映射可表示为：
>
> $$
> f(z)=\widetilde\Phi(z)+\widetilde\Psi(z)+\sum_{i=1}^N\omega_i\ln|z-\rho_i|,
> $$
> $\widetilde\Phi,\widetilde\Psi$ 全纯，$\omega_i\in\mathbb C$。

对数项是多连通域**特有的**——缺它则表示空间不完备。分解除一个加法复常数外唯一。

### 4.2 有界失真定理 (Theorem 4.2)

> 外边界 $\gamma_0$ 逆时针、内边界 $\gamma_1\cdots\gamma_N$ 顺时针。$f$ 全域有界失真且局部单射的**充要条件**为：
>
> $$
> \oint_{\gamma_0}\frac{f_z'(w)}{f_z(w)}dw+\sum_{i=1}^N\oint_{\gamma_i}\frac{f_z'(w)}{f_z(w)}dw=0, \tag{4a}
> $$
> 以及边界上的 $k\le\bar k$、$\sigma_1\le\bar\sigma_1$、$\sigma_2\ge\underline\sigma_2$。

与单连通不同，外边界 $\gamma_0$ 的积分**可以非零**，这允许映射与恒等映射不同伦但仍局部单射。GLID 不显式设硬上界，而是用**遇退化即趋于无穷**的能量自然形成边界界，再由定理 4.2 推广到全域。

### 4.3 离散化（带对数基）

Cauchy 坐标在多连通域上需对**所有**边界分量积分；外边界逆时针、内边界顺时针。多连通 Cauchy 映射有 $2N$ 维复零空间（对应洞的相似变换），固定每洞前两个系数为零去除。对数项用 $2N$ 个额外变量表示，令 $n=m+N$ 合并为：

$$
f(z)=\sum_{j=1}^n C_j(z)\phi_j+\sum_{j=1}^n C_j(z)\psi_j,\quad
C_j(z)=\begin{cases}\widetilde C_j(z),& j\le m\\ \ln|z-\rho_{j-m}|,& j>m\end{cases}
$$

$$
f_z=\sum_j D_j(z)\phi_j,\quad f_{\bar z}=\sum_j D_j(z)\psi_j,\quad
D_j(z)=\begin{cases}\widetilde D_j(z),& j\le m\\ 1/(z-\rho_{j-m}),& j>m\end{cases}
$$

（在 $j>m$ 处约定 $\phi_j=\psi_j$ 消冗余）。$D_j$ 全纯 ⇒ $f_z,f_{\bar z}$ 全纯，复零空间维数 $4N+N+1$。

### 4.4 光滑等距能量与闭式梯度/Hessian

为了用 Newton 法，能量须在 $\phi_j,\psi_j$ 中光滑。利用 $|f_z|^2,|f_{\bar z}|^2$ 的二次性以及

$$
\tfrac12(\sigma_1^2+\sigma_2^2)=|f_z|^2+|f_{\bar z}|^2,\qquad
\sigma_1\sigma_2=|f_z|^2-|f_{\bar z}|^2,
$$

各类能量都化为 $|f_z|^2,|f_{\bar z}|^2$ 的光滑函数：

| 能量           | 表达式                                                       | 特点                                      |
| -------------- | ------------------------------------------------------------ | ----------------------------------------- |
| ARAP           | $(\sigma_1-1)^2+(\sigma_2-1)^2$                              | $\sigma_2\to0$ 时仍有限，**不利**局部单射 |
| 对称 Dirichlet | $\tfrac12(\sigma_1^2+\sigma_2^2+\sigma_1^{-2}+\sigma_2^{-2})$ | $\sigma_2\to0$ 时 $\to\infty$，天然屏障   |
| Exp Dirichlet  | $\exp(s\,E_{\text{iso}})$                                    | 重罚高失真，权衡低平均 vs 低最大          |
| Advanced MIPS  | 面积/角度保持可调                                            | 灵活                                      |

失真定义为边界积分 $E^f=\oint_{\partial\Omega}E(w)\,ds$。令 $D=(D_1,\dots,D_n)$，构造实矩阵 $\mathbf D=\big(\begin{smallmatrix}\operatorname{Re}D&-\operatorname{Im}D\\\operatorname{Im}D&\operatorname{Re}D\end{smallmatrix}\big)$，则单点梯度与 Hessian 有闭式：

$$
\nabla E(z)=2\begin{bmatrix}\alpha_1\mathbf D^T\mathbf f_z\\\alpha_2\mathbf D^T\mathbf f_{\bar z}\end{bmatrix},\qquad
\nabla^2E(z)=\begin{bmatrix}\mathbf D^T&0\\0&\mathbf D^T\end{bmatrix}\mathbf K\begin{bmatrix}\mathbf D&0\\0&\mathbf D\end{bmatrix},
$$

$$
\mathbf K=\begin{bmatrix}
2\alpha_1 I+4\beta_1\mathbf f_z\mathbf f_z^T & 4\beta_3\mathbf f_z\mathbf f_{\bar z}^T\\
4\beta_3\mathbf f_{\bar z}\mathbf f_z^T & 2\alpha_2 I+4\beta_2\mathbf f_{\bar z}\mathbf f_{\bar z}^T
\end{bmatrix}\in\mathbb R^{4\times4},
$$

参数 $\{\alpha_1,\alpha_2,\beta_1,\beta_2,\beta_3\}$ 依能量而定（原文 Table 1）。P2P 软约束 $E_{\text{p2p}}^f=\tfrac12\sum_i|f(p_i)-q_i|^2$，全能量 $E_{\text{Def}}^f=E^f+\lambda E_{\text{p2p}}^f$。

### 4.5 Newton-Eigen：闭式正定修正

$\nabla^2 E^f$ 一般不正定。**关键观察**：单点 Hessian 的最近 Frobenius 范数 PSD 矩阵可闭式求得——

1. $\nabla^2E(z)$ 的非平凡特征向量 = $\mathbf B=[\mathbf D\,0;0\,\mathbf D]$ 的行 × $\mathbf K$ 的特征向量；
2. $\mathbf K$ 与 $\nabla^2E(z)$ 的特征值仅差正比例；
3. 问题归约为 $4\times4$ 的 $\mathbf K$ 的解析特征值分解。

$\mathbf K$ 的四个特征值：$\lambda_1=2\alpha_1$，$\lambda_2=2\alpha_2$，

$$
\lambda_{3,4}=s_1\pm\sqrt{s_2^2+16\beta_3^2|f_z|^2|f_{\bar z}|^2},\quad
s_{1,2}=\alpha_1+2\beta_1|f_z|^2\pm(\alpha_2+2\beta_2|f_{\bar z}|^2).
$$

把负特征值置零得 $\nabla^2E^+(w)$，再积分 $\nabla^2E^{f+}=\oint\nabla^2E^+(w)\,ds$；PSD 矩阵的锥结构保证积分仍 PSD。对 $E_{\text{iso}}$ 通常只有 $\lambda_1=2\alpha_1$ 可能为负，修正可直接写成闭式 $\mathbf K^+$。这比数值特征分解**快得多**，且迭代更有效。

### 4.6 局部单射认证（更紧的 Lipschitz）

GLID 在多连通域上推导出**比 BDHM 更紧**的 Lipschitz 常数：

$$
L_{f_z}=\frac{|f_z'(v_i)|+|f_z'(v_{i+1})|}{2}+\frac{l}{2}\Big(\sum_{j=1}^m L_j|s_j-s_{j+1}|+\sum_{j=m+1}^n L_j^h|\phi_j|\Big),
$$
$L_j=\tfrac{1}{2\pi d^2(z_j)}$，$L_j^h=\tfrac{2}{d^3(\rho_{j-m})}$，$s_j=\tfrac{\phi_j-\phi_{j-1}}{z_j-z_{j-1}}$。条件 (5)：$\sigma_2(v_i)+\sigma_2(v_{i+1})\ge(L_{f_z}+L_{f_{\bar z}})l$。

对积分条件 (4a)，GLID 给出比 BDHM **更强**（必要且充分，只要 (27) 成立）的判据：

> **定理 8.1.** $L$-Lipschitz 全纯函数 $g$ 在线段上若 $|g(v_i)|+|g(v_{i+1})|>Ll$，则
> $\int_{v_i}^{v_{i+1}}\tfrac{g'}{g}dz=\ln\big|\tfrac{g(v_{i+1})}{g(v_i)}\big|+\mathbf i\operatorname{Arg}\tfrac{g(v_{i+1})}{g(v_i)}$。
>
> **推论 8.2.** 在 (27) 成立下，$f_z$ 在多连通多边形内无零点 $\iff$
> $\displaystyle\sum_{j=0}^N\sum_i\operatorname{Arg}\frac{f_z(v_i^{j+1})}{f_z(v_i^j)}=0.$

认证流程：验证 (27) 全部成立 → 计算幅角和 (30)，为零则**保证全域局部单射**；否则 line search 回溯。

### 4.7 工程实现

GLID 的整条流水线（闭式微分、低维子空间、避免昂贵的正定化策略）专为 GPU 设计。开源实现 [renjiec/GLID](https://github.com/renjiec/GLID) 用 MATLAB（核心）+ C++（OpenGL UI，`glidviewer`）+ mex/CUDA（GPU 优化，`cuHarmonic`）。求解器包含基于网格的 AQP、SLIM，以及基于调和子空间的 Gradient Descent / LBFGS / Newton。

---

## 5. 三条路线对比

|          | 网格路线 (Lipman 2012)                         | BDHM (Chen-Weber 2015)                | GLID (Chen-Weber 2017)                                      |
| -------- | ---------------------------------------------- | ------------------------------------- | ----------------------------------------------------------- |
| 域       | 任意三角网格                                   | 单连通                                | **多连通**                                                  |
| 表示     | 逐面仿射 $A_j=\alpha[p]+\beta\bar{[p]}+\delta$ | $f=\Phi+\Psi$（Cauchy 坐标）          | $f=\widetilde\Phi+\widetilde\Psi+\sum\omega_i\ln|z-\rho_i|$ |
| 自由度   | 顶点 UV $\{u_i\}$                              | 复系数 $\{\phi_j,\psi_j\}$            | $\{\phi_j,\psi_j\}$ + 对数项                                |
| 约束施加 | 每个三角面                                     | **仅边界**                            | **仅边界**                                                  |
| 处理非凸 | 局部帧 → 最大凸子空间                          | $\theta$ 凸化 → 最大凸子集            | 光滑屏障能量（无显式凸化）                                  |
| 求解     | SOCP（凸）                                     | SOCP + 活跃集（凸）                   | **无约束 Newton-Eigen**                                     |
| 单射认证 | 凸约束内蕴含                                   | Lipschitz + $\gamma>0$                | 更紧 Lipschitz + 幅角和判据                                 |
| 积分条件 | —                                              | $\oint_{\gamma_0}\tfrac{f_z'}{f_z}=0$ | $\oint_{\gamma_0}+\sum\oint_{\gamma_i}=0$（外边界可非零）   |
| 零空间   | 锚点决定                                       | $1$ 维                                | $4N+N+1$ 维                                                 |
| 性能     | 取决于网格规模                                 | 交互级（边界采样）                    | GPU，几次迭代收敛                                           |

**一句话总结**：三者都把"局部单射 + 有界失真"这一非凸问题，转化为可高效求解的（凸或局部正定）子问题序列。网格路线在三角面上施加约束并以局部帧凸化；BDHM 用调和子空间把约束压到边界、用 $\theta$ 凸化后 SOCP；GLID 进一步推广到多连通域，并以闭式正定 Hessian 修正换来 GPU 上的无约束 Newton 高速收敛。