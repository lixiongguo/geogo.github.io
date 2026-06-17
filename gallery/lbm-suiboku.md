## LBM 水墨动画

水墨画的视觉本质是**墨水在水中的扩散与流动**。LBM 在格子 Boltzmann 方法上追踪粒子分布函数，天然适合模拟这种扩散-对流耦合过程。

### D2Q9 模型

二维空间中最常用的 D2Q9 格子在每个网格点追踪 9 个方向的分布函数 $f_i$，宏观密度 $\rho$ 和速度 $\mathbf{u}$ 由矩求得：

$$\rho = \sum_i f_i, \quad \rho\mathbf{u} = \sum_i \mathbf{c}_i f_i$$

### 两步演化：Streaming + Collision

**Streaming（对流）**：粒子沿 9 个方向移动到相邻格点。

**Collision（BGK 碰撞）**：向平衡分布 $f_i^{\text{eq}}$ 弛豫：

$$f_i^{\text{eq}} = w_i\rho\left[1 + 3(\mathbf{c}_i \cdot \mathbf{u}) + \frac{9}{2}(\mathbf{c}_i \cdot \mathbf{u})^2 - \frac{3}{2}\mathbf{u}^2\right]$$

### 墨水扩散

耦合标量对流-扩散方程追踪墨水浓度 $C$：

$$\frac{\partial C}{\partial t} + \mathbf{u} \cdot \nabla C = D \nabla^2 C$$

用第二套分布函数 $g_i$ 求解，扩散系数 $D$ 控制晕染速度。

### 控制参数

| 参数 | 效果 |
|:---|:---|
| **粘度** ($\tau$) | 越大墨迹越稠、流速越慢 |
| **扩散系数** ($D$) | 越大墨迹在水中晕散越快 |
| **笔触强度** | 鼠标落笔注入的墨水浓度 |

### 水墨效果

- **笔触**：拖拽落笔，墨迹随流体自然扩散
- **晕染 (Nijimi)**：高扩散 + 低流速 → 自然晕开
- **干笔 (Kasure)**：快速移动 → 断续飞白
- **叠加**：多层墨迹叠加产生浓淡变化

### 参考

- Chen & Doolen (1998). "Lattice Boltzmann method for fluid flows." *Annual Review of Fluid Mechanics*.
- Krüger et al. (2017). *The Lattice Boltzmann Method: Principles and Practice.* Springer.
