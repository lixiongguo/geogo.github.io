---
layout: post
title: "计算几何-Voronoi与Delaunay"
categories: Computational_Geometry
---

Voronoi 图与 Delaunay 三角剖分是计算几何中最经典的一对对偶结构。它们将离散的点集转化为连续的空间划分，在游戏开发、地理信息系统、机器学习、生物学等领域有广泛应用。

<!--more-->

---

## 1. Voronoi 图：空间划分的基础

### 1.1 定义

给定平面上 $n$ 个点（称为**站点**或 **sites**）$S = \{s_1, s_2, \ldots, s_n\}$，Voronoi 图将平面划分为 $n$ 个** Voronoi 单元（Cell）**：

$$V(s_i) = \{ p \in \mathbb{R}^2 : d(p, s_i) \leq d(p, s_j), \forall j \neq i \}$$

即 $V(s_i)$ 是平面上所有"距离 $s_i$ 最近"的点的集合。每个 Voronoi 单元是一个**凸多边形**。

### 1.2 直觉

想象 $n$ 个加油站同时开始以相同速度向外扩张，当相邻站的扩张区域相遇时停止——最终形成的领地划分就是 Voronoi 图。

### 1.3 Voronoi 图的关键性质

| 性质 | 说明 |
|:---|:---|
| **凸性** | 每个 Voronoi 单元都是凸多边形 |
| **最近邻查询** | 点 $p$ 落在哪个单元，哪个站点就是 $p$ 的最近邻 |
| **$n$ 个站点 → $O(n)$ 条 Voronoi 边 → $O(n)$ 个 Voronoi 顶点** | 欧拉公式保证：$V - E + F = 2$ |
| **Voronoi 顶点** | 每个顶点同时等距于至少 3 个站点（即外接圆心） |

### 1.4 朴素构造——$O(n^2 \log n)$

最直观的方法：对每个站点，计算它到所有其他站点的**垂直平分线（Bisector）**，然后求所有半平面的交集。每个站点需要 $O(n \log n)$ 求交，$n$ 个站点总计 $O(n^2 \log n)$。

这太慢了。我们需要更高效的方法。

---

## 2. Fortune 扫描线算法——$O(n \log n)$

### 2.1 核心思想

Fortune（1987）算法使用一条**从上到下移动的扫描线**来高效构建 Voronoi 图。它的精妙之处在于：不直接比较站点之间的距离，而是通过一条**海滩线（Beach Line）**间接维护距离关系。

### 2.2 海滩线与抛物线

**抛物线定义**：给定一个焦点 $s_i$ 和一条准线（扫描线 $y = y_L$），满足"到焦点距离 = 到准线距离"的点的轨迹是一条抛物线。

$$\text{Parabola}_{s_i}: \sqrt{(x - x_i)^2 + (y - y_i)^2} = y_L - y$$

**海滩线**是所有已发现站点的抛物线的"下包络"（lower envelope）：

$$\text{BeachLine}(x) = \min_{s_i \in S_{\text{above}}} \text{Parabola}_{s_i}(x)$$

> **关键性质**：海滩线上方已被"锁定"——Voronoi 边已经确定。海滩线下方尚未确定。

### 2.3 为什么海滩线有用？

海滩线有一个极为重要的性质：

> **海滩线上的每个点，到最近的上方站点和到扫描线的距离相等。**

这意味着：**如果两个站点的抛物线在海滩线上相交，交点恰好是这两个站点的 Voronoi 边与海滩线的交汇处**。因此，沿着海滩线追踪交点的移动轨迹，就能得到 Voronoi 边。

### 2.4 两种事件

Fortune 算法只处理两种事件：

**① 站点事件（Site Event）**

当扫描线到达一个新的站点 $s_i$ 时触发。

```
处理站点事件(s_i):
  1. 在海滩线上找到 x 坐标最接近 s_i 的弧段 arc
  2. 将 arc 分裂为左弧 arc_left 和右弧 arc_right
  3. 在两者之间插入 s_i 的新弧段 arc_new
  4. 新增两个 breakpoint（Voronoi 边的生长起点）
  5. 检查 arc_left 和 arc_new 之间、arc_new 和 arc_right 之间
     是否形成有效的圆事件
```

