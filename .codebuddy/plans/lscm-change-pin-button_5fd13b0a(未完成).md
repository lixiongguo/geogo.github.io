---
name: lscm-change-pin-button
overview: 在 LSCM 算法参数栏添加"改pin点"按钮，点击后重新选择一对不同的较远顶点作为 pin 点。
todos:
  - id: add-html-button
    content: 在参数面板 param-panel 中新增 param-lscm-pin span 及"改pin点"按钮元素
    status: pending
  - id: add-js-state-and-functions
    content: 新增 currentCustomAnchors 状态变量、chooseAlternativeAnchorPair 函数、updateModelPinPoints 函数
    status: pending
    dependencies:
      - add-html-button
  - id: modify-onparamchange
    content: 修改 onParamChange 控制按钮显隐，以及算法切换时重置自定义 anchors
    status: pending
    dependencies:
      - add-html-button
  - id: modify-solvers
    content: 修改 solveLSCMAsync 和 solveBDLSCMAsync 优先使用 currentCustomAnchors
    status: pending
    dependencies:
      - add-js-state-and-functions
  - id: add-click-handler-and-reset
    content: 绑定按钮点击事件 onChangePinClick，并在 loadModelPreview 中重置自定义 anchors
    status: pending
    dependencies:
      - add-js-state-and-functions
      - modify-onparamchange
---

## 用户需求

在 uv-unwrap.html 的 LSCM 算法被选中时，参数栏中新增一个"改pin点"按钮。点击该按钮后，系统重新选取一对不同于当前 pin 点的较远顶点作为新的 pin 点，并同步更新 3D 模型视图中的 pin 点标记显示。

## 核心功能

- 按钮仅在 LSCM 算法（含 BD-LSCM）被选中时显示，切换至其他算法时隐藏
- 点击按钮后，自动选取与当前 pin 点不同的一对较远顶点作为新 pin 点
- 新 pin 点会立即反映在 3D 模型视图中的橙色高亮点上
- 新 pin 点将在下次点击"展开"时传递给 WASM 求解器，影响 UV 展开结果
- 加载新模型或切换算法时，自定义 pin 点自动重置，恢复为默认最远顶点对

## 技术方案

### 实现策略

在现有参数面板 `param-panel` 中新增一个 `span` 元素承载按钮，通过 `onParamChange()` 控制显隐。新增状态变量 `currentCustomAnchors` 追踪用户手动选择的 pin 点，求解器优先使用该自定义值，null 时回退到自动选择。按钮点击时调用新增的 `chooseAlternativeAnchorPair()` 函数排除当前 pair 选出次优 pair。

### 关键决策

- **排除策略**：重新选取时排除当前 pin 点对（而非仅排除一个顶点），确保每次点击都产生不同于当前的结果
- **重置时机**：模型加载（`loadModelPreview`）时重置 `currentCustomAnchors = null`，确保新模型默认使用自动选点；算法切换出 LSCM 时也重置，避免残留
- **视图更新**：不重建整个模型组，只替换当前 `currentModelGroup` 中的 pin 点 `THREE.Points` 对象，性能更优

### 实现细节

#### 1. HTML 修改（参数面板内）

在 `param-none` span 之后、`param-tutte-boundary` 之前，新增 `param-lscm-pin` span：

```html
<span id="param-lscm-pin" style="display:none;font-size:12px;color:#c6d1f4;">
  <button id="change-pin-btn" type="button" style="padding:4px 10px;font-size:12px;border-radius:6px;cursor:pointer;">改pin点</button>
</span>
```

#### 2. CSS 修改

为按钮增加样式，保持与现有 UI 风格一致，hover 时有背景色变化。

#### 3. JavaScript 修改

- **新增状态变量**（行 385 附近）：`let currentCustomAnchors = null;`
- **新增函数 `chooseAlternativeAnchorPair(vertices, excludePair)`**（行 648 之后）：遍历顶点对，返回距离最大且不等于 `excludePair`（无序比较）的索引对 `[a, b]`
- **新增函数 `updateModelPinPoints(anchors)`**：从 `currentModelGroup` 中移除旧 `currentPins`，用新 anchors 创建 `THREE.Points` 并添加回组，更新 `currentPins` 引用
- **修改 `onParamChange()`**（行 719）：增加 `param-lscm-pin` 的显隐控制，`m === 'lscm'` 时 `display=''`，否则 `display='none'`；同时当算法非 LSCM 时重置 `currentCustomAnchors = null`
- **修改 `solveLSCMAsync`**（行 786）：`const anchors = currentCustomAnchors || chooseAnchorPair(vertices);`
- **修改 `solveBDLSCMAsync`**（行 880）：同上
- **修改 `loadModelPreview`**（行 1827 后）：`currentCustomAnchors = null;` 确保新模型重置自定义选点
- **添加按钮点击事件绑定**（行 775 附近）：`document.getElementById('change-pin-btn').addEventListener('click', onChangePinClick);`
- **新增 `onChangePinClick()` 函数**：若 `currentMeshData` 存在，获取当前 anchors（优先 customAnchors → chooseAnchorPair），调用 `chooseAlternativeAnchorPair` 得到新 pair → 存入 `currentCustomAnchors` → 调用 `updateModelPinPoints` 更新模型视图

### 性能考量

- `chooseAlternativeAnchorPair` 复杂度 O(n²)，与 `chooseAnchorPair` 一致，顶点数通常不超过数千，无性能问题
- 视图更新仅替换 pin 点对象（几个顶点），不重建整体模型组

### 边界处理

- 模型未加载时点击按钮：`currentMeshData` 为 null，忽略操作
- 顶点数少于 2：实际场景不会出现，但 added 逻辑中不处理（保持现有行为）
- 极端情况所有顶点重合：`chooseAlternativeAnchorPair` 返回 `[0, 1]` 回退