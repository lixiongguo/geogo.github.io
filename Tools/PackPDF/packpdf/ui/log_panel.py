"""彩色日志面板：普通信息（白）、警告（黄）、错误（红）。"""

from __future__ import annotations

import enum
import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import Callable


class LogLevel(enum.Enum):
    INFO = 'info'
    WARN = 'warn'
    ERROR = 'error'


class LogPanel(ttk.Frame):
    BG = '#1e1e1e'
    FG = {
        LogLevel.INFO: '#f0f0f0',
        LogLevel.WARN: '#ffd54f',
        LogLevel.ERROR: '#ff5252',
    }

    def __init__(self, master: tk.Misc, *, height: int = 14) -> None:
        super().__init__(master)
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(toolbar, text='日志').pack(side=tk.LEFT)
        ttk.Button(toolbar, text='清空', command=self.clear, width=8).pack(side=tk.RIGHT)

        self.text = scrolledtext.ScrolledText(
            self,
            height=height,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=self.BG,
            fg=self.FG[LogLevel.INFO],
            insertbackground=self.FG[LogLevel.INFO],
            font=('Consolas', 10),
            relief=tk.FLAT,
            borderwidth=0,
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        for level in LogLevel:
            self.text.tag_configure(level.value, foreground=self.FG[level])

    def clear(self) -> None:
        self.text.configure(state=tk.NORMAL)
        self.text.delete('1.0', tk.END)
        self.text.configure(state=tk.DISABLED)

    def append(self, msg: str, level: LogLevel = LogLevel.INFO) -> None:
        line = msg.rstrip('\n') + '\n'
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END, line, level.value)
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)

    def callback(self, level: LogLevel = LogLevel.INFO) -> Callable[[str], None]:
        return lambda msg: self.append(msg, level)

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