**② 圆事件（Circle Event）**

当三个相邻弧段对应的抛物线收缩到一个公共点时触发——这个点就是 Voronoi 顶点。

```
处理圆事件(arc_middle):
  1. 从海滩线中删除中间弧段 arc_middle
  2. 新增一个 Voronoi 顶点（两条 Voronoi 边的交点）
  3. 合并左右弧段的 breakpoint，产生一条新的 Voronoi 边
  4. 检查合并后的相邻弧段是否形成新的有效圆事件
```

> **直觉**：圆事件意味着中间站点的"领地"被左右两个邻居彻底挤掉了。被挤掉的那个点恰好是三个站点的**外接圆最低点**。

### 2.5 数据结构

| 数据结构 | 实现 | 操作 |
|:---|:---|:---|
| **事件队列** | 优先队列（最小堆） | 按事件 $y$ 坐标排序；插入/删除 $O(\log n)$ |
| **海滩线** | 平衡 BST（如红黑树） | 叶节点 = 弧段，内部节点 = breakpoint（Voronoi 边）；查找/插入/删除 $O(\log n)$ |
| **DCEL**（双向边链表） | 存储已确定的 Voronoi 边和顶点 | 边的插入 $O(1)$ |

### 2.6 完整伪代码

```
function FortuneVoronoi(Sites):
    // 初始化
    EQ = MinHeap()         // 事件队列
    BL = BalancedBST()     // 海滩线（初始为空）
    DCEL = []              // 存储 Voronoi 图结构

    // 将所有站点加入事件队列
    for each site s in Sites:
        EQ.push(s.y, type="site", site=s)

    while EQ 非空:
        event = EQ.pop()

        if event.type == "site":
            HandleSiteEvent(event.site)

        elif event.type == "circle":
            // 检查圆事件是否仍然有效（可能已被之前的圆事件使失效）
            if event.arc 仍然在海滩线中:
                HandleCircleEvent(event.arc)

    return DCEL

function HandleSiteEvent(s):
    if BL 为空:
        BL.insert(s)
        return

    // 找到 x 坐标最接近 s 的弧段
    arc = BL.findArcAbove(s.x)
    // 如果 arc 有一个待处理的圆事件，使其失效
    if arc.circleEvent exists:
        EQ.remove(arc.circleEvent)
        arc.circleEvent = null

    // 分裂弧段
    BL.split(arc, s)  // arc → arc_left, arc_new, arc_right

    // 检查新增邻接关系是否产生圆事件
    CheckCircleEvent(arc_left, arc_new)
    CheckCircleEvent(arc_new, arc_right)

function HandleCircleEvent(arc):
    arc_left = arc.predecessor
    arc_right = arc.successor

    // 创建 Voronoi 顶点
    vertex = Circumcircle(arc_left.site, arc.site, arc_right.site).bottom
    DCEL.addVertex(vertex)

    // 从海滩线中删除中间弧段
    BL.remove(arc)

    // 使相邻弧段的旧圆事件失效
    if arc_left.circleEvent exists:
        EQ.remove(arc_left.circleEvent)
        arc_left.circleEvent = null
    if arc_right.circleEvent exists:
        EQ.remove(arc_right.circleEvent)
        arc_right.circleEvent = null

    // 合并左右弧段，检查新圆事件
    CheckCircleEvent(arc_left, arc_right)

function CheckCircleEvent(arc_a, arc_b):
    if arc_a 和 arc_b 之间没有其他弧段（即它们相邻）:
        circle = Circumcircle(arc_a.site, arc中间.site, arc_b.site)
        if circle.bottom > sweepLine.y:  // 圆的最低点在扫描线下方
            event = CircleEvent(y=circle.bottom, arc=arc_中间)
            EQ.push(event)
            arc_中间.circleEvent = event
```

### 2.7 复杂度分析

