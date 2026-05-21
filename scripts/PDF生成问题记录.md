# PDF 生成问题记录

使用 `tools/merge_pdf.py` 将 .md 文章集合生成为 PDF 的完整问题解决记录。

---

## 工具链说明

整个生成管线由以下工具协同工作，每一层职责不同：

| 工具 | 角色 | 输入 | 输出 | 核心能力 |
|------|------|------|------|----------|
| **Python** (`merge_pdf.py`) | 编排者 | .md 文件夹 | — | 文件合并、预处理、路径解析、HTTP 下载、格式转换 |
| **pandoc** | 文档转换器 | .md (Markdown) | .tex (LaTeX) | 通用文档格式互转，理解 30+ 种格式的语法差异 |
| **xelatex** | 排版引擎 | .tex (LaTeX) | .pdf | 将 LaTeX 源码编译为 PDF，原生支持 Unicode/CJK |
| **PIL/Pillow** | 图像处理 | GIF 图片 | PNG 图片 | GIF→PNG 转换（xelatex 不支持 GIF） |
| **PyPDF2** | PDF 验证 | .pdf | 页数 | 解析 PDF 结构，获取准确页数 |

### pandoc 原理

pandoc 的工作方式是**解析 → AST → 渲染**：

```
.md 文本
  → [词法分析] Token 流
  → [语法分析] AST（抽象语法树，所有格式的内部统一表示）
  → [Writer] .tex / .html / .docx / .epub ...
```

这意味着 pandoc 不只是在做"字符串替换"，而是真正理解了 Markdown 的层级结构（标题、段落、列表、代码块、数学公式等），然后以目标格式的惯用写法重新输出。

**关键细节**：pandoc 在解析 Markdown 中的 `$...$`（内联数学）时，如果内容过于复杂（如包含 `\begin{cases}` 这样的 LaTeX 环境），可能无法正确识别数学模式的边界，导致将 `$` 转义为 `\$`（字面量美元符号），从而在输出的 .tex 中断开数学模式。这是本项目遇到的核心问题之一。

### xelatex 原理

xelatex 是 LaTeX 的现代编译引擎，与传统 pdfLaTeX 的区别：

| | pdfLaTeX | XeLaTeX |
|---|---------|---------|
| 字体 | 仅支持 TeX 专用字体（.tfm） | 直接使用系统字体（.ttf/.otf） |
| Unicode | 不原生支持 | 原生支持 UTF-8 |
| 中文 | 需要 CJK 宏包/复杂配置 | `\setCJKmainfont{SimSun}` 即可 |
| 图片格式 | PNG、JPG、PDF | PNG、JPG、PDF（不支持 GIF/BMP） |

**编译流程**：
```
.tex 源码
  → [xelatex pass 1] 生成 .aux（标签/引用/目录信息）
  → [xelatex pass 2] 读取 .aux，生成最终 .pdf（含完整目录、交叉引用）
```

这就是为什么需要两次 `xelatex` 编译——第一次记录目录结构到 .aux 辅助文件，第二次才能渲染出正确的页码和书签。

### LaTeX 数学模式

LaTeX 有两种数学模式：

| 模式 | Markdown 写法 | LaTeX 输出 | 显示方式 |
|------|-------------|-----------|---------|
| **内联** (inline) | `$E=mc^2$` | `\(E=mc^2\)` 或 `$E=mc^2$` | 嵌入段落中 |
| **显示** (display) | `$$E=mc^2$$` | `\[E=mc^2\]` 或 `$$E=mc^2$$` | 独占一行、居中 |

**关键约束**：数学模式中**不能出现中文/全角标点**，必须用 `\text{...}` 包裹。例如：

```latex
% ❌ 错误：xelatex 报 Missing $ inserted
$$ x_i \text{ 的第 } j \text{ 个邻居} $$

% ✅ 正确
$$ x_i \text{ 的第 } j \text{ 个邻居} $$
```

---

## 生成流程详解

整个 `merge_pdf.py` 的执行分为 **4 个阶段**：

### 阶段 1：Markdown 预处理（Python）

```
.md 文件逐个读取
  ├── 剥离 YAML 前置元数据 (--- ... ---)
  ├── 清理 Jekyll 标签 ({% raw %}...{% endraw %})
  ├── 移除 <!--more--> 注释
  ├── 处理图片引用：
  │   ├── HTTP URL → urllib 下载到本地 → 检测 GIF 头 → PIL 转 PNG
  │   ├── 本地相对路径 → 解析为绝对路径（尝试多个 base dir）
  │   └── 路径不存在 → 移除引用
  ├── 移除 <img> HTML 标签
  ├── 数学模式升级：$ 内含 \begin{cases} → $$...$$
  └── 数学模式 CJK 处理：$$...$$ 和 $...$ 内中文 → \text{...}
```

