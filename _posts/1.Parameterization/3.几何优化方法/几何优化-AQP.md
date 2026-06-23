---
layout: post
title: "Accelerated Quadratic Proxy (AQP) — 加速二次代理几何优化"
categories: ["Parameterization", "Parameterization-GeometricOptimization"]
mathjax: true
---



> **论文**：Shahar Z. Kovalsky, Meirav Galun, Yaron Lipman. *Accelerated Quadratic Proxy for Geometric Optimization*. SIGGRAPH 2016.

AQP（Accelerated Quadratic Proxy）是一种针对大规模几何优化的一阶加速算法。核心思想：将复杂的几何能量**分解为拉普拉斯二次项 + 非线性余项**，用二次项作预条件子，再结合 Nesterov 加速，对比 L-BFGS 有显著优势。本算法只需用到前两次迭代结果，是纯一阶方法，无需求 Hessian 或 Hessian-vector 乘积。

---

## 建立 Convex Proxy

对逐元素（per-element）能量 $\mathcal{D}(J)$，构造凸二次代理 $\mathcal{P}^{R_f^k}(J)$，满足以下三条性质：

**1. Majorizer（上界）**：

$$
\mathcal{P}^{R_f^k}(J) \geq \mathcal{D}(J), \quad \forall J
$$

**2. Matching gradients（梯度匹配）**：

$$
\nabla_J \mathcal{P}^{R_f^k}(J_f^k) = \nabla_J \mathcal{D}(J_f^k)
$$

**3. Closest minimizer（最近极小点）**：

$$
\arg\min_J \mathcal{P}^{R_f^k}(J) = \mathrm{Proj}_{\mathcal{D}}(J_f^k)
$$

AQP 的全局做法是：将能量分解为 $f(x) = h(x) + g(x)$，其中 $h(x) = \frac{1}{2}x^T H x$ 为以 Laplacian 为 Hessian 的严格凸二次项，$g(x)$ 为光滑非线性余项。每步在 $y_n$ 处最小化代理问题 $\min_p h(y_n + p) + g(y_n) + \nabla g(y_n)^T p$，等价于求解以 $H$ 为左端矩阵的 KKT 系统——$H$ 稀疏且**与迭代无关**，可预分解。

### 核心思想

1. **问题背景**：几何能量优化（保持刚性、最小化形变失真等）常面临病态（ill-conditioning），梯度下降、L-BFGS 收敛缓慢，大规模网格尤其明显。
2. **关键观察**：
   - 病态性主要由 Hessian 中的**拉普拉斯项**主导；
   - 将能量分解为**二次项（拉普拉斯主导）+ 非线性项**，用二次项作**预条件子**，改善条件数。
3. **加速技术**：结合 Nesterov 加速（动量法），动态调整 $\theta$，进一步减少迭代次数。

该方法通过结合预条件与加速技术，为几何优化提供高效、鲁棒、可扩展的解法，尤其适用于计算机图形学中的大规模网格处理。

---

## 1. 几何优化问题的一般化

无论是网格变形、参数化还是其他几何处理任务，本质上都是对某种能量做最小化：

$$
\min_{x \in \mathbb{R}^{dn}} f(x) \quad \text{s.t.} \quad Ax = b
$$

其中 $x = \mathrm{vec}(X)$ 为 $d$ 维顶点位置矩阵 $X \in \mathbb{R}^{d \times n}$ 的列堆叠，$A$ 为位置约束（如固定边界）。

**关键分解**（AQP 的核心结构）：

$$
f(x) = h(x) + g(x), \qquad h(x) = \frac{1}{2} x^T H x
$$

$H = L \otimes I_d$（Kronecker 积：Laplacian 作用于每个坐标），在 $\ker A$ 上严格正定。$g(x)$ 吸收所有非线性部分。

等价地，也可写成可分离形式：

$$
\min_{x} E(x) = \sum_{i=1}^m f_i(R_i x)
$$

其中 $R_i$ 为极稀疏选择/差分矩阵（面梯度、Jacobian 等），$f_i$ 为局部能量。

**核心困难**：$f_i$ 往往非凸；Newton 法每次需 Hessian，大规模不可行；L-BFGS 有改善但仍较慢。

**一阶迭代形式**：算法仅使用前两步的目标值与梯度：

