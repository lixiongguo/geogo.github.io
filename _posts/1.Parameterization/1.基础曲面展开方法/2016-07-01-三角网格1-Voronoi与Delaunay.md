---
layout: post
title: "三角网格——Voronoi与Delaunay"
categories: Computational_Geometry
---

Voronoi 图与 Delaunay 三角剖分是计算几何中最经典的一对对偶结构。它们将离散的点集转化为连续的空间划分，在游戏开发、地理信息系统、机器学习、生物学等领域有广泛应用。

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

最直观的方法：对每个站点，计算它到所有其他站点的**垂直平分线（Bisector）**，然后求所有半平面的交集。每个站点需要 $O(n \log n)$ 求交，$n$ 个站点总计 $O(n^2 \log n)$。这太慢了。我们需要更高效的方法。

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

![image-20260714194211678](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260714194211678.png)

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

### 算法要点

数据结构：事件队列用优先队列（最小堆），按事件 $y$ 排序，插入/删除 $O(\log n)$；海滩线用平衡 BST（如红黑树），叶节点为弧段、内部节点为 breakpoint（Voronoi 边），查找与更新 $O(\log n)$；已确定的边与顶点用 DCEL 存储，边插入 $O(1)$。

复杂度：时间 $O(n\log n)$，空间 $O(n)$：站点事件 $n$ 个，有效圆事件 $O(n)$，每事件对 BST 做常数次 $O(\log n)$ 操作。

退化情况：同高站点按 $x$ 次序处理；四点及以上共圆时 Voronoi 顶点度 $>3$，需合并圆事件；三点共线则外接圆退化、无圆事件；重合站点预处理去重。



## Delaunay 三角剖分

给定平面上 $n$ 个点的点集 $P$，Delaunay 三角剖分是满足**空圆性质**的三角剖分：

> 对于三角剖分中的每一个三角形 $\triangle p_i p_j p_k$，其外接圆的**严格内部**不包含 $P$ 中的任何其他点。

等价定义（Delaunay 边）：

> 一条边 $e = (p_i, p_j)$ 是 Delaunay 边，当且仅当存在一个通过 $p_i$ 和 $p_j$ 的圆，其内部不包含 $P$ 中任何其他点。


### 关键性质

| 性质 | 说明 |
|:---|:---|
| **空圆性** | 每个三角形的外接圆为空（定义性质） |
| **最大化最小角** | 在所有三角剖分中，Delaunay 三角剖分使最小内角最大化 |
| **唯一性** | 无四点共圆时唯一；四点共圆时可翻转对角线 |
| **凸包** | 外层边界构成点集的凸包 |
| **最近邻** | 每个点的最近邻一定是其 Delaunay 邻居 |
| **对偶性** | 与 Voronoi 图互为对偶（见下一节） |
| **Lifting 性质** | Delaunay = 抬升点三维凸包的**下投影**（见下） |

### 3.2 Growing Circle（扩张圆）直觉

空圆性质可用**扩张圆（growing / expanding circle）**来读：圆心沿边的垂直平分线移动，圆始终穿过两端点，半径随之增大，直到「碰到」第三个站点为止。

**边是否为 Delaunay。** 固定 $p_i,p_j$，过这两点的圆，其圆心必在线段 $p_ip_j$ 的**垂直平分线**上。取以 $p_ip_j$ 为直径的圆作为最小者（圆心为中点），沿平分线向某一侧连续移动圆心——此即一串**growing circle**：

1. 圆始终过 $p_i,p_j$，内部起初通常为空（或至少直径圆是候选）；
2. 半径增大，直到圆周**首次碰到**另一个站点 $p_k$；
3. 若在碰触瞬间圆的**内部仍不含**其他点，则 $(p_i,p_j)$ 满足空圆边定义，因而是 **Delaunay 边**；同时 $\triangle p_i p_j p_k$ 的外接圆即为该停滞时刻的圆，故该三角形也是 Delaunay 三角形。

向平分线**另一侧**再做一次扩张，通常会碰到另一点 $p_\ell$，对应共享边 $p_ip_j$ 的另一个相邻三角形（内部边两侧各一）。

**三角形外接圆。** 对已是 Delaunay 的三角形，其外接圆可视为扩张过程的**终止态**：圆「卡住」在三个站点上，且内部空——这正是本节开头的空圆定义。若扩张尚未到第三点时内部已「吞进」某点，则该候选边/三角形不合法，需翻边或在 Bowyer–Watson 中被标为坏三角形。

<img src="/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260714203718725.png" alt="image-20260714203718725" style="zoom:50%;" />

