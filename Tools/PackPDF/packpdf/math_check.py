"""Markdown 公式规范检查。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class CheckRule:
    id: str
    title: str
    description: str
    wrong: str
    correct: str
    reason: str


CHECK_RULES: tuple[CheckRule, ...] = (
    CheckRule(
        id='space',
        title='规则 1：$ 前后须有空格',
        description='行内公式 `$...$` 与中文、数字之间应留空格，避免 pandoc 将 `$` 转义为 `\\$`。',
        wrong='在$\\mathbb{R}^3$中  /  扭曲$\\leq C$2.',
        correct='在 $\\mathbb{R}^3$ 中  /  扭曲 $\\leq C$ 2.',
        reason='pandoc 在 `$` 紧邻中文或数字时可能转义，导致公式命令落在非数学环境而编译失败。',
    ),
    CheckRule(
        id='cjk_inline',
        title='规则 2：$...$ 内不得有裸中文',
        description='行内公式中如需中文，须用 `\\text{...}` 包裹；更推荐把中文移到公式外。',
        wrong='$x为未知数$  /  $|V|个顶点$',
        correct='$x$ 为未知数  /  $|V|$ 个顶点  /  $\\text{为网格}$',
        reason='数学字体不含 CJK 字形，裸中文在数学环境中无法正确渲染或编译。',
    ),
    CheckRule(
        id='cases_inline',
        title='规则 3：\\begin{cases} 不得在行内 $...$ 中',
        description='含 `\\begin{cases}` 或复杂环境的公式应改为独立 `$$...$$` 块。',
        wrong='$A = \\begin{cases}...\\end{cases}$',
        correct='$$A = \\begin{cases}...\\end{cases}$$',
        reason='pandoc 的 tex_math_dollars 无法正确解析行内数学中的 cases 环境。',
    ),
    CheckRule(
        id='display_blank',
        title='规则 4：$$...$$ 块内不得有空行',
        description='`$$` 与 `$$` 之间必须是连续 LaTeX 块，中间不能插入空行。',
        wrong='$$\\nx=1\\n\\ny=2\\n$$',
        correct='$$\\nx=1\\ny=2\\n$$',
        reason='空行会被 pandoc 当作段落分隔，提前结束数学块解析。',
    ),
    CheckRule(
        id='sub_cmd',
        title='规则 5：\\sub 不是标准命令',
        description='应使用 `\\subset`（真子集）或 `\\subseteq`（子集）。',
        wrong='U_i \\sub M',
        correct='U_i \\subset M',
        reason='`\\sub` 非 LaTeX 标准命令，xelatex 会报错。',
    ),
    CheckRule(
        id='double_wrap',
        title='规则 6：不要 \\(\\) 与 $ 双重包裹',
        description='行内数学只选一种写法：`$...$` 或 `\\(...\\)`，不要嵌套。',
        wrong='\\($x$\\)',
        correct='$x$  或  \\(x\\)',
        reason='双重包裹会导致 pandoc 解析混乱。',
    ),
    CheckRule(
        id='dollar_pair',
        title='规则 7：$$ 必须成对',
        description='文件中 `$$` 单独成行时须成对出现，不能遗留未闭合块。',
        wrong='$$ x=1 （无闭合）',
        correct='$$ x=1 $$',
        reason='未配对的 `$$` 会使后续全部公式识别错位。',
    ),
)

_RULE_BY_ID = {r.id: r for r in CHECK_RULES}


@dataclass
class CheckIssue:
    rule_id: str
    line: int | None
    detail: str
    line_text: str = ''

    @property
    def rule(self) -> CheckRule:
        return _RULE_BY_ID[self.rule_id]

    def _location(self, file_path: str = '') -> str:
        loc = f'第 {self.line} 行' if self.line else '文件末尾'
        if file_path:
            return f'{file_path} · {loc}'
        return loc

    def format_short(self) -> str:
        loc = f'L{self.line}' if self.line else 'EOF'
        return f'{loc} | {self.rule.title} | {self.detail}'

    def snippet_text(self, max_len: int = 120) -> str:
        if not self.line_text:
            return ''
        text = self.line_text
        if len(text) > max_len:
            return text[: max_len - 3] + '...'
        return text

    def format_log_lines(self, file_path: str = '') -> list[str]:
        """结构化日志行：位置、违反规则、问题、行内容、规则说明。"""
        lines = [
            f'位置: {self._location(file_path)}',
            f'违反: {self.rule.title}',
            f'问题: {self.detail}',
        ]
        if self.line_text:
            snippet = self.line_text
            if len(snippet) > 120:
                snippet = snippet[:117] + '...'
            lines.append(f'内容: {snippet}')
        lines.append(f'说明: {self.rule.description}')
        return lines

    def format_log(self, file_path: str = '') -> str:
        return '\n'.join(f'  {line}' for line in self.format_log_lines(file_path))


@dataclass
class FileCheckResult:
    path: str
    issues: list[CheckIssue] = field(default_factory=list)

    def rel_path(self, root: str | Path) -> str:
        try:
            return str(Path(self.path).relative_to(Path(root).resolve()))
        except ValueError:
            return self.path


@dataclass
class MathCheckResult:
    files: list[FileCheckResult] = field(default_factory=list)
    total_files: int = 0

    @property
    def files_with_issues(self) -> int:
        return sum(1 for f in self.files if f.issues)

    @property
    def total_issues(self) -> int:
        return sum(len(f.issues) for f in self.files)

    @property
    def violated_rule_ids(self) -> set[str]:
        ids: set[str] = set()
        for fr in self.files:
            for issue in fr.issues:
                ids.add(issue.rule_id)
        return ids


def get_check_rules() -> tuple[CheckRule, ...]:
    return CHECK_RULES


def format_rules_markdown() -> str:
    """生成公式检查规范的 Markdown 文本。"""
    lines = [
        '# 公式检查规范',
        '',
        '以下规则用于自动扫描 `.md` 文件中的公式写法，避免 pandoc / xelatex 编译失败。',
        '',
    ]
    for rule in CHECK_RULES:
        lines.extend([
            f'## {rule.title}',
            '',
            rule.description,
            '',
            f'- **错误示例**：`{rule.wrong}`',
            f'- **正确示例**：`{rule.correct}`',
            f'- **原因**：{rule.reason}',
            '',
        ])
    return '\n'.join(lines)


def check_file(filepath: str | Path) -> list[CheckIssue]:
    text = Path(filepath).read_text('utf-8')
    issues: list[CheckIssue] = []
    lines = text.split('\n')

    def _line_text(line_num: int | None) -> str:
        if line_num and 1 <= line_num <= len(lines):
            return lines[line_num - 1].strip()
        return ''

    def _issue(rule_id: str, line_num: int | None, detail: str) -> CheckIssue:
        return CheckIssue(rule_id, line_num, detail, _line_text(line_num))

    for m in re.finditer(r'[\u4e00-\u9fff]\$[^\$]|\$[^\$][\u4e00-\u9fff]', text):
        ln = text[: m.start()].count('\n') + 1
        issues.append(_issue('space', ln, '$ 前后缺少空格'))

    for m in re.finditer(r'(?<!\$)\$(?!\$)((?:(?!\$).)+?)\$(?!\$)', text):
        body = m.group(1)
        body_no_text = re.sub(r'\\text\{[^}]*\}', '', body)
        if re.search(r'[\u4e00-\u9fff]', body_no_text):
            ln = text[: m.start()].count('\n') + 1
            issues.append(_issue('cjk_inline', ln, '行内公式含裸中文，应移出 $...$ 或用 \\text{} 包裹'))

    for m in re.finditer(r'(?<!\$)\$(?!\$)(.+?)\\begin\{cases\}(.+?)\$(?!\$)', text, re.DOTALL):
        ln = text[: m.start()].count('\n') + 1
        issues.append(_issue('cases_inline', ln, '\\begin{cases} 不得放在行内 $...$ 中，应改为 $$...$$'))

    for m in re.finditer(r'\$\$(.+?)\$\$', text, re.DOTALL):
        if '\n\n' in m.group(1):
            ln = text[: m.start()].count('\n') + 1
            issues.append(_issue('display_blank', ln, '$$ 块内存在空行'))

    for m in re.finditer(r'\\sub(?![a-zA-Z])', text):
        ln = text[: m.start()].count('\n') + 1
        issues.append(_issue('sub_cmd', ln, '\\sub 应改为 \\subset 或 \\subseteq'))

    for m in re.finditer(r'\\\(\$[^$]*\$\\\)', text):
        ln = text[: m.start()].count('\n') + 1
        issues.append(_issue('double_wrap', ln, '\\(\\) 与 $ 双重包裹'))

    in_block = False
    for line in lines:
        if line.strip() == '$$':
            in_block = not in_block
    if in_block:
        issues.append(_issue('dollar_pair', None, '$$ 未配对（文件末尾仍有未闭合块）'))

    return issues


def check_directory(root: str | Path, *, recursive: bool = True) -> MathCheckResult:
    root = Path(root)
    pattern = '**/*.md' if recursive else '*.md'
    files = sorted(root.glob(pattern))
    result = MathCheckResult(total_files=len(files))
    for fp in files:
        issues = check_file(fp)
        if issues:
            result.files.append(FileCheckResult(path=str(fp), issues=issues))
    return result


def check_paths(paths: list[str | Path]) -> MathCheckResult:
    """递归检查多个章节目录下的 .md 文件。"""
    md_files: list[Path] = []
    for raw in paths:
        root = Path(raw)
        if root.is_dir():
            md_files.extend(root.rglob('*.md'))
    unique = sorted({fp.resolve() for fp in md_files})
    result = MathCheckResult(total_files=len(unique))
    for fp in unique:
        issues = check_file(fp)
        if issues:
            result.files.append(FileCheckResult(path=str(fp), issues=issues))
    return result
