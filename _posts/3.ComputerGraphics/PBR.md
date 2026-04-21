---
layout: post
title: "PBR（基于物理的渲染）"
date: 2025-10-30
categories: [3.ComputerGraphics, Game&Shaders]
---

PBR（Physically Based Rendering，基于物理的渲染）是一组基于真实世界光学物理规律的渲染技术。相比传统的 Phong / Blinn-Phong 经验模型，PBR 使用更符合物理的光照模型，使得材质在不同光照环境下表现一致且自然。

---

## 1. PBR 与传统渲染的区别

| 维度 | 传统渲染（Phong） | PBR |
|:---|:---|:---|
| **理论基础** | 经验公式，不遵循物理 | 基于光学物理（辐射度量学） |
| **参数含义** | 抽象系数（ambient/diffuse/specular/shininess） | 物理参数（albedo/metallic/roughness/IOR） |
| **光照适应性** | 同一材质在不同光照下表现不一致 | 材质参数与光照无关，任何环境下都正确 |
| **能量守恒** | ❌ 无保证 | ✅ 出射光能量 ≤ 入射光能量 |
| **艺术家工作量** | 需为每种光照调整材质参数 | 一次设置，到处使用 |

---

## 2. 渲染方程（Reflectance Equation）

PBR 的理论基础是 Kajiya（1986）提出的渲染方程：

$$L_o(\mathbf{p}, \omega_o) = \int_{\Omega^+} f_r(\mathbf{p}, \omega_i, \omega_o) \cdot L_i(\mathbf{p}, \omega_i) \cdot (\mathbf{n} \cdot \omega_i) \, d\omega_i$$

| 符号 | 含义 |
|:---|:---|
| $L_o(\mathbf{p}, \omega_o)$ | 点 $\mathbf{p}$ 沿观察方向 $\omega_o$ 的出射辐射率 |
| $L_i(\mathbf{p}, \omega_i)$ | 沿入射方向 $\omega_i$ 的入射辐射率 |
| $f_r(\mathbf{p}, \omega_i, \omega_o)$ | BRDF（双向反射分布函数） |
| $\mathbf{n} \cdot \omega_i$ | 余弦项（Lambert 定律） |
| $\Omega^+$ | 上半球面 |

> 渲染方程本质上在问：**点 $\mathbf{p}$ 沿方向 $\omega_o$ 出射了多少光？** 答案是：所有入射方向的入射光，经 BRDF 反射后的积分。

---

## 3. BRDF 与 Cook-Torrance 模型

### 3.1 BRDF

BRDF（Bidirectional Reflectance Distribution Function）描述了入射光如何被反射到出射方向：

$$f_r(\omega_i, \omega_o) = \frac{\text{出射亮度}}{\text{入射照度}}$$

在 PBR 中，BRDF 被分为**漫反射**和**镜面反射**两部分：

$$f_r = k_d \cdot f_{\text{lambert}} + k_s \cdot f_{\text{cook-torrance}}$$

### 3.2 Lambert 漫反射

漫反射假设光在表面内部均匀散射，各方向出射光等量：

$$f_{\text{lambert}} = \frac{c}{\pi}$$

其中 $c$ 是表面颜色（albedo）。除以 $\pi$ 是归一化因子，确保半球积分等于 albedo。

### 3.3 Cook-Torrance 镜面反射

Cook-Torrance（1982）基于**微平面理论**，是 PBR 中最常用的镜面 BRDF：

$$f_{\text{cook-torrance}} = \frac{D(\mathbf{h}) \cdot F(\omega_o, \mathbf{h}) \cdot G(\omega_i, \omega_o, \mathbf{h})}{4 \cdot (\mathbf{n} \cdot \omega_i) \cdot (\mathbf{n} \cdot \omega_o)}$$

其中 $\mathbf{h} = \frac{\omega_i + \omega_o}{\|\omega_i + \omega_o\|}$ 是**半程向量（Halfway Vector）**。

三项分别对应微平面理论的三个核心函数（**DFG**）：

---

## 4. DFG 三大核心函数

### 4.1 D — 法线分布函数（Normal Distribution Function）

描述微平面的法线与半程向量 $\mathbf{h}$ 对齐的程度。值越大，镜面高光越集中。

**GGX / Trowbridge-Reitz 分布**（最常用）：

$$D_{\text{GGX}}(\mathbf{h}) = \frac{\alpha^2}{\pi \cdot ((\mathbf{n} \cdot \mathbf{h})^2 \cdot (\alpha^2 - 1) + 1)^2}$$

其中 $\alpha = \text{roughness}^2$ 是粗糙度的平方。

