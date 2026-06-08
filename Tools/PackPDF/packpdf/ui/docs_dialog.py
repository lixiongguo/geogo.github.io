"""PackPDF 文档查看器。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from packpdf.math_check import format_rules_markdown

APP_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class DocEntry:
    title: str
    path: Path | None = None
    content: str | None = None

    def load_text(self) -> str:
        if self.content is not None:
            return self.content
        if self.path and self.path.is_file():
            return self.path.read_text(encoding='utf-8')
        return '（文档不存在）'


def discover_docs() -> list[DocEntry]:
    entries: list[DocEntry] = []

    readme = APP_DIR / 'README.md'
    if readme.is_file():
        entries.append(DocEntry('PackPDF 使用说明', path=readme))

    docs_dir = APP_DIR / 'docs'
    if docs_dir.is_dir():
        for path in sorted(docs_dir.glob('*.md')):
            entries.append(DocEntry(path.stem, path=path))

    entries.append(DocEntry('公式检查规范', content=format_rules_markdown()))
    return entries


class DocsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle('查看文档')
        self.resize(860, 620)
        self.setMinimumSize(640, 480)
        self._entries = discover_docs()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter, 1)

        self._list = QListWidget()
        self._list.setMinimumWidth(180)
        self._list.setMaximumWidth(260)
        for entry in self._entries:
            self._list.addItem(QListWidgetItem(entry.title))
        self._list.currentRowChanged.connect(self._on_select)
        splitter.addWidget(self._list)

        self._viewer = QPlainTextEdit()
        self._viewer.setReadOnly(True)
        font = QFont('Consolas', 11)
        font.setStyleHint(QFont.Monospace)
        self._viewer.setFont(font)
        self._viewer.setStyleSheet(
            'QPlainTextEdit {'
            '  background-color: #1a1a1a;'
            '  color: #e8e8e8;'
            '  border: 1px solid #333;'
            '  padding: 8px;'
            '}'
        )
        splitter.addWidget(self._viewer)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        if self._entries:
            self._list.setCurrentRow(0)

    def _on_select(self, row: int) -> None:
        if row < 0 or row >= len(self._entries):
            self._viewer.clear()
            return
        entry = self._entries[row]
        self._viewer.setPlainText(entry.load_text())
        self._viewer.verticalScrollBar().setValue(0)


def show_docs_dialog(parent: QWidget | None = None) -> None:
    dlg = DocsDialog(parent)
    dlg.exec_()
