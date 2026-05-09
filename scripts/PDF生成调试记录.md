# 参数化专著 PDF 生成 - 调试记录

## 时间线

| 日期 | 阶段 | 说明 |
|------|------|------|
| 2026-05-09 | 第一阶段 | weasyprint 方案尝试失败（公式不渲染） |
| 2026-05-09 | 第二阶段 | matplotlib SVG 数学渲染 → 太慢（~1700 公式） |
| 2026-05-09 | 第三阶段 | pandoc + tectonic 方案，逐个击破公式兼容性问题 |
| 2026-05-09 | ✅ 文字版 | **文字+公式 PDF 生成成功（1.1 MB）** |
| 2026-05-09 | 第四阶段 | 图片还原——上传本地图片到 OSS、下载缓存、嵌入 PDF |
| 2026-05-09 | ✅ 完整版 | **含图片完整 PDF 生成成功（32.3 MB / 714 张图片）** |

---

## 最终方案：pandoc + tectonic

**工具链**：
- `pandoc 3.9.0.2` — Markdown → LaTeX 转换
- `tectonic 0.16.9` — XeTeX 引擎，自动下载缺失宏包

**YAML 头**：
```yaml
documentclass: ctexart     # CTex 文档类，原生支持中文
toc: true
numbersections: true
papersize: a4
fontsize: 12pt
linestretch: 1.5
geometry: margin=2.5cm
```

**Pandoc 参数**：
```
--from=markdown+tex_math_dollars+tex_math_single_backslash+raw_tex
--pdf-engine=tectonic
```

---

## 遇到的错误与修复

### 错误 1：`\includegraphics` 未定义（Undefined control sequence）

**现象**：
```
error: texput.tex:325: Undefined control sequence
```

**原因**：脚本将 Markdown 图片 `![]()` 替换为 `\includegraphics{}`，但 LaTeX 模板未加载 `graphicx` 宏包。

**修复**：改为移除所有图片引用，用 `[图: alt]` 占位。

---

### 错误 2：数学公式中的中文字符丢失

**现象**：
```
warning: Missing character: There is no "为" in font [latinmodern-math.otf]
warning: Missing character: There is no "网" in font [latinmodern-math.otf]
```

**原因**：源文档存在中文出现在数学环境中的情况，例如：
```latex
$$M=\{V,E,F |V,E,F为网格的顶点,边,面\}$$
```
拉丁数学字体（latinmodern-math.otf）不含中文字形。

**统计**：全书共 **63 处** 数学环境含中文。

**修复**：编写 `wrap_chinese_in_math()` 函数，将数学表达式中的 CJK 片段自动包围 `\text{...}`。

---

### 错误 3：`\{` / `\}` 导致中文包裹函数失败

**现象**：`wrap_chinese_in_math()` 最初版本将 `\{` 视为 LaTeX 命令 `\{` 后跟参数 `{...}`，导致大括号匹配错乱，中文未被包裹。

**修复**：在反斜杠处理分支中加入单字符转义检测：
```python
if j < len(math_body) and math_body[j] in r'{}$%&_^~# ':
    result.append(math_body[i:j+1])
    i = j + 1
    continue
```

---

### 错误 4：`\\mathbf` 出现在非数学环境（LaTeX Error）

**现象**：
```
error: texput.tex:592: LaTeX Error: \mathbf allowed only in math mode.
```

**原因**：pandoc 将 `\\\$\\\$` 渲染为文本中的字面量 `\$\$`，导致其后的 `\mathbf{}` 被当作正文文本而非数学。

**根本原因**：源文档中有不规范数学分隔符。例如：
```
$$
```

只出现了单侧 `$$`（缺失配对），pandoc 无法正确识别为数学块边界。

**修复**：预处理中增加 `$$` 配对检查，补齐或移除孤立分隔符。

---

### 错误 5：`\begin{cases}` 在行内数学 `$...$` 中失败

**现象**：pandoc 将 `$A(v,u) = \begin{cases}...\end{cases}$` 转义为 `\$A(v,u)...\$`（字面美元符），数学完全丢失。

**原因**：pandoc 的 `tex_math_dollars` 解析器不允许在行内 `$...$` 中嵌套 `\begin{cases}` 环境。