$$
x_n = \mathcal{A}_\theta(x_{n-1}, x_{n-2})
$$

类似 GD（用一步历史）和 L-BFGS（用多步历史），AQP 固定只用两步。

---

## 2. 两个关键观察 (Key Observations)

**观察 1 — 拉普拉斯病态主导**

几何能量的病态性在极大程度上源于能量中的 **Laplacian-like 项**。在局部用 Hessian 取为 Laplacian 的凸二次代理，可显著降低该病态效应；且 Laplacian 是稀疏常数矩阵，每步只需一次回代（back-substitution）。

**观察 2 — 加速与预条件相互支持**

最优加速参数 $\theta$ 应随问题条件数 $\kappa$ 设定（见 Section 4）。但二次代理的预条件效应使 $\kappa(Q)$ 近乎**与网格规模无关**，从而 $\theta$ 可用几乎**普适的固定值**（实验中 $\eta = 100$ 或 $1000$），无需针对每种能量、每种网格精细调参。

两个观察相互支持：预条件使条件数稳定 → 加速参数可通用 → 加速进一步减少迭代。

---

## 3. 能量分解

### 3.1 通用形式

几乎所有几何能量可写为：

$$
f(x) = \sum_j E(T_j)\,|t_j|
$$

其中 $T_j \in \mathbb{R}^{d \times d}$ 为第 $j$ 个元素的微分（Jacobian），$|t_j|$ 为面积/体积权重。

**常见能量及其 AQP 分解**（$H = L \otimes I_d$）：

**ARAP**：

$$
f_{\text{ARAP}}(x) = \frac{1}{2}x^T H x - \sum_j \|T_j\|_* |t_j| + c_0
$$

**Isometric Distortion (ISO)**：

$$
f_{\text{ISO}}(x) = \frac{1}{2}x^T H x + \frac{1}{2}\sum_j \left\|T_j^{-1}\right\|_F^2 |t_j|
$$

**Conformal Distortion (CONF, $d=2$)**：

$$
f_{\text{CONF}}(x) = \frac{1}{2}x^T H x + \frac{1}{2}\sum_j \left(\frac{1}{\sigma_d(T_j)^2} - 1\right)\|T_j\|_F^2 |t_j|
$$

其中二次项来自恒等式：

$$
\frac{1}{2}x^T H x = \frac{1}{2}\sum_j \|T_j\|_F^2\,|t_j| = \frac{1}{2}\sum_{j,k} \sigma_k(T_j)^2\,|t_j|
$$

| 能量 | 局部能量 $E(T)$ | $g(x)$ 中的非线性部分 |
|:---|:---|:---|
| Dirichlet | $\|T\|_F^2$ | 无（纯二次） |
| ARAP | $\frac{1}{2}\|T-R\|_F^2$ | $-\|T\|_*$ 核范数项 |
| Symmetric Dirichlet | $\frac{1}{2}(\|T\|_F^2 + \|T^{-1}\|_F^2)$ | $\frac{1}{2}\|T^{-1}\|_F^2$ |
| MIPS | $\|T\|_F \|T^{-1}\|_F$ | 全部在 $g$ 中 |
| CONF | $\frac{1}{2}(\sigma_1/\sigma_d)^2$ | 共形比相关项 |

**梯度**（链式法则）：

$$
\nabla f(x) = \sum_j J_j^T \,\mathrm{vec}(\nabla E(T_j))\,|t_j|, \qquad \mathrm{vec}(T_j(x)) = J_j x
$$

### 3.2 Kronecker 积结构

$H = L \otimes I_d$ 使代理 Hessian 具有 Kronecker 结构。对三角形网格梯度算子：

$$
H = \sum_T (A_T \otimes I_d)\, G_T^T G_T
$$

其中 $A_T$ 为面积权重，$G_T$ 为面梯度算子。利用 $(A \otimes I)\,\mathrm{vec}(X) = \mathrm{vec}(AX)$ 可加速组装与求解。

Laplacian 在网格尺寸 $\delta$ 上的条件数约为 $\delta^{-2}$；消去 Dirichlet 二次项可大幅改善 $Q$ 的条件数（Figure 3b）。

---

## 4. 算法

### 4.1 主体框架（Algorithm 1）

