---
layout: post
title: "BSP 树：二叉空间分割"
date: 2026-04-07
categories: [1.Parameterization, 5.计算几何]
---

## 1. BSP 是什么

**BSP（Binary Space Partitioning，二叉空间分割）** 是一种使用超平面递归划分空间到凸集的方法。通过该方法划分空间可以得到表示空间中对象的**树形数据结构**，即 **BSP 树**。

BSP 树的核心思想非常直观：选择一个平面（分割平面），将空间一分为二；对每个子空间递归执行同样的操作，直到满足终止条件。

> **历史**：BSP 由 Fuchs 等人于 1980 年首次提出，Schumacker 于 1969 年提出了类似思想。第一个使用 BSP 树的商业游戏是经典的 **Doom**（1993 年，id Software）。

**两种主要形式**：

| 类型 | 分割平面 | 特点 |
|:---|:---|:---|
| **多边形对齐（Polygon-aligned）** | 多边形所在的平面 | 分割更精细，适合渲染排序 |
| **轴对齐（Axis-aligned）** | AABB 的坐标轴平面 | 构造简单，类似八叉树 |

---

## 2. BSP 算法

### 2.1 数学基础

给定空间中的一个超平面 $h$，将空间分为两个半空间：

- **正半空间** $h^+$（Positive Half-Space）：平面法向量所指的一侧
- **负半空间** $h^-$（Negative Half-Space）：平面的另一侧

对于平面 $Ax + By + Cz + D = 0$ 和点 $P = (x_0, y_0, z_0)$，有符号距离为：

$$d = Ax_0 + By_0 + Cz_0 + D$$

- $d > 0$：点在平面**正面**
- $d < 0$：点在平面**背面**
- $d = 0$：点在**平面上**

### 2.2 BSP 树的正式定义

设 $S$ 是一个对象（点、多边形、多边形组等空间对象）的集合，$S(v)$ 表示与结点 $v$ 相关联的对象集。BSP 树 $T(S)$ 定义如下：

1. 若 $|S| \leq 1$，则 $T$ 是叶子节点 $v$，存储 $S(v) := S$
2. 若 $|S| > 1$，则 $T$ 的根是节点 $v$，$v$ 存储分割平面 $h_v$ 和集合 $S(v) := \{x \in S \mid x \subseteq h_v\}$（恰好落在平面上的对象）。$v$ 有两个子节点：
   - $T^-$：对象 $S^- := \{x \cap h_v^- \mid x \in S\}$ 的 BSP
   - $T^+$：对象 $S^+ := \{x \cap h_v^+ \mid x \in S\}$ 的 BSP

### 2.3 BSP 树的构造算法

**构造伪代码**：

```
function BuildBSP(PolygonList):
    if PolygonList is empty:
        return null

    // 步骤1：选择分割平面
    Pick a polygon P from PolygonList as splitting plane
    Create a new node N
    N.plane = P.plane

    // 步骤2：分类多边形
    Initialize frontList, backList, coplanarList as empty
    coplanarList = {P}

    for each polygon Q in PolygonList (excluding P):
        if Q is entirely in front of N.plane:
            add Q to frontList
        else if Q is entirely behind N.plane:
            add Q to backList
        else:  // Q spans the plane (跨平面)
            Split Q by N.plane into Q_front and Q_back
            add Q_front to frontList
            add Q_back to backList

    // 步骤3：递归构造子树
    N.front = BuildBSP(frontList)
    N.back  = BuildBSP(backList)

    return N
```

### 2.4 分割平面选择策略

选择好的分割平面是 BSP 树效率的关键：

| 策略 | 说明 | 时间复杂度 |
|:---|:---|:---|
| **随机选择** | 随机选取一个多边形作为分割平面 | $O(n)$，但树质量差 |
| **最小分割** | 选择使跨平面的多边形最少的平面 | $O(n^2)$，每步检查所有候选 |
| **平衡选择** | 使前后子树的多边形数量尽可能均衡 | $O(n^2 \log^2 n)$ |

构造多边形对齐 BSP 树的总时间复杂度为：

$$T(n) = O(n \log^2 n)$$

这是因为在 $O(\log n)$ 层的递归中，每层需要 $O(n \log n)$ 的时间来寻找最优分割平面。

### 2.5 多边形分割

当多边形跨越分割平面时，需要将其分割为两部分。步骤如下：

1. 遍历多边形的每条边，计算两个端点到分割平面的有符号距离 $d_1, d_2$
2. 若 $d_1$ 和 $d_2$ 符号不同，则该边与平面相交，计算交点
3. 在交点处将多边形分割为两个新多边形，分别放入前后子空间

## 4. BSP 与光栅化

在现代 GPU 管线中，BSP 树不直接用于栅格化（现代 GPU 使用 Z-buffer），但 BSP 在以下方面仍有重要应用：

### 4.1 PVS（Potential Visibility Set）计算

BSP 树可以预计算每个区域**可能可见**的多边形集合（PVS），大幅减少需要渲染的图元数量：

1. 构建 BSP 树
2. 对每个叶子区域，通过 BSP 遍历确定从该区域可见的其他叶子
3. 合并这些叶子的多边形，形成 PVS
4. 渲染时只绘制 PVS 中的多边形

这是 **Quake**（1996）引擎的核心技术。

### 4.2 软件光栅化

在没有 Z-buffer 硬件的条件下（如早期游戏），BSP 树可以按从后到前的顺序进行多边形扫描转换，直接替代深度缓冲：

```
// 软件渲染流程
for each polygon in BSP-order (back-to-front):
    Rasterize(polygon)  // 直接绘制，后面的覆盖前面的
```

