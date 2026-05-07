---
layout: post
title: "最优传输3-顾老师的Semi-Discrete解法"
categories  : OptimalTransport
---

半离散最优传输的变分原理

顾老师这条 Semi-Discrete OT 路线可以概括为：  
**凸几何（Minkowski/Alexandrov） -> 对偶势函数 -> 凹能量优化 -> Laguerre 单元质量匹配**。

## 1) 凸几何起点：Minkowski 问题

经典的 Minkowski 问题关注：给定法向与面积测度，是否存在对应凸体，并且是否唯一（在平移意义下）。

![image-20250928211208672](..\..\..\imgs\image-20250928211208672.png)

**图像摘要**：该图强调“几何测度 -> 凸体形状”的反问题思想，这是半离散 OT 变分框架的几何来源。

## 2) Alexandrov 拓展

![image-20250928200336960](..\..\..\imgs\image-20250928200336960.png)

**图像摘要**：Alexandrov 将 Minkowski 问题推广到更弱正则与更一般测度情形，使“离散面积匹配”具有严谨的存在唯一性基础。  
在 OT 语境下，这对应“每个单元质量必须匹配目标权重”。

### 中心定理

![image-20250928200412933](..\..\..\imgs\image-20250928200412933.png)

**图像摘要**：中心定理给出“几何构造问题 <-> 变分极值问题”的桥梁，为数值算法提供可优化目标函数。

## 3) Legendre-Fenchel 对偶

![image-20250928214054586](..\..\..\imgs\image-20250928214054586.png)

**图像摘要**：通过 Legendre-Fenchel 对偶，把映射/分割问题转成势函数优化问题。  
在半离散 OT 中，常用权重（或势）$\psi_i$ 定义 Laguerre 单元：

$$
L_i(\psi)=\{x\in\Omega\mid c(x,y_i)-\psi_i\le c(x,y_j)-\psi_j,\ \forall j\}.
$$

质量约束是

$$
\int_{L_i(\psi)} \rho(x)\,dx = m_i,\qquad \sum_i m_i=\int_\Omega \rho(x)\,dx.
$$

对应的变分目标（符号按常见文献写法）可写为

$$
E(\psi)=\sum_i \psi_i m_i-\int_\Omega \min_j\big(c(x,y_j)-\psi_j\big)\rho(x)\,dx.
$$

其梯度为残差：

$$
\frac{\partial E}{\partial \psi_i}=m_i-|L_i(\psi)|.
$$

## 4) Alexandrov 变分证明与 Hessian 结构

![image-20250928214253775](..\..\..\imgs\image-20250928214253775.png)

**图像摘要**：该图强调目标能量的良好曲率性质（常见为凹/凸结构，取决于符号约定），以及 Hessian 稀疏、对角占优倾向。  
这正是 Newton 或阻尼 Newton 可高效收敛的原因。

## 5) 计算示意图与算法直觉

![image-20250928214324614](..\..\..\imgs\image-20250928214324614.png)

**图像摘要**：图中展示了加权单元划分随权重更新而变化，直到各单元质量匹配。  
从工程角度，算法可以写成：

1. 初始化权重 $\psi$；  
2. 构造 Laguerre/Power 图并计算每个单元质量；  
3. 计算残差 $r_i=m_i-|L_i(\psi)|$；  
4. 用 Newton/L-BFGS/梯度法更新 $\psi$；  
5. 残差足够小则停止。

## 6) 小补充：为什么这套方法实用

- 把 OT 主问题降成低维权重优化（变量数约为目标点数）；  
- 几何意义清晰（每一步都可视化为单元形变）；  
- 易于与图形学任务结合（网格参数化、重采样、面积控制）。

因此，顾老师的 Semi-Discrete 解法可以理解为“几何理论驱动的优化算法”：  
既有凸几何支撑，又有可落地的数值流程。

## 参考文献

- Villani, C. (2009). *Optimal Transport: Old and New*. Springer.
- Peyre, G., & Cuturi, M. (2019). *Computational Optimal Transport*. Foundations and Trends in Machine Learning.
- Brenier, Y. (1991). *Polar factorization and monotone rearrangement of vector-valued functions*.
- Benamou, J.-D., & Brenier, Y. (2000). *A computational fluid mechanics solution to the Monge-Kantorovich mass transfer problem*.
- Cuturi, M. (2013). *Sinkhorn distances: Lightspeed computation of optimal transport*.