**输入**：可行初值 $x$，参数 $\eta > 0$

**初始化**：$x_{-1} = x_0 = x$；$\displaystyle\theta = \frac{1 - \sqrt{1/\eta}}{1 + \sqrt{1/\eta}}$

**迭代**（第 $n$ 步）：

**Step 1 — 加速（Acceleration）**：

$$
y_n = (1 + \theta)\,x_{n-1} - \theta\,x_{n-2}
$$

$\theta$ 根据能量条件数自适应（理论上 $\eta = \kappa(Q)$，实践中取固定值）。

**Step 2 — 二次代理最小化（Quadratic Proxy Minimization）**：

$$
p_n = \arg\min_p \; h(y_n + p) + g(y_n) + \nabla g(y_n)^T p \quad \text{s.t.} \quad Ap = 0
$$

等价于 KKT 系统：

$$
\begin{bmatrix} H & A^T \\ A & 0 \end{bmatrix}
\begin{bmatrix} p_n \\ \lambda \end{bmatrix} =
\begin{bmatrix} -\nabla f(y_n) \\ 0 \end{bmatrix}
$$

$H$ 为 Laplacian 矩阵，稀疏且**恒定**——预处理阶段 LU 分解一次，每步仅回代。

**Step 3 — 线搜索（Line Search）**：

$$
x_n = y_n + t\,p_n, \quad 0 < t \leq 1
$$

回溯线搜索保证充分下降。对 ISO/CONF 能量，采用 [Smith & Schaefer 2015] 的 barrier 准则限制步长，避免三角形翻转。

**终止**：$\|\nabla f\| < \varepsilon$ 或能量变化足够小。

**实验对比**（Figure 1）：2D ISO 变形，AQP 约 105 次迭代、0.11 秒收敛；L-BFGS 需约 2300 次迭代（约 ×20 倍加速，极端案例可达 ×200）。

### 4.2 加速步骤的依据

**Lemma 2**：对谱半径 $\rho < 1$ 的迭代矩阵 $M$，递推 $z_n = M[(1+\theta)z_{n-1} - \theta z_{n-2}]$ 中：

- $\theta = 0$：收敛率 $\rho$
- $\theta = \theta_{\text{acc}} = \frac{2}{\rho}(1 - \sqrt{1-\rho}) - 1$：收敛率 $1 - \sqrt{1-\rho}$（最优）

**Lemma 3**：取步长 $t = \lambda_1^{-1}$ 时，$\rho(M) = 1 - \kappa^{-1}$，其中 $\kappa = \kappa(Q)$，$Q = (K^T H K)^{-1}(K^T(H+G)K)$。

代入得 AQP 使用的加速系数：

$$
\theta = \frac{1 - \sqrt{\kappa^{-1}}}{1 + \sqrt{\kappa^{-1}}}
$$

与 Nesterov 加速的系数序列密切相关。**Theorem 1**：取 $\eta = \kappa(Q)$ 时，误差满足 $\|e_n\| \leq c(1 - \sqrt{\kappa^{-1}})^n$。

关键：不是对 $x_k$ 本身做代理（那会退化为普通梯度下降），而是对**外推点** $y_k$ 做代理，利用动量"超前"加速收敛。

### 4.3 KKT 条件（带约束情形）

带线性约束 $Ax = b$ 时，代理最小化变为：

$$
\min_p \; \nabla f(y_n)^T p + \frac{1}{2} p^T H p \quad \text{s.t.} \quad Ap = 0
$$

KKT 系统即式 (7)。左端矩阵可逆（$H$ 在 $\ker A$ 上正定）。

**注意区分于 Newton 法**：Newton 的 KKT 系统左端为 $\nabla^2 f(y_n)$（每步变化、可能不定）；AQP 的 $H$ 是**固定的 Laplacian 代理**（正定），可预分解，每步代价极低。

### 4.4 与 Global-Local / Proximal 的关系

- **无加速版 QP**：对 ARAP 能量退化为 global-local 算法 [Liu et al. 2008]（每步线性求解 = global step，梯度中旋转投影 = local step）。
- **Proximal Gradient**：系统 $(H + \frac{1}{t}I)$ 依赖步长 $t$，无法预分解；AQP 每步只求解一次式 (7)。

---

