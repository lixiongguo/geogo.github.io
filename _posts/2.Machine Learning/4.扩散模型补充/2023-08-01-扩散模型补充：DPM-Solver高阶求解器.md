---
layout: post
title: "扩散模型补充：DPM-Solver高阶求解器"
date: 2023-08-01
categories: [DiffusionSupplement]
---
> DPM-Solver（Lu et al. 2022）最明显的优点就是快——比 DDIM 还要快。DDIM 需要 100 步的效果，DPM-Solver 只需约 10 步即可达到。

![image-20250701195952902](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701195952902.png)

---

## 1. 前向扩散过程

扩散概率模型（DPMs）定义了一个前向过程 $\{x_t\}_{t \in [0,T]}$（$T > 0$），对于任意 $t \in [0, T]$，$x_t$ 关于 $x_0$ 的条件分布满足：

![image-20250701201155950](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701201155950.png)

$$
q_{0t}(x_t | x_0) = \mathcal{N}(x_t | \alpha_t x_0, \sigma_t^2 I) \tag{2.1}
$$

以下 SDE 拥有与 (2.1) 相同的转移分布，对任意 $t \in [0, T]$：

![image-20250701201508237](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701201508237.png)

![image-20250701200631387](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701200631387.png)

$$
dx_t = f(t) x_t dt + g(t) dw_t, \quad x_0 \sim q_0(x_0)
$$

![image-20250701201541019](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701201541019.png)

其中 $w_t \in \mathbb{R}^d$ 为标准维纳过程，且：

$$
f(t) = \frac{d\log\alpha_t}{dt}, \quad g(t)^2 = \frac{d\sigma_t^2}{dt} - 2\frac{d\log\alpha_t}{dt}\sigma_t^2 \tag{2.3}
$$

> 详见 [EDM：扩散模型设计空间的统一框架]({% post_url 2.Machine Learning/4.扩散模型补充/2023-07-01-扩散模型补充：EDM统一框架 %}) 通用加噪公式。

---

## 2. 逆向过程

### 2.1 反向 SDE

上述 SDE 具有如下逆向过程（reverse-time SDE）：

![image-20250701201806780](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701201806780.png)

$$
dx_t = [f(t)x_t - g(t)^2 \nabla_x \log q_t(x_t)] dt + g(t) d\bar{w}_t, \quad x_T \sim q_T(x_T) \tag{2.4}
$$

![image-20250701201833515](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701201833515.png)

其中 $\bar{w}_t$ 为反向时间的标准维纳过程。

### 2.2 噪声预测网络

一般用神经网络 $\epsilon_\theta(x_t, t)$ 来逼近缩放的得分函数：

$$
\epsilon_\theta(x_t, t) \approx -\sigma_t \nabla_x \log q_t(x_t)
$$

其训练目标为：

![image-20250701202218396](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701202218396.png)

$$
\mathcal{L}(\theta) = \int_0^T \lambda(t) \, \mathbb{E}_{q_0(x_0)} \mathbb{E}_{q(\epsilon)} \left[\|\epsilon_\theta(x_t, t) - \epsilon\|^2\right] dt + C
$$

![image-20250701202231679](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701202231679.png)

其中 $\lambda(t)$ 为权重函数，$\epsilon \sim \mathcal{N}(0, I)$，$x_t = \alpha_t x_0 + \sigma_t \epsilon$，$C$ 为与 $\theta$ 无关的常数。

### 2.3 带噪声预测的逆向 SDE

代入噪声预测后，逆向 SDE 变为：

![image-20250701202505703](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701202505703.png)

$$
dx_t = \left[f(t)x_t + \frac{g(t)^2}{\sigma_t}\epsilon_\theta(x_t, t)\right] dt + g(t) d\bar{w}_t, \quad x_T \sim \mathcal{N}(0, \tilde{\sigma}^2 I) \tag{2.5}
$$

---

## 3. 概率流 ODE

### 3.1 从 SDE 到 ODE

当离散化 SDE 时，步长受维纳过程随机性限制——大步长（少量步数）常导致不收敛，尤其在高维空间。为加速采样，可考虑关联的概率流 ODE（PF-ODE）：

![image-20250701202619215](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701202619215.png)

Song 等人证明如下概率流 ODE 与 (2.4) 具有一致的边缘分布：

![image-20250701202805329](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701202805329.png)

$$
\frac{dx_t}{dt} = f(t)x_t - \frac{1}{2}g(t)^2 \nabla_x \log q_t(x_t), \quad x_T \sim q_T(x_T) \tag{2.6}
$$

### 3.2 噪声预测形式的 ODE

进一步代入噪声预测网络：

![image-20250701203003063](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701203003063.png)

