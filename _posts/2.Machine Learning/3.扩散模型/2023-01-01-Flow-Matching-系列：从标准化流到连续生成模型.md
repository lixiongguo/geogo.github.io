---
layout: post
title: "Flow Matching 系列：从标准化流到连续生成模型"
date: 2023-01-01
categories: [扩散模型]
---
在刘慈欣的科幻巨著《三体III·死神永生》中，歌者文明使用了一种终极武器——**二向箔**——将三维空间"压扁"为二维平面。有趣的是，在数学和计算机图形学中，我们也在做一件看似相似的事：将复杂分布"展平"为简单分布再重建。**Flow Matching** 就是这样一种生成建模技术——它通过向量场驱动的连续流，将简单高斯分布优雅地转化为复杂数据分布。

本文是 Flow Matching 系列的**总览**，详细内容请参阅以下四篇：

- [**第一篇：标准化流基础——从离散流到连续流**]({% post_url 2.Machine Learning/Diffusion/3.1.标准化流基础-从离散流到连续流 %})  
  介绍标准化流（Normalizing Flow）和连续标准化流（CNF）的基础概念，包括向量场、ODE、连续性方程等核心数学工具。

- [**第二篇：Flow Matching——仿真无关的连续流训练**]({% post_url 2.Machine Learning/Diffusion/3.2.Flow Matching-仿真无关的连续流训练 %})  
  提出 Flow Matching 训练目标，实现 CNF 的 simulation-free 训练，并介绍最优传输（OT）位移路径的高效性。

- [**第三篇：条件流匹配——条件概率路径与边缘化**]({% post_url 2.Machine Learning/Diffusion/3.3.条件流匹配-条件概率路径与边缘化 %})  
  深入讨论 Flow Matching 的核心理论创新：条件概率路径的构造、边缘化聚合，以及条件流匹配（CFM）目标与 FM 目标的梯度等价性定理。

- [**第四篇：Rectified Flow——直线路径的流模型**]({% post_url 2.Machine Learning/Diffusion/3.4.Rectified Flow-直线路径的流模型 %})  
  介绍 Rectified Flow：学习直线 ODE 路径实现一步生成的方法，包括非交叉性、传输代价降低和 reflow 三个关键特性。

---

## 方法对比总结

| 方法 | 类型 | 核心思想 | 优势 | 局限 |
|:---|:---|:---|:---|:---|
| **Normalizing Flow** | 离散 | 逐层可逆变换堆叠 | 精确似然计算 | 构造可逆网络困难 |
| **CNF** | 连续 | 用 ODE 描述流变换 | 灵活，无需可逆约束 | 训练需要模拟 ODE |
| **Flow Matching** | 连续 | 回归条件向量场，simulation-free | 训练简单，OT 路径高效 | 条件路径设计 |
| **Rectified Flow** | 连续 | 学习直线路径，一步 Euler | 推理极快 | 非线性版复杂度增加 |
