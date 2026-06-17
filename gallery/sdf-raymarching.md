## SDF（有符号距离场）

SDF（Signed Distance Function / Signed Distance Field）是空间中每个点到最近表面的**有符号距离**：点在物体内部为负值，外部为正值，表面为零。

$$f(\mathbf{p}) = d(\mathbf{p}, \text{surface}) \cdot \text{sign}(\text{inside})$$

### 基本图元

| 图元 | SDF 表达式 | 
|:---|:---|
| **球体** | $f(\mathbf{p}) = \|\mathbf{p} - \mathbf{c}\| - r$ |
| **立方体** | $f(\mathbf{p}) = \max(\|p_x\|,\ \|p_y\|,\ \|p_z\|) - s$ |
| **平面** | $f(\mathbf{p}) = \mathbf{p} \cdot \mathbf{n} - d$ |
| **圆环** | $f(\mathbf{p}) = \|(\sqrt{p_x^2 + p_z^2} - R,\ p_y)\| - r$ |
| **圆柱** | $f(\mathbf{p}) = \|(p_x,\ p_z)\| - r$（裁剪 y 后） |

### 组合操作（CSG）

| 操作 | 表达式 |
|:---|:---|
| **并集** | $\min(f_1, f_2)$ |
| **交集** | $\max(f_1, f_2)$ |
| **差集** | $\max(f_1, -f_2)$ |
| **光滑混合** | $\text{smin}(f_1, f_2, k)$ |

光滑混合（Smooth Minimum）：

$$\text{smin}(a, b, k) = -\log\left(e^{-k \cdot a} + e^{-k \cdot b}\right) \cdot \frac{1}{k}$$

```glsl
float smin(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0) / k;
    return min(a, b) - h * h * k * 0.25;
}
```

### 形变

| 形变 | 操作 |
|:---|:---|
| **平移** | $f(\mathbf{p} - \mathbf{t})$ |
| **旋转** | $f(R^{-1} \cdot \mathbf{p})$ |
| **缩放** | $f(\mathbf{p} / s) \cdot s$ |
| **镜像** | $f(\text{abs}(\mathbf{p}))$ — 在原点处镜像 |
| **重复/平铺** | $f(\text{mod}(\mathbf{p}, c) - c/2)$ — 无限周期复制 |

---

## Ray Marching（光线步进）

Ray Marching 是结合 SDF 的实时渲染方法。核心算法是 **Sphere Tracing**：

### 算法

```glsl
vec3 rayMarch(vec3 ro, vec3 rd) {
    float t = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = ro + rd * t;       // 当前采样点
        float d = sdfScene(p);       // 到最近表面的距离
        if (d < EPS) break;          // 击中表面
        t += d;                      // 安全步进
        if (t > FAR) break;          // 超出范围
    }
    return ro + rd * t;
}
```

**关键洞察**：SDF 给出的距离保证了以该距离为半径的球体内**不会碰到任何表面**，因此可以安全地一次前进 `d` 的距离。

### 法线计算

通过梯度近似：

```glsl
vec3 calcNormal(vec3 p) {
    float h = 0.001;
    return normalize(vec3(
        sdfScene(p + vec3(h, 0, 0)) - sdfScene(p - vec3(h, 0, 0)),
        sdfScene(p + vec3(0, h, 0)) - sdfScene(p - vec3(0, h, 0)),
        sdfScene(p + vec3(0, 0, h)) - sdfScene(p - vec3(0, 0, h))
    ));
}
```

### AO（环境光遮蔽）

在法线方向采样几步 SDF，距离越近越暗：

$$AO = \frac{1}{n} \sum_{i=1}^{n} \max\left(0,\ \frac{\text{sdf}(p + N \cdot t_i) - t_i}{t_i}\right)$$

### 软阴影

从着色点向光源方向步进，检查是否有遮挡。遮挡物越近，阴影越暗：

$$k = \min\left(1,\ 32 \cdot \frac{d_i}{t_i}\right)$$

---

## Marching Cube（移动立方体）

Marching Cube 将 SDF（或其他标量场）转换为三角网格，用于离线渲染或 3D 打印。

### 算法流程

1. 在三维网格的每个顶点求 SDF 值
2. 每条边上：若两端 SDF 异号，则该边与曲面相交
3. 根据 8 个顶点的正负组合查表，确定该体素内的三角形拓扑
4. 线性插值求交点的精确位置

$$
\mathbf{p}_{\text{intersect}} = \mathbf{p}_1 + \frac{|f_1|}{|f_1| + |f_2|} (\mathbf{p}_2 - \mathbf{p}_1)
$$

### 配置表

8 个顶点，每个顶点两种状态（内/外），共 $2^8 = 256$ 种配置。利用对称性可简化为 **15 种基本情形**：

| 情形 | 描述 | 三角数 |
|:---|:---|:---|
| 0 | 全部在内/外 | 0 |
| 1 | 一个顶角不同 | 1 |
| 2 | 两个相邻顶角 | 2 |
| 3 | 对角/相邻三个 | 2–3 |
| 4 | 四顶角切片 | 2–4 |

### 应用

- 医学影像（CT/MRI）的三维重建
- SDF 网格生成（CSG → mesh）
- 元球渲染（Metaball）
- 地形等值面提取

---

## MetaBall（元球）

MetaBall 是有机融合多个球体的技术：多个球体的**势能函数叠加**后取等值面。

### 势能函数

单个球的势能：

$$f_i(\mathbf{p}) = \frac{1}{\|\mathbf{p} - \mathbf{c}_i\|^2}$$

多个球的总势能：

$$F(\mathbf{p}) = \sum_i f_i(\mathbf{p})$$

取 $F(\mathbf{p}) = \text{threshold}$ 的等值面即可得到融合后的光滑曲面。

### SDF 等效实现

```glsl
float sdMetaBall(vec3 p) {
    float d = 0.0;
    for (int i = 0; i < BALL_COUNT; i++) {
        float dist = length(p - balls[i].center);
        d += 1.0 / (dist * dist);  // 势能叠加
    }
    return 1.0 / sqrt(d) - threshold;  // 转回距离
}
```

### 特性对比

| 方法 | 融合效果 | 计算量 | 用途 |
|:---|:---|:---|:---|
| **普通球体** | 无融合，硬边界 | O(n) | 刚性球体 |
| **MetaBall** | 自然融合，有机感 | O(n) | 流体、有机体 |
| **SDF Smooth Union** | 可控融合半径 | O(log n) | CSG 建模 |

### 典型效果

多个球体靠近时会自动"拉丝"融合，远离时恢复独立球体形态——这正是 MetaBall 的经典视觉效果，广泛用于 2D/3D 的有机形态生成。

---

## 总结

| 技术 | 核心思想 | 输出形式 |
|:---|:---|:---|
| **SDF** | 空间各点到表面的距离 | 隐式曲面 |
| **Ray Marching** | 沿 SDF 安全步进求交 | 像素图像 |
| **Marching Cube** | 体素等值面提取 | 三角网格 |
| **MetaBall** | 势能场叠加 + 等值面 | 隐式曲面 → 图像或网格 |
