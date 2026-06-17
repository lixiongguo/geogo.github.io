## Boid — 群体运动算法

Boid 算法由 Craig Reynolds 于 1986 年提出，用三条简单规则模拟鸟群、鱼群等群体运动行为——**没有中央控制，完全由个体自治产生涌现现象**。

### 三条核心规则

每个个体（Boid）根据周围邻居的状态调整自己的速度，三条规则等权叠加：

| 规则 | 含义 | 效果 |
|:---|:---|:---|
| **分离 (Separation)** | 远离附近个体，避免碰撞 | 保持最小间距 |
| **对齐 (Alignment)** | 匹配邻域的平均速度方向 | 形成一致航向 |
| **凝聚 (Cohesion)** | 飞向邻域的平均位置 | 防止群体解散 |

### 形式化定义

对 Boid $i$，定义邻域 $N_i = \{\ j \mid \|\mathbf{p}_j - \mathbf{p}_i\| < r\ \}$（或取前 $k$ 个最近邻居）。

**分离：**

$$\mathbf{F}_{\text{sep}} = -\sum_{j \in N_i} \frac{\mathbf{p}_j - \mathbf{p}_i}{\|\mathbf{p}_j - \mathbf{p}_i\|^2}$$

排斥力与距离平方成反比——越近的邻居排斥越强。

**对齐：**

$$\mathbf{F}_{\text{align}} = \frac{1}{\|N_i\|}\sum_{j \in N_i} \mathbf{v}_j - \mathbf{v}_i$$

将自身速度拉向邻居的平均速度。

**凝聚：**

$$\mathbf{F}_{\text{coh}} = \frac{1}{\|N_i\|}\sum_{j \in N_i} \mathbf{p}_j - \mathbf{p}_i$$

将自身位置拉向邻居的质心。

### 更新方程

每帧对每个 Boid 更新速度与位置：

$$\mathbf{v}_i \gets \mathbf{v}_i + w_s \cdot \mathbf{F}_{\text{sep}} + w_a \cdot \mathbf{F}_{\text{align}} + w_c \cdot \mathbf{F}_{\text{coh}}$$

$$\mathbf{v}_i \gets \text{clamp}(\|\mathbf{v}_i\|, v_{\min}, v_{\max}) \cdot \frac{\mathbf{v}_i}{\|\mathbf{v}_i\|}$$

$$\mathbf{p}_i \gets \mathbf{p}_i + \mathbf{v}_i \cdot \Delta t$$

### 扩展规则

| 扩展 | 效果 |
|:---|:---|
| **边界回避** | 遇到边界时转向，避免飞出视野 |
| **目标吸引** | 群体向鼠标/目标点靠拢 |
| **障碍回避** | 射线检测避障物 |
| **视野限制** | 只考虑前方锥形视野内的邻居 |
| **多群体** | 不同群体用不同规则权重，出现分离/合并 |
| **捕食者-猎物** | 分离对捕食者更强，猎物额外逃离 |

### 复杂度与优化

朴素实现是 $O(n^2)$（每对 Boid 检查距离），实际优化方法：

- **空间哈希 / 网格**：将空间划分为单元格，只检查相邻单元格
- **K-D Tree**：对空间位置建树，$O(n \log n)$ 邻居查询
- **固定 $k$ 近邻**：不扫描所有邻居，只取最近的 $k$ 个

### 涌现现象

三条简单规则的叠加产生复杂群体行为：

- **群体转向**：领头个体偏转 → 对齐传播 → 整个群体同步转向
- **分裂与合并**：遇到障碍 → 分离压倒凝聚 → 分裂 → 绕过障碍 → 凝聚恢复 → 合并
- **漩涡**：边界 + 速度限制产生回转漩涡
- **线形队形**：对齐 + 凝聚在高速时易形成线形（V 形）

### 与其他模型的对比

| 方法 | 机制 | 全局控制 | 适用场景 |
|:---|:---|:---|:---|
| **Boid** | 3 条局部规则叠加 | 无中心 | 鸟群、鱼群 |
| **Vicsek 模型** | 仅对齐 + 随机噪声 | 无中心 | 物理相变研究 |
| **Couzin 模型** | 分区规则（排斥/对齐/吸引） | 无中心 | 分层群体行为 |
| **ORCA** | 速度障碍法 | 无中心 | 机器人导航 |
| **势场法** | 全局势函数梯度 | 全局势场 | 路径规划 |

### 参考

- Reynolds, C. W. (1987). "Flocks, herds and schools: A distributed behavioral model." *SIGGRAPH '87*.
- Vicsek, T., et al. (1995). "Novel type of phase transition in a system of self-driven particles." *Physical Review Letters*.
- Couzin, I. D., et al. (2002). "Collective memory and spatial sorting in animal groups." *Journal of Theoretical Biology*.
