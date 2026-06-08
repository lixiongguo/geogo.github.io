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

    @property
    def rule(self) -> CheckRule:
        return _RULE_BY_ID[self.rule_id]

    def format_short(self) -> str:
        loc = f'L{self.line}' if self.line else 'EOF'
        return f'[{self.rule.title}] {loc}: {self.detail}'

    def format_log(self) -> str:
        return self.format_short()


@dataclass
class FileCheckResult:
    path: str
    issues: list[CheckIssue] = field(default_factory=list)


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


def check_file(filepath: str | Path) -> list[CheckIssue]:
    text = Path(filepath).read_text('utf-8')
    issues: list[CheckIssue] = []
    lines = text.split('\n')

    for m in re.finditer(r'[\u4e00-\u9fff]\$[^\$]|\$[^\$][\u4e00-\u9fff]', text):
        ln = text[: m.start()].count('\n') + 1
        issues.append(CheckIssue('space', ln, '$ 前后缺少空格'))

    for m in re.finditer(r'(?<!\$)\$(?!\$)((?:(?!\$).)+?)\$(?!\$)', text):
        body = m.group(1)
        body_no_text = re.sub(r'\\text\{[^}]*\}', '', body)
        if re.search(r'[\u4e00-\u9fff]', body_no_text):
            ln = text[: m.start()].count('\n') + 1
            issues.append(CheckIssue('cjk_inline', ln, '行内公式含中文'))

    for m in re.finditer(r'(?<!\$)\$(?!\$)(.+?)\\begin\{cases\}(.+?)\$(?!\$)', text, re.DOTALL):
        ln = text[: m.start()].count('\n') + 1
        issues.append(CheckIssue('cases_inline', ln, '\\begin{cases} 在行内公式中'))

    for m in re.finditer(r'\$\$(.+?)\$\$', text, re.DOTALL):
        if '\n\n' in m.group(1):
            ln = text[: m.start()].count('\n') + 1
            issues.append(CheckIssue('display_blank', ln, '$$ 块内存在空行'))

    for m in re.finditer(r'\\sub(?![a-zA-Z])', text):
        ln = text[: m.start()].count('\n') + 1
        issues.append(CheckIssue('sub_cmd', ln, '\\sub 应改为 \\subset'))

    for m in re.finditer(r'\\\(\$[^$]*\$\\\)', text):
        ln = text[: m.start()].count('\n') + 1
        issues.append(CheckIssue('double_wrap', ln, '\\(\\) 与 $ 双重包裹'))

    in_block = False
    for line in lines:
        if line.strip() == '$$':
            in_block = not in_block
    if in_block:
        issues.append(CheckIssue('dollar_pair', None, '$$ 未配对'))

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
