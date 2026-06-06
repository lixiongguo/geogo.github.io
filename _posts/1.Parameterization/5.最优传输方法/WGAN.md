## WGAN与最优传输

### 从 GAN 的困境到 Wasserstein 距离

原始 GAN（Goodfellow et al. 2014）的损失函数等价于最小化生成分布 $$P_g$$ 与真实分布 $$P_r$$ 之间的 **JS 散度（Jensen-Shannon Divergence）**：

$$
\min_G \max_D \; \mathbb{E}_{x \sim P_r}[\log D(x)] + \mathbb{E}_{z \sim p(z)}[\log(1 - D(G(z)))]
$$

JS 散度的一个著名缺陷是：当两个分布的支撑集不重叠时，散度为常数 $$\log 2$$，梯度消失，导致生成器无法训练（vanishing gradient）。Arjovsky & Bottou (2017) 指出这在高维空间中几乎必然发生。

原始 GAN 的三大问题——(1) 训练不稳定：判别器 $D$ 过强时生成器梯度消失 $\nabla \log(1-D(G(z)))\to 0$；(2) 梯度无意义：$P_r$ 与 $P_g$ 支撑不交时 JS 散度为常数 $\log 2$；(3) 模式坍塌。

WGAN 在一定程度上也缓解了原始 GAN 的**模式坍塌**，但它主要解决的核心问题是**训练不稳定和梯度消失/无意义**。原始 GAN 判别器训练越好，梯度越接近零，生成器无法获得有意义的梯度信号，训练极易崩溃。

**WGAN（Arjovsky, Chintala & Bottou, 2017）** 的突破在于：用 **Wasserstein-1 距离**（也就是最优传输中的 Earth Mover's Distance）替代 JS 散度。

### Wasserstein-1 距离 = Kantorovich 问题

回顾 Kantorovich 问题——当代价函数 $$c(x,y) = \|x - y\|$$（欧氏距离）时：

*图：1-Wasserstein 距离的**原始问题**——给定 $P_r$（真实分布）与 $P_g$（生成分布），在度量空间 $(\mathcal{X}, d)$ 上（通常 $\mathcal{X}=\mathbb{R}^d$，$d(x,y)=\|x-y\|$）：*

$$
W_1(P_r, P_g) = \inf_{\gamma \in \Pi(P_r, P_g)} \mathbb{E}_{(x,y)\sim\gamma}[\|x-y\|],
$$

其中 $\Pi(P_r, P_g)$ 是所有以 $P_r$、$P_g$ 为边缘的联合分布（传输计划）的集合。这是涉及高维耦合变量 $\gamma$ 的原始问题，直接计算代价极高。

等价地（与正文符号一致）：

$$
W_1(P_r, P_g) = \min_{\pi \in \Pi(P_r, P_g)} \int_{X \times Y} \|x - y\| \, d\pi(x,y).
$$

这就是 **1-Wasserstein 距离**，度量了将一个分布"搬运"为另一个分布所需的最小平均位移。直观理解：将分布 $$P_g$$ 的"土堆"搬运到 $$P_r$$ 的形状，最小化总工作量（质量 × 运输距离）。

对任意一对分布，$$W_1$$ 都具有良好定义的梯度信息——不像 JS 散度在支撑不交时退化：

![image-20260209163519850](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260209163519850.png)

*图：Arjovsky & Bottou 的经典反例——$P$ 支撑在 $x=0$、$Q$ 支撑在 $x=\theta$（$y\sim U(0,1)$），当 $\theta\neq 0$ 时两分布支撑不交。*

![image-20260209163549080](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20260209163549080.png)

*图：三种度量的对比（$\theta\neq 0$ 时）：*

$$
D_{\mathrm{KL}}(P\|Q) = D_{\mathrm{KL}}(Q\|P) = +\infty, 
D_{\mathrm{JS}}(P,Q) = \log 2, 
W(P,Q) = |\theta|.
$$

*当 $\theta=0$ 时三者均为 0。JS 在 $\theta=0$ 处不可微，而 Wasserstein 距离 $|\theta|$ 光滑，利于梯度下降。*

