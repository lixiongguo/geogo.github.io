---
layout: post
title: "扩散模型系列：DDPM、DDIM 与 Score Matching"
date: 2022-09-01
categories: [扩散模型]
---
扩散模型是当前生成式 AI 的核心技术之一。从 DDPM 的马尔可夫链去噪，到 DDIM 的确定性加速采样，再到 Score Matching 的统一得分框架——这些方法共享相同的数学内核，但各有侧重。

本文是扩散模型系列的**总览**，详细内容请参阅以下三篇：

- [**第一篇：DDPM——前向扩散与逆向去噪**]({% post_url 2.Machine Learning/Diffusion/2.1.DDPM-前向扩散与逆向去噪 %})  
  介绍 DDPM 的核心原理：前向马尔可夫加噪过程、逆向去噪过程、变分训练目标，以及其 VP-SDE 形式。

- [**第二篇：DDIM——隐式确定性采样加速**]({% post_url 2.Machine Learning/Diffusion/2.2.DDIM-隐式确定性采样加速 %})  
  介绍 DDIM 如何通过非马尔可夫前向过程和确定性采样，将 1000 步降至 50-100 步，并揭示其与概率流 ODE 的联系。

- [**第三篇：Score Matching——基于得分的生成模型**]({% post_url 2.Machine Learning/Diffusion/2.3.ScoreMatching-基于得分的生成模型 %})  
  介绍得分匹配的统一框架：得分函数、去噪得分匹配（DSM）、Langevin 动力学采样，以及 Score Matching ↔ DDPM ↔ EDM 的内在联系。

---

## 三方法对比

| 维度 | DDPM | DDIM | Score Matching |
|:---|:---|:---|:---|
| **前向过程** | 马尔可夫链 | 非马尔可夫 | 多噪声水平加噪 |
| **逆向过程** | 逆向马尔可夫链 | 确定性隐式采样 | Langevin 动力学 |
| **训练目标** | $\|\epsilon - \epsilon_\theta\|^2$ | 同 DDPM | $\|s_\theta - \nabla \log q\|^2$ |
| **采样速度** | 慢（与训练步数一致） | 快（50-100 步） | 中等（需多步 Langevin） |
| **核心数学** | ELBO 变分推断 | PF-ODE 一阶离散 | 得分函数梯度场 |
| **关系** | = VP-SDE 离散化 | = DDPM 的 ODE 极限 | = DDPM 的前身/统一框架 |
