---
layout: post
title: "有界失真映射：从理论到算法（完整版）"
categories: ["Parameterization", "Parameterization-GeometricOptimization"]
---

### Wirtinger 导数

Wirtinger 导数本质上是一套处理复变函数微分的“代数技巧”。它把复变量 z*z* 和 zˉ*z*ˉ 当作两个**形式上独立**的变量来处理，从而将复分析中的微分运算转化为类似多元实微积分的计算。

将平面点表为复数 $z = x + iy$，平面映射表为 $f(z) = u(x,y) + i v(x,y)$。

把 $$x,y$$ 方向的偏导组合：

$$
f_z \equiv \frac{\partial f}{\partial z} = \frac{1}{2}(f_x - i f_y),
\qquad
f_{\bar z} \equiv \frac{\partial f}{\partial \bar z} = \frac{1}{2}(f_x + i f_y)
$$

若 $$f_{\bar z} = 0$$，则映射简化为 $$df = f_z dz$$（复数乘法），局部无穷小圆仍映射为圆——即**共形映射**（保角），这比CR方程要更加简洁。

若 $$f_{\bar z} \neq 0$$，局部无穷小圆变为椭圆，其长短轴（即 Jacobi 矩阵的奇异值）为：
$$
\sigma_1(z) = |f_z(z)| + |f_{\bar z}(z)|, \qquad
\sigma_2(z) = \big| |f_z(z)| - |f_{\bar z}(z)| \big|
$$


因此 $$\det J_f > 0$$ 等价于 $$|f_z| > |f_{\bar z}|$$（局部保向，无翻转）。


| 导数           | 几何含义                                   | 简记             |
| -------------- | ------------------------------------------ | ---------------- |
| $$f_z$$        | **共形部分**：复数乘法 = 旋转 + 一致缩放   | 描述局部相似变换 |
| $$f_{\bar z}$$ | **反共形部分**：偏离共形的拉伸、剪切、翻转 | 描述局部畸变程度 |


**局部共形扭曲**（Beltrami 系数 / Jacobian 条件数）：

$$
K_f(z) = \frac{\sigma_1(z)}{\sigma_2(z)} = \frac{|f_z(z)| + |f_{\bar z}(z)|}{|f_z(z)| - |f_{\bar z}(z)|}
$$

有界扭曲条件 $$K_f(z) \le K$$（$$K \ge 1$$）等价于：

$$
|f_{\bar z}(z)| \le \kappa \cdot |f_z(z)|, \qquad
\kappa = \frac{K-1}{K+1} \in [0,1)
$$

| 边界情况         | $$\kappa$$       | 含义                                       |
| ---------------- | ---------------- | ------------------------------------------ |
| $$K = 1$$        | $$\kappa = 0$$   | 共形映射（$$f_{\bar z}=0$$）               |
| $$K = 3$$        | $$\kappa = 0.5$$ | 最大拉伸 3× 最小拉伸                       |
| $$K \to \infty$$ | $$\kappa \to 1$$ | 允许翻转（$$|f_z| \approx |f_{\bar z}|$$） |

**两个核心约束：**
$$
\begin{aligned}
|f_z(z)| > |f_{\bar z}(z)| \quad &\Longleftrightarrow \; \det J_f > 0 \quad \text{(局部无翻转，保向)} \\
|f_{\bar z}(z)| \le \kappa \cdot |f_z(z)| \quad &\Longleftrightarrow \; K_f(z) \le K \quad \text{(有界扭曲)}
\end{aligned}
$$

---



### Cauchy 重心坐标与调和映射的有限维表示

平面调和映射的**标准复分解**：任意平面调和函数可写为**两个全纯函数的和与共轭差**：

$$
f(z) = \Phi(z) + \overline{\Psi(z)}
$$

其中 $$\Phi = h, \Psi = g$$ 均为全纯函数（此即 $$f(z) = h(z) + \overline{g(z)}$$，等价于调和条件 $$\Delta f = 0$$）。

**核心思想**：用有限基函数展开 $$\Phi, \Psi$$，使调和性被"硬编码"进基函数空间——无论系数如何选择，$$f$$ 自动是调和映射。

使用 **Cauchy 复重心坐标** ：

<img src="/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260721203255144.png" alt="image-20260721203255144" style="zoom:50%;" />

