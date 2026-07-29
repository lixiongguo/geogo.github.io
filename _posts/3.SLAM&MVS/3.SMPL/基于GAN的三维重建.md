---
layout: post
title: "基于GAN生成网络的重建"
categories: [TechSharing]
mathjax: true
---

> 路线：**Pix2Pix / CycleGAN**（条件图像翻译与 PatchGAN）→ **Pix2Surf**（衣物 → SMPL UV）→ **Adversarial Loss** 在超分 / 修复等后续视觉任务中的延续。GAN 基础见 [生成模型与 GAN]({% post_url 2.Machine Learning/2.扩散模型/2020-01-11-生成模型与GAN生成对抗网络 %})；感知超分见 [ESRGAN](ESRGAN.md)。

---

## Pix2Pix

> Isola et al., *Image-to-Image Translation with Conditional Adversarial Networks*, CVPR 2017.

### cGAN 开始

Pix2Pix 把图像翻译写成**条件 GAN（cGAN）**：输入条件图 $x$（如语义分割、边缘图），输出目标图 $y$（如照片、上色结果）。生成器 $G$、判别器 $D$ 都看到 $x$：

$$
\mathcal{L}_{\mathrm{cGAN}}(G,D)
=
\mathbb{E}_{x,y}\!\bigl[\log D(x,y)\bigr]
+
\mathbb{E}_{x,z}\!\bigl[\log\bigl(1-D(x,G(x,z))\bigr)\bigr].
$$

实践中再加 $L_1$ 重建，避免只靠对抗而模糊、漂移：

$$
\mathcal{L}_{L_1}(G)=\mathbb{E}_{x,y,z}\bigl[\|y-G(x,z)\|_1\bigr],
\quad
G^*=\arg\min_G\max_D\;
\mathcal{L}_{\mathrm{cGAN}}+\lambda\mathcal{L}_{L_1}.
$$

架构上 $G$ 常用 **U-Net**（跳连保留空间对齐），$D$ 用 **PatchGAN**（只判局部 $N\times N$ 块是否真实，强迫高频细节可信）。

### 为什么 PatchGAN 更好？

判别器的感受野决定它在“管”图像的哪一尺度。Pix2Pix 对比了三种极端：

| 判别器 | 感受野 | 实际效果 |
| :--- | :--- | :--- |
| **PixelGAN**（$1\times1$） | 单像素 | 只对齐颜色直方图，几乎不改空间结构 |
| **ImageGAN**（整图） | 全图 | 参数多、难训；偏重全局是否像真图，对局部纹理约束弱 |
| **PatchGAN**（如 $70\times70$） | 局部块 | 锐利纹理、少模糊；参数少，可卷积滑过任意分辨率 |

**为何局部判决反而更好**（相对整图 $D$）：

1. **与 $L_1$ 分工**：$L_1$ 已能抓住低频（整体布局、大色块）；再让整图 $D$ 重复管低频收益有限。PatchGAN 专盯**高频**——边缘、材质、重复纹理是否像真，两者互补。
2. **马尔可夫假设**：假定相距超过 $N$ 的像素条件独立，图像是**纹理的马尔可夫随机场**。对风格化、上色、分割→照片这类任务，局部统计往往就是“真假”的关键。
3. **参数与泛化**：全卷积、参数量远小于 ImageGAN；同一套 $D$ 可滑窗用于训练时未见过的分辨率。
4. **训练信号更密**：一张图产出许多 patch 判决，梯度更丰富，不易只优化“整图平均看起来还行”而放过局部糊斑。

经验上：$N$ 太小（近 PixelGAN）细节仍弱；$N$ 太大接近 ImageGAN 则纹理变糊、训练变重。中等 patch（论文常用约 70）在质量与开销上折中最好。因此 Pix2Pix 的默认配方是 **U-Net + PatchGAN + $L_1$**。

### 为什么“纯 U-Net”做不好图像翻译？

若只用像素损失（$L_1$ / $L_2$）训练 U-Net：

- **模糊**：像素损失偏好条件均值，高频纹理被平均掉；
- **感知不对齐**：低维语义对了，材质、锐利边缘仍假；
- **无分布约束**：输出只要“靠近 GT 均值”即可，不必落在真实图像流形上。

对抗项逼迫 $G(x)$ 在局部统计上像真图；PatchGAN 正是用低维、局部判决换来锐利纹理。因此 Pix2Pix = **U-Net 对齐结构 + cGAN/PatchGAN 补细节**，而不是单纯回归。

---

## CycleGAN

> Zhu et al., *Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks*, ICCV 2017.

Pix2Pix 需要**成对** $(x,y)$。许多域迁移（照片↔画风、夏↔冬）拿不到配对，CycleGAN 改用**无配对**数据：域 $X$、$Y$ 各有一批样本，学双向映射 $G:X\to Y$、$F:Y\to X$。

- **对抗**：使 $G(X)$ 像 $Y$，$F(Y)$ 像 $X$；
- **循环一致**：强制 $F(G(x))\approx x$、$G(F(y))\approx y$，防止任意一对一乱映射。

