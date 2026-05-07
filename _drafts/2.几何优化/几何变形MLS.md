## 利用 MLS 做网格变形

![image-20251218190043391](..\..\..\imgs\image-20251218190043391.png)

移动最小二乘法是一种用于**局部拟合数据点**的方法，常用于曲线/曲面重建、散乱数据插值等。它的核心思想是：

> 在每个目标点附近，用加权最小二乘法拟合一个局部多项式（比如常数、线性函数），权重由目标点与邻近点的距离决定（越近权重越大）。

**移动最小二乘（Moving Least Squares, MLS）** 和 **As-Rigid-As-Possible (ARAP)** 确实**思路高度相近**，甚至可以说 ARAP 是 MLS 思想在**几何形变（deformation）领域**的一种具体化、优化和推广。使用 MLS 不需要先进行三角化。

![image-20251218192214246](..\..\..\imgs\image-20251218192214246.png)

---

## 最简单的 MLS：一维线性例子

**目标**：用**线性 MLS** 估计函数在 $x=1$ 处的值，基于三个散乱数据点：

| $x_i$ | $y_i$ |
| :---: | :---: |
|   0   |   1   |
|   1   |   2   |
|   2   |   1   |

与常数阶类似，但用**局部线性函数**拟合：

$$
p(x) = a_0 + a_1 x.
$$

**步骤 1：基函数与系数**

$$
\mathbf{p}(x) = \begin{bmatrix} 1 \\ x \end{bmatrix}, \qquad
p(x) = \mathbf{a}^\top \mathbf{p}(x) = a_0 + a_1 x, \qquad
\mathbf{a} = [a_0,\, a_1]^\top.
$$

**步骤 2：高斯权重**（平滑长度 $h=1$）

$$
w_i(x) = \exp\left( -\frac{(x - x_i)^2}{h^2} \right).
$$

在 $x=1$ 处：

$$
w_1 = e^{-(1-0)^2} = e^{-1} \approx 0.3679,\quad
w_2 = e^{-(1-1)^2} = 1,\quad
w_3 = e^{-(1-2)^2} = e^{-1} \approx 0.3679.
$$

**步骤 3：加权最小二乘**

最小化

$$
J(\mathbf{a}) = \sum_{i=1}^{3} w_i \,(a_0 + a_1 x_i - y_i)^2.
$$

设计矩阵 $\mathbf{P} \in \mathbb{R}^{3\times 2}$：

$$
\mathbf{P} =
\begin{bmatrix}
1 & x_1 \\ 1 & x_2 \\ 1 & x_3
\end{bmatrix}
=
\begin{bmatrix}
1 & 0 \\ 1 & 1 \\ 1 & 2
\end{bmatrix}.
$$

权重矩阵与数据向量：

$$
\mathbf{W}(x) = \mathrm{diag}(w_1,w_2,w_3) \approx \mathrm{diag}(0.3679,\, 1,\, 0.3679), \qquad
\mathbf{y} = [1,\, 2,\, 1]^\top.
$$

**MLS 正规方程**：

$$
(\mathbf{P}^\top \mathbf{W} \mathbf{P})\,\mathbf{a} = \mathbf{P}^\top \mathbf{W} \mathbf{y}.
$$

代入数值解出 $\mathbf{a}$ 后，即得 $p(1)=a_0+a_1$。

## 问题背景：如何用少量控制点自然地变形图像？

用户拖动几个控制点（如把眼睛拉大、把脸变瘦），希望：

- **控制点精确移动到目标位置**
- **周围区域平滑、自然地跟随变形**
- **不产生撕裂、折叠或过度扭曲**

传统方法（如仿射变换、TPS）要么太刚性，要么全局影响太大。MLS 提供了一种**局部加权、能量最小化**的解决方案。

### 核心思想：局部拟合 + 全局协调

MLS 的核心是：对图像中每个像素，基于附近控制点的位移，计算一个**局部最优**的仿射（或相似、刚性）变换，然后加权融合。

**步骤概览：**

1. 用户指定一组源控制点 $\{p_i\}$ 和对应的目标位置 $\{q_i\}$
2. 对图像中任意一点 $v$（如一个像素坐标）：
   - 计算它到每个控制点 $p_i$ 的权重 $w_i(v)$（通常与距离成反比）
   - 基于权重，拟合一个局部变换 $T_v(\cdot)$（如相似变换），使得 $T_v(p_i) \approx q_i$
   - 将 $v$ 映射到新位置：$v' = T_v(v)$
3. 所有像素按此规则变形，得到新图像

> **关键链**：每个点有自己的局部变换，但受全局控制点约束。

---

## MLS 形变：控制点与仿射拟合

设控制点 $p_i$ 及其形变后位置 $q_i$（行向量）。对图像中一点 $v$，求仿射变换 $l_v(x)$，使加权平方误差最小：

$$
\sum_i w_i \,\bigl\lVert l_v(p_i) - q_i \bigr\rVert^2.
\qquad (1)
$$

权重（距离越近越大，$\alpha$ 为参数）：

$$
w_i = \frac{1}{\lVert p_i - v \rVert^{2\alpha}}.
$$

因 $l_v(x)$ 为仿射变换，可写为线性部分与平移：

$$
l_v(x) = x M + T.
\qquad (2)
$$

对式 (1) 关于 $T$ 求极小，可得

$$
T = q_* - p_* M,
$$

其中 $p_*$、$q_*$ 为加权重心：

