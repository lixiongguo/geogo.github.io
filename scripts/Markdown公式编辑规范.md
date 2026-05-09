# Markdown 数学公式编辑规范

> 适用场景：Jekyll 博客 / pandoc 转换 / PDF 生成
> 工具链：pandoc + tectonic（XeTeX）+ `tex_math_dollars` 扩展

---

## 一、核心原则

**Markdown 中的公式写作应满足"双可"：网页中可渲染、PDF 中可编译。**

以下规范基于实际 PDF 生成过程中踩过的坑总结，每条规则都对应一个曾经导致编译失败的 bug。

---

## 二、行内公式 `$...$`

### 规则 1：`$` 前后必须有空格（除特定情况外）

| ❌ 错误 | ✅ 正确 |
|---------|--------|
| `在$\mathbb{R}^3$中` | `在 $\mathbb{R}^3$ 中` |
| `扭曲$\leq C$2.` | `扭曲 $\leq C$ 2.` |
| `定义$\kappa$为曲率` | `定义 $\kappa$ 为曲率` |

**例外**：公式前是 `(` 或 `（` 等标点时，不做强制要求。例如：
```
（$\mathbf{x}$ 表示坐标）
```
此类边缘情况预处理器会自动处理。

**原因**：pandoc 在列表编号环境中，`$` 紧邻中文字符或数字时会被转义为 `\$`，导致 `\mathbf`、`\symbb` 等命令出现在非数学环境中编译报错。

### 规则 2：`$...$` 内不得有中文

| ❌ 错误 | ✅ 正确 |
|---------|--------|
| `$x为未知数$` | `$x$ 为未知数` |
| `$|V|个顶点$` | `$|V|$ 个顶点` |
| `$M=\{V,E,F为网格\}$` | `$M=\{V,E,F\text{为网格}\}$` |

如果确实需要在公式内写中文注释，用 `\text{...}` 包裹：
```latex
$M=\{V,E,F \mid \text{$V,E,F$ 为网格的顶点,边,面}\}$
```
> 推荐更清晰的做法：将中文描述移到公式外部。

**原因**：数学字体（latinmodern-math）不含 CJK 字形，中文字符在数学环境中无法渲染。

### 规则 3：`\begin{cases}` 不得出现在 `$...$` 内

| ❌ 错误 | ✅ 正确 |
|---------|--------|
| `$A(v,u) = \begin{cases}...\end{cases}$` | 改为独立公式：`$$\nA(v,u) = \begin{cases}...\end{cases}\n$$` |

**原因**：pandoc 的 `tex_math_dollars` 不解析行内数学中的 `\begin{cases}` 环境。

---

## 三、独立公式 `$$...$$` 与 `\[...\]`

### 规则 4：`$$...$$` 块内不得有空行

| ❌ 错误 | ✅ 正确 |
|---------|--------|
| `$$\nx = 1\n\ny = 2\n$$` | `$$\nx = 1\ny = 2\n$$` |

即 `$$` 和 `$$` 之间必须是一个连续的 LaTeX 块，中间不得出现空行。

**原因**：pandoc 将空行视为段落分隔符，遇到 `$$` 内的空行会提前结束数学块解析，导致后续内容散落到正文中。

### 规则 5：`$$` 必须成对出现

| ❌ 错误 | ✅ 正确 |
|---------|--------|
| `$$ x = 1 ` （缺闭合） | `$$ x = 1 $$` |
| 单独一行的 `$$` | 要么是某个公式的开或闭，不能孤立 |

**原因**：孤立的 `$$` 会被 pandoc 解析为不完整的数学块，影响其后的全部公式识别。

### 规则 6：`\sub` 不是标准命令

| ❌ 错误 | ✅ 正确 |
|---------|--------|
| `\phi_i:U_i \sub M \to \Omega` | `\phi_i:U_i \subset M \to \Omega` |

`\sub` 不是 LaTeX 标准命令。请使用 `\subset`（包含）或 `\subseteq`（包含或等于）。

---

## 四、表格

### 规则 7：在用于 PDF 输出的文档中，避免在表格单元格内使用 `^` 和 `_`

| ❌ 错误 | ✅ 正确 |
|---------|--------|
| `\| $O(n)$ \| $O(n^{1.5})$ \|` | 将表格改用列表或代码块表示 |
| 表格内写 `E^{1.5}` | 确保在 `$...$` 包裹内：`$E^{1.5}$` |

**原因**：pandoc 将 markdown 表格渲染为 LaTeX `tabular` 环境时，单元格内的 `^` 和 `_` 会裸露在数学模式外，导致编译错误。

**替代方案**：
```markdown
<!-- 原始表格 -->
| 操作 | 复杂度 |
|------|--------|
| 分解 | $O(n^{1.5})$ |

<!-- 改为列表 -->
- **分解**：$O(n^{1.5})$
```

