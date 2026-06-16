---
name: expand-quadcover-article
overview: 逐节扩充"全局参数化-多值分支覆盖方法"文章，修复公式错误，补充缺失的动机说明和实现细节，整合暂存草稿内容，增加贯穿全文的示例。
todos:
  - id: fix-layer-shift
    content: 修正 layer shift 公式：用代码实现（先求有向 matching 总和，mod4 映射到 [-1,0,1]，除 4）替换原文 $h(v)/4$ 的歧义写法，并补充边界顶点跳过的说明
    status: completed
  - id: expand-symmetric-function
    content: 扩充对称覆盖函数小节：补充 sheet 0↔2、1↔3 反对称条件与 cross field 4-RoSy 对称性的关联推导，说明为什么需要这个条件来保证投影回基空间时 UV 方向一致
    status: completed
  - id: explain-projection-formula
    content: 阐释投影公式 $\phi_i(p)=[u'(\tau_U^0(p)), v'(\tau_U^1(p))]^T$ 的原理：解释 sheet 0 的 X 方向对应 u 方向、sheet 1 的 X 方向对应 v 方向的几何直觉，并补充分支顶点取所有 sheet preimage 平均的投影策略（参考 QuadCover.cpp projectCoverUVToMesh）
    status: completed
    dependencies:
      - expand-symmetric-function
  - id: complete-basis-topology
    content: 补全函数空间基的拓扑公式：明确 $n_p = 2g + n_b - 1$，解释 spanning tree cotree 边生成同调环 + BFS 连接边界分量的构造过程，并补充纯四边形约束 $\mu_j \in 2\mathbb Z$ 的含义
    status: completed
  - id: expand-phase5
    content: 整合暂存2-QuadCover.md 内容，将 Phase 5 全局连续性扩展为四步详解：构造 cut graph（同调环路径）、计算 period 系数 $\mu_j$、KKT 系统构造 harmonic 基并做 $\phi = \tilde\phi + \sum \Delta\mu_j h_j$ 修正、roundMu 纯四边形 vs 普通四边形舍入策略
    status: completed
    dependencies:
      - complete-basis-topology
      - explain-projection-formula
  - id: fix-hodge-decomposition
    content: 在 Hodge 分解小节插入与 Poisson 求解的对应关系：点明 $L\tilde u = \mathrm{div}(\vec X)$ 本身就是 Hodge 分解的实现——Laplacian 的正则性自动滤掉旋度分量 $C_K$，解得 $P_K+H_K$ 对应的势函数；补充离散 cotangent Laplacian 和散度算子的构造方式
    status: completed
  - id: add-running-example
    content: 在 matching、branch cover、Poisson 求解、period 修正各阶段末尾插入一个带单一奇异点（$ls=1/4$）的简化 mesh 示例，跟踪 sheet 粘接、UV 积分、period 舍入的全流程
    status: completed
    dependencies:
      - expand-phase5
      - fix-hodge-decomposition
---

## 用户需求

逐节扩充 `2018-01-02-全局参数化-多值分支覆盖方法.md`（原 346 行），解决以下 7 个问题：

### 1. Layer shift 公式修正

原公式 $h(v)=(\sum r)\bmod 4,\ ls(v)=h(v)/4$ 使 $ls$ 只能是 0 或小数，与"layer shift 表示跨 sheet 的净旋转"的语义矛盾。需要按代码实现修正：先求有向 matching 总和，再 mod4 映射到 [-1, 0, 1]，然后除以 4，得到 $ls(v) \in \{-0.25, 0, 0.25\}$。

### 2. 对称覆盖函数的动机补充

$f(\tau_U^0(p))=-f(\tau_U^2(p)),\ f(\tau_U^1(p))=-f(\tau_U^3(p))$ 的反对称条件过于突兀。需要解释：cover 上 sheet 0 和 sheet 2（以及 1 和 3）对应的 cross field 方向恰好反向（相差 180°），因此标量函数在这两对 sheet 上取值也取反，才能保证投影回基空间时 UV 方向一致。

### 3. 投影公式原理阐释

$\phi_i(p)=[u'(\tau_U^0(p)), v'(\tau_U^1(p))]^T$ 为何 u 取 layer 0、v 取 layer 1？需要说明：cover 上 sheet 0 的 X 方向对应基空间上 cross field 的 $\vec d$ 方向（u 方向），sheet 1 的 X 方向对应 $\vec d^\perp$（v 方向）。所以 u 从 sheet 0 取，v 从 sheet 1 取，从而投影回基空间时得到正交的 UV 参数。

### 4. 函数空间基的拓扑公式补齐

原文只说"取 $np$ 条 cut path"但未给出 $np$ 如何确定。需明确 $n_p = 2g + n_b - 1$（$g$ 为亏格，$n_b$ 为边界分量数），并解释：cut path 来自 cotree 边的同调环 + 连接不同边界分量的路径。

### 5. Phase 5 全局连续性四步展开

原文 Phase 5 仅用 3 行公式带过，需整合 `暂存2-QuadCover.md` 的四步详解：

- Step 1：构造 cut graph（spanning tree + cotree 边 → 同调生成环）
- Step 2：计算 period 系数 $\mu_j$
- Step 3：用 KKT 系统构造 harmonic 基并做修正
- Step 4：投影回原曲面

### 6. Hodge 分解落地

$K = P_K + C_K + H_K$ 过于抽象。需要点明：Poisson 求解 $L\tilde u = \mathrm{div}(\vec X)$ 本质就是 Hodge 分解——Laplacian 的正则性自动滤掉了旋度分量 $C_K$，解得的就是 $P_K + H_K$ 对应的势函数。

### 7. 增加贯穿全文的示例

需要在文章适当位置（每个阶段结束后）插入一个带一个奇异点（$ls(v)=1/4$）的简单 mesh 示例，跟着走完 matching → branch cover → Poisson → period fix → 投影的全流程。

## 实现方式

这是一个纯文档编辑任务，不涉及代码开发。

### 修改策略

- **单文件原地扩充**：在 `2018-01-02-全局参数化-多值分支覆盖方法.md` 内部逐节插入新内容
- **参考代码实现**：`QuadCover.cpp` 中的 `computeLayerShift()`、`buildBranchCover()`、`buildCutGraphAndPaths()`、`buildHarmonicBasis()`、`enforceGlobalContinuity()` 等函数是修正公式和补充细节的权威依据
- **整合暂存草稿**：`暂存2-QuadCover.md` 的 Phase 5 四步内容可直接嵌入主文章，减少从零编写
- **保持现有风格**：沿用原文的 LaTeX 公式 + 中文叙述 + OSS 图片引用的风格

### 结构规划

文章中从上到下依次修改/扩充以下位置：

1. Layer shift 小节 → 替换公式
2. 对称覆盖函数小节 → 插入动机说明段落
3. 投影公式处 → 插入原理解释段落
4. 函数空间基小节 → 补充拓扑公式 $n_p = 2g + n_b - 1$ 及来源说明
5. Phase 5 / 全局连续性小节 → 替换为四步详解（整合暂存草稿 + 代码 KKT 细节）
6. Hodge 分解小节 → 插入与 Poisson 求解的对应关系段落
7. 全文各 Phase 末尾 → 插入示例跟踪段落