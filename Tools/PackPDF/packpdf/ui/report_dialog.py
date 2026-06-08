"""公式检查 / 自动修复报告弹窗。"""

from __future__ import annotations

from pathlib import Path

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from packpdf.math_check import AUTO_FIXABLE_RULE_IDS, MathCheckResult
from packpdf.math_fix import MathFixResult
from packpdf.word_count import WordCountResult


def format_check_report(result: MathCheckResult, base: str = '') -> str:
    if result.files_with_issues == 0:
        return '无问题文件。'
    lines: list[str] = []
    for fr in result.files:
        rel = fr.rel_path(base) if base else fr.path
        lines.append(f'{rel}  {len(fr.issues)} 处')
    return '\n'.join(lines)


def format_fix_report(
    result: MathFixResult,
    base: str = '',
    check_before: MathCheckResult | None = None,
) -> str:
    if result.error:
        return result.error
    if result.details:
        base_path = Path(base).resolve() if base else None
        lines: list[str] = []
        for path, changes in result.details:
            p = Path(path)
            if base_path:
                try:
                    rel = str(p.relative_to(base_path))
                except ValueError:
                    rel = path
            else:
                rel = path
            lines.append(f'{rel}  {len(changes)} 处')
        return '\n'.join(lines)

    lines = ['无文件被修复。']
    if check_before and check_before.total_issues:
        fixable = 0
        manual: dict[str, int] = {}
        for fr in check_before.files:
            for issue in fr.issues:
                if issue.rule_id in AUTO_FIXABLE_RULE_IDS:
                    fixable += 1
                else:
                    manual[issue.rule.title] = manual.get(issue.rule.title, 0) + 1
        if manual:
            lines.append('')
            lines.append('以下问题须手动修改：')
            for title, count in sorted(manual.items()):
                lines.append(f'  · {title}（{count} 处）')
        if fixable:
            lines.append('')
            lines.append(
                f'另有 {fixable} 处理论上可自动修复但未改写文件，'
                '请确认文件可写或查看日志详情。'
            )
        elif not manual:
            lines.append('')
            lines.append('未检测到可自动修复的问题类型。')
    return '\n'.join(lines)


class TextReportDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None,
        *,
        title: str,
        summary: str,
        body: str,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(520, 360)
        self.setMinimumSize(360, 200)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        layout.addWidget(QLabel(f'<b>{summary}</b>'))

        text = QPlainTextEdit()
        text.setReadOnly(True)
        font = QFont('Consolas', 11)
        font.setStyleHint(QFont.Monospace)
        text.setFont(font)
        text.setStyleSheet(
            'QPlainTextEdit {'
            '  background-color: #1a1a1a;'
            '  color: #e8e8e8;'
            '  border: 1px solid #333;'
            '  padding: 8px;'
            '}'
        )
        text.setPlainText(body)
        layout.addWidget(text, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(buttons)
        layout.addLayout(row)


def show_check_report(
    parent: QWidget | None,
    result: MathCheckResult,
    base: str = '',
) -> None:
    if result.files_with_issues == 0:
        title = '公式检查通过'
        summary = f'已检查 {result.total_files} 个文件，全部通过。'
    else:
        title = '公式检查报告'
        summary = f'{result.files_with_issues} 个文件有问题，共 {result.total_issues} 处'
    body = format_check_report(result, base)
    dlg = TextReportDialog(parent, title=title, summary=summary, body=body)
    dlg.exec_()


def show_fix_report(
    parent: QWidget | None,
    result: MathFixResult,
    base: str = '',
    check_before: MathCheckResult | None = None,
) -> None:
    if result.error:
        title = '自动修复失败'
        summary = '修复失败'
    elif result.fixed_files == 0:
        title = '自动修复报告'
        summary = f'扫描 {result.scanned} 个文件，无文件被修复'
        if check_before and check_before.total_issues:
            manual = sum(
                1
                for fr in check_before.files
                for issue in fr.issues
                if issue.rule_id not in AUTO_FIXABLE_RULE_IDS
            )
            if manual:
                summary += f'（{manual} 处须手动处理）'
    else:
        total_changes = sum(len(changes) for _, changes in result.details)
        title = '自动修复报告'
        summary = f'已修复 {result.fixed_files} 个文件，共 {total_changes} 处'
    body = format_fix_report(result, base, check_before)
    dlg = TextReportDialog(parent, title=title, summary=summary, body=body)
    dlg.exec_()


def format_word_count_report(result: WordCountResult, base: str = '') -> str:
    if not result.files:
        return '未找到 .md 文件。'
    lines: list[str] = []
    for fr in result.files:
        rel = fr.rel_path(base) if base else fr.path
        lines.append(f'{rel}  总字符 {fr.chars}  中文 {fr.cjk}')
    lines.append('')
    lines.append(
        f'合计  {result.total_files} 个文件  '
        f'总字符 {result.total_chars}  中文 {result.total_cjk}'
    )
    return '\n'.join(lines)


def show_word_count_report(
    parent: QWidget | None,
    result: WordCountResult,
    base: str = '',
) -> None:
    if not result.files:
        title = '字数统计'
        summary = '未找到 .md 文件'
    else:
        title = '字数统计报告'
        summary = (
            f'{result.total_files} 个文件，'
            f'总字符 {result.total_chars}，中文 {result.total_cjk}'
        )
    body = format_word_count_report(result, base)
    dlg = TextReportDialog(parent, title=title, summary=summary, body=body)
    dlg.exec_()
