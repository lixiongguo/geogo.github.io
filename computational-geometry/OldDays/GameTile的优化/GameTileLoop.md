# GameTileLoop 技术文档

> 源文件：`computational-geometry/OldDays/GameTile的优化/GameTileLoop.cs`  
> Gallery 复刻：`gallery/advanced-text.html` 中的 `GameTileLoop` 标签页

---

## 概述

`GameTileLoop` 是一个基于 Unity UGUI `ScrollRect` 的 **循环复用列表容器**。它的目标不是为每条数据都创建一个 UI 节点，而是只创建「可视区域 + 少量缓冲」数量的 item，然后在滚动时重绑定数据索引、调整 content padding 和渲染顺序。

这类控件通常也叫：

- 虚拟列表 / Virtual List
- 无限滚动列表 / Recycled Scroll View
- UI 对象池列表
- ScrollRect item recycling

核心收益是把 UI GameObject 数量从 `O(dataCount)` 降到 `O(visibleCount + buffer)`，用于背包、排行榜、聊天记录、关卡列表等大数据量 UI。

---

## 源码核心结构

### 关键字段

| 字段 | 含义 |
|------|------|
| `m_scrollRect` | 父级 `ScrollRect` |
| `m_content` | `ScrollRect.content`，滚动内容容器 |
| `m_LayoutGroup` | `GridLayoutGroup` / `VerticalLayoutGroup` / `HorizontalLayoutGroup` |
| `m_GridSize` | 单个 item 的尺寸 + spacing |
| `m_GridSizeOne` | 主滚动方向上的单元尺寸 |
| `m_viewItemRowCount` / `m_viewItemColCount` | 需要保留的行/列数 |
| `m_viewItemCount` | 实际创建的 item 池大小 |
| `m_startRowOrCol` | 当前滚动到的起始行/列 |
| `last_startRowOrCol` | 上一次起始行/列，用于判断是否需要刷新 |
| `showBottomStartRowOrCol` | 滚到底部时允许的最大起始行/列 |
| `totalRowOrCol` | 总数据需要的行/列数 |
| `addRowOrCol` | 缓冲行/列，默认 `1` |
| `onUpdateItem` | 业务回调：`onUpdateItem(obj, currentDataIndex)` |

---

## 初始化流程

### 1. 读取布局信息

`OnInit()` 会根据当前挂载的布局组件推导 item 尺寸：

- `GridLayoutGroup`：使用 `cellSize + spacing`
- 其他 layout：从 template 的 `LayoutElement` 读取宽高
- `HorizontalLayoutGroup` / `VerticalLayoutGroup`：读取对应方向 spacing

然后保存原始 padding：

```csharp
m_oldPadding = m_LayoutGroup.padding;
SetGridSize = m_itemSize + m_itemSpacing;
```

### 2. 绑定 ScrollRect

`InitM_ScrowRect()` 负责找到父级 `ScrollRect`、记录 content 初始位置，并计算可视区域能显示多少行/列：

```csharp
canShowRowOrCol = Mathf.CeilToInt(ViewSpace / height);
m_viewItemRowCount = canShowRowOrCol + addRowOrCol;
m_viewItemCount = m_viewItemRowCount * m_viewItemColCount;
m_scrollRect.onValueChanged.AddListener(ScorwRectMove);
```

这里的关键是：**只创建可视行数 + 缓冲行数的 item**，不随数据量增长。

---

## 数据量与池大小

外部调用：

```csharp
EnsureSize<T>(realDataCount)
```

内部会：

1. 初始化 ScrollRect
2. `count = Min(realDataCount, m_viewItemCount)`
3. 创建或删除池内 item，使 `ChildCount == count`
4. 延迟到下一帧读取真实 `RectTransform` 尺寸
5. 设置 `dataCount = realDataCount`

延迟一帧的原因是源码注释里提到：

> 因为 ContentSizeFitter 的 RectTransform 下一帧有用

这说明它要等待 Unity layout 系统完成尺寸计算，再读取 item 的真实 size 和 anchoredPosition。

---

## 滚动更新算法

### 1. 计算当前起始行/列

`ScorwRectMove(Vector2 data)` 中根据 content 的 anchoredPosition 得到滚动偏移：

```csharp
currentOffset = currentPos.y - panelPos.y;
m_startRowOrCol = Mathf.Min(
    Mathf.FloorToInt(currentOffset / m_GridSizeOne),
    showBottomStartRowOrCol
);
```

垂直方向时，滚动距离除以单元高度得到当前起始行。水平方向则用 x 轴。

### 2. 起始行变化时才刷新

如果 `last_startRowOrCol == m_startRowOrCol`，说明还没跨过一个 item 单元，不需要重排 item。

跨过行/列后，根据移动距离分三种：

| 情况 | 策略 |
|------|------|
| 移动距离 >= 可视行/列 | 大跳跃，整池 item 全量刷新 |
| 向下/向右移动 | 前面的 item 移到尾部，复用并绑定新数据 |
| 向上/向左移动 | 尾部 item 移到头部，复用并绑定新数据 |

源码里有一段注释很好地概括了对象复用：

```csharp
// childList 比如原来是 0 1；2 3；4 5 向上移动了两行，
// 变成 2 3；4 5；0 1
```

这就是循环队列式复用。

### 3. 用 padding 撑开完整滚动高度

`ExpandPadding()` 不创建真实 item，而是动态修改 layout padding：