**修复**：预处理中将包含 `\begin{cases}` 的行内数学自动提升为块级公式：
```python
if r'\begin{cases}' in body:
    return '\n$$' + body + '$$\n'
```

---

### 错误 6：图片从 OSS 远程 URL 无法渲染

**现象**：`\includegraphics{https://lgximgs.oss-cn-beijing.aliyuncs.com/...}` 在 tectonic 中不可用。

**原因**：LaTeX 的 `\includegraphics` 不支持 HTTP URL（需要本地文件），且全书共 **427 张远程图片**，批量下载耗时长。

**修复**：PDF 版本专注于文字与公式，移除所有图片引用。

> ⚠️ 此错误在第四阶段得到了真正的解决：将图片下载到本地缓存再嵌入 PDF（见下方错误 9-10）。

---

### 错误 7：`$$` 块内空行导致 pandoc 断开数学识别

**现象**：
```
error: texput.tex:592: LaTeX Error: \mathbf allowed only in math mode.
```

**原因**：pandoc 将空行视为段落分隔。`$$` 块内部出现 `\n\n` 时，pandoc 认为数学块已结束，将闭合 `$$` 误解为新的数学块开头，导致内容散落到正文中。

**统计**：全书 `$$` 块中有 **291 处** 含空行。

**修复**：在 `preprocess_math()` 的 `fix_display_dollar()` 中，用正则 `\n\s*\n` → `\n` 去掉块内空行。

---

### 错误 8：`$ ...$` 中 `$` 后紧跟空格不被 pandoc 识别

**现象**：
```
error: texput.tex:2029: LaTeX Error: \symbballowed only in math mode.
```
pandoc 将 `$ \mathbb{R}^3$` 输出为 `\$ \mathbb{R}^3\$`（字面美元符）。

**原因**：pandoc 的 `tex_math_dollars` 要求 `$` 后紧跟数学内容（无空格）。`$ ` 被解释为文本美元符。

**统计**：全书 **633 处** `$` 后紧跟空格。

**修复**：

1. 用正则去掉 `$` 内部首尾空格（`.strip()`）
2. **关键修复**：为每个 `$...$` 块添加外部空格 ` $...$ `，因为仅去掉内部空格后，pandoc 在列表环境中仍会将紧邻中文的 `$` 转义。

```python
def _wrap(m):
    return ' $' + m.group(1) + '$ '
content = re.sub(r'(?<!\$)\$([^\n$]+?)\$(?!\$)', _wrap, content)
```

---

### 错误 9：`\sub` 非标准命令

**现象**：
```
error: texput.tex:5759: Undefined control sequence
```

**原因**：源文件将 `\subset` 误写为 `\sub`。`\sub` 不是 LaTeX 标准命令。

**统计**：全书 **2 处**。

**修复**：正则替换 `\sub` → `\subset`（排除 `\subsection`、`\subset`、`\subsetneq` 等已知命令）。

---

### 错误 10：markdown 表格中 `^` `_` 裸露在数学外

**现象**：
```
error: texput.tex:7551: Missing $ inserted
```

**原因**：pandoc 将 markdown 表格 `| $O(n^{1.5})$ |` 渲染为 LaTeX `tabular` 时，某些单元格内的 `^` 和 `{` 可能脱离 `$` 包裹，裸露在正文中。

