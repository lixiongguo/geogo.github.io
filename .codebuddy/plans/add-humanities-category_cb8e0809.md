---
name: add-humanities-category
overview: 在 Jekyll 博客侧边栏中新增独立的「人文社科」板块，与现有「文章分类」栏区分开
todos:
  - id: add-humanities-section
    content: 在 sidebar.html 中新增独立的「人文社科」sidebar 区块，并补充 case/when 映射
    status: completed
---

## Product Overview

在 Jekyll 博客的侧边栏中新增一个**独立的**「人文社科」板块，与现有「文章分类」「算法测试」等栏目在视觉和结构上明确区分开。

## Core Features

- 新增独立的 sidebar 区块，标题为「人文社科」，与「文章分类」「算法测试」并列
- 分类标识使用 `Humanities`（与现有 RL、Math、DL&ML 等英文命名风格一致）
- 点击可跳转到分类页面展示对应文章列表
- 自动显示该分类下的文章数量
- 通过 front matter 中 `category: Humanities` 将文章归入此分类
- 不修改原有「文章分类」列表中的 case/when 逻辑，保持两套分类体系独立

## 当前 sidebar.html 结构（按区块顺序）

1. `sidebar-header` — 头像 + About me
2. `gallery-card` — Gallery 链接
3. **`sidebar-nav`** — 「文章分类」（全部文章 + case/when 映射列表 + Others）第 23-69 行
4. **`sidebar-nav algo-section`** — 「算法测试」（曲面展开、四边形网格化）第 71-77 行
5. `sidebar-nav` — 围棋项目卡片 第 79-89 行
6. `sidebar-footer` — 名言 + 访客统计

新板块将插入在第 4 个区块（算法测试）之后、第 5 个区块（围棋卡片）之前，参考 `algo-section` 的 HTML 结构写法。

## Tech Stack

- **静态站点生成器**: Jekyll（已有项目）
- **模板引擎**: Liquid（Jekyll 内置）

## Implementation Approach

参考现有 `algo-section`（第 71-77 行）的独立区块写法，在侧边栏中新增一个 `sidebar-item sidebar-nav` 独立区块。该区块包含独立的 `nav-title` 标题「人文社科」和一个指向 `category#Humanities` 的导航链接，使用与现有条目一致的 CSS 类名（`algo-link-with-icon`、`algo-mini-icon` 等），确保样式统一。同时为了兼容性，也在原有 case/when 映射中添加 `Humanities -> 人文社科` 的映射分支，防止该分类在「文章分类」列表中以英文显示。

## Implementation Notes

- 仅修改一个文件：`_includes/sidebar.html`
- 新增独立区块插入位置：在第 77 行（`algo-section` 结束标签 `</div>`）之后、第 79 行（围棋卡片区块开始）之前
- 在 case/when 映射中（约第 43 行之后）同步添加 `{% when 'Humanities' %}{% assign cat_display = '人文社科' %}` 分支
- 使用 `site.categories.Humanities.size` 获取文章数量，当无文章时显示 (0)

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 确认 sidebar.html 中精确插入位置（行号、缩进格式），以及验证 algo-section 区块的完整 HTML 结构作为参考模板
- Expected outcome: 确保新增区块的代码风格、缩进、类名使用与现有代码完全一致