### 阶段 2：Markdown → LaTeX 转换（pandoc）

```
merged.md
  → pandoc --standalone \
      -f markdown+tex_math_dollars+raw_tex \
      -V mainfont=SimSun -V CJKmainfont=SimSun \
      -V geometry=margin=2.5cm
  → merged.tex
```

参数说明：
- `--standalone`：生成完整 LaTeX 文档（含 preamble）
- `-f markdown+tex_math_dollars+raw_tex`：启用 `$$` 数学块和原始 TeX 语法
- `-V mainfont=SimSun`：主字体设为宋体
- `-V CJKmainfont=SimSun`：CJK 字体设为宋体
- `-V geometry=margin=2.5cm`：页边距 2.5cm

### 阶段 3：LaTeX 后处理（Python）

pandoc 输出的 .tex 仍有不完美之处，需要额外修复：

```
merged.tex
  ├── \$ 恢复为 $（pandoc 错误转义的数学分隔符）
  ├── 图片路径规范化（\ → /，解析 ..）
  ├── \begin{figure}[htbp] → [H]（防止图片漂移到错误页面）
  └── 添加 \usepackage{float}（支持 [H] 定位）
```

### 阶段 4：PDF 编译（xelatex × 2）

```
merged.tex → xelatex pass 1 → merged.pdf (no TOC) + .aux + .toc
           → xelatex pass 2 → merged.pdf (完整 TOC + 书签 + 交叉引用)
```

两次编译的必要性：
- **Pass 1**：处理所有内容，将章节标题写入 `.aux` 和 `.toc` 文件
- **Pass 2**：读取 `.toc` 生成目录页，更新所有页码引用

---

## 已解决的问题

| # | 问题 | 根因 | 解决方式 |
|---|------|------|----------|
| 1 | `\begin{cases}` 不在数学模式中 → xelatex 报 Missing $ | pandoc 将 `$` 转义为 `\$`，导致数学模式断开 | Markdown 预处理：将包含 `\begin{cases}` 的 `$...$` 升级为 `$$...$$` |
| 2 | `\begin{cases}` 内中文全角逗号/文字 → xelatex 报 Missing $ | LaTeX 数学模式不能直接包含 CJK 字符 | Markdown 预处理：`$$...$$` 和 `$...$` 内中文包裹为 `\text{...}` |
| 3 | 图片 `Division by 0` 错误 | HTTP 图片实际是 GIF 格式但扩展名为 .png，xelatex 不支持 GIF | 下载后检测 GIF header (`GIF89a`)，用 PIL 转换为真 PNG |
| 4 | 图片路径包含 `..` 未解析 | `os.path.join` 不自动 normalize `..` | 使用 `os.path.normpath()` |
| 5 | PDF 0 页（假阳性） | PDF 1.7 使用压缩对象流，页对象在 stream 内，正则扫描不到 | 使用 PyPDF2 解析页数 |
| 6 | `<img>` 标签导致 xelatex 错误 | HTML 标签在 LaTeX 中无意义 | Markdown 预处理移除 |
| 7 | `{% raw %}` 标签残留 | Jekyll Liquid 标签 | 预处理替换为空 |
| 8 | HTTP 远程图片无法加载 | xelatex 只认本地文件 | `urllib` 预先下载到临时目录 |
| 9 | 无目录书签 | xelatex 需两次编译 | 循环执行 2 次 |

---

## 依赖

| 工具 | 安装方式 | 用途 |
|------|--------|------|
| **pandoc** | [pandoc.org/installing.html](https://pandoc.org/installing.html) | Markdown → LaTeX 转换 |
| **xelatex** | MiKTeX 或 TeX Live | LaTeX → PDF 编译 |
| **PIL/Pillow** | `pip install Pillow` | GIF→PNG 图片格式转换 |
| **PyPDF2** | `pip install PyPDF2` | PDF 页数验证 |

---

## 用法

```bash
python tools/merge_pdf.py "<md文件夹>" "<输出.pdf>" "[标题]"
```

示例：
```bash
python tools/merge_pdf.py "_posts/1.Parameterization/0.曲面展开" "输出.pdf" "曲面展开"
```