给定边界多边形 cage 顶点 $$P = \{z_1, z_2, \dots, z_n\}$$（逆时针排列），全纯函数 $$\Phi, \Psi$$ 表示为：
$$
\Phi(z) = \sum_{j=1}^{n} C_j(z) \, \phi_j, \qquad
\Psi(z) = \sum_{j=1}^{n} C_j(z) \, \psi_j
$$

其中 $$C_j(z)$$ 定义为 Cauchy 积分公式应用于 piecewise linear 基函数 $$\lambda_j$$：

$$
C_j(z) = \frac{1}{2\pi i} \int_{\partial\Omega} \frac{\lambda_j(\zeta)}{\zeta - z} \, d\zeta
$$

这里 $$\lambda_j$$ 是 cage 顶点 $$z_j$$ 处的 piecewise linear 帽函数（在 $$z_j$$ 为 1，其余顶点为 0，边界上线性）。

**闭式表达** (BDHM Appendix A)：设 $$z_j$$ 的前后边分别为 $$e_j^- = [z_{j-1}, z_j]$$ 和 $$e_j^+ = [z_j, z_{j+1}]$$（取模 $$n$$），则：

$$
C_j(z) = \frac{1}{2\pi i}\left[
\frac{z_{j+1} - z}{z_{j+1} - z_j} \ln\frac{z_{j+1} - z}{z_j - z}
- \frac{z - z_{j-1}}{z_j - z_{j-1}} \ln\frac{z - z_{j-1}}{z_j - z}
\right]
$$

其一阶和二阶导数分别为：

$$
C_j'(z) = \frac{1}{2\pi i}\left[
\frac{1}{z_{j+1} - z_j} \ln\frac{z_{j+1} - z}{z_j - z}
+ \frac{1}{z_j - z_{j-1}} \ln\frac{z - z_{j-1}}{z_j - z}
\right]
$$

$$
C_j''(z) = \frac{1}{2\pi i}\left[
\frac{1}{(z_{j+1} - z_j)(z_{j+1} - z)} - \frac{1}{(z_{j+1} - z_j)(z_j - z)}
+ \frac{1}{(z_j - z_{j-1})(z - z_{j-1})} - \frac{1}{(z_j - z_{j-1})(z_j - z)}
\right]
$$



## 有界失真映射

**定义 (有界失真映射).** 连续可微的平面映射 $$f : \Omega \subset \mathbb{C} \to \mathbb{C}$$ 称为 $$(k,\sigma_1,\sigma_2)$$-有界失真映射，若对 $$\forall z \in \Omega$$：

$$
0 \le k(z) \le k < 1, \qquad
\sigma_1(z) \le \sigma_1 < \infty, \qquad
0 < \sigma_2 \le \sigma_2(z)
$$

其中 $$k(z) = |f_{\bar z}|/|f_z|$$ 是伸缩商 (dilatation)，$$\sigma_1(z),\sigma_2(z)$$ 是 Jacobi 矩阵的奇异值。$$k,\sigma_1,\sigma_2$$ 为预设的全局常数。

**观察1.** $$(k,\sigma_1,\sigma_2)$$-有界失真映射必然是局部单射且保向的。

> 证明：$$\sigma_2(z) > 0$$ 蕴含 $$\det J_f = \sigma_1\sigma_2 > 0$$，即 Jacobian 处处非零且保向。又 $$\det J_f = |f_z|^2 - |f_{\bar z}|^2 > 0$$，得到 $$|f_z| > |f_{\bar z}|$$。

| 条件                         | 控制         | 失效后果             |
| ---------------------------- | ------------ | -------------------- |
| $$k(z) \le k$$               | 共形扭曲上限 | 局部角度畸变过大     |
| $$\sigma_1(z) \le \sigma_1$$ | 最大拉伸上限 | 局部面积过度放大     |
| $$\sigma_2 \le \sigma_2(z)$$ | 最小拉伸下限 | 局部塌缩退化（折叠） |

![image-20260721204130135](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260721204130135.png)



上述定义要求检查域中**每一个点**。以下定理将其简化为**仅需检查边界**：

