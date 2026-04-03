## 利用 MLS 做网格变形

![image-20251218190043391](..\..\..\..\imgs\image-20251218190043391.png)

移动最小二乘法是一种用于**局部拟合数据点**的方法，常用于曲线/曲面重建、散乱数据插值等。它的核心思想是：

> 在每个目标点附近，用加权最小二乘法拟合一个局部多项式（比如常数、线性函数），权重由目标点与邻近点的距离决定（越近权重越大）。

**移动最小二乘（Moving Least Squares, MLS）** 和 **As-Rigid-As-Possible (ARAP)** 确实**思路高度相近**，甚至可以说 ARAP 是 MLS 思想在**几何形变（deformation）领域**的一种具体化、优化和推广。使用 MLS 不需要先进行三角化。

![image-20251218192214246](..\..\..\..\imgs\image-20251218192214246.png)

### MLS 形变：控制点与仿射拟合

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

$\hat{p}_i$、$\hat{q}_i$ 即相对加权重心的坐标。注意 $M$ 不必是一般仿射矩阵；论文中进一步限制为相似变换、刚性变换等以控制局部剪切与缩放。

### 与 ARAP 的对比（概念）

| 方法 | 核心目标 |
|------|----------|
| MLS（刚性基函数版本） | 在每个查询点附近，用**加权最小二乘**拟合**局部刚性变换**（旋转+平移），使重建/插值尽可能保持局部形状。 |
| ARAP | 在网格形变中对每个顶点或面片**惩罚偏离刚性变换的程度**，使局部形变“尽可能刚性”。 |

（上表与原文插图一致，可对照下图。）

![image-20251218194058586](..\..\..\..\imgs\image-20251218194058586.png)

---

## 最简单的 MLS：一维线性例子

**目标**：用**线性 MLS** 估计函数在 $x=1$ 处的值，基于三个散乱数据点：

| $x_i$ | $y_i$ |
|:-----:|:-----:|
| 0 | 1 |
| 1 | 2 |
| 2 | 1 |

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
