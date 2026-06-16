---
name: merge-bounded-distortion-articles
overview: 将 `2018-03-20-有界失真平面变形.md` 的 §2（网格路线 CPL + Lipman 2012 + BD-LSCM）合并入 `扭曲有界调和映射.md`，形成覆盖三条路线（网格 BDHM + 单连通 BDHM + 多连通 GLID）的统一文档。
todos:
  - id: insert-mesh-section
    content: 在扭曲有界调和映射.md 第195行插入网格路线章节：从2018-03-20-有界失真平面变形.md提取§2内容（第70-177行，2.1单面有界空间→2.2局部帧凸化→2.3组装整网格→2.4算法框架→2.5 BD-LSCM），章节标题改为`## 第二部分：网格路线 — 扭曲有界映射空间 (Lipman 2012)`，子章节编号改为2.1-2.5
    status: completed
  - id: renumber-parts
    content: 将原第二/三/四部分的编号顺移：原`## 第二部分：BDHM`改为`## 第三部分：BDHM`，原`## 第三部分：GLID`改为`## 第四部分：GLID`，原`## 第四部分：总结与对比`改为`## 第五部分：总结与对比`
    status: completed
    dependencies:
      - insert-mesh-section
  - id: update-intro
    content: 更新导言段落（第7-10行）：补充Lipman 2012引用，将"本文整合两篇SIGGRAPH论文"改为"本文整合三篇SIGGRAPH核心论文"，新增条目 `(0) Lipman 2012 — Bounded Distortion Mapping Spaces for Triangular Meshes`
    status: completed
    dependencies:
      - insert-mesh-section
  - id: update-comparison-table
    content: 在第五部分对比表（原第727-739行）新增"网格路线 (Lipman 2012)"列，填入：拓扑=任意三角网格、表示=逐面仿射α[p]+β[p̄]+δ、自由度=顶点UV、约束施加=每个三角面、处理非凸=局部帧→最大凸子空间、求解=SOCP、单射认证=凸约束内蕴含、零空间=锚点决定、每次迭代=SOCP、能量选择=Dirichlet/ARAP/LSCM
    status: completed
    dependencies:
      - renumber-parts
  - id: update-evolution-diagram
    content: 在演进图（原第743-750行）顶部新增网格路线分支：`扭曲有界映射空间 (Lipman 2012, SIGGRAPH)`→`逐面仿射 + 局部帧凸化 → SOCP`，并使原Cauchy→BDHM→GLID链显示为并列分支
    status: completed
    dependencies:
      - renumber-parts
  - id: update-engineering-notes
    content: 在实践要点（原第752-758行）新增网格路线注意事项：项6关于局部帧迭代重对齐需每轮更新、项7关于网格规模对SOCP求解时间的影响
    status: completed
    dependencies:
      - renumber-parts
---

## 需求概述

按照之前对比分析的建议，将两篇有界失真映射文章合并为一篇统一文档，形成覆盖"网格路线 (CPL/Lipman 2012) + BDHM (单连通 SOCP) + GLID (多连通 Newton-Eigen)"三条路线的完整综述。

## 核心变更

1. 从源文件 A `2018-03-20-有界失真平面变形.md` 提取 §2 网格路线（第70-177行，约110行）
2. 插入源文件 B `扭曲有界调和映射.md` 第一部分结束处（第195行 `---` 后），作为新的**第二部分：网格路线**
3. 原第二、三、四部分编号分别+1，变为第三、四、五部分
4. 同步更新导言、对比表、演进图、实践要点