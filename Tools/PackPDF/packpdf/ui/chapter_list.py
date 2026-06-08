"""章节目录复选框列表（单行横向排列，超出可左右滚动）。"""

from __future__ import annotations

from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QWidget,
)


class ChapterList(QWidget):
    ROW_HEIGHT = 28

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        on_change: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_change = on_change
        self._order: list[str] = []
        self._checkboxes: dict[str, QCheckBox] = {}

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setFixedHeight(self.ROW_HEIGHT)

        self._row_host = QWidget()
        self._row_layout = QHBoxLayout(self._row_host)
        self._row_layout.setContentsMargins(0, 0, 0, 0)
        self._row_layout.setSpacing(12)
        self._row_layout.addStretch()
        self._scroll.setWidget(self._row_host)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._scroll)

        self.setFixedHeight(self.ROW_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()

    def _clear_row(self) -> None:
        while self._row_layout.count() > 1:
            item = self._row_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._checkboxes.clear()

    def set_chapters(self, names: list[str], selected: set[str] | None = None) -> None:
        self._clear_row()
        self._order = list(names)
        sel = selected or set(names)

        for i, name in enumerate(names):
            cb = QCheckBox(name, self._row_host)
            cb.setChecked(name in sel)
            cb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            cb.stateChanged.connect(lambda _state, _n=name: self._notify())
            self._checkboxes[name] = cb
            self._row_layout.insertWidget(i, cb)

    def get_selected(self) -> list[str]:
        return [n for n in self._order if self._checkboxes.get(n) and self._checkboxes[n].isChecked()]

    def selected_set(self) -> set[str]:
        return set(self.get_selected())
