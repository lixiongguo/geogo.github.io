## SPH / PBF 粒子水体

本 demo 对比两种主流的**拉格朗日**粒子流体求解器：**SPH**（力驱动）与 **PBF**（位置约束驱动）。可在工具栏切换求解器，粒子布局、交互与渲染保持一致。

> 与 [2D 交互水面](/gallery/water-2d.html)（欧拉高度场）、[2D 水线波动](/gallery/water-line.html)（1D 波方程）互补：二者均在粒子位置直接演化，适合大变形与自由表面。

---

### 拉格朗日 vs 欧拉

| | 拉格朗日（SPH / PBF） | 欧拉（网格） |
|:---|:---|:---|
| 追踪对象 | 粒子轨迹 $\mathbf{x}_i(t)$ | 固定格点上的 $\rho,\mathbf{v}$ |
| 优势 | 大变形、无网格、自然自由面 | 求压 Poisson 成熟、规则域高效 |
| 代价 | 邻域搜索、需调参 | 对流耗散、界面捕捉较难 |

---

### SPH：力驱动积分

**光滑粒子流体动力学（SPH）** 通过核函数把粒子「抹平」成连续场，再求力积分。

每步（5 个子步）：

1. **邻域搜索**（空间哈希）
2. **密度**（Poly6）：$\rho_i = \sum_j m_j W_{\text{poly6}}$
3. **压力**（弱可压缩）：$P_i = k(\rho_i - \rho_0)$
4. **力**：Spiky 压力梯度 + 粘度 Laplacian + 重力
5. **XSPH** 速度平滑 + 欧拉积分

| 核 | 用途 |
|:---|:---|
| **Poly6** | 密度估计 |
| **Spiky** | 压力梯度 |
| **Viscosity** | 速度扩散 |

**特点**：物理直观，与文献公式一一对应；弱可压缩时需较小时间步，易出现密度震荡。

---

### PBF：位置约束投影

**Position Based Fluids（PBF）**（Macklin & Müller, 2013）不显式求压力力，而是：

1. **预测位置**：$\mathbf{x}_i^* = \mathbf{x}_i + \mathbf{v}_i \Delta t$（含重力与交互）
2. **密度约束**：$C_i = \rho_i / \rho_0 - 1$
3. **拉格朗日乘子**：
   $$ \lambda_i = -\frac{C_i}{\sum_k \|\nabla W_{ik}\|^2 + \varepsilon} $$
4. **位置修正**（迭代 5 次）：
   $$ \Delta \mathbf{x}_i = \frac{1}{\rho_0}\sum_j (\lambda_i + \lambda_j + s_{\text{corr}})\,\nabla W_{ij} $$
5. **速度更新**：$\mathbf{v}_i = (\mathbf{x}_i' - \mathbf{x}_i) / \Delta t$，再 XSPH 粘度混合

$s_{\text{corr}}$ 为**张力修正**（tensile instability correction），减轻粒子成簇。

| 对比项 | SPH | PBF |
|:---|:---|:---|
| 驱动量 | 力 $\mathbf{F}$ | 约束 $C_i=0$ |
| 时间步 | 较小（$\sim 5.5\times10^{-4}$） | 较大（$\sim 3\times10^{-3}$） |
| 不可压缩性 | 依赖状态方程刚度 $k$ | 迭代投影，更稳 |
| 交互调参 | **压力** $k$ | **刚度**（乘子缩放） |

---

### 交互

| 操作 | 效果 |
|:---|:---|
| **求解器** | SPH ↔ PBF 切换（重置粒子） |
| **拖拽** | 径向推动水体 |
| **点击（靠上）** | 注入粒子 |
| **注水** | 顶部落下一块水 |
| **粘度** | SPH 粘度核强度 / 二者 XSPH 混合 |
| **压力 / 刚度** | SPH 气体常数 $k$ / PBF 约束强度 |
| **重力** | 向下加速度 |

---

### 实现要点

- 共享：Poly6 / Spiky 核、空间哈希、SoA 粒子数组（最多约 3500）
- SPH：5 子步力积分
- PBF：每帧 5 次约束投影 + 张力修正
- 渲染：按密度着色 + `lighter` 混合

---

### 局限

- 2D 演示，非完整 3D 管道
- PBF 未实现 Macklin 原文的各向异性粘度与完整边界处理
- 未含表面张力、多相流

---

### 参考

- Müller et al. (2003). "Particle-Based Fluid Simulation for Interactive Applications." *SCA*.
- Macklin & Müller (2013). "Position Based Fluids." *ACM TOG / SIGGRAPH*.
- Monaghan (2005). "Smoothed particle hydrodynamics." *Reports on Progress in Physics*.