| 度量            | 不相交分布           | 梯度性质   |
| :-------------- | :------------------- | :--------- |
| **KL 散度**     | $$\infty$$（无意义） | 梯度爆炸   |
| **JS 散度**     | $$\log 2$$（常数）   | 梯度为零   |
| **Wasserstein** | 正比于空间距离       | 平滑有梯度 |

关键区别：即使两个分布的支撑集不相交，Wasserstein 距离仍能提供有意义的、平滑的度量，反映两个分布之间的几何距离。

### Kantorovich-Rubinstein 对偶：WGAN 的数学核心

**Kantorovich-Rubinstein 对偶定理**——若 $\mathcal{X}$ 是 Polish 空间，则*
$$
W_1(P_r, P_g) = \sup_{\substack{f:\mathcal{X}\to\mathbb{R} \\ \|f\|_{\mathrm{Lip}}\leq 1}}
\left\{ \mathbb{E}_{x\sim P_r}[f(x)] - \mathbb{E}_{y\sim P_g}[f(y)] \right\},
$$

其中 $\|f\|_{\mathrm{Lip}}\leq 1$ 表示 $f$ 是 1-Lipschitz 函数：

$$
|f(x) - f(y)| \leq \|x - y\|, \quad \forall x, y \in \mathcal{X}.
$$

直接计算 $$W_1$$ 的最小化代价极高。WGAN 的真正力量来自 **Kantorovich-Rubinstein 对偶定理**——前面讨论的 Kantorovich 对偶在 $$c(x,y) = \|x - y\|$$ 下的特化形式：

$$
\boxed{W_1(P_r, P_g) = \sup_{\|f\|_L \leq 1} \left[ \mathbb{E}_{x \sim P_r}[f(x)] - \mathbb{E}_{x \sim P_g}[f(x)] \right]}
$$

其中约束 $$\|f\|_L \leq 1$$ 表示 $$f$$ 是 **1-Lipschitz 函数**：$$|f(x) - f(y)| \leq \|x - y\|$$。

将 Kantorovich 对偶的一般形式：

$$
\sup_{\phi,\psi} \left\{ \int \phi \, dP_r + \int \psi \, dP_g \mid \phi(x) + \psi(y) \leq \|x - y\| \right\}
$$

在代价为欧氏距离时，约束 $$\phi(x) + \psi(y) \leq \|x - y\|$$ 等价于 $$\phi = -f,\; \psi = f$$ 且 $$f$$ 1-Lipschitz。因此对偶化简为仅含一个函数 $$f$$ 的形式——WGAN 中的 **critic**（或 discriminator）恰好就是 Kantorovich 势的对偶变量。

### WGAN 的 Loss 设计

因遍历所有联合分布 $\Pi(p_r,p_g)$ 计算 $\inf$ 不可行，WGAN 利用 KR 对偶化为 $\sup$ 问题。一般 Lipschitz 常数 $K$ 下

$$
W(p_r, p_g) = \frac{1}{K} \sup_{\|f\|_L \leq K}
\left\{ \mathbb{E}_{x\sim p_r}[f(x)] - \mathbb{E}_{x\sim p_g}[f(x)] \right\}.
$$

*取 $K=1$ 即得正文 boxed 公式。*

WGAN 将判别器替换为**批评器（Critic）** $$f_w$$，输出一个标量分数（而非概率），不再使用 sigmoid：

**Critic 损失**（最大化 Wasserstein 距离估计）：

$$
\mathcal{L}_{\text{critic}} = \mathbb{E}_{x \sim P_g}[f_w(x)] - \mathbb{E}_{x \sim P_r}[f_w(x)]
$$

**Generator 损失**（最小化 Wasserstein 距离）：

$$
\mathcal{L}_{\text{generator}} = -\mathbb{E}_{z \sim p(z)}[f_w(G(z))]
$$

为强制 Lipschitz 约束，WGAN 的原始方案是**权重裁剪（Weight Clipping）**——每次参数更新后将权重硬截断：