---

## 五、其他常见问题

### 规则 8：不要用 `\(\)` 和 `$` 双重包裹

| ❌ 错误 | ✅ 正确 |
|---------|--------|
| `在 \($ \mathbb{R}^2 $\) 中` | `在 $\mathbb{R}^2$ 中`（只用一种） |

统一使用 `$...$` 表示行内公式、`$$...$$` 表示独立公式。

### 规则 9：图片使用 `![alt](url)` 标准语法

| ❌ 错误 | ✅ 正确 |
|---------|--------|
| `<img src="url" style="zoom:80%"/>` | `![alt](url)` |

PDF 生成时图片会被移除（仅保留 `[图: alt]` 占位），但标准语法确保网页端正常渲染。

### 规则 10：长破折号

在中文语境中使用 `——`（U+2014，两个 EM DASH），而非连续的 `------`。后者会在 LaTeX 中产生不可预期的结果。

---

## 六、快速检查清单

在提交文章前逐项确认：

- [ ] `$...$` 前后是否与中文/数字之间有空格？
- [ ] `$...$` 内有没有残留的中文字符？
- [ ] 是否把 `\begin{cases}` 放在了 `$...$` 中？
- [ ] `$$...$$` 块内有没有空行？
- [ ] 所有 `$$` 是否成对出现？
- [ ] 有没有拼写 `\sub`（应该用 `\subset`）？
- [ ] 表格单元格内的 `^` 和 `_` 是否都在 `$...$` 内？
- [ ] 有没有 `\($...$\)` 双重包裹的情况？

---

## 七、自动检查脚本

```python
#!/usr/bin/env python3
"""检查 markdown 文件中的公式编辑规范问题"""
import re, sys
from pathlib import Path

def check_file(filepath):
    text = Path(filepath).read_text('utf-8')
    issues = []
    lines = text.split('\n')

    # 1. $ 与中文紧邻
    for m in re.finditer(r'[\u4e00-\u9fff]\$| \$[\u4e00-\u9fff]', text):
        ln = text[:m.start()].count('\n') + 1
        issues.append(f"  L{ln}: $ 前后缺少空格")

    # 2. $...$ 含中文 (不含已经在 \text{...} 中的)
    for m in re.finditer(r'(?<!\$)\$(?!\$)((?:(?!\$).)+?)\$(?!\$)', text):
        body = m.group(1)
        # 跳过 \text{...} 包裹的
        body_no_text = re.sub(r'\\text\{[^}]*\}', '', body)
        if re.search(r'[\u4e00-\u9fff]', body_no_text):
            ln = text[:m.start()].count('\n') + 1
            issues.append(f"  L{ln}: 行内公式含中文 (应移到外部或用 \\text{{...}})")

    # 3. $ 内的 \begin{cases}
    for m in re.finditer(r'(?<!\$)\$(?!\$)(.+?)\\begin\{cases\}(.+?)\$(?!\$)', text, re.DOTALL):
        ln = text[:m.start()].count('\n') + 1
        issues.append(f"  L{ln}: \\begin{{cases}} 在行内公式中 (应改为 $$ 块)")

    # 4. $$ 块有空行
    for m in re.finditer(r'\$\$(.+?)\$\$', text, re.DOTALL):
        body = m.group(1)
        if '\n\n' in body:
            ln = text[:m.start()].count('\n') + 1
            issues.append(f"  L{ln}: $$ 块内存在空行")

    # 5. \sub 裸用
    for m in re.finditer(r'\\sub(?![a-zA-Z])', text):
        if not m.group().startswith(('\\subsection', '\\substack', '\\subset', '\\subseteq')):
            ln = text[:m.start()].count('\n') + 1
            issues.append(f"  L{ln}: \\sub 非标准命令 (请用 \\subset)")

    # 6. 双重包裹 \(\$) 
    for m in re.finditer(r'\\\(\$[^$]*\$\\\)', text):
        ln = text[:m.start()].count('\n') + 1
        issues.append(f"  L{ln}: \(\) 与 $ 双重包裹 (二选一即可)")

    return issues

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python check_math.py <file.md>")
        sys.exit(1)

    filepath = sys.argv[1]
    issues = check_file(filepath)
    if issues:
        print(f"📋 {filepath}: 发现 {len(issues)} 个问题")
        for i in issues:
            print(i)
    else:
        print(f"✅ {filepath}: 通过检查")
```

---

## 八、更新记录

| 日期 | 版本 | 内容 |
|------|------|------|
| 2026-05-09 | v1.0 | 基于 46 篇专著文章 PDF 生成的调试经验，总结 10 条编辑规范 |