$$
\frac{dx_t}{dt} = h_\theta(x_t, t) = f(t)x_t + \frac{g(t)^2}{2\sigma_t}\epsilon_\theta(x_t, t), \quad x_T \sim \mathcal{N}(0, \tilde{\sigma}^2 I) \tag{2.7}
$$

ODE 可以采用更大的步长且有更高效的采样器：

![image-20250701203113347](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701203113347.png)

> 通过求解从 $T$ 到 $0$ 的 ODE 即可采样。Song 等人使用 RK45 ODE 求解器，约需 60 次函数评估达到可比质量。

---

## 4. 半线性结构与解析形式

### 4.1 半线性分解

本文的核心 Insight：将 (2.7) 式分成两个部分——一个线性部分，一个非线性部分，统称**半线性 ODE**（semi-linear ODE）。

![image-20250701203652430](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701203652430.png)

> $f(t)x_t$ 关于 $x_t$ 是线性的，而 $\frac{g(t)^2}{2\sigma_t}\epsilon_\theta(x_t, t)$ 由于神经网络 $\epsilon_\theta$ 一般是非线性的。以往的黑箱 ODE 求解器忽视了这种半线性结构，把整个 $h_\theta$ 当作输入，引入了不必要的离散化误差。

### 4.2 引入 log-SNR

定义 $\lambda_t = \log(\alpha_t / \sigma_t)$（log-SNR 的一半），则 $\lambda_t$ 是 $t$ 的严格递减函数。利用 $g(t)$ 和 $\lambda_t$ 的关系，可重写 ODE：

![image-20250701203816371](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701203816371.png)

![image-20250701204043817](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701204043817.png)

结合 $f(t) = d\log\alpha_t / dt$，半线性 ODE 可化为：

![image-20250701204140248](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701204140248.png)

$$
x_t = \frac{\alpha_t}{\alpha_s}x_s - \alpha_t \int_{\lambda_s}^{\lambda_t} e^{-\lambda} \epsilon_\theta(x_\lambda, \lambda) d\lambda \tag{3.3}
$$

### 4.3 精确解（命题 3.1）

![image-20250701204236363](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701204236363.png)

> **命题 3.1（扩散 ODE 的精确解）**：给定初始值 $x_s$（$s > 0$），扩散 ODE 在时刻 $t \in [0, s]$ 的解 $x_t$ 为：

$$
x_t = \frac{\alpha_t}{\alpha_s}x_s - \alpha_t \int_{\lambda_s}^{\lambda_t} e^{-\lambda} \epsilon_\theta(x_\lambda, \lambda) d\lambda \tag{3.4}
$$

---

## 5. DPM-Solver 的数值方法

### 5.1 Taylor 展开逼近

要计算 $\tilde{x}_{t_{i-1}}$ 作为 $x_{t_i}$ 的近似，需逼近 $\epsilon_\theta$ 从 $\lambda_{t_{i-1}}$ 到 $\lambda_{t_i}$ 的指数加权积分。

![image-20250701204435443](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701204435443.png)

$$
\tilde{x}_{t_{i-1}} = \frac{\alpha_{t_{i-1}}}{\alpha_{t_i}} x_{t_i} - \alpha_{t_{i-1}} \int_{\lambda_{t_i}}^{\lambda_{t_{i-1}}} e^{-\lambda} \epsilon_\theta(x_\lambda, \lambda) d\lambda \tag{3.5}
$$

记 $h_i = \lambda_{t_{i-1}} - \lambda_{t_i}$，对 $\epsilon_\theta(x_\lambda, \lambda)$ 在 $\lambda_{t_i}$ 处做 $(k-1)$ 阶 Taylor 展开：

![image-20250701204637390](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701204637390.png)

$$
\epsilon_\theta(x_\lambda, \lambda) = \sum_{n=0}^{k-1} \frac{(\lambda - \lambda_{t_i})^n}{n!} \epsilon_\theta^{(n)}(x_{\lambda_{t_i}}, \lambda_{t_i}) + \mathcal{O}((\lambda - \lambda_{t_i})^k)
$$

代入积分得到 DPM-Solver-k 的更新公式：

![image-20250701204513319](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701204513319.png)

### 5.2 DPM-Solver-1

> **DPM-Solver-1**（$k=1$）：给定初始值 $x_T$ 和 $M+1$ 个时间步 $\{t_i\}_{i=0}^M$（从 $t_0 = T$ 递减到 $t_M = 0$），以 $\tilde{x}_{t_0} = x_T$ 开始，序列 $\{\tilde{x}_{t_i}\}_{i=1}^M$ 按以下迭代计算：