$$
w \leftarrow \text{clip}(w, -c, c)
$$

其中 $$c$$ 为裁剪阈值（典型值 0.01）。

**WGAN vs 原始 GAN** 的核心区别：

| 维度               | 原始 GAN        | WGAN                 |
| :----------------- | :-------------- | :------------------- |
| **判别器输出**     | 概率（sigmoid） | 标量分数（无激活）   |
| **分布度量**       | JS 散度         | Wasserstein-1 距离   |
| **Lipschitz 约束** | 无              | 权重裁剪 $$[-c, c]$$ |
| **训练稳定性**     | 差，易模式坍塌  | 显著改善             |
| **Loss 曲线**      | 无意义          | 可反映生成质量       |
| **优化器**         | Adam            | RMSProp（推荐）      |

### WGAN 的三种 Lipschitz 约束实现

对偶中的 Lipschitz 约束 $$\|\nabla f\| \leq 1$$ 是使 Kantorovich-Rubinstein 对偶成立的关键。三代 WGAN 的不同在于如何施加这一约束：

**WGAN (2017) —— Weight Clipping**：将网络参数硬截断到 $$[-c, c]$$ 区间。简单粗暴但严重限制 critic 的表达能力，且对超参数 $$c$$ 极其敏感。

**WGAN-GP (Gulrajani et al. 2017) —— Gradient Penalty**：在训练数据与生成数据之间随机插值点上施加梯度惩罚：

$$
\mathcal{L}_{\text{GP}} = \lambda \cdot \mathbb{E}_{\hat{x}} \left[ (\|\nabla_{\hat{x}} f(\hat{x})\|_2 - 1)^2 \right]
$$

其中 $$\hat{x} = \epsilon x_r + (1 - \epsilon) x_g,\; \epsilon \sim U(0,1)$$。这个方法稳定且效果好，但只在插值点上约束 Lipschitz，非全局保证。

**SN-GAN (Miyato et al. 2018) —— Spectral Normalization**：将每一层的谱范数归一化为 1。由矩阵范数的 Lipschitz 性质，$$\|f\|_L \leq \prod \|W_i\|_2$$，每层的谱范数 ≤ 1 即保证整体 Lipschitz ≤ 1。这是最优雅的全局 Lipschitz 约束方案，但计算 SVD 有一定开销。

### 从最优传输看生成模型

$$W_1(f) = \mathbb{E}_{P_r}[f] - \mathbb{E}_{P_g}[f]$$ 的两项完美对应了最优传输的**经济解释**：

- $$\mathbb{E}_{P_r}[f(x)]$$：在源分布上"买入"质量的总收入
- $$\mathbb{E}_{P_g}[f(x)]$$：在生成分布上"卖出"质量的支出
- 差值的最大可能值就是 Wasserstein 距离

至此，WGAN 与 Monge-Kantorovich 最优传输的联系可扼要总结如下：

| 最优传输概念                  | WGAN 对应                                                    |
| ----------------------------- | ------------------------------------------------------------ |
| Monge 问题                    | 生成器 $$G: z \mapsto x$$（确定性的推前映射）                |
| Kantorovich 问题              | $$W_1(P_r, P_g)$$（Earth Mover's Distance）                  |
| Kantorovich 对偶              | $$W_1 = \sup_{\|f\|_L \leq 1} \mathbb{E}_{P_r}[f] - \mathbb{E}_{P_g}[f]$$ |
| Kantorovich 势 $$\phi, \psi$$ | Critic $$f$$ 和其变换                                        |
| 代价函数 $$c(x,y) = \|x-y\|$$ | 1-Wasserstein 距离的度量                                     |
| 1-Lipschitz 约束              | Weight Clipping / Gradient Penalty / Spectral Norm           |
| 最优传输代价梯度              | Critic 的梯度指导生成器更新方向                              |

> **注**：生成器 $$G(z)$$ 天然是一个 **Monge 映射**——将低维噪声分布推前为数据分布。WGAN 的框架本质上是用 Kantorovich 松弛和其对偶来度量这个映射的质量，并用 critic 的梯度来改善它。