**定理(BDHM).** 定义在单连通域 $$\Omega$$ 上的复值调和映射 $$f$$ 是 $$(k,\sigma_1,\sigma_2)$$-有界失真的充要条件为：
$$
\begin{aligned}
\oint_{\partial\Omega} \frac{f_z''(z)}{f_z(z)} \, dz &= 0  \\
0 \le k(w) \le k < 1, \quad &\forall w \in \partial\Omega  \\
\sigma_1(w) \le \sigma_1 < \infty, \quad &\forall w \in \partial\Omega  \\
0 < \sigma_2 \le \sigma_2(w), \quad &\forall w \in \partial\Omega 
\end{aligned}
$$

**积分为零条件的含义**：由 Cauchy 幅角原理，$$\frac{1}{2\pi i} \oint f_z''/f_z \, dz = N$$ 是 $$f_z$$ 在全域内的零点个数（计重数）,积分 = 0 等价于 $$f_z(z) \neq 0 \; \forall z \in \Omega$$，即共形部分处处非零。

**其余三个条件**是原定义中 $$k \le k < 1$$, $$\sigma_1 \le \sigma_1 < \infty$$, $$0 < \sigma_2 \le \sigma_2$$ 限制到边界上的版本。



### 约束凸化

定理4中 $$|f_{\bar z}| \le k |f_z|$$ 和 $$\sigma_2 \le |f_z| - |f_{\bar z}|$$ 都是**非凸**的（含变量在分母或非线性项 $$|f_z|$$）。

**核心不等式：**

对于任意复数 $$w$$，$$\operatorname{Re}[w e^{i\theta}] \le |w|$$（实部不大于模），且当且仅当 $$\theta = -\arg w$$ 时取等号。

因此用 $$\operatorname{Re}[f_z e^{i\theta}]$$ 替代 $$|f_z|$$ 得到凸的（实际上是一个**二阶锥**）约束：

| 原非凸约束                            | 锥类型     | 凸化约束                                                     | 来源   |
| ------------------------------------- | ---------- | ------------------------------------------------------------ | ------ |
| $$\sigma_2 \le |f_z| - |f_{\bar z}|$$ | SOC        | $$|f_{\bar z}| \le \operatorname{Re}[f_z e^{i\theta}] - \sigma_2$$ | 式(12) |
| $$|f_{\bar z}| \le k \cdot |f_z|$$    | SOC        | $$|f_{\bar z}| \le k \cdot \operatorname{Re}[f_z e^{i\theta}]$$ | 式(15) |
| $$|f_z| + |f_{\bar z}| \le \sigma_1$$ | Linear+SOC | 保持原约束（已凸）                                           | 式(10) |

**推导第一个凸约束：**

由 $$\operatorname{Re}[f_z e^{i\theta}] \le |f_z|$$，代入 $$\sigma_2 \le |f_z| - |f_{\bar z}|$$：

$$
|f_{\bar z}| \le |f_z| - \sigma_2 \le \operatorname{Re}[f_z e^{i\theta}] \; \Longleftarrow \text{不成立，方向反了！}
$$

正确推导：目标是用 $$\operatorname{Re}[f_z e^{i\theta}]$$ 替代 $$|f_z|$$ 的下界。原约束重排为 $$|f_{\bar z}| + \sigma_2 \le |f_z|$$，然后应用 $$\operatorname{Re}[f_z e^{i\theta}] \le |f_z|$$：

$$
|f_{\bar z}| + \sigma_2 \le \operatorname{Re}[f_z e^{i\theta}] \quad \Longrightarrow \quad |f_{\bar z}| \le \operatorname{Re}[f_z e^{i\theta}] - \sigma_2
$$

**极大性的含义**：凸化后约束定义的空间是所有满足原非凸约束的**极大凸子集**——没有其他严格更大的凸子集仍满足原约束。这保证了凸近似是"最优"的。

**ARAP 能量的凸近似：**

ARAP 能量定义为 $$E_{\text{ARAP}} = \frac12 \int (\sigma_1-1)^2 + (\sigma_2-1)^2 \, da$$。在局部单射保向条件下可展开为：

$$
E_{\text{ARAP}} = \frac12 \int \big[ (|f_z|+|f_{\bar z}|-1)^2 + (|f_z|-|f_{\bar z}|-1)^2 \big] da
= \int (|f_z|-1)^2 + |f_{\bar z}|^2 \, da
$$

此能量含有非凸项 $$|f_z|$$，凸化近似为二次泛函：