**修复**：将 markdown 表格统一转为 ````text` 代码块，避免进入 LaTeX 表格渲染路径。

---

### 错误 11：图片 `header-includes` 转义导致 `Missing \begin{document}`

**现象**：
```
error: texput.tex:111: LaTeX Error: Missing \begin{document}.
```
生成的 TeX 中出现了字面文本：
```latex
\textbackslash usepackage\{graphicx\}
```

**原因**：YAML `header-includes` 中 `\\\\usepackage` 经 Python 字符串和 YAML 双重解析后变成了字面文本而非 LaTeX 命令。

**修复**：直接删除 `header-includes`。pandoc 的 `ctexart` 模板已自动加载 `graphicx`。`grffile` 在现代 LaTeX 发行版中已内置。

---

### 错误 12：本地图片未上传到 OSS —— `replace_imgs_to_oss.py` 正则不匹配反斜杠

**现象**：dry-run 显示 0 处替换，但 `grep` 发现有大量 `../../imgs\xxx.png` 本地路径。

**原因**：脚本的正则 `imgs/[^)]+` 只匹配正斜杠 `imgs/`，但 Windows 下保存的文件使用反斜杠 `imgs\`。

**统计**：
- 本地图片引用：**691 处**，分布于 **71 个 .md 文件**
- 涉及唯一图片：**657 张**（`imgs/` 目录中 656 张存在，1 张缺失）

**修复**：将正则中的 `imgs/` 改为 `imgs[/\\]`（同时匹配正反斜杠）：
```python
MD_IMG_PATTERN = re.compile(
    r'(!\[[^\]]*\])\(([^)]*imgs[/\\][^)]+)\)',
    re.IGNORECASE
)
```

---

### 错误 13：`\includegraphics` 不支持远程 URL —— 需下载到本地

**现象**：LaTeX 的 `\includegraphics{https://...}` 在 tectonic 中无法加载远程图片。

**方案演进**：
1. ❌ 直接用 OSS URL → LaTeX 不支持 HTTP 获取
2. ❌ 下载全部 427+657 = 1084 张到本地 → 下载慢但可行
3. ✅ 并行下载 + 本地缓存 → 仅首次下载，后续从 `_pdf_images/` 缓存读取

**实现**：

```python
def download_all_images(urls, max_workers=8):
    """并行下载，缓存到 scripts/_pdf_images/"""
    for url, local_path in tasks:
        if local_path.exists() and local_path.stat().st_size > 100:
            continue  # 缓存命中，跳过下载
        urllib.request.urlretrieve(url, local_path)
```

在 `preprocess_content()` 中，将远程 URL 替换为本地绝对路径：
```python
def _replace_img(m):
    local = url_map.get(url)
    if local:
        return f'![{alt}]({local})'  # 替换为本地路径
```

---

## 第四阶段：图片上传与 PDF 嵌入 完整流程

```
步骤 0: 发现本地路径图片（284 张使用 ../../imgs/ 引用）
    ↓
步骤 1: 修复 replace_imgs_to_oss.py 正则（imgs/ → imgs[/\\]）
    ↓
步骤 2: python replace_imgs_to_oss.py --dry-run  → 691 处引用，657 张图片
    ↓
步骤 3: export OSS_ACCESS_KEY_* → python upload_to_oss.py
    ↓   635 OK + 21 EXIST + 1 SKIP / 657
步骤 4: python replace_imgs_to_oss.py  实际替换路径
    ↓   71 个 .md 文件，691 处路径全部替换为 OSS URL
步骤 5: python build_monograph_pdf.py  下载 OSS 图片到本地缓存 → 嵌入 PDF
    →   ✅ 32.3 MB / 714 张嵌入图片
```

## 预处理流水线

```
原始 .md 文件
    │
    ├── strip_frontmatter()        去除 YAML 头
    ├── preprocess_content()
    │   ├── 移除图片 ![]()  → [图: alt]
    │   ├── 移除 HTML <details> / <summary>
    │   ├── 修复破折号 ------
    │   └── preprocess_math()
    │       ├── \[...\] 中文 → \text{}
    │       ├── $$...$$ 中文 → \text{}
    │       ├── $...$ 中文 → \text{}
    │       └── $...\begin{cases}...$ → $$...$$
    │
    ├── 合并 46 文件为 _monograph_combined.md
    │
    └── pandoc + tectonic → PDF
```

---

## 关键代码

### `wrap_chinese_in_math()` 状态机

逐字符解析数学体 `math_body`，状态转换：

| 当前位置 | 动作 |
|----------|------|
| `\text{` 或 `\mbox{` | 跳过整个 `{...}` 组（已包裹的中文） |
| `\{` `\}` `\$` `\%` 等 | 跳过 1 个字符（单字符转义） |
| `\command` | 跳过命令名，如有 `{...}` 参数也跳过 |
| CJK 字符序列 | 包裹为 `\text{中文...}` |
| 其他 | 原样输出 |

---

## 已知限制

1. ~~无图片~~ ✅ **已解决** — 图片从 OSS 下载到本地缓存后嵌入 PDF
2. **字体依赖** — 使用 macOS 系统字体（Songti.ttc, Kaiti.ttc 等），其他平台可能需调整
3. **数学中文** — 预处理器可应对大部分情况，但极端嵌套（如 `\text{` 内有 unmatched `}`）可能失败
4. **$$ 配对** — 孤立的 `$$` 会扰乱 pandoc 解析（预处理器会自动去除块内空行）
5. **图片缓存** — 首次生成需下载 ~700+ 张图片（约 5-10 分钟），后续从 `_pdf_images/` 缓存秒级读取

---

## 使用方法

```bash
cd /path/to/lixiongguo.github.io

# 完整版（含图片，首次需下载 ~700+ 张到缓存）
python3 scripts/build_monograph_pdf.py

# 文字版（仅公式，无图片，快速生成）
python3 scripts/build_monograph_pdf.py --no-img
```

输出文件：`参数化算法专著.pdf`

**缓存机制**：图片下载到 `scripts/_pdf_images/`，后续生成时仅下载新增/更新的图片，已有图片直接使用缓存。

---

## 编辑规范

基于以上所有问题总结出了一份 **Markdown 公式编辑规范**，参见 [`scripts/Markdown公式编辑规范.md`](Markdown公式编辑规范.md)。

规范包含：
- 10 条具体编辑规则（各有错误/正确对照示例和原因说明）
- 快速检查清单
- 自动检查脚本（`check_math.py`）
- 覆盖行内公式、独立公式、表格、特殊符号等所有已发现的问题

---

## 最终成功的关键修复总结

经过多轮迭代（13 个错误，4 个阶段），最终版本解决了以下所有问题：

| # | 问题 | 根本原因 | 修复方式 |
|---|------|---------|---------|
| 1 | 图片 URL 无法渲染 | `\includegraphics` 不支持 HTTP URL | 下载到本地缓存 `_pdf_images/`，替换为绝对路径 |
| 2 | 数学公式中文丢失 | 拉丁数学字体不含 CJK 字形 | `wrap_chinese_in_math()` 包裹为 `\text{中文}` |
| 3 | `\{ \}` 导致解析失败 | `\{` 被错误识别为 LaTeX 命令 | 添加单字符转义检测分支 |
| 4 | `\mathbf` 在非数学模式 | `$$` 块内空行导致 pandoc 断开数学 | `preprocess_math()` 去空行 |
| 5 | `$ \mathbb{} $` 不被识别 | pandoc 不允许 `$` 后紧跟空格 | `.strip()` + 外部空格 ` $...$ ` |
| 6 | `\sub` 未定义 | 应为 `\subset`，拼写错误 | 正则 `\sub` → `\subset`（保留已知命令） |
| 7 | 表格中 `^ {` 非数学 | markdown 表格 LaTeX 渲染路径裸露特殊字符 | 表格转为 ````text` 代码块 |
| 8 | `header-includes` 转义 | YAML 双重解析将 LaTeX 命令变为字面文本 | 删除 `header-includes`（pandoc 已自动加载 `graphicx`） |
| 9 | 本地图片未上传 OSS | `replace_imgs_to_oss.py` 正则只匹配 `imgs/` 正斜杠 | 改为 `imgs[/\\]` 同时匹配反斜杠 |
| 10 | **列表内 `$...$` 被转义** | pandoc 列表环境中 `$` 紧邻中文/数字被转义 | 为每个 `$...$` 添加外部空格 ` $...$ ` |

### 预处理最终流水线

```
步骤 0: 提取所有远程图片 URL → 并行下载到 scripts/_pdf_images/ 缓存
    ↓
原始 .md → 去 frontmatter
        → 远程图片 URL → 本地路径 (从 url_map)
        → 去 HTML details/summary/br
        → markdown 表格 → text 代码块
        → 破折号标准化
        → \sub → \subset
        → \($...$\) 双包裹修复
        → $ 内部空格 strip
        → $$ 块内空行去重 + 中文 → \text{}
        → $ 外部空格添加 ( $...$ )  ← 关键修复
        → 合并 46 文件
        → pandoc + tectonic → PDF  (图片通过本地绝对路径嵌入)
```

**最终产物**：`参数化算法专著.pdf` — 32.3 MB，714 张嵌入图片，LaTeX 数学公式渲染。