$$
\mathcal{L}_{\mathrm{cyc}}(G,F)
=
\mathbb{E}_{x\sim X}\bigl[\|F(G(x))-x\|_1\bigr]
+
\mathbb{E}_{y\sim Y}\bigl[\|G(F(y))-y\|_1\bigr].
$$

总目标大致为两个域的 GAN 损失 + $\lambda\mathcal{L}_{\mathrm{cyc}}$（常再加 identity 损失稳住色彩）。相对 Pix2Pix：牺牲配对监督的精度，换来无标注域迁移能力；三维重建管线里常作**外观迁移 / 数据增广**前置，而不是直接出几何。

---

## Pix2Surf

> Mir, Alldieck, Pons-Moll. *Learning to Transfer Texture from Clothing Images to 3D Humans*, CVPR 2020.

将普通照片中衣物的纹理贴到 3D 网格模型上（兼容 SMPL + 参数化衣物模板），实时虚拟试穿。

![image-20251113112342478](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251113112342478.png)

### 问题设定

电商图（正/背）纹理丰富，但姿态、尺码、背景各异。目标：把 2D 衣物外观映射到预定义 3D 衣物表面的 **UV 纹理图**，再随 SMPL 姿态/体型变换。

### 两阶段思路

1. **离线非刚性配准（慢但准）**  
   自动分割（GrabCut）→ 用 MGN 式参数化衣物 $G(\theta,\beta)$（SMPL 子网格 + 位移）拟合轮廓 → 再自由顶点非刚变形合边界。得到图像像素 ↔ 3D 表面稠密对应，但单张约数分钟，且偶发失败。

![image-20251113112508975](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251113112508975.png)

2. **学习 Pix2Surf（快）**  
   只用成功配准样本训练 CNN，测试时毫秒级出对应，无需再跑优化。

### 为什么不直接做 Pix2Pix 式图像翻译？

直接学 $I\mapsto Y$（照片 → UV 纹理）容易**过拟合到训练纹理外观**，对新花色泛化差。关键假设：

> **图像像素 ↔ UV 的光滑对应只依赖轮廓形状，不依赖纹理颜色。**

因此输入不用 RGB，而用 **坐标掩膜（coordinate mask）** $X$：前景像素存自身坐标 $(i,j)$，背景为 $0$。网络 $f$ 预测 **UV 对应图** $C$：每个 UV 位置 $(k,l)$ 给出应对齐的图像坐标 $C_{k,l}=(i,j)$，再可微采样得到纹理。

相对直接回归颜色：对应场变化远小于外观空间，更易泛化到未见花纹。

### 用了哪些方法？（相对朴素翻译的加强）

![image-20251113112317601](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251113112317601.png)

| 组件 | 作用 |
| :--- | :--- |
| **非刚性配准造伪标签** | 轮廓项 + 形状先验 + 耦合 / 边 / Laplacian，得到 $C,Y$ |
| **坐标掩膜输入** | 强迫网络看形状而非颜色 |
| **预测对应而非 RGB** | 几何对应 + 从原图采样，避免编造纹理 |
| **损失组合** | $\mathcal{L}_{\mathrm{reg}}$（对应 $L_2$）+ $\mathcal{L}_{\mathrm{recon}}$（可微采样光度）+ $\mathcal{L}_{\mathrm{perc}}$（感知）+ $\mathcal{L}_{\mathrm{tv}}$（平滑） |
| **自定义 UV** | 衣物切成前/后两大岛，避免 SMPL 官方 UV 碎片化导致映射不连续 |
| **分割网络** | 测试时去背景；T 恤正视图还需去掉可见的后片面料 |

对比基线：Shape Context + TPS 翘曲、直接 Pix2Pix 出纹理图——Pix2Surf 在真实感与泛化上更稳，且比优化配准快几个数量级。

### 运行效果

![image-20251022100821749](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251022100821749.png)