**与 Voronoi 的衔接。** 扩张圆的圆心始终在 $p_ip_j$ 的垂直平分线上，而该平分线正是站点 $p_i,p_j$ 之间的 **Voronoi 边**所在直线。圆停在第三点 $p_k$ 时，圆心同时等距于 $p_i,p_j,p_k$，即落在第三条平分线上——三点外心，也就是 **Voronoi 顶点**。因此：
$$
\text{growing circle 卡住三国点}
\;\Longleftrightarrow\;
\text{空外接圆}
\;\Longleftrightarrow\;
\text{Delaunay 三角形}
\;\Longleftrightarrow\;
\text{一个 Voronoi 顶点}.
$$

四点共圆时，同一圆心处「同时」碰上第四点，扩张在两侧终止圆重合。

### Lifting 性质（抛物面提升）

空圆性看起来像二维判定，但可通过一次坐标变换变成三维凸包。想法是：把每个平面点**竖直抬高**到抛物面上，使「是否在圆内」变成「是否在某张平面的下方」——后者正是凸包下侧面的定义。

**提升映射。** 对 $p=(x,y)$ 令
$$
\hat{p}=\bigl(x,\;y,\;x^2+y^2\bigr),
$$
即抬到旋转抛物面 $z=x^2+y^2$ 上；点集 $P$ 提升为 $\hat{P}$。

**结论（下投影）。** 对 $\hat{P}$ 求三维凸包 $\mathrm{CH}(\hat{P})$，只保留**下包络**（从 $z=-\infty$ 往上看得到的那些面，记为 $\partial_{-}\mathrm{CH}$），再沿 $z$ 方向投影回 $xy$ 平面——得到的三角剖分恰为 Delaunay：

$$
\boxed{\mathrm{Delaunay}(P)=\pi_{xy}\!\bigl(\partial_{-}\mathrm{CH}(\hat{P})\bigr)},
\qquad \pi_{xy}:(x,y,z)\mapsto(x,y).
$$

无四点共圆时，每个下三角面一一对应一个 Delaunay 三角形。上包络的投影则是**最远点 Delaunay**（对偶于最远点 Voronoi），与日常最近邻 Delaunay 不是同一对象。

构造管道：抬升 → 3D 凸包 → **只要下面、丢掉上面** → 投影回 2D；复杂度 $O(n\log n)$。

