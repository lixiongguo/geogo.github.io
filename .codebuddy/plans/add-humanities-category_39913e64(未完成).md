---
name: add-humanities-category
overview: 在 Jekyll 博客的侧边栏新增「人文社科」文章分类，修改 sidebar.html 添加分类映射
todos:
  - id: add-humanities-category
    content: 在 sidebar.html 的 case/when 映射中添加 Humanities -> 人文社科 分支
    status: pending
---

## Product Overview

在 Jekyll 博客的侧边栏「文章分类」下新增一个「人文社科」分类，用于发布人文社科类文章。

## Core Features

- 在 sidebar 的分类列表中新增「人文社科」条目
- 分类标识使用 `Humanities`（与现有 RL、Math、DL&ML 等英文命名风格保持一致）
- 显示名称为中文「人文社科」（与现有分类的中文显示名风格一致）
- 支持通过 front matter 中的 `category: Humanities` 将文章归入此分类
- 自动显示该分类下的文章数量
- 点击后跳转到分类页面并展示对应文章列表

## Tech Stack

- **静态站点生成器**: Jekyll（已有项目）
- **模板引擎**: Liquid（Jekyll 内置）
- **前端**: 原生 HTML/CSS/JS

## Implementation Approach

这是一个极简修改任务。当前侧边栏 `_includes/sidebar.html` 通过遍历 `site.categories` 并使用 Liquid 的 `case/when` 语句将英文分类名映射为中文显示名。只需在该 `case/when` 映射中添加一行 `{% when 'Humanities' %}{% assign cat_display = '人文社科' %}` 即可。后续用户在 `_posts/` 目录下新建 Markdown 文件时，在 front matter 中设置 `category: Humanities` 即可将文章归入此分类，Jekyll 会自动将其纳入侧边栏列表和分类页面。

## Implementation Notes

- 仅需修改一个文件：`_includes/sidebar.html` 第 36-45 行的 case/when 区块
- 新分支插入位置：在 `{% when 'DL&ML' %}{% assign cat_display = '深度学习与机器学习' %}` 之后、`{% else %}` 之前
- 文章 front matter 中使用单数形式 `category: Humanities`（注意现有文章有的用复数 `categories` 有的用单数 `category`，两者 Jekyll 都支持）
- 分类页面的展示逻辑已在 `_includes/category.html` 和 `_layouts/category.html` 中实现，无需额外修改

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 确认 sidebar.html 中 case/when 分支的精确插入位置和缩进格式
- Expected outcome: 验证修改点的准确性，确保新分类分支与现有代码风格完全一致