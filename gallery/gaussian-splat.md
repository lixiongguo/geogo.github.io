## 3D Gaussian Splatting（3DGS）高斯基元渲染

3D Gaussian Splatting 是 2023 年提出的新一代场景重建与渲染方法，它用**数百万个各向异性的 3D 高斯椭球体**精确建模现实场景，实现照片级真实感的实时渲染。

### 核心思想

与传统的点云或 Mesh 不同，每个高斯核在三维空间中具有：

- **位置** `μ ∈ ℝ³`（均值中心）
- **协方差矩阵** `Σ ∈ ℝ³ˣ³`（椭球的形状与方向）
- **颜色** 由球面谐波函数（Spherical Harmonics, SH）表示
- **不透明度** `α ∈ [0,1]`

场景由 $N$ 个 3D 高斯混合表示：

$$G(\mathbf{x}) = \exp\left(-\frac{1}{2}(\mathbf{x} - \mathbf{\mu})^\top \mathbf{\Sigma}^{-1} (\mathbf{x} - \mathbf{\mu})\right)$$

### 渲染流程（Tile-based Rasterization）

1. **排好深度序**：所有高斯核按到相机的距离排序
2. **投影到屏幕**：3D 协方差矩阵 → 2D 屏幕协方差矩阵
3. **α-blending**：从近到远逐层叠加颜色

$$C = \sum_{i=1}^{N} c_i \alpha_i \prod_{j=1}^{i-1} (1 - \alpha_j)$$

### 特点

| 优势 | 说明 |
|:---|:---|
| **照片级真实感** | 捕捉视相关效果（高光、反射） |
| **实时渲染** | ≥30 FPS 在普通 GPU 上 |
| **显式表示** | 无需神经网络推理，直接光栅化 |
| **紧凑** | 场景压缩为几 MB ~ 几十 MB 的 `.spz` / `.ply` 文件 |

### SPZ 格式

`.spz` 格式是专门为 Gaussian Splatting 优化的压缩格式，将位置、协方差、颜色、SH 系数等数据压缩存储，便于网络传输。

### 参考

- Kerbl et al. (2023). "3D Gaussian Splatting for Real-Time Radiance Field Rendering." *ACM Transactions on Graphics (SIGGRAPH 2023)*.
- gsplat.js: WebGL-based 3DGS viewer by Kevin Kwok.
