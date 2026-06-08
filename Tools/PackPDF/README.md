# PackPDF / 文档整理工具

将 Markdown 文章合并为 PDF，上传本地图片到阿里云 OSS 图床，并检查公式规范。

**GUI 一键启动**：双击 `run.bat` 或 `python app.py`

可在任意机器上使用：复制整个 `Tools/PackPDF` 目录即可。

## GUI 功能

| 标签页 | 功能 |
|--------|------|
| **PDF 打包** | 选择 md 目录 → 合并 → pandoc + xelatex 生成 PDF |
| **图床上传** | 扫描 `_posts/` 本地图片 → 上传 OSS → 替换 md 路径 |
| **公式检查** | 递归检查目录下 `.md` 的公式写作规范 |

底部**彩色日志**：
- 白色 — 普通信息
- 黄色 — 警告（缺失图片、规范问题等）
- 红色 — 错误（上传失败、编译失败等）

## 环境要求

| 组件 | 用途 | 何时需要 |
|------|------|----------|
| Python 3.9+ | 编排与 GUI | 始终 |
| [Pandoc](https://pandoc.org/installing.html) | Markdown 转换 | 始终 |
| MiKTeX / TeX Live（含 **xelatex**） | 章节 PDF | `merge_pdf.py` / GUI |
| [Tectonic](https://tectonic-typesetting.github.io/) | 专著 PDF | `build_monograph.py` |
| Pillow、PyPDF2、oss2 | GIF 转 PNG、页数统计、OSS 上传 | `pip install -r requirements.txt` |

**中文字体**：章节模式默认 SimSun（宋体）。macOS/Linux 请安装 CJK 字体或修改 `packpdf/core.py` 中的字体变量。

## 快速开始（GUI）

**Windows**：双击 `run.bat`

```powershell
cd Tools/PackPDF
pip install -r requirements.txt
python app.py
```

**macOS / Linux**：`chmod +x run.sh && ./run.sh`

顶部设置**项目根目录**（博客仓库），各标签页共用。图床需 OSS AccessKey，可填 GUI 或设环境变量 `OSS_ACCESS_KEY_ID` / `OSS_ACCESS_KEY_SECRET`。

## 命令行工具

```bash
cd Tools/PackPDF

# 单章/目录打包（xelatex）
python merge_pdf.py "<md目录>" "<输出.pdf>" "文档标题" --single-chapter
python merge_pdf.py --check-deps

# 整本专著（tectonic，默认输出到仓库根目录 参数化算法专著.pdf）
python build_monograph.py
python build_monograph.py --no-img
python build_monograph.py -o my_book.pdf

# 辅助工具
python count_words.py "_posts/1.Parameterization/1.基础曲面展开方法"
python check_math.py --all "_posts/1.Parameterization"
python fix_math.py "_posts/1.Parameterization/1.基础曲面展开方法"
```

## 目录结构

```
PackPDF/
├── app.py                 # GUI 主程序
├── merge_pdf.py           # CLI：章节打包
├── build_monograph.py     # CLI：整本专著
├── count_words.py         # 字数统计
├── check_math.py          # 公式规范检查
├── fix_math.py            # 公式批量修复
├── run.bat / run.sh
├── requirements.txt
├── docs/                  # 公式规范与调试记录
├── build/                 # 中间产物（gitignore）
└── packpdf/
    ├── core.py            # 章节合并 + xelatex
    ├── monograph.py       # 专著合并 + tectonic
    ├── preprocess.py      # 公式/表格预处理
    ├── oss.py             # 图床上传
    ├── math_check.py      # 公式检查
    ├── deps.py
    ├── config.py
    └── ui/log_panel.py    # 彩色日志组件
```

## 自定义工具路径

```powershell
$env:PACKPDF_EXTRA_PATH = "D:\Tools\Pandoc;D:\MiKTeX\miktex\bin\x64"
```

## 文档

- `docs/Markdown公式编辑规范.md` — 写作规范
- `docs/PDF生成问题记录.md` — 工具链说明与踩坑记录
- `docs/PDF生成调试记录.md` — 专著生成调试过程

## 常见问题

- **找不到 pandoc / xelatex**：GUI 中点「检测依赖」，或设置 `PACKPDF_EXTRA_PATH`
- **公式编译失败**：先 `python check_math.py --all <目录>`，参考 `docs/Markdown公式编辑规范.md`
- **GIF 图片缺失**：安装 Pillow
- **编译失败**：查看 `build/merged.log` 或 `build/monograph/` 下的日志
