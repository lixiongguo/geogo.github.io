"""公式检查依据与结果弹窗。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from packpdf.math_check import CHECK_RULES, MathCheckResult

if TYPE_CHECKING:
    pass


class MathCheckReportDialog(QDialog):
    """展示检查依据（规则）与可选的检查结果。"""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        result: MathCheckResult | None = None,
        title: str = '公式检查依据',
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(720, 560)
        self.setMinimumSize(560, 420)
        self.setModal(True)

        violated = result.violated_rule_ids if result else set()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header
        header = QLabel(
            '<b style="font-size:13px;">检查依据（Markdown 公式编辑规范）</b>'
        )
        layout.addWidget(header)

        if result is None:
            sub = '以下规则用于自动扫描 .md 文件；完整说明见 docs/Markdown公式编辑规范.md'
        elif result.files_with_issues == 0:
            sub = f'已检查 {result.total_files} 个文件，全部通过。'
        else:
            sub = (
                f'已检查 {result.total_files} 个文件：'
                f'{result.files_with_issues} 个有问题，共 {result.total_issues} 处。'
                f' 下方高亮为本次触发的规则。'
            )
        layout.addWidget(QLabel(sub))

        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Rules tab
        rules_tab = self._build_rules_tab(violated)
        tabs.addTab(rules_tab, '检查依据')

        # Results tab (if available)
        if result and result.files:
            result_tab = self._build_results_tab(result)
            tabs.addTab(result_tab, '问题明细')
            tabs.setCurrentWidget(result_tab)

        # Close button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _build_rules_tab(self, violated: set[str]) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        layout.addStretch()

        for rule in CHECK_RULES:
            hit = rule.id in violated
            title = rule.title + ('  ← 本次触发' if hit else '')
            box = QGroupBox(title)
            box_layout = QVBoxLayout(box)
            box_layout.setSpacing(4)

            box_layout.addWidget(QLabel(rule.description))

            err_label = QLabel(
                f'<span style="color:#c62828;font-weight:bold;">错误示例：</span>'
                f'<code style="font-family:Consolas;font-size:11px;">{rule.wrong}</code>'
            )
            box_layout.addWidget(err_label)

            ok_label = QLabel(
                f'<span style="color:#2e7d32;font-weight:bold;">正确示例：</span>'
                f'<code style="font-family:Consolas;font-size:11px;">{rule.correct}</code>'
            )
            box_layout.addWidget(ok_label)

            box_layout.addWidget(
                QLabel(f'<span style="color:#666;">原因：{rule.reason}</span>')
            )

            if hit:
                box.setStyleSheet(
                    'QGroupBox { border: 1px solid #c17900; padding: 8px; margin-top: 12px; }'
                    'QGroupBox::title { color: #c17900; }'
                )
            else:
                box.setStyleSheet(
                    'QGroupBox { border: 1px solid #444; padding: 8px; margin-top: 12px; }'
                )

            layout.addWidget(box)

        scroll.setWidget(widget)
        return scroll

    def _build_results_tab(self, result: MathCheckResult) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)

        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setStyleSheet(
            'QPlainTextEdit {'
            '  background-color: #1e1e1e;'
            '  color: #e0e0e0;'
            '  font-family: Consolas, monospace;'
            '  font-size: 11px;'
            '}'
        )
        text.setPlainText(self._format_results(result))
        layout.addWidget(text)
        return widget

    @staticmethod
    def _format_results(result: MathCheckResult) -> str:
        lines: list[str] = []
        for fr in result.files:
            lines.append(f'▶ {fr.path}')
            for issue in fr.issues:
                lines.append(f'    ⚠ {issue.format_short()}')
                lines.append(f'      → {issue.rule.description}')
            lines.append('')
        return '\n'.join(lines)


def show_check_rules(parent: QWidget | None = None) -> None:
    dlg = MathCheckReportDialog(parent, result=None, title='公式检查依据')
    dlg.exec_()


def show_check_report(parent: QWidget | None, result: MathCheckResult) -> None:
    title = '公式检查结果' if result.files_with_issues else '公式检查通过'
    dlg = MathCheckReportDialog(parent, result=result, title=title)
    dlg.exec_()