$$
E_{\text{ARAP}}^{\text{convex}} = \int |f_z e^{i\theta} - 1|^2 + |f_{\bar z}|^2 \, da
$$

当 $$\theta = -\arg f_z$$ 时，$$f_z e^{i\theta} = |f_z|$$，凸化能量退化为原 ARAP。





### BDHM 算法流程 

#### 2.4.1 预处理：cage 与三组采样

要变形由多边形 **$$P$$** 围成的域 $$\Omega$$，先计算 **向外偏置** 的多边形 **cage $$\hat P$$**（约为 $$P$$ 周长的 **0.1%**）。Cauchy 坐标及其导数相对 **$$\hat P$$** 定义，但只在 **$$P$$ 上或内部** 求值（预处理一次）。这样 $$C_j, C_j'$$ 在真实边界附近不会碰到 $$\ln$$ 奇点（§1.2）。

在边界 $$P$$ 上按不同密度均匀采样，得到三组点集：

| 集合      | 作用                                                         | 典型规模（论文）       |
| :-------- | :----------------------------------------------------------- | :--------------------- |
| **$$M$$** | 离散近似 **$$E_{\text{ARAP}}$$**（式 (20)）；**仅边界**采样，域内加点未见收益 | 数百点                 |
| **$$A$$** | **候选约束点池**：每轮在此扫描畸变、更新 active set；初始可取边界顶点 | $$\|A\|\approx 2000$$  |
| **$$B$$** | **全局验证**（§2.5）：相邻样本连成边界段，逐段 Lipschitz 上/下界 | $$\|B\|\approx 10000$$ |

用户另选少量 **操控点** $$\mathcal{H}=\{r_j\to q_j\}$$（在 $$P$$ 上或内部）。论文记号里 handle 集与边界同名，下文用 $$\mathcal{H}$$ 避免混淆。

用户设定畸变界 $$k,\sigma_1,\sigma_2$$，拖动 $$\mathcal{H}$$ 后求解：

$$
\begin{aligned}
\min_{\phi,\psi} \quad & E_{\text{ARAP}} + \lambda E_{\text{P2P}} \\
\text{s.t.} \quad & \psi_1 = 0 \quad (\text{固定 } f=\Phi+\overline{\Psi}\text{ 的常数自由度}) \\
\forall p \in A_k: \quad & |f_{\bar z}(p)| \le k \cdot \operatorname{Re}\!\big[f_z(p) e^{i\theta(p)}\big] \\
\forall p \in A_{\sigma_1}: \quad & |f_z(p)| + |f_{\bar z}(p)| \le \sigma_1 \\
\forall p \in A_{\sigma_2}: \quad & |f_{\bar z}(p)| \le \operatorname{Re}\!\big[f_z(p) e^{i\theta(p)}\big] - \sigma_2
\end{aligned}
\tag{19}
$$

**ARAP 能量**（边界离散，式 (20)）：

$$
E_{\text{ARAP}} = \frac{1}{|M|} \sum_{p_j \in M} \Big( \big|f_z(p_j) e^{i\theta(p_j)} - 1\big|^2 + |f_{\bar z}(p_j)|^2 \Big).
$$

**软位置约束**（式 (21)）：

$$
E_{\text{P2P}} = \sum_{j=1}^{|\mathcal{H}|} |f(r_j) - q_j|^2.
$$

也可改为硬约束 $$f(r_j)=q_j$$，但可能使 SOCP **不可行**（畸变界过紧时手柄拖不动）；论文默认用软约束，保证 (19) **始终可行**。

其中 $$f_z = D\phi$$，$$f_{\bar z} = \overline{D\psi}$$；三个不等式只在 **active set** 的子集 $$A_k,A_{\sigma_1},A_{\sigma_2}\subseteq A$$ 上施加，而非全体 $$A$$。

#### 2.4.3 为何需要两层迭代：有限约束 vs 全域证书

(19) 是凸 SOCP，**总有解**，但畸变界只保证在 **有限个活跃点** 成立。要得到 **全域** $$(k,\sigma_1,\sigma_2)$$-有界失真，必须对解做 **Section 6 全局验证**（§2.5）。

因此算法有两层逻辑：

