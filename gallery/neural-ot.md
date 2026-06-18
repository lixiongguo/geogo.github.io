## Neural Lagrangian OT 可视化

本 demo 展示 **Neural Lagrangian Optimal Transport (NLOT)** 的核心思想：用神经网络参数化的**时变速度场** $v_\theta(x,t)$ 驱动粒子（拉格朗日视角），将源分布 $\rho_0$ 连续推送到目标分布 $\rho_1$，而不是在网格上显式求解密度 PDE。

> 页面动画为**已收敛流的视觉示意**（预定义粒子路径 + 近邻插值速度场），用于直观理解 NLOT 的流动形态，并非在浏览器内实时训练神经网络。

---

### 最优传输（OT）问题

给定源、目标概率密度 $\rho_0, \rho_1$，寻找代价最小的传输计划。Benamou–Brenier 动态表述将 OT 写成**连续性方程 + 动能最小**：

$$\min_{(\rho, v)} \int_0^1 \int \frac{1}{2}\|v(x,t)\|^2 \,\rho(x,t)\, dx\, dt$$

$$\text{s.t.}\quad \partial_t \rho + \nabla \cdot (\rho v) = 0, \quad \rho(\cdot,0)=\rho_0,\; \rho(\cdot,1)=\rho_1$$

---

### Neural Lagrangian 视角

NLOT 用粒子流 $X_t^\theta$ 表示密度推进（push-forward）：

$$\frac{d x_t}{dt} = v_\theta(x_t, t), \qquad \rho_t = (X_t^\theta)_{\#}\rho_0$$

训练目标通常包含**动能正则**、**终点分布匹配**与网络正则：

$$\mathcal{E}(\theta) + \lambda\, D\bigl((X_1^\theta)_{\#}\rho_0,\, \rho_1\bigr) + R(\theta)$$

| 项 | 含义 |
|:---|:---|
| $\mathcal{E}(\theta)$ | 路径动能 / 控制代价 |
| $D(\cdot,\cdot)$ | 终点与 $\rho_1$ 的散度（Wasserstein、MMD 等） |
| $R(\theta)$ | 网络权重正则 |

---

### 页面元素

| 颜色 | 含义 |
|:---|:---|
| 绿色云 | 源分布 $\rho_0$（左下高斯团） |
| 蓝色粒子 | 当前时刻 $x_t$ |
| 粉色云 | 目标分布 $\rho_1$（可切换形状） |
| 黄色箭头 | 由近邻粒子路径估计的 $v_\theta$ 示意 |

左下角 HUD 显示 flow time $t$、动能、终点匹配误差与粒子数；右下角 Loss 曲线为示意，竖线对应当前 $t$。

---

### 交互

| 控件 | 效果 |
|:---|:---|
| **暂停 / 播放** | 控制 $t \in [0,1]$ 循环 |
| **重新采样** | 按当前设置重抽粒子与弯曲路径 |
| **目标分布** | 三峰混合 / 圆环 / 双月形 |
| **粒子数** | 300–2400，影响密度云细腻度 |
| **流动时间** | 动画播放速度 |
| **轨迹 / 速度场 / Loss** | 开关叠加层 |

切换目标分布可观察同一源高斯如何被**连续时间流**推送到不同几何形状——这正是 OT 流与 Eulerian 密度场方法在视觉上的主要区别。

---

### 与 Eulerian OT / CFM 的对比

| 方法 | 存储 | 特点 |
|:---|:---|:---|
| **网格密度 PDE** | $\rho(x,t)$ on grid | 易可视化密度，高维代价大 |
| **Neural Lagrangian OT** | 粒子 + $v_\theta$ | 天然高维、与生成模型结合 |
| **Flow Matching / CFM** | 学习向量场 | 类似思路，常固定直线路径或条件流 |

---

### 参考

- Benamou & Brenier (2000). "A computational fluid mechanics solution to the Monge–Kantorovich mass transfer problem." *Numerische Mathematik*.
- 相关 Neural OT / Lagrangian OT 文献（粒子 push-forward + 神经速度场）。