$$
\tilde{x}_{t_i} = \frac{\alpha_{t_i}}{\alpha_{t_{i-1}}} \tilde{x}_{t_{i-1}} - \sigma_{t_i}(e^{h_i} - 1) \epsilon_\theta(\tilde{x}_{t_{i-1}}, t_{i-1}), \quad h_i = \lambda_{t_{i-1}} - \lambda_{t_i} \tag{3.7}
$$

### 5.3 DPM-Solver-2

![image-20250701204523100](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701204523100.png)

**Algorithm 1: DPM-Solver-2**

1. $\tilde{x}_{t_0} = x_T$
2. **for** $i = 1$ **to** $M$ **do**
3. $\quad s_i = t_{i-1} \cdot r + t_i \cdot (1-r)$（$r$ 为某中点参数）
4. $\quad u_i = \frac{\alpha_{s_i}}{\alpha_{t_{i-1}}} \tilde{x}_{t_{i-1}} - \sigma_{s_i}(e^{h_i/2} - 1) \epsilon_\theta(\tilde{x}_{t_{i-1}}, t_{i-1})$
5. $\quad \tilde{x}_{t_i} = \frac{\alpha_{t_i}}{\alpha_{t_{i-1}}} \tilde{x}_{t_{i-1}} - \sigma_{t_i}(e^{h_i} - 1) \epsilon_\theta(u_i, s_i)$
6. **end for**
7. **return** $\tilde{x}_{t_M}$

### 5.4 DPM-Solver 中心定理

![image-20250701210313219](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701210313219.png)

> **定理 3.2（DPM-Solver-k 为 k 阶求解器）**：假设 $\epsilon_\theta(x_t, t)$ 满足正则性条件，则对 $k = 1, 2, 3$，DPM-Solver-k 是扩散 ODE 的 k 阶求解器。即对 DPM-Solver-k 计算的序列 $\{\tilde{x}_{t_i}\}_{i=0}^M$，在 $t=0$ 处的逼近误差满足：
>
> $$\tilde{x}_{t_M} - x_0 = \mathcal{O}(h_{\max}^k), \quad h_{\max} = \max_{1 \le i \le M} (\lambda_{t_{i-1}} - \lambda_{t_i})$$

---

## 6. 步长选择

![image-20250701210341426](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701210341426.png)

提出两种时间步长策略：

1. **均匀 $\lambda$ 分割**：将 $[\lambda_T, \lambda_0]$ 均匀分割，即 $\lambda_{t_i} = \lambda_T + \frac{i}{M}(\lambda_0 - \lambda_T)$。注意这与以往按 $t$ 均匀分割不同。实验表明 DPM-Solver 配合均匀 $\lambda$ 步长即可在极少量步数下生成优质样本。
2. **自适应步长**：组合不同阶的 DPM-Solver，动态调整步长。

---

## 7. DDIM 是 DPM-Solver-1 的特例

![image-20250701210452860](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250701210452860.png)

DDIM 的一步更新为（从 $t_{i-1}$ 到 $t_i$）：

$$
x_{t_i} = \frac{\alpha_{t_i}}{\alpha_{t_{i-1}}} x_{t_{i-1}} - \alpha_{t_i}\left(\frac{\sigma_{t_i}}{\alpha_{t_i}} - \frac{\sigma_{t_{i-1}}}{\alpha_{t_{i-1}}}\right) \epsilon_\theta(x_{t_{i-1}}, t_{i-1}) \tag{4.1}
$$

由 $\lambda_t = \log(\alpha_t/\sigma_t)$ 有 $\sigma_t/\alpha_t = e^{-\lambda_t}$，代入 $h_i = \lambda_{t_{i-1}} - \lambda_{t_i}$ 后，(4.1) 恰好退化为一阶 DPM-Solver-1 的 (3.7) 式。

> **关键洞察**：虽然 DDIM 和 DPM-Solver 从完全不同的视角出发，但 DPM-Solver 的半线性 ODE 表述揭示了 DDIM 充分利用了扩散 ODE 的半线性结构，这是 DDIM 优于传统 Euler 方法的原因。DPM-Solver 进一步将这一思想推广到高阶求解器和收敛阶分析。

---

## 总结

| 方法 | 阶数 | 核心思想 | 优势 |
|:---|:---|:---|:---|
| **DDIM** | 1 阶 | 隐式确定性采样 | 加速采样，保持一致 marginal |
| **DPM-Solver-1** | 1 阶 | 半线性 ODE + 指数积分 | 等价于 DDIM，但揭示了其数学本质 |
| **DPM-Solver-2** | 2 阶 | 中点法 + 指数积分 | 约 20 步达 DDIM 100 步效果 |
| **DPM-Solver-3** | 3 阶 | 高阶 Taylor + 指数积分 | 约 10 步即可，极致加速 |