![image-20251022100843489](https://lgximgs.oss-cn-beijing.aliyuncs.com/images/image-20251022100843489.png)

---

## 后续视觉算法中的 Adversarial Loss

Pix2Pix / CycleGAN 把对抗损失定型为：**像素 / 重建项管对齐与低频，对抗项把输出推进真实图像流形、补高频**。同一配方在后续视觉任务里反复出现（常写作 $\mathcal{L}_{\mathrm{adv}}$ 或 $\ell_{\mathrm{Gen}}$）。

一般形式（生成器侧，非饱和写法）：

$$
\mathcal{L}_{\mathrm{adv}}(G)
=
\mathbb{E}_{x}\!\bigl[-\log D(G(x))\bigr]
\quad\text{或}\quad
\mathbb{E}\bigl[(D(G(x))-1)^2\bigr]
\ \text{（LSGAN）}.
$$

与重建 / 感知项加权：$\mathcal{L}=\mathcal{L}_{\mathrm{rec}}+\lambda_{\mathrm{adv}}\mathcal{L}_{\mathrm{adv}}+\cdots$，其中 $\lambda_{\mathrm{adv}}$ 通常很小（如 SRGAN 的 $10^{-3}$），避免生成器只顾骗 $D$ 而丢掉内容。

### 典型下游

| 方向 | 代表 | 对抗损失扮演的角色 |
| :--- | :--- | :--- |
| **感知超分** | SRGAN / [ESRGAN](ESRGAN.md) | 对抗 + 感知损失对抗 MSE 过平滑；ESRGAN 再用 **RaGAN**（相对真假）加强纹理 |
| **高分辨率翻译** | pix2pixHD、SPADE | 多尺度 PatchGAN，管不同频率的真假 |
| **人脸修复 / 美颜** | GFPGAN 等；端上磨皮通路 | 对抗项恢复肤质、毛发等高频，避免纯回归“塑料脸” |
| **域自适应** | DANN、CycleGAN 式 | 特征或图像级对抗，缩小源/目标域差距 |
| **新视图 / 外观生成** | 部分 NeRF / 纹理补全变体 | 渲染图过判别器，减轻模糊、提升照片感（非所有 NeRF 默认使用） |
| **几何+外观联合** | 部分人体 / 衣物重建 | 渲染结果或 UV 纹理上加 $\mathcal{L}_{\mathrm{adv}}$，外观更自然 |

### 和 PatchGAN 的延续关系

- **超分、修复、翻译**：多数仍用 **局部 / 多尺度判别器**（PatchGAN 思想），而不是单标量“整图真假”。
- **Relativistic / hinge / WGAN-GP**：改的是对抗目标与训练稳定性，**“用 $D$ 约束分布、用重建约束内容”** 的分工不变。
- **工程取舍**：$\lambda_{\mathrm{adv}}$ 过大 → 假纹理、伪影；过小 → 退回模糊回归。ESRGAN 的网络插值、两阶段预训练，都是在调这条权衡。

一句话：Adversarial Loss 在视觉里几乎总是**感知真实感的正则**，不是替代几何或对应监督；Pix2Surf 甚至刻意少用“直接 GAN 出纹理”，改预测对应——说明对抗很强，但任务不对时不如几何归纳偏置。

---

## 小结

| 方法 | 输入 → 输出 | 监督 | 与 3D 的关系 |
| :--- | :--- | :--- | :--- |
| Pix2Pix | 条件图 → 目标图 | 成对 + PatchGAN | 2D 翻译；可作纹理预处理 |
| CycleGAN | 域 $X$ ↔ 域 $Y$ | 无配对 + 对抗 | 域迁移 / 增广 |
| Pix2Surf | 衣物照片 → UV 纹理 | 配准伪标签（偏对应） | 纹理上 SMPL 衣物，真·3D 试穿 |
| SRGAN / ESRGAN 等 | LR → HR 等 | 对抗 + 感知 / 像素 | 提升外观真实感，常接重建管线后处理 |

共同主线：用 **2D 生成 / 对应学习 / 对抗真实感** 绕开昂贵标注或弥补像素损失的平滑，把外观接到可动画的人体/衣物网格或成像管线上。

---

## 参考文献

1. Ian Goodfellow et al. *Generative Adversarial Nets*. NeurIPS 2014.
2. Mehdi Mirza, Simon Osindero. *Conditional Generative Adversarial Nets*. arXiv:1411.1784, 2014.
3. Phillip Isola, Jun-Yan Zhu, Tinghui Zhou, Alexei A. Efros. *Image-to-Image Translation with Conditional Adversarial Networks*. CVPR 2017. ([Pix2Pix](https://phillipi.github.io/pix2pix/))
4. Jun-Yan Zhu, Taesung Park, Phillip Isola, Alexei A. Efros. *Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks*. ICCV 2017. ([CycleGAN](https://junyanz.github.io/CycleGAN/))
5. Aymen Mir, Thiemo Alldieck, Gerard Pons-Moll. *Learning to Transfer Texture from Clothing Images to 3D Humans*. CVPR 2020. ([Pix2Surf](https://virtualhumans.mpi-inf.mpg.de/pix2surf/))
6. Christian Ledig et al. *Photo-Realistic Single Image Super-Resolution Using a Generative Adversarial Network*. CVPR 2017. (SRGAN)
7. Xintao Wang et al. *ESRGAN: Enhanced Super-Resolution Generative Adversarial Networks*. ECCVW 2018.
8. Ting-Chun Wang et al. *High-Resolution Image Synthesis and Semantic Manipulation with Conditional GANs*. CVPR 2018. (pix2pixHD，多尺度 PatchGAN)
9. Matthew Loper et al. *SMPL: A Skinned Multi-Person Linear Model*. SIGGRAPH Asia 2015.
10. Bharat Lal Bhatnagar et al. *Multi-Garment Net: Learning to Dress 3D People from Images*. ICCV 2019.
11. Justin Johnson, Alexandre Alahi, Li Fei-Fei. *Perceptual Losses for Real-Time Style Transfer and Super-Resolution*. ECCV 2016.
12. Max Jaderberg et al. *Spatial Transformer Networks*. NeurIPS 2015.