### 4.3 遮挡剔除（Occlusion Culling）

BSP 树用于快速判断哪些物体被近处物体遮挡，从而跳过不必要的渲染：

- 从相机位置遍历 BSP 树
- 如果一个子空间完全被遮挡，则剪掉整个子树
- 这比逐像素的 Z-buffer 测试更高效（批量剔除）

---

## 5. BSP 与画家算法

### 5.1 画家算法的问题

画家算法（Painter's Algorithm）的核心思想是：**从远到近绘制**，后绘制的覆盖先绘制的，自然实现正确的遮挡关系。

但画家算法有以下致命缺陷：
- **多边形交叉**：两个多边形部分重叠时，无法确定谁先谁后
- **循环遮挡**：A 遮挡 B，B 遮挡 C，C 又遮挡 A 时，不存在合法排序

### 5.2 BSP 树解决画家算法的问题

BSP 树通过**预处理**解决了画家算法的所有问题：无论相机处于任何位置，BSP 树都能给出一个**正确的从后到前**的绘制顺序。

**遍历伪代码**：

```
function DrawBSP(Node, CameraPosition):
    if Node is null:
        return

    if CameraPosition is in front of Node.plane:
        // 相机在正面：先画背面（远离相机），再画平面，最后画正面
        DrawBSP(Node.back, CameraPosition)
        DrawPolygon(Node.polygon)
        DrawBSP(Node.front, CameraPosition)
    else:
        // 相机在背面：先画正面，再画平面，最后画背面
        DrawBSP(Node.front, CameraPosition)
        DrawPolygon(Node.polygon)
        DrawBSP(Node.back, CameraPosition)
```

> **关键**：BSP 树将"排列顺序"的决策在**预处理阶段**完成，运行时只需根据相机位置做 $O(\log n)$ 的树遍历，非常高效。

---

## 6. BSP 与三角剖分

BSP 树本身不直接用于三角剖分，但在计算几何中与三角剖分有密切联系。

### 6.1 BSP 辅助三角剖分

- **空间引导**：BSP 树的分割平面可以作为三角剖分的约束边，确保某些边界被保留
- **局部化处理**：先将空间用 BSP 树分割为小区域，再在每个叶区域进行局部三角剖分
- **碰撞检测**：在增量式三角剖分（如 Bowyer-Watson）中，BSP 树可用于快速定位新插入点的所在区域

### 6.2 二维 BSP 与线段求交

在二维情况下，BSP 树可以用线段作为分割元素。一个重要应用是判断一组线段是否存在交叉：

1. 用线段构建 BSP 树
2. 每插入一条线段时，检查它是否与已有的分割线段相交
3. 如果没有交叉，则线段集合是简单的（Simple）

### 6.3 BSP 与布尔运算

BSP 树天然支持多边形/多面体的布尔运算（并、交、差）：

- 将每个多面体表示为一棵 BSP 树
- 对两棵 BSP 树进行合并操作
- 结果 BSP 树即为布尔运算的结果

这也是 **CSG（Constructive Solid Geometry）** 系统的核心技术。

---

## 7. BSP 的优势与局限

### 优势

| 优势 | 说明 |
|:---|:---|
| **正确排序** | 保证任意视点下的从后到前顺序 |
| **快速查询** | 光线追踪 $O(\log n)$，碰撞检测高效 |
| **PVS 预计算** | 大规模场景的可见性预剔除 |
| **布尔运算** | 天然支持 CSG 建模 |
| **通用性** | 适用于任意维度和任意形状的对象 |

### 局限

| 局限 | 说明 |
|:---|:---|
| **预处理代价高** | 构造 $O(n \log^2 n)$，且多边形分割可能大幅增加面数 |
| **内存开销** | 分割产生的额外多边形导致存储增大 |
| **不适合动态场景** | 场景变化时需要重建 BSP 树 |
| **现代 GPU 替代** | Z-buffer 和 BVH 在许多应用中更高效 |
| **树深度** | 不平衡的 BSP 树可能很深，影响查询效率 |

---

## 总结对比：BSP 树 vs 其他空间划分结构

| 结构 | 分割方式 | 构造复杂度 | 查询复杂度 | 动态更新 | 典型应用 |
|:---|:---|:---|:---|:---|:---|
| **BSP 树** | 任意超平面 | $O(n \log^2 n)$ | $O(\log n)$ | ❌ 困难 | 可见性排序、光线追踪 |
| **KD 树** | 轴对齐平面 | $O(n \log n)$ | $O(\log n)$ | ⚠️ 中等 | 光线追踪、近邻搜索 |
| **八叉树** | 三个轴向平面 | $O(n)$ | $O(n)$（最坏） | ✅ 容易 | 碰撞检测、场景管理 |
| **BVH** | 包围盒 | $O(n \log n)$ | $O(\log n)$ | ✅ 容易 | 光线追踪（现代标准） |
| **四叉树** | 两个轴向平面 | $O(n)$ | $O(n)$（最坏） | ✅ 容易 | 2D 空间查询、图像处理 |

## 参考

- [BSP算法 - 知乎](https://zhuanlan.zhihu.com/p/34818189)
- [Binary space partitioning - 知乎](https://zhuanlan.zhihu.com/p/53388395)
- Fuchs, H., et al. (1980). "On visible surface generation by a priori tree structures." *SIGGRAPH*.
- [空间加速结构——BSP tree和k-d tree](https://www.cnblogs.com/silence394/p/17285230.html)
- [几何体数据结构学习(5) BSP树](https://zhuanlan.zhihu.com/p/427829138)
