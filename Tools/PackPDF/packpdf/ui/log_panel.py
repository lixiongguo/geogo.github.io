"""彩色日志面板：INFO（白）、WARN（黄）、ERROR（红）。"""

from __future__ import annotations

import enum
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class LogLevel(enum.Enum):
    INFO = 'info'
    WARN = 'warn'
    ERROR = 'error'


_LOG_FONT_SIZE = 18

_COLORS = {
    LogLevel.INFO:  '#ffffff',
    LogLevel.WARN:  '#ffeb3b',
    LogLevel.ERROR: '#ff5252',
}


class LogPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        log_font = QFont('Consolas', _LOG_FONT_SIZE)
        log_font.setStyleHint(QFont.Monospace)
        log_font.setBold(True)
        self._log.setFont(log_font)
        self._log.setStyleSheet(
            'QPlainTextEdit {'
            '  background-color: #1a1a1a;'
            '  color: #ffffff;'
            f'  font-family: Consolas, "Courier New", "DejaVu Sans Mono", Menlo, monospace;'
            f'  font-size: {_LOG_FONT_SIZE}px;'
            '  font-weight: bold;'
            '  border: none;'
            '}'
        )
        self._log.document().setMaximumBlockCount(2000)
        self._log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 4)
        toolbar.addStretch()
        btn = QPushButton('清空')
        btn.setFixedWidth(60)
        btn.clicked.connect(self.clear)
        toolbar.addWidget(btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(toolbar)
        layout.addWidget(self._log, 1)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def clear(self) -> None:
        self._log.clear()

    def append(self, msg: str, level: LogLevel = LogLevel.INFO) -> None:
        color = _COLORS.get(level, _COLORS[LogLevel.INFO])
        escaped = msg.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        html = (
            f'<span style="color:{color}; font-size:{_LOG_FONT_SIZE}px; '
            f'font-weight:bold; line-height:1.45;">{escaped}</span><br>'
        )
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
        upper = msg.upper()
        if upper.startswith(('ERROR', '[ERROR]', 'FAIL', '[FAIL]', '失败', '[缺失]')):
            self.error(msg)
        elif upper.startswith(('WARN', '[WARN]', 'WARNING', 'SKIP_MISS', '⚠', '[警告]')):
            self.warn(msg)
        else:
            self.info(msg)
