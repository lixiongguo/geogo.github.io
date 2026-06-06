---
layout: post
title: "Monge问题与Kantorivch问题"
category: Parameterization
categories: ["Parameterization", "Parameterization-OptimalTransport"]
---

最优传输问题源于法国数学家 **Gaspard Monge** 于 1781 年提出的"**堆土问题**"：如何将一堆土以最小总代价搬运到指定位置，形成目标土堆。其核心是寻找一个将源分布映射到目标分布的最优方案。20 世纪 40 年代，**Kantorovich** 将问题松弛为联合分布上的线性规划，奠定了最优传输的现代数学基础，并因此获得 1975 年诺贝尔经济学奖。如今，最优传输广泛应用于计算机图形学、图像处理、机器学习、经济均衡分析等领域。

## Monge问题与Kantorivch问题

**Monge 问题（原始形式）**：给定两个概率测度 $$\mu$$（定义在 $$X$$ 上）和 $$\nu$$（定义在 $$Y$$ 上），以及代价函数 $$c(x,y)$$（表示将单位质量从 $$x$$ 运到 $$y$$ 所需的代价），求映射 $$T: X \to Y$$ 使得：
$$
 \min_{T} \int_X c(x, T(x)) \, d\mu(x) \quad \text{s.t.} \quad T_{\#}\mu = \nu
$$

其中 $$T_{\#}\mu = \nu$$ 是**推前（push-forward）条件**，即对任意可测集 $$B \subseteq Y$$：
$$
 \nu(B) = \mu(T^{-1}(B))
$$

Monge 问题的本质困难在于：$$T$$ 必须是**映射**（每个 $$x$$ 只能映射到唯一一个 $$y$$），这意味着质量不允许分裂。这导致问题**非凸且可能无解**。

 **Kantorovich 问题**：将映射要求放宽为**传输计划（transport plan）** $$\pi$$——一个定义在乘积空间 $$X \times Y$$ 上的联合概率测度。$$\pi(x,y)$$ 表示从 $$x$$ 运往 $$y$$ 的质量份额：

$$
 \min_{\pi \in \Pi(\mu,\nu)} \int_{X \times Y} c(x,y) \, d\pi(x,y)
$$

 其中 $$\Pi(\mu,\nu)$$ 是所有边缘分布分别为 $$\mu$$ 和 $$\nu$$ 的联合概率测度的集合：
$$
\Pi(\mu,\nu) = \left\{ \pi \mid \pi_x = \mu,\; \pi_y = \nu \right\}
$$

### Kantorovich 对偶(DP)

线性规划自然引出对偶问题。对偶变量的经济解释为"价格函数"——$$\phi(x)$$ 是在 $$x$$ 处买入的价格，$$\psi(y)$$ 是在 $$y$$ 处卖出的价格。无套利条件要求 $$\phi(x) + \psi(y) \leq c(x,y)$$（否则可在 $$x$$ 买入、在 $$y$$ 卖出套利）。

 **对偶问题（Kantorovich Duality）**：

$$
\min_{\pi \in \Pi(\mu,\nu)} \int c \, d\pi \;=\; \sup_{(\phi,\psi)} \left\{ \int_X \phi \, d\mu + \int_Y \psi \, d\nu \;\mid\; \phi(x) + \psi(y) \leq c(x,y) \right\}
$$

其中满足不等式约束的函数对 $$(\phi,\psi)$$ 称为 （Kantorovich Potential）**,$\psi$ 可通过 $$c$$-变换由 $$\phi$$ 确定。

**Kantorovich 势**也称为"**影子价格**"：在最优传输的经济解释中，$$\phi(x)$$ 代表产地 $$x$$ 的资源"出厂价"，$$\psi(y)$$ 代表消费地 $$y$$ 的"收货价"。约束 $$\phi(x) + \psi(y) \leq c(x,y)$$ 意味着买入价与卖出价之差不高于运输成本，若差价高于运费，商人可倒卖牟利。当等号成立时，价格场 $$(\phi,\psi)$$ 达到均衡，此时对偶目标 $$\int \phi d\mu + \int \psi d\nu$$ 达到最大的社会总剩余，而最优传输计划正是由这些均衡价格导出的资源配置。

## $$c$$-变换与Legredre变换

 **定义（$$c$$-变换）**：给定函数 $$\psi: Y \to \mathbb{R}$$，其 $$c$$-变换定义为：

$$
 \psi^c(x) = \inf_{y \in Y} \left[ c(x,y) - \psi(y) \right]
$$

 类似地，$$\phi$$ 的 $$c$$-变换为：
$$
\phi^c(y) = \inf_{x \in X} \left[ c(x,y) - \phi(x) \right]
$$

对固定的 $x$ $$y \mapsto c(x,y) - \psi(y)$$ 的下确界

**$$c$$-凹性（$$c$$-concavity）**：若 $$c$$ 连续，则 $$\psi^c$$ 是 **$$c$$-凹函数**——即 $$-\psi^c$$ 是 $$c$$-凸函数。直观地说，$$c$$-变换把任意函数"投影"到满足对偶结构的 $$c$$-凹函数类中。

原始对偶需要在所有函数对 $$(\phi, \psi)$$ 中搜索。利用 $$c$$-变换，**问题可化为仅含一个势函数**：

$$
\min_{\pi \in \Pi(\mu,\nu)} \int c \, d\pi
= \sup_{\psi: Y \to \mathbb{R}} \left\{ \int_X \psi^c \, d\mu + \int_Y \psi \, d\nu \right\}
$$

等价地，也可只用 $$\phi: X \to \mathbb{R}$$ 表述：

$$
= \sup_{\phi: X \to \mathbb{R}} \left\{ \int_X \phi \, d\mu + \int_Y \phi^c \, d\nu \right\}.
$$

**证明思路**：给定任意可行对 $$(\phi, \psi)$$ 满足 $$\phi(x)+\psi(y)\leq c(x,y)$$，令 $$\tilde\psi = \psi$$、$$\tilde\phi = \phi^c$$，则 $$(\tilde\phi, \tilde\psi)$$ 仍可行且目标值不变或更大（因为 $$\phi \leq \phi^{cc}$$）。因此最优解总可取为 **$$c$$-共轭对** $$(\phi, \phi^c)$$ 或 $$(\psi^c, \psi)$$。

在最优解处，Kantorovich 势满足 **$$c$$-共轭关系** $$\phi = \psi^c$$、$$\psi = \phi^c$$（差一个常数不影响目标值）。

#### 二次代价下的 $$c$$-变换

当代价 $$c(x,y) = \frac{1}{2}\|x-y\|^2 = \frac{1}{2}\|x\|^2 + \frac{1}{2}\|y\|^2 - \langle x, y \rangle$$ 时，

$$
\psi^c(x) = \frac{1}{2}\|x\|^2 + \inf_{y \in Y} \left\{ \frac{1}{2}\|y\|^2 - \psi(y) - \langle x, y \rangle \right\}.
$$

若令凸函数 $$\bar\psi(y) = \frac{1}{2}\|y\|^2 - \psi(y)$$，则

$$
\psi^c(x) = \frac{1}{2}\|x\|^2 - \bar\psi^*(x),
$$

其中 $$\bar\psi^*$$ 是经典的 Legendre-Fenchel 共轭。

#### 内积代价与 Legendre 变换

当代价函数为内积 $$c(x,y) = \langle x, y \rangle$$ 时，$$c$$-变换退化为 Legendre 变换（凸共轭）的负号版本：

$$
\psi^c(x) = \inf_{y} \left[ \langle x, y \rangle - \psi(y) \right], \qquad 
\phi^*(y) = \sup_{x} \left[ \langle x, y \rangle - \phi(x) \right],
$$

即 $$\phi^* = (-\phi)^c$$。此时 $$c$$-上微分还原为次微分 $$\partial^c \phi(y) = \partial \phi^*(y)$$，约束 $$\phi(x) + \psi(y) \leq \langle x, y \rangle$$ 等价于 Fenchel 不等式 $$\psi(y) \leq \phi^*(y)$$，最优解处 $$\psi = \phi^*$$。

二次代价可通过展开化为内积形式：
$$
c(x,y) = \frac{1}{2}\|x-y\|^2 = \frac{1}{2}\|x\|^2 - \langle x, y \rangle + \frac{1}{2}\|y\|^2.
$$



## $c$-上微分（$c$-superdifferential）

$$c$$-变换刻画了"价格"之间的对偶关系；**$$c$$-上微分**则刻画在最优解处"谁与谁配对运输"——它是次微分（subdifferential）概念在一般代价下的推广。

给定函数 $$\psi: Y \to \mathbb{R}$$（Kantorovich 对偶中 $$Y$$ 侧的势），点 $$x \in X$$ 处的 **$$c$$-上微分** 定义为：

$$
\partial^c \psi(x) := \left\{ y \in Y \;\middle|\; \psi^c(x) + \psi(y) = c(x, y) \right\}.
$$

等价地，$$y \in \partial^c \psi(x)$$ 当且仅当 $$y$$ 达到 $$c$$-变换中的下确界：

$$
\psi^c(x) = c(x, y) - \psi(y) = \inf_{y' \in Y} \left[ c(x, y') - \psi(y') \right].
$$

对称地，对 $$c$$-凹函数 $\psi: X \to \mathbb{R}$，定义

$$
\partial^c \psi(y) := \left\{ x \in X \;\middle|\; \psi(x) + \psi^c(y) = c(x, y) \right\}.
$$

$$\partial^c \psi(x)$$ 是使不等式 $$\psi^c(x) + \psi(y) \leq c(x,y)$$ **取等号**的所有目标点 $$y$$。

#### 与最优传输映射的关系

若 Kantorovich 势 $$\psi$$ 达到对偶问题的上确界，且 Monge 映射 $$T$$ 存在，则对 $$\mu$$-几乎处处的 $$x$$ 有

$$
T(x) \in \partial^c \psi(x).
$$

在 **twist 条件**（$$y \mapsto \nabla_x c(x,y)$$ 对每个 $$x$$ 单射）下，$$\partial^c \psi(x)$$ 至多含一个点，从而 $$T(x) = \nabla_x c(x, y)\big|_{y = T(x)}$$ 唯一确定——这正是扭曲条件一节中公式

$$
T(x) = \arg\min_y \left[ c(x,y) - \psi(y) \right]
$$

的集合版本。

#### 二次代价：$$c$$-上微分 = 凸函数次微分

当 $$c(x,y) = \frac{1}{2}\|x-y\|^2$$ 且 $$\phi = \psi^c$$ 为 Brenier 凸势时，条件 $$\psi^c(x) + \psi(y) = c(x,y)$$ 化为

$$
\phi(x) + \psi(y) = \frac{1}{2}\|x\|^2 + \frac{1}{2}\|y\|^2 - \langle x, y \rangle.
$$

令 $$\bar\phi(x) = \phi(x) - \frac{1}{2}\|x\|^2$$、$$\bar\psi(y) = \frac{1}{2}\|y\|^2 - \psi(y)$$（均为凸函数），则取等号等价于

$$
\bar\phi(x) + \bar\psi(y) = \langle x, y \rangle,
$$

即 $$y \in \partial \bar\phi(x)$$（$$\bar\phi$$ 的次微分）且 $$x \in \partial \bar\psi(y)$$。因此

$$
\partial^c \psi(x) = \partial \bar\phi(x),  T(x) = \nabla \bar\phi(x) = \nabla \phi(x)
$$

在 $$\bar\phi$$ 可微的点处退化为梯度映射。不可微点处，次微分是多值的，对应质量分裂的 Kantorovich 计划。



#### 半离散情形：Laguerre 单元

在半离散 OT 中，目标测度 $$\nu = \sum_j \lambda_j \delta_{y_j}$$，势函数 $$\psi(y_j) = \psi_j$$ 为有限维权重。此时

$$
\psi^c(x) = \min_j \left[ c(x, y_j) - \psi_j \right],
$$

而

$$
\partial^c \psi(x) = \arg\min_j \left[ c(x, y_j) - \psi_j \right]
$$

给出每个 $$x$$ 应被送往的目标点。对二次代价 $$c(x,y) = \frac{1}{2}\|x-y\|^2$$，使下确界取到的 $$j$$ 构成 **Laguerre / Power 单元**：

$$
L_j(\psi) = \left\{ x \;\middle|\; \|x - y_j\|^2 - \psi_j \leq \|x - y_k\|^2 - \psi_k,\; \forall k \right\}.
$$

这正是半离散 OT 把连续域分割为加权 Voronoi 单元的几何来源——每个 cell 内所有点共享同一个 $$c$$-上微分（同一目标原子 $$y_j$$）。

#### $$W_1$$ 代价下的特化

当代价 $$c(x,y) = \|x - y\|$$ 时，$$c$$-变换给出

$$
\psi^c(x) = \inf_{y \in Y} \left[ \|x - y\| - \psi(y) \right].
$$

此时 $$\psi^c$$ 自动 **1-Lipschitz**：对任意 $$x, x'$$，

$$
|\psi^c(x) - \psi^c(x')| \leq \|x - x'\|
$$

（三角不等式直接推出）。Kantorovich-Rubinstein 对偶正是把一般对偶化简为单个 1-Lipschitz 函数 $$f = -\psi^c$$ 的情形——这也是 WGAN 中 critic 必须满足 Lipschitz 约束的来源（详见后文 WGAN 一节）。



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

| 度量 | 不相交分布 | 梯度性质 |
|:---|:---|:---|
| **KL 散度** | $$\infty$$（无意义） | 梯度爆炸 |
| **JS 散度** | $$\log 2$$（常数） | 梯度为零 |
| **Wasserstein** | 正比于空间距离 | 平滑有梯度 |

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

| 维度 | 原始 GAN | WGAN |
|:---|:---|:---|
| **判别器输出** | 概率（sigmoid） | 标量分数（无激活） |
| **分布度量** | JS 散度 | Wasserstein-1 距离 |
| **Lipschitz 约束** | 无 | 权重裁剪 $$[-c, c]$$ |
| **训练稳定性** | 差，易模式坍塌 | 显著改善 |
| **Loss 曲线** | 无意义 | 可反映生成质量 |
| **优化器** | Adam | RMSProp（推荐） |

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

| 最优传输概念 | WGAN 对应 |
|------------|----------|
| Monge 问题 | 生成器 $$G: z \mapsto x$$（确定性的推前映射） |
| Kantorovich 问题 | $$W_1(P_r, P_g)$$（Earth Mover's Distance） |
| Kantorovich 对偶 | $$W_1 = \sup_{\|f\|_L \leq 1} \mathbb{E}_{P_r}[f] - \mathbb{E}_{P_g}[f]$$ |
| Kantorovich 势 $$\phi, \psi$$ | Critic $$f$$ 和其变换 |
| 代价函数 $$c(x,y) = \|x-y\|$$ | 1-Wasserstein 距离的度量 |
| 1-Lipschitz 约束 | Weight Clipping / Gradient Penalty / Spectral Norm |
| 最优传输代价梯度 | Critic 的梯度指导生成器更新方向 |

> **注**：生成器 $$G(z)$$ 天然是一个 **Monge 映射**——将低维噪声分布推前为数据分布。WGAN 的框架本质上是用 Kantorovich 松弛和其对偶来度量这个映射的质量，并用 critic 的梯度来改善它。