## 5. 预条件与 Nesterov 加速

### 5.1 条件数与预条件

条件数 $\kappa(H) = \lambda_{\max}/\lambda_{\min}$ 衡量病态程度。几何问题中 $\kappa$ 常极大（小面积三角形导致 $\lambda_{\max} \gg \lambda_{\min}$）。

**预条件效果**：Figure 3(b) 显示 $\kappa(Q)$（AQP）随网格规模增长缓慢，而 $\kappa(Q_{\text{GD}}) = \kappa(K^T(H+G)K)$（标准梯度下降）增长迅速。Laplacian 代理将 $\kappa$ 从 $O(\delta^{-2})$ 量级大幅压低。

### 5.2 消融实验（Figure 3）

| 变体 | 含义 | 性能 |
|:---|:---|:---|
| **AQP** | 完整算法 | 最优 |
| **QP** | $\theta = 0$（无加速） | 明显慢于 AQP |
| **AGD** | $H = I$（无 Laplacian 代理） | 随网格增大急剧变慢 |

加速与二次代理**不可解耦**，二者相互支持。

### 5.3 与标准方法对比（Figure 4）

在 2D/3D 变形（ARAP、ISO）上，AQP 在迭代次数和运行时间上均优于 AGD 和 L-BFGS；迭代次数随网格规模增长缓慢，某些问题近乎常数。

---

## 6. 参考：Proximal（近端）方法的框架

AQP 的二次代理可视为 proximal 梯度法的特例。近端方法一般形式：

$$
x_{k+1} = \mathrm{prox}_{\alpha F}(x_k - \alpha \nabla G(x_k)), \quad f = F + G
$$

**近端算子**：

$$
\mathrm{prox}_{\alpha F}(v) = \arg\min_u \left\{ F(u) + \frac{1}{2\alpha}\|u - v\|^2 \right\}
$$

AQP 中 $F = h$（二次项），$G = g$（非线性项）；$h$ 的 proximal 步即求解式 (7)。与通用 proximal gradient 的区别：$H$ 不含 $1/t$ 项、可预分解、每步只求解一次。

---

## 7. 与其他方法的对比

| 方法 | 收敛率 | 每次迭代代价 | Hessian | 适用规模 |
|:---|:---|:---|:---|:---|
| 梯度下降 (GD) | $O(1/k)$ | 低 | 无 | 大 |
| Nesterov 加速 (AGD) | $O(1/k^2)$ | 低 | 无 | 大 |
| **AQP** | **$O(\sqrt{\kappa^{-1}})$ 局部** | **低-中（预分解 + 回代）** | **Laplacian 代理** | **大** |
| L-BFGS | 超线性 | 中 | 近似 | 中-大 |
| Newton | 二次 | 高（每步变 Hessian） | 精确 | 小-中 |

**AQP vs L-BFGS**：AQP 利用能量 $f = h + g$ 的结构，Laplacian 预条件 + Nesterov 加速，实验上快一个数量级以上。

**AQP vs Newton**：AQP 矩阵恒定正定、可预分解；Newton 每步组装/分解变 Hessian，规模大时不可行。

---

## 8. 总结

AQP 的核心流程：

1. **能量分解**：$f(x) = h(x) + g(x)$，$h(x) = \frac{1}{2}x^T(L \otimes I_d)x$
2. **Nesterov 外推**：$y_n = (1+\theta)x_{n-1} - \theta x_{n-2}$
3. **二次代理求解**：KKT 系统 (7)，$H$ 预分解，每步回代
4. **线搜索**：回溯 +（可选）翻转 barrier
5. **重复**直至收敛

纯一阶、只用前两轮结果、无需求真实 Hessian——迭代次数近乎与网格分辨率无关，适合大规模几何处理管线。

---

## 参考文献

- Kovalsky S. Z., Galun M., Lipman Y. *Accelerated Quadratic Proxy for Geometric Optimization*. SIGGRAPH 2016.
- Nesterov Y. *A method for solving the convex programming problem with convergence rate $O(1/k^2)$*. 1983.
- Liu T., et al. *A local/global approach to mesh parameterization*. CGF 2008. (Global-Local)
- Smith J., Schaefer S. *Bijective parameterization with free boundaries*. SIGGRAPH 2015. (翻转 barrier)