| 粗糙度 | 效果 |
|:---|:---|
| $\alpha \to 0$ | NDF 趋近 Dirac delta，高光极度集中（镜面） |
| $\alpha \to 1$ | NDF 接近均匀分布，高光极度弥散（粗糙表面） |

### 4.2 F — 菲涅尔方程（Fresnel Equation）

描述反射率随入射角变化。掠射角（grazing angle）时反射更强——这就是为什么水面远看比近看更亮。

**Schlick 近似**（工程中最常用）：

$$F_{\text{Schlick}}(\cos\theta, F_0) = F_0 + (1 - F_0) \cdot (1 - \cos\theta)^5$$

其中 $F_0$ 是法向入射时的基础反射率（即 $\cos\theta = 1$ 时的反射率）：

| 材质类型 | $F_0$ |
|:---|:---|
| **电介质（非金属）** | 0.02 ~ 0.05（常见值 0.04） |
| **导体（金属）** | 0.5 ~ 1.0（来自 albedo 颜色的 RGB 分量） |

### 4.3 G — 几何函数（Geometry Function）

描述微平面之间的**自遮挡（self-shadowing）**。粗糙表面上，凹陷处的微平面会被邻近的微平面遮挡，导致部分光线无法反射。

**Smith-GGX 几何函数**：

$$G_{\text{Smith-GGX}}(\omega_i, \omega_o) = G_1(\omega_o) \cdot G_1(\omega_i)$$

$$G_1(\mathbf{v}) = \frac{\mathbf{n} \cdot \mathbf{v}}{(\mathbf{n} \cdot \mathbf{v})(1 - k) + k}$$

其中 $k = \frac{(\alpha + 1)^2}{8}$（Schlick-GGX 近似中的 $k$ 值）。

| 效果 | 说明 |
|:---|:---|
| **粗糙度低** | $k$ 小，遮挡少，$G \approx 1$ |
| **粗糙度高** | $k$ 大，遮挡严重，$G$ 在掠射角时显著下降 |
| **几何函数 + 菲涅尔** | 掠射角时两者都导致镜面反射减少，**但在物理上菲涅尔增加更快**，因此总效果是掠射角反射增强 |

---

## 5. 能量守恒

PBR 的一个核心约束：**出射光总能量不超过入射光能量**。

在实现中，通过控制漫反射和镜面反射的比例来保证：

$$k_d + k_s \leq 1$$

- $k_s = F$（菲涅尔项给出的镜面反射比例）
- $k_d = (1 - k_s) \times (1 - \text{metallic})$（非金属才有漫反射）

**金属**：metallic = 1 → $k_d = 0$（无漫反射，所有光都被镜面反射，颜色来自反射光）
**非金属**：metallic = 0 → $k_d = 1 - F$（有漫反射颜色，镜面反射几乎无色）

---

## 6. PBR 材质参数与贴图

### 6.1 核心参数

| 参数 | 含义 | 取值范围 | 对应贴图 |
|:---|:---|:---|:---|
| **Albedo / Base Color** | 表面基础颜色（无光照信息） | RGB [0,1] | Albedo Map |
| **Metallic** | 是否为金属 | 0（非金属）或 1（金属） | Metallic Map |
| **Roughness** | 表面粗糙度 | 0（光滑镜面）~ 1（粗糙漫射） | Roughness Map |
| **AO** | 环境光遮蔽 | [0,1]，0 = 完全遮蔽 | AO Map |
| **Normal** | 表面法线扰动 | RGB 编码的 XYZ 法线 | Normal Map |

### 6.2 可选参数

| 参数 | 含义 | 用途 |
|:---|:---|:---|
| **Emissive** | 自发光 | 发光屏幕、LED、火焰 |
| **Height / Displacement** | 表面高度/位移 | 视差映射（Parallax Mapping）或曲面细分（Tessellation） |
| **Opacity** | 不透明度 | 半透明材质（玻璃、叶片） |
| **Clearcoat** | 透明涂层 | 车漆、钢琴漆（Disney BRDF 扩展） |
| **Sheen** | 绒毛边缘反射 | 布料、天鹅绒 |
| **Transmission** | 透射 | 玻璃、水（替代不透明的折射建模） |
| **IOR** | 折射率 | 非金属的 $F_0$ 计算来源 |

### 6.3 贴图色彩空间

| 贴图 | 色彩空间 | 原因 |
|:---|:---|:---|
| **Albedo** | **sRGB** | 包含人眼感知的非线性颜色信息 |
| **Normal / Metallic / Roughness / AO** | **Linear** | 是物理参数，不应经过 gamma 校正 |