```
┌─────────────────────────────────────────────────────────────┐
│  外循环（θ 收紧，通常 1–3 轮）                                │
│    1. 在 A_k, A_σ1, A_σ2 上解 SOCP (19)                      │
│    2. 全局验证 (B 上 Lipschitz 证书)                          │
│    3. 若证书失败 → active set 加点 / 线搜索 → 回到 1 或 2     │
│    4. 验证通过 → θ ← −arg f̃_z，若能量仍可降则回到 1           │
└─────────────────────────────────────────────────────────────┘
         ↑ 每轮 SOCP 前：在 A 上扫描，更新 A_k, A_σ1, A_σ2
```

**$$\theta$$ 外循环**：验证通过后设 $$\theta(w)=-\arg \tilde f_z(w)$$，其中 $$\tilde f_z$$ 是对未知 $$f_z$$ 的估计。于是 $$e^{i\theta}=|\tilde f_z|/\tilde f_z$$，反复出现的 $$\operatorname{Re}[f_z e^{i\theta}]$$ 逼近 $$|f_z|$$——这正是非凸约束 (11)(14) 与凸约束 (12)(15) 的**唯一差别**。实践上：

- 首轮 $$\tilde f_z\equiv 0$$（恒等映射，$$\theta=0$$），保证初始 SOCP 可行；
- 之后 $$\tilde f_z$$ 取**上一轮** SOCP 解的 $$f_z$$，凸子空间逐轮收紧；
- 能量不再下降时停止（通常 **1–3 次** $$\theta$$ 更新）。

#### 2.4.4 Active Set 机制（核心）

**动机**：若在 $$A$$ 的每个点同时施加三种 SOC 约束，变量 $$2n$$ 个复系数、约束可达数千，MOSEK 内点法代价高。**Active set** 只在「需要」的点上加不等式——与 [Poranne & Lipman 2014]（Provably Good）的 **单** active set 不同，BDHM 维护 **三个独立** 活跃集：

$$
A_k \subseteq A,\quad A_{\sigma_1} \subseteq A,\quad A_{\sigma_2} \subseteq A.
$$

**初始化**：$$A_k = A_{\sigma_1} = A_{\sigma_2} = \{\text{边界 }P\text{ 的顶点}\}$$，$$\theta\equiv 0$$。

**每轮 SOCP 求解之前**（在候选池 $$A$$ 上操作）：

| 步骤                      | 操作                                                         |
| :------------------------ | :----------------------------------------------------------- |
| **1. 显式违反**           | 计算 $$k(p),\sigma_1(p),\sigma_2(p)$$；若 $$k(p)>k$$ 加入 $$A_k$$；若 $$\sigma_1(p)>\sigma_1$$ 加入 $$A_{\sigma_1}$$；若 $$\sigma_2(p)<\sigma_2$$ 加入 $$A_{\sigma_2}$$ |
| **2. 近违反（局部极值）** | 找 $$k,\sigma_1$$ 的**局部极大**、$$\sigma_2$$ 的**局部极小**（沿 $$A$$ 的边界采样序）；若接近用户界也提前激活：<br>• $$k(p_i)$$ 局部极大且 $$k(p_i)>0.95k$$ → $$A_k$$<br>• $$\sigma_1(p_i)$$ 局部极大且 $$\sigma_1(p_i)>0.95\sigma_1$$ → $$A_{\sigma_1}$$<br>• $$\sigma_2(p_i)$$ 局部极小且 $$\sigma_2(p_i)<1.15\sigma_2$$ → $$A_{\sigma_2}$$ |
| **3. 移除**               | 活跃点畸变已充分远离界则删约束，避免 SOCP 膨胀：<br>• $$k(p)<0.945k$$ 从 $$A_k$$ 移除<br>• $$\sigma_1(p)<0.945\sigma_1$$ 从 $$A_{\sigma_1}$$ 移除<br>• $$\sigma_2(p)>1.2\sigma_2$$ 从 $$A_{\sigma_2}$$ 移除 |

**为何三个集合**：实验上 **很少** 同时违反多种畸变界（共形 $$k$$、最大拉伸 $$\sigma_1$$、最小拉伸 $$\sigma_2$$ 的「瓶颈」往往在不同位置）。分开维护可使 **活跃约束总数** 远小于「单集 + 三约束/点」——论文报告相对 Poranne–Lipman 2014 显著加速。