| 维度 | 复杂度 |
|:---|:---|
| **时间** | $O(n \log n)$ |
| **空间** | $O(n)$ |

证明要点：
- 站点事件恰好 $n$ 个
- 有效圆事件至多 $2n - 5$ 个（每对相邻弧段最多一个）
- 每个事件的处理涉及 BST 的常数次操作，每次 $O(\log n)$
- 因此总时间 $O(n \log n)$

### 2.8 退化情况

| 情况 | 处理 |
|:---|:---|
| **两个站点 $y$ 坐标相同** | 按 $x$ 坐标排序处理 |
| **四个或更多站点共圆** | Voronoi 顶点的度 > 3，海滩线处理时需合并多个圆事件 |
| **三个站点共线** | 外接圆退化为直线，不产生圆事件 |
| **两个站点重合** | 预处理去重 |

---

## 3. Delaunay 三角剖分

### 3.1 定义

给定平面上 $n$ 个点的点集 $P$，Delaunay 三角剖分是满足**空圆性质**的三角剖分：

> 对于三角剖分中的每一个三角形 $\triangle p_i p_j p_k$，其外接圆的**严格内部**不包含 $P$ 中的任何其他点。

等价定义（Delaunay 边）：

> 一条边 $e = (p_i, p_j)$ 是 Delaunay 边，当且仅当存在一个通过 $p_i$ 和 $p_j$ 的圆，其内部不包含 $P$ 中任何其他点。

### 3.2 关键性质

| 性质 | 说明 |
|:---|:---|
| **空圆性** | 每个三角形的外接圆为空（定义性质） |
| **最大化最小角** | 在所有三角剖分中，Delaunay 三角剖分使最小内角最大化 |
| **唯一性** | 无四点共圆时唯一；四点共圆时可翻转对角线 |
| **凸包** | 外层边界构成点集的凸包 |
| **最近邻** | 每个点的最近邻一定是其 Delaunay 邻居 |
| **对偶性** | 与 Voronoi 图互为对偶（见下一节） |
| **Lifting 性质** | 将点提升到抛物面 $z = x^2 + y^2$ 上，其下凸包投影即为 Delaunay 三角剖分 |

### 3.3 增量插入算法（Bowyer-Watson）

Bowyer-Watson 算法是最常用的 Delaunay 三角剖分构造方法，核心思想是逐点插入 + 局部重构。

**算法流程**：

```
function BowyerWatson(Points):
    // 1. 创建超级三角形（包含所有点）
    superTri = BoundingTriangle(all points)
    triangles = [superTri]

    // 2. 逐点插入
    for each point p in Points:
        badTriangles = []

        // 找到所有外接圆包含 p 的"坏三角形"
        for each tri in triangles:
            if p in Circumcircle(tri):
                badTriangles.append(tri)

        // 找到"空腔"的边界多边形
        polygon = []  // 有序边列表
        for each tri in badTriangles:
            for each edge in tri.edges:
                if edge 不被其他坏三角形共享:
                    polygon.append(edge)

        // 删除坏三角形
        for each tri in badTriangles:
            triangles.remove(tri)

        // 用 p 和空腔边界重建三角形
        for each edge in polygon:
            triangles.append(Triangle(edge, p))

    // 3. 删除与超级三角形共享顶点的所有三角形
    triangles = [tri for tri in triangles
                 if tri 不包含超级三角形的顶点]

    return triangles
```

### 3.4 Lawson Flip（翻转）优化

增量插入后，可能引入不满足空圆性的三角形。**Lawson Flip** 通过局部翻转来修复：

```
function LawsonFlip(triangles):
    changed = true
    while changed:
        changed = false
        for each edge e in all internal edges:
            t1, t2 = e 的两个相邻三角形
            if NOT EmptyCircumcircle(t1) OR NOT EmptyCircumcircle(t2):
                // 翻转对角线
                FlipEdge(e)
                changed = true
```

**翻转的正确性保证**：Lawson（1972）证明了，只要反复翻转不满足空圆性的边，最终一定会收敛到 Delaunay 三角剖分。这得益于翻转会**增加目标函数值**（最小角的某种度量），而目标函数有上界。