```csharp
frontSpace = Mathf.CeilToInt(m_startRowOrCol * m_GridSizeOne);
behindSpace = Mathf.CeilToInt(Mathf.Max(0, m_GridSizeOne * showBottomStartRowOrCol - frontSpace));
```

垂直列表时：

```csharp
m_LayoutGroup.padding = new RectOffset(
    m_oldPadding.left,
    m_oldPadding.right,
    m_oldPadding.top + frontSpace,
    m_oldPadding.bottom + behindSpace
);
```

这使得 `ScrollRect` 仍然感觉 content 很长，但真正存在的 UI 节点只有池中的少量 item。

---

## ScrollTo 定位

`ScrollTo(index)` 支持跳转到指定数据索引所在行/列：

1. 将数据索引换算成 `rowOrCol`
2. 如果目标在开头范围，回到 `panelPos`
3. 如果目标靠近尾部，滚到底部
4. 否则把目标放在可视区域中间附近

如果当前 ScrollRect 还不能移动，则把目标暂存到 `nextFrameIndex`，等初始化完成后再执行。

---

## 与 ListView 目录代码的关系

同目录下的 `ListView/Standard Assets/UListView` 是另一套虚拟列表抽象：

| 文件 | 特点 |
|------|------|
| `IUListView.cs` | 抽象基类：计算 content size、start index、item position、点击检测 |
| `USimpleListView.cs` | 等尺寸一维列表，池大小为可视数量 + 1 |
| `UGridListView.cs` | 等尺寸网格列表，按行/列计算 start index |
| `USimpleDiffSizeListView.cs` | 支持不同尺寸 item，但 start index 需要线性累加 |

`GameTileLoop` 更贴近项目业务框架（`GameTile`、`GameUIComponent`、`Events.Common.NextFrameExecute`），而 `IUListView` 更像独立组件库。

两者的共同思想都是：

```text
content offset → start index → 复用固定 item 池 → 绑定新数据
```

---

## Gallery 复刻说明

复刻 demo 放在：

```text
gallery/advanced-text.html
```

页面顶部可以在两个标签之间切换：

- `AdvancedText`：图文混排复刻
- `GameTileLoop`：虚拟滚动复刻

GameTileLoop demo 中：

| Demo 元素 | 对应源码 |
|-----------|----------|
| `dataCount` 滑条 | `DataCount` / `EnsureSize(realDataCount)` |
| `m_startRowOrCol` 滑条 | `ScorwRectMove()` 计算得到的起始行 |
| 固定数量卡片 | `ChildCount == m_viewItemCount` |
| 卡片上的 pool item 编号 | 被复用的 UI GameObject |
| 卡片上的 dataIndex | `onUpdateItem(obj, currentDataIndex)` |
| front / behind padding 数值 | `ExpandPadding()` |
| `ScrollTo(dataCount / 2)` | `ScrollTo(index)` |

为了便于在浏览器中展示，demo 使用 Three.js 正交相机绘制 UI 卡片，没有引入真实 DOM 滚动容器。其目的是复刻算法结构，而不是一比一复刻 Unity `ScrollRect` 行为。

---

## 技术归纳

这段经验可以归结为：

- Unity UGUI **虚拟滚动列表**
- ScrollRect **对象池复用**
- 大数据量 UI **性能优化**
- LayoutGroup / RectTransform **布局控制**
- 可视区裁剪与滚动索引计算

更适合的简历表述：

> 维护/开发 Unity UGUI 虚拟滚动容器：基于 ScrollRect 和 LayoutGroup 实现 item 循环复用，通过起始行计算、动态 padding 和对象池将大数据量列表的 UI 节点数控制在可视区规模，并支持 ScrollTo 定位与增删数据刷新。

避免写成：

- 「无限地图渲染」
- 「底层渲染引擎优化」
- 「GPU Instancing 优化」

它更准确地属于 **UI 虚拟化 / 列表性能优化**。

---

## 可迁移到 Web / Three.js 的思路

在 Web 或 Three.js 中可以对应为：

| Unity | Web / Three.js |
|-------|----------------|
| `ScrollRect.content.anchoredPosition` | `scrollTop` / 自定义 offset |
| `m_startRowOrCol` | `Math.floor(scrollTop / itemHeight)` |
| `ChildCount` item 池 | 固定数量 DOM 节点 / Mesh |
| `onUpdateItem` | 重新绑定数据到节点 |
| `ExpandPadding()` | `padding-top` / `padding-bottom` / spacer |
| `SetSiblingIndex` | DOM reorder / mesh z-order |

Web 里常见实现就是：

```text
totalHeight = dataCount * itemHeight
startIndex = floor(scrollTop / itemHeight)
visibleItems = data.slice(startIndex, startIndex + poolCount)
translateY = startIndex * itemHeight
```

`GameTileLoop` 的 `ExpandPadding()` 则是 Unity LayoutGroup 环境下对这套思路的实现。

---

## 小结

`GameTileLoop` 的关键不是“滚动”，而是 **把滚动位置映射成数据起始索引，并用少量 UI 对象持续表现大量数据**。

核心链路：

```text
数据量 → 计算总行数 → 创建可视区 + 缓冲池
滚动偏移 → 起始行/列 → 复用 item → onUpdateItem 绑定数据
起始行变化 → 调整 padding → 维持完整 content 滚动感
```

这与 `AdvancedText` 的“顶点分流”一样，都是项目 UI 性能优化中的典型工程手法：不改变用户看到的结果，但显著减少底层对象数量和刷新成本。
