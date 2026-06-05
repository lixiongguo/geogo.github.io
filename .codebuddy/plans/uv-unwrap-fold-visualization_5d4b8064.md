---
name: uv-unwrap-fold-visualization
overview: 在 UV 展开面板中，根据 3D 网格边的二面角将边分类为"峰折"（凸边/山脊）和"谷折"（凹边/沟槽），并用不同颜色渲染，直观展示展开后每条边的折叠类型。
todos:
  - id: compute-fold-types
    content: 新增 computeEdgeFoldTypes 函数：基于 3D 顶点坐标和三角形面计算每条边的峰折/谷折/平坦分类
    status: completed
  - id: modify-uv-mesh
    content: 修改 buildUvMesh 函数：按边分类将 UV 边分三组独立渲染，用不同颜色区分峰折(橙红)、谷折(青蓝)、平坦/边界(灰蓝)
    status: completed
    dependencies:
      - compute-fold-types
  - id: add-legend
    content: 在 UV 面板区域添加峰折/谷折颜色图例，方便用户理解颜色含义
    status: completed
    dependencies:
      - modify-uv-mesh
---

## 需求概述

在 UV 展开页面的右侧 UV 网格面板中，基于原始 3D 网格的二面角计算，对展开后的每条边用不同颜色渲染，以区分峰折（mountain fold）、谷折（valley fold）和平坦/边界边。

## 核心功能

- **二面角计算**：在 JavaScript 端根据 `currentMeshData.positions`（3D 顶点坐标）和 `faces`（三角形面索引）计算每个三角形的法向量，再对每条内部边（被两个三角形共享的边）计算二面角
- **边分类**：根据二面角的符号和阈值，将每条边分类为峰折（局部凸起，正值）、谷折（局部凹陷，负值）或平坦/边界（绝对值小于阈值或无配对三角形）
- **UV 面板分色渲染**：修改 `buildUvMesh()` 函数，将三类边分别渲染为独立颜色的 `THREE.LineSegments`，组合到 `THREE.Group` 中返回

## 技术方案

### 二面角计算逻辑

利用 `currentMeshData.positions`（`Array<[number,number,number]>`）和 `currentMeshData.faces`（`Array<[number,number,number]>`）在 JS 端计算：

1. **预计算每个三角形的法向量**：遍历所有三角形面，用叉积计算面法向量并归一化
2. **构建边到面的映射**：遍历所有面，以 `"min(a,b)_max(a,b)"` 为键，记录每条边被哪些面共享
3. **对每条内部边计算二面角**：

- 用 `n1`、`n2` 表示两个共享面的法向量
- 边方向向量 `e = v2 - v1`
- 二面角 `θ = atan2(dot(e, cross(n1, n2)), dot(n1, n2))`
- `θ > +threshold` → 峰折（mountain fold）
- `θ < -threshold` → 谷折（valley fold）
- `|θ| <= threshold` → 平坦（flat）

4. **边界边**（只被 1 个三角形使用）→ 标记为"平坦/边界"

阈值设为约 1°（~0.0175 rad），过滤噪声。

### 渲染方案

修改 `buildUvMesh(uv, faces, anchors, showPins)` 函数：

- 构建三个独立的 `LineSegments`：
- **peakLines**：峰折边 → 暖色（如 `#ff6b6b` 橙红）
- **valleyLines**：谷折边 → 冷色（如 `#4ecdc4` 青蓝）
- **flatLines**：平坦/边界边 → 保持现有风格（如 `#5a7fcc` 灰蓝，透明度略低）
- 将三个 `LineSegments` 组合到一个 `THREE.Group` 中
- 返回 `{ lines: group, peaks: peakLines, valleys: valleyLines, flats: flatLines, pins }`

### 性能分析

- 时间：O(F + E)，F=面数，E=边数。对 10 万面模型，计算在 ~20ms 内完成
- 空间：额外 O(F + E) 用于存储法向量和边映射

### 兼容性

- `buildUvMesh` 返回值结构变更：`lines` 从 `LineSegments` 变为 `THREE.Group`。调用处（第 3394 行）`uvScene.add(currentUvLines)` 仍然兼容（Group 和 LineSegments 都是 Object3D）
- 不影响 PDF 导出、扭曲着色等其他功能
- 四边形网格同样支持（使用三角形面索引即可，二面角定义在三角面上）

## 实现细节

### 目录结构

只修改一个文件：

```
uv-unwrap.html  # [MODIFY] 新增 computeEdgeFoldTypes() 函数 + 修改 buildUvMesh() 函数 + 添加图例UI
```

### 关键修改点

1. **新增 `computeEdgeFoldTypes(positions, faces, threshold)` 函数**（约第 2740 行之前）

- 输入：3D 顶点坐标、三角形面索引、阈值
- 输出：`Map<string, string>`，键为边去重键 `"min_max"`，值为 `"peak"` / `"valley"` / `"flat"`

2. **修改 `buildUvMesh(uv, faces, anchors, showPins)`**（第 2741-2797 行）

- 调用 `computeEdgeFoldTypes(currentMeshData.positions, faces)` 获取边分类
- 将 `segments` 拆分为 `peakSegs`、`valleySegs`、`flatSegs` 三个数组
- 分别构建 `LineSegments` 并组合到 `THREE.Group`

3. **在图例/UI 区域添加峰折/谷折颜色说明**（可选，提升可读性）

- 在 UV 面板标题或底部添加小色块图例