**与验证的闭环**：SOCP 解算完后，在 **$$B$$** 上做段-wise 全局界（§2.5）。若证书显示某段超限，说明 active set **过稀**——将违反段上的样本补进对应 $$A_*$$，**重新解 SOCP**；论文称这是 line search 失败时最常见的补救路径，而非用户界本身不可达。

**与 Lipman / Provably Good 的对比**（见 [几何变形 Provably good mapping](几何变形2-Provably good mapping.md) §8.1）：

|                 | Poranne–Lipman 2014                              | BDHM                              |
| :-------------- | :----------------------------------------------- | :-------------------------------- |
| Active set 个数 | 1（统一畸变 $$D$$）                              | 3（$$k,\sigma_1,\sigma_2$$）      |
| 激活判据        | 局部极大 + $$K_{\text{on}}/K_{\text{off}}$$ 滞回 | 违反界 + 0.95/0.945/1.15/1.2 滞回 |
| 证书            | 填充距离 + 连续性模                              | 边界段 Lipschitz（§2.5–2.6）      |

#### 2.4.5 验证失败时的线搜索

设 $$\phi^{i-1},\psi^{i-1}$$ 为**上一轮已验证**的系数，$$\phi^i,\psi^i$$ 为当前 SOCP 解。在区间 $$t\in(0,1]$$ 上插值

$$
\phi(t)=(1-t)\phi^{i-1}+t\phi^i,\qquad \psi(t)=(1-t)\psi^{i-1}+t\psi^i,
$$

对 $$\phi(t),\psi(t)$$ 计算全局畸变界 $$\tilde k,\tilde\sigma_1,\tilde\sigma_2$$。若超过用户允许的松弛（默认 **$$1.2k,\,1.3\sigma_1,\,0.7\sigma_2$$**，最多 **10** 次二分），则令 $$t\leftarrow t/2$$ 重算，直到得到可证书映射或步长耗尽。

线搜索失败时：先 **扩充 active set** 再解 SOCP，而非立即判定问题不可行。

#### 2.4.6 完整算法伪码

```
输入: 边界 P, cage P̂, 采样 M⊂A⊂B⊂∂P, 操控点 H, 用户界 k,σ₁,σ₂
预处理: 相对 P̂ 算 C, C'；在 M,A,B 上存表；Lf_{C'} 矩阵
初始化: A_k,A_σ1,A_σ2 ← P 的顶点; θ←0; φ,ψ ← 恒等映射系数

用户拖动手柄 → 更新 q_j
重复 (θ 外循环):
  重复 (active set 内循环):
    在 A 上更新 A_k, A_σ1, A_σ2（违反 / 近违反 / 移除）
    解 SOCP (19) → φ^i, ψ^i
    线搜索 t∈(0,1]: 验证 φ(t),ψ(t) 的全局界
    若验证失败且 t 已耗尽 → 继续 active set 内循环
  若验证通过:
    若 E_ARAP 相对上轮无显著下降 → 结束
    否则 θ(w)←−arg f_z(w)（用当前解）, 保存 φ,ψ 为已验证解
输出: 最终 φ,ψ 及证书界 k̃,σ̃₁,σ̃₂
```

#### 2.4.7 共形特例

当 $$K \to 1$$（$$\kappa \to 0$$）时，有界扭曲约束退化为 $$f_{\bar z} = 0$$，即 $$f$$ 为全纯函数，等价于仅保留 $$\phi$$ 系数（$$\psi = 0$$），Cauchy 坐标的共轭部分消失，映射完全是共形的。此时 (19) 简化为 (22)：只需 $$\sigma_1,\sigma_2$$ 对 $$|f_z|$$ 的界，且 $$E_{\text{ARAP}}$$ 中 $$|f_{\bar z}|^2$$ 项消失。

### 

### 2.6 Lipschitz 常数与更紧的边界条件

要将 Theorem 4 的无限多边界不等式化为有限个可计算的充分条件，需知道 $$f_z, f_{\bar z}$$ 在边界线段上的 Lipschitz 常数。

**Lipschitz 连续性的加法性质：** 若 $$g, q$$ 分别为 $$L_g, L_q$$-Lipschitz，则线性组合 $$a g + b q$$ 为 $$(|a|L_g + |b|L_q)$$-Lipschitz。

利用式 (9) $$f_z(z) = \sum_{j=1}^n C_j'(z) \phi_j$$，可得初始 Lipschitz 常数：

