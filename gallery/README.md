# Gallery 新增条目指南

## 文件结构

每个 Gallery 条目由 **三个文件 + 两条注册** 组成：

```
gallery/
├── 我的新作品.html      # 交互页面（只写左侧画布内容）
├── 我的新作品.md        # 说明文档（Markdown）
│
_data/
├── gallery.yml          # [注册1] 卡片索引信息
├── gallery_help.yml     # [自动生成] 说明面板 HTML
```

## `.md` ↔ `.html` 如何对应？

**不是靠文件名，而是靠 `slug` 关联**。关联链如下：

```
.html frontmatter slug          流水线自动 slug(.md)         gallery.yml slug
        ↓                              ↓                         ↓
   "webgl-water"    ←──── 同一个 slug ────→    "webgl-water"
        ↓                              ↓
  page.slug 查 _data/gallery_help  →  key = "webgl-water" → HTML 内容
```

所以 `.html` 和 `.md` 的**文件名可以不同**，只要 slug 相同即可。例如：

```
WebGL Water.html   →  slug: webgl-water
WebGL Water.md     →  pipeline slugify("WebGL Water") = webgl-water  ✓

cpu-path-tracing.html  →  slug: cpu-path-tracing
cpu-path-tracing.md    →  pipeline slugify("cpu-path-tracing") = cpu-path-tracing  ✓
```

> slug 规则：取 `.md` 文件名 → 小写 → 非字母数字替换为 `-` → 去首尾 `-`

---

## 快速新增（三步）

### 第一步：创建 HTML 页面

在 `gallery/` 下新建 `我的新作品.html`，**只需写 Jekyll frontmatter + 左侧交互内容**：

```html
---
layout: gallery_item          # 固定写法，使用统一分屏布局
slug: my-new-work             # 唯一标识，小写英文+连字符
title: 我的新作品              # 页面标题
---

<!-- 以下内容会自动渲染到左侧 canvas-panel -->
<style>
  /* 你的自定义样式 */
</style>

<!-- 你的交互内容：canvas、控制面板、html 等 -->

<script>
  // 你的交互脚本
</script>
```

> **重点**：`layout: gallery_item` 是统一布局，自动提供：
> - 暗色主题 + 分屏布局（左交互 + 右说明）
> - 右侧 380px 说明面板，内容来自你的 `.md` 文件
> - 响应式适配（移动端上下布局）
> - MathJax 数学公式渲染

### 第二步：编写说明文档

在 `gallery/` 下新建 `我的新作品.md`，写详细说明：

```markdown
## 标题

这里写你的技术说明、算法原理、使用指南等。

支持全部 Markdown 语法：图片、表格、代码块、数学公式等。

### 图片

![图片描述](图片URL)

### 表格

| 特性 | 说明 |
|:---|:---|
| ... | ... |

### 数学公式

$$E = mc^2$$

行内公式 $x^2 + y^2 = r^2$

### 代码

```python
print("hello")
```
```

> 说明文档会通过流水线自动转为 HTML，渲染到右侧帮助面板。

### 第三步：注册到索引

编辑 `_data/gallery.yml`，在末尾追加一条：

```yaml
- slug: my-new-work
  title: 我的新作品
  description: 一句话描述，会显示在 Gallery 卡片列表页
  thumbnail: /assets/gallery/my-new-work.png
  detail_url: "/gallery/我的新作品.html"
```

| 字段 | 说明 |
|:---|:---|
| `slug` | 与 HTML 的 frontmatter 中 `slug` 一致 |
| `title` | 卡片标题 |
| `description` | 卡片一句话描述 |
| `thumbnail` | 缩略图路径（放在 `assets/` 下） |
| `detail_url` | 指向你新建的 `.html` 文件 |

---

## 运行流水线

每次修改 `.md` 文件后，运行：

```bash
python3 Tools/gallery_pipeline.py
```

这会：
1. 扫描所有 `gallery/*.md`
2. 转为 HTML
3. 输出 `_data/gallery_help.yml`

Jekyll 构建时会自动读取 `_data/gallery_help.yml` 渲染帮助面板。

---

## 命名规范

| 规范 | 说明 |
|:---|:---|
| 文件名 | 用中文（与标题一致），如 `我的新作品.html`、`我的新作品.md` |
| slug | 小写英文 + 连字符，如 `my-new-work` |
| slug 唯一性 | 必须与已有 slug 不重复 |
| 缩略图 | 放 `assets/gallery/` 下，命名与 slug 一致 |

---

## 完整示例

假设要新增「分形山」条目：

**1. `gallery/分形山.html`**
```html
---
layout: gallery_item
slug: fractal-mountain
title: 分形山
---
<style>
  canvas { display: block; margin: 0 auto; }
</style>
<canvas id="mountain" width="800" height="500"></canvas>
<script>
  // 分形山生成算法...
  const canvas = document.getElementById('mountain');
  const ctx = canvas.getContext('2d');
  // ...
</script>
```

**2. `gallery/分形山.md`**
```markdown
## 分形山 — Diamond-Square 算法

分形山使用中点位移法生成自然地形的三维高度场...

### 算法步骤

1. 初始化四个角点
2. 对每条边取中点，加随机偏移
3. 对中心点取均值，加随机偏移
4. 递归缩小网格

$$
h_{mid} = \frac{h_1 + h_2 + h_3 + h_4}{4} + \text{random}(\sigma)
$$
```

**3. `_data/gallery.yml` 追加**
```yaml
- slug: fractal-mountain
  title: 分形山
  description: Diamond-Square 算法实时生成分形山脉地形。
  thumbnail: /assets/gallery/fractal-mountain.png
  detail_url: "/gallery/分形山.html"
```

**4. 运行流水线**
```bash
python3 Tools/gallery_pipeline.py
```

---

## 已有条目

| slug | 标题 | 文件 |
|:---|:---|:---|
| `webgl-water` | WebGL 水面焦散 | `WebGL Water.html` / `WebGL Water.md` |
| `cpu-path-tracing` | CPU 路径追踪 | `cpu-path-tracing.html` / `cpu-path-tracing.md` |
| `wfc` | WFC 纹理合成 | `wfc.html` / `wfc.md` |

---

## 注意事项

- 修改 `.md` 后**必须运行** `gallery_pipeline.py`，否则帮助面板不会更新
- `.html` 中不要写 `<html>`/`<head>`/`<body>` 标签，这些由布局模板提供
- 页面特定的 `<style>` 和 `<script>` 写在 `.html` 内容中即可
- 如果需要页面级别的额外 head 内容（如特定 meta 标签），可用 `head_extra` 字段
- slug 一旦确定尽量不要改，否则需要同步更新 `gallery.yml` 中的对应项