![image-20260714194923763](../../../imgs//image-20260714194923763.png)

<img src="/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260714195237033.png" alt="image-20260714195237033" style="zoom:50%;" />

**为何圆变成平面。** 平面上的圆
$$
(x-a)^2+(y-b)^2=r^2
$$
展开为 $x^2+y^2-2ax-2by+(a^2+b^2-r^2)=0$。在抛物面上用 $z$ 替换 $x^2+y^2$，立刻得到**线性方程**
$$
z-2ax-2by+c=0,\qquad c=a^2+b^2-r^2,
$$
即三维中一张平面 $\Pi$。反过来，不平行于 $z$ 轴的平面与抛物面相交，交线投影回 $xy$ 仍是圆（或退化成直线）。因此：

| 平面上 | 抬升后 |
|:---|:---|
| $q$ 在圆**内** | $\hat{q}$ 在 $\Pi$ **下方**（$z$ 更小） |
| $q$ 在圆**外** | $\hat{q}$ 在 $\Pi$ **上方** |
| $q$ 在圆周上 | $\hat{q}$ 落在 $\Pi$ 上（四点共圆 $\Leftrightarrow$ 四点抬升共面） |

**空圆何以等于下侧面。** 取候选三角形 $\triangle p_ip_jp_k$，其三抬升点张成平面 $\Pi$。若外接圆**内部不含**其他点，则一切其余 $\hat{q}$ 都在 $\Pi$ 上方——从下方看，$\hat{p}_i\hat{p}_j\hat{p}_k$ 没有被别的点挡住，正是凸包的一张**下侧面**。投影回去就是 Delaunay 三角形。若有点落在圆内，对应抬升点会戳到 $\Pi$ 下方，该面不可能出现在下包络上。

![image-20260714195957273](/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260714195957273.png)

**InCircle 谓词 = 三维定向。** 判定第四点是否在外接圆内，可用
$$
\mathrm{InCircle}(p_i,p_j,p_k,q)
=
\det\begin{bmatrix}
x_i&y_i&x_i^2+y_i^2&1\\
x_j&y_j&x_j^2+y_j^2&1\\
x_k&y_k&x_k^2+y_k^2&1\\
x_q&y_q&x_q^2+y_q^2&1
\end{bmatrix}.
$$
这恰是四面体 $(\hat{p}_i,\hat{p}_j,\hat{p}_k,\hat{q})$ 的有向体积：符号告诉你 $\hat{q}$ 在 $\Pi$ 哪一侧，为零则四点抬升共面（共圆）。故空圆检验就是一次 3D orient；许多库把 Delaunay 直接当作凸包算法的副产品。

**附带读法。** Lawson 翻边：四边形两条对角线中，落在下表面上的那条才是 Delaunay，另一条抬升后沉入凸包内部。后文 Voronoi 对偶也可由此读出——下侧面所对应圆的圆心（圆参数 $(a,b)$）正是外心，也即 Voronoi 顶点。

## 算法实现

### 3.4 增量插入算法（Bowyer-Watson）

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

### 3.5 Lawson Flip（翻转）优化

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

### 3.6 复杂度

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

<img src="/Users/lgxgeogo/Desktop/MyDoc/lixiongguo.github.io/imgs//image-20260714194341910.png" alt="image-20260714194341910" style="zoom:50%;" />

**核心观察**：

> Voronoi 图的每个顶点，恰好是三个（或更多）Voronoi 单元的公共交汇点——这意味着它等距于三个（或更多）站点。而这三个站点的**外接圆圆心**就是这个 Voronoi 顶点。

因此：
- Voronoi 顶点 = Delaunay 三角形的外心
- 连接相邻 Voronoi 顶点的 Voronoi 边 ⊥ Delaunay 边

下方从 §3.1 的 lifting 出发，把这一对偶**推出来**，而不是当作独立事实接受。

### 4.3 四点共圆：退化时两边的对应

一般位置假设下：**没有四点共圆、没有三点共线**。此时每个 Voronoi 顶点恰由 **3** 个站点决定（度均为 3），Delaunay 三角剖分**唯一**。四点共圆正是打破这一假设的经典退化，在对偶两侧表现为同一事件的两种脸谱。

设凸四边形 $ABCD$ 的四点共圆，公共圆心为 $o$，半径为 $r$。则

$$
d(o,A)=d(o,B)=d(o,C)=d(o,D)=r.
$$

**在 Voronoi 一侧**：

- $o$ 同时落在四个站点的垂直平分线上，是 **4 个 Voronoi 单元的公共交点**；
- 该 Voronoi 顶点的**度 $\ge 4$**（非一般位置下的 3），四条 Voronoi 边从 $o$ 射出；
- 对偶意义下，不再对应「一个三角形的外心」，而是对应凸四边形 $ABCD$ 这一整块共圆结构——若强行三角剖分，两条可能对角线共享**同一个外心** $o$。

**在 Delaunay 一侧**：

- 空圆准则的严格说法是：外接圆**内部**不含其他点。共圆时第四点落在圆周上，属**边界情形**；
- 四边形的**两条对角线**都满足弱空圆性（圆内部仍空），故 $AC$ 与 $BD$ 都可成为 Delaunay 边；
- 因而 Delaunay 三角剖分**不唯一**：剖分成 $\triangle ABC+\triangle ADC$ 或 $\triangle ABD+\triangle BCD$ 皆合法；二者之间恰可用一次 **Lawson 翻边**互换，且翻转不改变空圆性的强弱满足。

| 一般位置 | 四点共圆（凸四边形） |
|:---|:---|
| Voronoi 顶点度 $=3$ | 度 $\ge 4$，四单元共顶点 |
| 一个外心 ↔ 一个三角形 | 同一外心 $o$ ↔ 整个共圆四边形 |
| Delaunay 唯一 | 两条对角线皆合法，剖分可翻转 |

**判定与算法含义**（与 §2.8、§3.5 呼应）：

- **InCircle 谓词**恰在区分「第四点在圆内 / 圆上 / 圆外」：圆上即共圆，是 Delaunay 合法性的临界状态；
- Fortune 需合并多个圆事件（多个弧同时在同一点消失）；对偶构造时，应对度 $\ge 4$ 的 Voronoi 顶点把对偶面剖成任意三角剖分（或显式保留可翻转边）；
- 工程上常用扰动（symbolic perturbation）消除共圆，使输出唯一、度数回归 3。

> **一句话**：四点共圆 $\Leftrightarrow$ Voronoi 出现高阶顶点（$\ge 4$ 单元交于一点）$\Leftrightarrow$ Delaunay 在对应四边形上对角线可任选（唯一性丧失）。两侧描述的是同一退化。

### 4.4 为什么对偶关系有用？

1. **构造加速**：构造了其中一个，就能在 $O(n)$ 时间内得到另一个（无需重新计算）
2. **性质互推**：Delaunay 的空圆性 ↔ Voronoi 的最近邻性；四点共圆则同时造成 Voronoi 高阶顶点与 Delaunay 不唯一
3. **算法选择**：有时构造 Delaunay 更容易（增量插入），有时构造 Voronoi 更方便（Fortune 算法）

### 4.5 从 Delaunay 到 Voronoi

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
