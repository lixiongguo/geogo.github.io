## 三角面翻转与MIPS能量

<img src="https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20250227120632868.png" alt="image-20250227120632868" style="zoom: 80%;" />

对于一些带有突出部分的曲面等复杂形状，如果参数化过程只是对共形能量或等距能量进行优化那么可能会造成**三角面的翻转**，而MIPS能量和对称Dirichlet能量都有对翻转进行惩罚。

其中MIPS（Most Isometric ParameterizationS）能量定义为奇异值之比：
$$
E_{\text{MIPS}} = \frac{\sigma_1}{\sigma_2} + \frac{\sigma_2}{\sigma_1}
$$

若直接对 $\sigma_1, \sigma_2$ 做优化，需要反复 SVD 分解且无法得到闭式梯度，难以高效求解。因此 MIPS 的关键在于**用 Jacobian 矩阵的代数不变量消去 SVD**。

利用恒等式 $\sigma_1^2 + \sigma_2^2 = \|J_t\|_F^2$ 和 $\sigma_1\sigma_2 = \det(J_t)$：

$$
E_{\text{MIPS}} = \frac{\sigma_1}{\sigma_2} + \frac{\sigma_2}{\sigma_1}
= \frac{\sigma_1^2 + \sigma_2^2}{\sigma_1 \sigma_2}
= \frac{\|J_t\|_F^2}{\det(J_t)}
$$

对每个三角形 $t$，$J_t$ 的分量是 UV 坐标的线性函数，因此 $E_{\text{MIPS}}$ 变为 UV 坐标的**有理函数**——分子是二次型，分母是三角形面积（亦为 UV 坐标的双线性形式）。

对三角网格，总能量为按面积加权的求和：

$$
E_{\text{MIPS}} = \sum_{t} A_t^{\text{3D}} \cdot \frac{\|J_t\|_F^2}{\det(J_t)}
$$

其中 $A_t^{\text{3D}}$ 是三角面片 $t$ 在原始 3D 曲面上的面积。$\det(J_t) > 0$ 保证无翻转，因此 MIPS 是**自障碍函数**（self-barrier）：翻转时 $\det(J_t) \to 0^+$ 导致能量趋于无穷大。

MIPS 与对称 Dirichlet 两者都充当翻转 barrier，但行为不同：

$$
E_{\text{MIPS}} = \frac{\sigma_1}{\sigma_2} + \frac{\sigma_2}{\sigma_1},\qquad
E_{\text{SD}} = \sigma_1^2 + \sigma_2^2 + \sigma_1^{-2} + \sigma_2^{-2}
$$

MIPS 仅阻止 $\sigma_i \to 0$（分母趋于零），而**对称 Dirichlet 同时阻止压缩（$\sigma_i \to 0$）和拉伸（$\sigma_i \to \infty$）**，因此对等距性的约束更强。在实践上，对称 Dirichlet 是更稳健的选择，但 MIPS 的化简形式 $\|J_t\|_F^2 / \det(J_t)$ 因其简洁性在教学中被广泛引用。