> ⚠️ **常见错误**：将 sRGB 的 albedo 贴图当作 Linear 读取，导致渲染结果偏暗。应确保在着色器中正确进行 sRGB → Linear 的转换。

### 6.4 Albedo 贴图的注意事项

Albedo 贴图是**纯颜色**，不应包含：

| ❌ 不应包含 | ✅ 正确做法 |
|:---|:---|
| 光照/阴影信息 | 纯净的表面颜色 |
| 高光/反射 | 反射信息由 PBR 着色器计算 |
| 法线/凹凸细节 | 几何细节由 Normal Map 提供 |
| 脏迹/污渍（应为独立层） | 脏迹通过独立贴图叠加 |

---

## 7. 金属度-粗糙度工作流（Metalness-Roughness Workflow）

这是当前游戏和实时渲染中最主流的 PBR 工作流（由 Disney/Pixar 推广，UE4/Unity 标配）。

**核心思想**：用两张贴图（Metallic + Roughness）替代传统工作流中的多张贴图，简化材质定义。

### 7.1 金属 vs 非金属的行为差异

| 属性 | 非金属（绝缘体） | 金属（导体） |
|:---|:---|:---|
| **$F_0$** | 0.04（近似常数） | 来自 albedo 的 RGB 分量（0.5~1.0） |
| **漫反射** | ✅ 有（albedo 颜色） | ❌ 无（albedo 被忽略） |
| **镜面反射颜色** | 无色（白色高光） | 有色（来自 albedo） |
| **Albedo 贴图含义** | 表面颜色 | 反射颜色（非视觉颜色） |

### 7.2 着色器伪代码

```
function PBRShading(point, normal, viewDir, lightDir, lightColor, params):
    h = normalize(viewDir + lightDir)

    // 能量守恒
    F0 = lerp(vec3(0.04), params.albedo, params.metallic)
    ks = FresnelSchlick(max(dot(viewDir, h), 0), F0)
    kd = (1 - ks) * (1 - params.metallic)

    // Cook-Torrance 镜面反射
    D = DistributionGGX(normal, h, params.roughness)
    G = GeometrySmith(normal, viewDir, lightDir, params.roughness)
    F = FresnelSchlick(max(dot(viewDir, h), 0), F0)

    nominator = D * G * F
    denominator = 4 * max(dot(normal, lightDir), 0) * max(dot(normal, viewDir), 0) + 0.001
    specular = nominator / denominator

    // 漫反射（Lambert）
    diffuse = params.albedo / PI

    // 合成
    Lo = (kd * diffuse + ks * specular) * lightColor
       * max(dot(normal, lightDir), 0)

    // 环境光遮蔽
    Lo *= params.ao

    // 自发光
    Lo += params.emissive

    return Lo
```

---

## 8. 与传统 Blinn-Phong 的对比

```
// 传统 Blinn-Phong（经验模型）
color = ambient + diffuse * max(N·L, 0) + specular * pow(max(N·H, 0), shininess)

// PBR Cook-Torrance（物理模型）
color = (kd * albedo/π + ks * D*F*G / (4*(N·L)*(N·V))) * radiance * N·L
```

| 维度 | Blinn-Phong | Cook-Torrance PBR |
|:---|:---|:---|
| **漫反射** | Lambert（相同） | Lambert（相同） |
| **镜面反射** | $\cos^n(\mathbf{N} \cdot \mathbf{H})$ 经验公式 | D·F·G 物理模型 |
| **菲涅尔** | 无（或简单混合） | Schlick 近似 |
| **能量守恒** | ❌ | ✅ |
| **参数** | shininess（无物理含义） | roughness（物理参数） |
| **金属支持** | 困难（需手动调参） | 原生支持 |

---

## 参考

- Cook, R. L., & Torrance, K. E. (1982). "A reflectance model for computer graphics." *ACM TOG*.
- Kajiya, J. T. (1986). "The rendering equation." *SIGGRAPH*.
- Walter, B., et al. (2007). "Microfacet models for refraction through rough surfaces." *EGSR*.
- Burley, B. (2012). "Physically-based shading at Disney." *SIGGRAPH Course*.
- Pharr, M., Jakob, W., & Humphreys, G. (2016). *Physically Based Rendering: From Theory to Implementation* (3rd ed.).
- LearnOpenGL CN: [PBR 理论](https://learnopengl-cn.github.io/07%20PBR/01%20Theory/)
- ISUX: [The PBR Guide](https://isux.tencent.com/articles/THE-PBR-GUIDE-1.html)