$$
p_* = \frac{\sum_i w_i p_i}{\sum_i w_i}, \qquad
q_* = \frac{\sum_i w_i q_i}{\sum_i w_i}.
$$

代入式 (2) 得

$$
l_v(x) = (x - p_*) M + q_*.
\qquad (3)
$$

于是式 (1) 等价于只关于 $M$ 的最小二乘：

$$
\sum_i w_i \,\bigl\lVert \hat{p}_i M - \hat{q}_i \bigr\rVert^2,
\qquad (4)
$$

其中

$$
\hat{p}_i = p_i - p_*, \qquad \hat{q}_i = q_i - q_*.
$$

$\hat{p}_i$、$\hat{q}_i$ 即相对加权重心的坐标。注意 $M$ 不必是一般仿射矩阵；论文中进一步限制为**相似变换**、**刚性变换**等以控制局部剪切与缩放。

---

## 数学细节：以"相似变换"为例

直接优化旋转/缩放较复杂。MLS 的巧妙之处在于**重写目标函数**，得到闭式解。

### 1. 定义加权质心

$$
p_* = \frac{\sum w_i p_i}{\sum w_i}, \qquad q_* = \frac{\sum w_i q_i}{\sum w_i}
$$

### 2. 构造协方差矩阵

$$
M_{\text{cov}} = \sum w_i \, (\hat{p}_i)^\top \hat{q}_i, \quad \text{其中 } \hat{p}_i = p_i - p_*,\; \hat{q}_i = q_i - q_*
$$

### 3. 最优变形公式（相似变换版本）

$$
v' = T_v(v) = q_* + \frac{1}{\sigma_v} R_v (v - p_*)
$$

其中：

$$
\sigma_v = \sqrt{\frac{\sum w_i \lVert \hat{q}_i \rVert^2}{\sum w_i \lVert \hat{p}_i \rVert^2}}
$$

$R_v$ 从 SVD 分解 $M_{\text{cov}} = U \Sigma V^\top$ 中得到的最优旋转：

$$
R_v = V \begin{bmatrix} 1 & 0 \\ 0 & \det(VU^\top) \end{bmatrix} U^\top
$$

这个公式保证了**局部相似性**（保角、无剪切），视觉效果自然。

> **直觉**：MLS 不直接迭代优化旋转矩阵，而是通过 SVD 分解一步到位——将协方差矩阵分解为"缩放 × 旋转"，直接提取出最优旋转 $R_v$。

---

## 权重函数设计

权重 $w_i(v)$ 决定了控制点的影响范围，常用：

$$
w_i(v) = \frac{1}{\lVert v - p_i \rVert^{2\alpha}} \quad (\alpha > 0)
$$

- $\alpha$ 控制衰减速度（通常取 1 或 2）
- 距离越近，权重越大
- 可加极小值防止除零

| $\alpha$ 值 | 效果 |
|:-----------:|:-----|
| $\alpha = 1$ | 衰减适中，适合一般变形 |
| $\alpha = 2$ | 衰减快，变形更局部化 |
| 高斯核 $w = e^{-d^2/h^2}$ | 平滑衰减，避免硬边界 |

---

## 与 ARAP、TPS 的对比

| 方法 | 核心目标 |
|------|----------|
| **MLS（刚性/相似基函数版本）** | 在每个查询点附近，用**加权最小二乘**拟合**局部刚性变换**（旋转+平移），使重建/插值尽可能保持局部形状。**局部加权拟合**，逐点独立计算，无需全局求解。 |
| **ARAP** | 在网格形变中对每个顶点或面片**惩罚偏离刚性变换的程度**，使局部形变"尽可能刚性"。 |
| **TPS** | 寻找一个**全局光滑函数**，使得控制点精确映射到目标位置，且弯曲能量最小；需解一个大型线性方程组。**全局能量最小化**。 |

> **MLS 是"局部加权拟合"，TPS 是"全局能量最小化"，ARAP 是"网格上的局部刚性约束"。**

---

## 典型应用场景

| 应用 | 推荐方法 | 原因 |
|:-----|:--------:|:-----|
| 人脸美颜 / 表情编辑 | Image MLS | 局部控制、实时、自然 |
| 医学图像非刚性配准 | TPS（或其变种） | 全局光滑、理论成熟 |
| 卡通动画变形 | Image MLS | 交互友好，避免全局抖动 |
| 遥感图像校正 | TPS | 控制点少，需全局一致性 |
| Photoshop 液化工具 | MLS 思想 | 用户拖拽即时反馈 |

### 总结：一句话概括

> **Image MLS** 是"**局部、实时、交互友好**"的变形工具，适合**编辑**；
> **TPS** 是"**全局、光滑、理论严谨**"的插值方法，适合**配准**。

**选择建议：**

- 要实时拖拽、局部变形？→ 选 **Image MLS**
- 要全局对齐、有少量控制点？→ 选 **TPS**
- 要在网格上做形变、保持局部刚性？→ 选 **ARAP**

---

## 参考资料

- Schaefer S, McPhail T, Warren J. **Image deformation using moving least squares**. ACM Transactions on Graphics (TOG), 2006. [原文](https://dl.acm.org/doi/10.1145/1141911.1141919)
- Botsch M, et al. **Polygon Mesh Processing**. Chapter on Deformation.
- Bookstein F L. **Principal warps: Thin-plate splines and the decomposition of deformations**. IEEE TPAMI, 1989.
- Igarashi T, Moscovich T, Hughes J F. **As-rigid-as-possible shape manipulation**. ACM SIGGRAPH, 2005.