$$
L_{f_z} = \sum_{j=1}^{n} L_{C_j'} \cdot |\phi_j|, \qquad
L_{f_{\bar z}} = \sum_{j=1}^{n} L_{C_j'} \cdot |\psi_j|
$$

**Proposition 10 (Cauchy 坐标导数的 Lipschitz 常数).** $$C_j'(z)$$ 在域内（除 cage 顶点外）的 Lipschitz 常数为：

$$
L_{C_j'} = \frac{|z_{j+1} - z_{j-1}|}{2\pi \; d(z_{j-1}) \; d(z_j) \; d(z_{j+1})}
$$

其中 $$z_{j-1}, z_{j+1}$$ 是 cage 上与 $$z_j$$ 相邻的顶点，$$d(z_j)$$ 是点 $$z_j$$ 到当前线段 $$[v_1, v_2]$$ 的距离。在预处理阶段，BDHM 预计算一个 $$|B| \times n$$ 的 Lipschitz 常数矩阵（$$|B|$$ 是边界线段数，$$n$$ 是 cage 顶点数），运行时只需乘上动态变化的 $$|\phi_j|, |\psi_j|$$。

**优化：更紧的 Lipschitz 常数。** 利用 Cauchy 坐标的**常数精度**（$$\sum C_j'(z) = 0$$）和**线性精度**（$$\sum C_j'(z) z_j = 1$$），可用 $$\phi_j + b + a z_j$$ 替代 $$\phi_j$$ 来减小 Lipschitz 常数：

$$
f_z(z) = \sum_{j=1}^n C_j'(z)(\phi_j + b + a z_j), \qquad
L_{f_z}^{\text{opt}} = \sum_{j=1}^n L_{C_j'} \cdot |\phi_j + b + a z_j|
$$

其中 $$a, b \in \mathbb{C}$$ 可按需在每个线段上选择。若选择 $$a, b$$ 使 $$\phi_j + b + a z_j = 0$$ 对两个最大的 $$L_{C_j'}$$ 项成立，则这两项贡献为零，大幅降低了 Lipschitz 常数的量级。这让充分条件更紧致，允许更大的 Newton/优化步长。

**BDHM 的实用启发式：** 对每段，找到最大的 $$L_{C_r'}$$ 及其最大邻项 $$L_{C_q'}$$，解线性方程组：

$$
\phi_r + b + a z_r = 0, \qquad \phi_q + b + a z_q = 0
$$

得到 $$a, b$$，代入上式得到更紧的 $$L_{f_z}^{\text{opt}}$$。BDHM 报告此方法在典型模型上（$$n=78$$ cage 顶点、$$|B|=340$$ 个线段）效果显著。

### 2.7 无零点条件的高效验证 (Theorem 11)

除 Lipschitz 边界外，还需验证 $$f_z$$ 全域非零。BDHM 给出一个比数值积分快数个数量级的充分条件。

**Theorem 11.** 设 $$f$$ 是单连通域 $$\Omega$$ 上的复值调和映射，$$\theta(w)$$ 是边界上任意实值连续函数。定义 $$\gamma(w) = \operatorname{Re}[f_z(w) e^{i\theta(w)}]$$。若 $$\gamma(w) > 0$$ 在边界上处处成立，则 $$f_z$$ 在域内无零点。

**实际验证：** 利用 $$\gamma$$ 的 Lipschitz 常数，可以仅在边界样本点上验证。设 $$\theta$$ 为分段线性函数（取值 $$\theta(w_i) = -\arg f_z(w_i)$$），对每个线段 $$[w_{i-1}, w_i]$$（长度 $$l$$），充分条件为：

$$
(2 + |\theta_i - \theta_{i-1}|) \, l \, L_{f_z} < (2 - |\theta_i - \theta_{i-1}|) \, \frac{|f_z(w_{i-1})| + |f_z(w_i)|}{2}
$$

在 BDHM 的实现中，$$\theta$$ 的累积值通过相邻样本间的主值分支差计算（$$\Delta\theta_i = \operatorname{Arg}(f_z(w_i) / f_z(w_{i-1}))$$），避免了 $$\operatorname{arg}$$ 的分支跳跃问题。这可在约 15,000 个边界段上约 25ms 内完成验证。