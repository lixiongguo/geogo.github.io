"""彩色日志面板：INFO（白）、WARN（黄）、ERROR（红）。"""

from __future__ import annotations

import enum
from PyQt5.QtWidgets import (
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
)


class LogLevel(enum.Enum):
    INFO = 'info'
    WARN = 'warn'
    ERROR = 'error'


_COLORS = {
    LogLevel.INFO:  '#e0e0e0',
    LogLevel.WARN:  '#ffd54f',
    LogLevel.ERROR: '#ff5252',
}


class LogPanel(QWidget):
    def __init__(self, parent: QWidget | None = None, *, height: int = 14) -> None:
        super().__init__(parent)
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setStyleSheet(
            'QPlainTextEdit {'
            '  background-color: #1e1e1e;'
            '  color: #e0e0e0;'
            '  font-family: Menlo, "Courier New", "DejaVu Sans Mono", Consolas, monospace;'
            '  font-size: 11px;'
            '  border: none;'
            '}'
        )
        self._log.setMinimumHeight(height * 17)
        self._log.document().setMaximumBlockCount(2000)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 4)
        toolbar.addWidget(QLabel('日志'))
        toolbar.addStretch()
        btn = QPushButton('清空')
        btn.setFixedWidth(60)
        btn.clicked.connect(self.clear)
        toolbar.addWidget(btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(toolbar)
        layout.addWidget(self._log)

    def clear(self) -> None:
        self._log.clear()

    def append(self, msg: str, level: LogLevel = LogLevel.INFO) -> None:
        color = _COLORS.get(level, _COLORS[LogLevel.INFO])
        escaped = msg.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        html = f'<span style="color:{color};">{escaped}</span><br>'
        self._log.appendHtml(html)
        self._log.verticalScrollBar().setValue(
            self._log.verticalScrollBar().maximum()
        )

    def info(self, msg: str) -> None:
        self.append(msg, LogLevel.INFO)

    def warn(self, msg: str) -> None:
        self.append(msg, LogLevel.WARN)

    def error(self, msg: str) -> None:
        self.append(msg, LogLevel.ERROR)

    def log_from_prefix(self, msg: str) -> None:
        """根据常见前缀自动着色。"""
        upper = msg.upper()
        if upper.startswith(('ERROR', '[ERROR]', 'FAIL', '[FAIL]', '失败', '[缺失]')):
            self.error(msg)
        elif upper.startswith(('WARN', '[WARN]', 'WARNING', 'SKIP_MISS', '⚠', '[警告]')):
            self.warn(msg)
        else:
            self.info(msg)