### 3.5 复杂度

| 维度 | 复杂度 |
|:---|:---|
| **最坏情况** | $O(n^2)$（所有点近似共圆时，每次插入可能破坏 $O(n)$ 个三角形） |
| **平均情况** | $O(n \log n)$（随机插入顺序下，每次期望只破坏 $O(1)$ 个三角形） |
| **空间** | $O(n)$ |

> **工程实践**：使用随机打乱点序后进行增量插入，期望复杂度 $O(n \log n)$。大多数实际实现都采用这一策略。

---

## 4. Delaunay 与 Voronoi 的对偶关系

### 4.1 对偶变换

Delaunay 三角剖分和 Voronoi 图是**互为对偶**的两个几何结构：

| Delaunay | Voronoi |
|:---|:---|
| 三角形 | Voronoi 顶点 |
| 三角形外心 | Voronoi 顶点坐标 |
| Delaunay 边 | Voronoi 边（垂直于 Delaunay 边） |
| Delaunay 顶点（站点） | Voronoi 单元 |
| Delaunay 三角剖分 | Voronoi 图 |

### 4.2 对偶关系的几何解释

**核心观察**：

> Voronoi 图的每个顶点，恰好是三个（或更多）Voronoi 单元的公共交汇点——这意味着它等距于三个（或更多）站点。而这三个站点的**外接圆圆心**就是这个 Voronoi 顶点。

因此：
- Voronoi 顶点 = Delaunay 三角形的外心
- 连接相邻 Voronoi 顶点的 Voronoi 边 ⊥ Delaunay 边

### 4.3 为什么对偶关系有用？

1. **构造加速**：构造了其中一个，就能在 $O(n)$ 时间内得到另一个（无需重新计算）
2. **性质互推**：Delaunay 的空圆性 ↔ Voronoi 的最近邻性
3. **算法选择**：有时构造 Delaunay 更容易（增量插入），有时构造 Voronoi 更方便（Fortune 算法）

### 4.4 从 Delaunay 到 Voronoi

```
function DelaunayToVoronoi(DelaunayTriangles):
    voronoiVertices = []
    voronoiEdges = []

    for each triangle T in DelaunayTriangles:
        // 计算外心作为 Voronoi 顶点
        v = Circumcenter(T)
        voronoiVertices.append(v)

    for each Delaunay edge e (shared by T1 and T2):
        // 连接两个外心
        voronoiEdges.append(Circumcenter(T1), Circumcenter(T2))

    return VoronoiDiagram(voronoiVertices, voronoiEdges)
```

---

## 总结

Voronoi 图和 Delaunay 三角剖分是计算几何中的"双子星"：

$$\boxed{\text{点集 } P} \xrightarrow{\text{最近邻划分}} \boxed{\text{Voronoi 图}} \xleftrightarrow{\text{对偶}} \boxed{\text{Delaunay 三角剖分}}$$

| 方法 | 目标 | 复杂度 | 核心思想 |
|:---|:---|:---|:---|
| **Fortune 算法** | 构造 Voronoi 图 | $O(n \log n)$ | 扫描线 + 海滩线 + 两种事件 |
| **Bowyer-Watson** | 构造 Delaunay 三角剖分 | $O(n \log n)$ 平均 | 增量插入 + 空腔重构 + Lawson Flip |
| **对偶变换** | Voronoi ↔ Delaunay | $O(n)$ | 外心 = Voronoi 顶点 |

## 参考

- Fortune, S. (1987). "A sweepline algorithm for Voronoi diagrams." *Algorithmica*.
- Bowyer, A. (1981). "Computing Dirichlet tessellations." *The Computer Journal*.
- Watson, D. F. (1981). "Computing the n-dimensional Delaunay tessellation." *The Computer Journal*.
- Lawson, C. L. (1972). "Generation of a triangular grid with application to contour plotting." *California Institute of Technology*.
- de Berg, M., et al. (2008). *Computational Geometry: Algorithms and Applications*. Chapter 7 & 9.
