"""章节目录复选框列表（横向排列，自动换行）。"""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from typing import Callable


class ChapterList(QWidget):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        on_change: Callable[[], None] | None = None,
        height: int = 72,
    ) -> None:
        super().__init__(parent)
        self._on_change = on_change
        self._order: list[str] = []
        self._checkboxes: dict[str, QCheckBox] = {}
        self._flow_items: list[QCheckBox] = []

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 4)
        btn_all = QPushButton('全选')
        btn_all.setFixedWidth(60)
        btn_all.clicked.connect(self.select_all)
        toolbar.addWidget(btn_all)
        btn_none = QPushButton('全不选')
        btn_none.setFixedWidth(60)
        btn_none.clicked.connect(self.select_none)
        toolbar.addWidget(btn_none)
        toolbar.addStretch()

        # Scrollable flow layout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setMinimumHeight(height + 10)

        self._flow_widget = QWidget()
        self._flow_layout = _FlowLayout(self._flow_widget, h_spacing=10, v_spacing=4)
        scroll.setWidget(self._flow_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(toolbar)
        layout.addWidget(scroll)

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()

    def set_chapters(self, names: list[str], selected: set[str] | None = None) -> None:
        # Clear old
        while self._flow_layout.count():
            item = self._flow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._checkboxes.clear()
        self._flow_items.clear()
        self._order = list(names)
        sel = selected or set(names)

        for name in names:
            cb = QCheckBox(name)
            cb.setChecked(name in sel)
            cb.stateChanged.connect(lambda _s, n=name: self._notify())
            self._checkboxes[name] = cb
            self._flow_items.append(cb)
            self._flow_layout.addWidget(cb)

        self._flow_widget.updateGeometry()

    def get_selected(self) -> list[str]:
        return [n for n in self._order if self._checkboxes.get(n) and self._checkboxes[n].isChecked()]

    def select_all(self) -> None:
        for cb in self._checkboxes.values():
            cb.blockSignals(True)
            cb.setChecked(True)
            cb.blockSignals(False)
        self._notify()

    def select_none(self) -> None:
        for cb in self._checkboxes.values():
            cb.blockSignals(True)
            cb.setChecked(False)
            cb.blockSignals(False)
        self._notify()

    def selected_set(self) -> set[str]:
        return set(self.get_selected())


class _FlowLayout(QVBoxLayout):
    """Simple flow layout: places checkboxes in horizontal rows, wrapping as needed."""

    def __init__(self, parent: QWidget, h_spacing: int = 10, v_spacing: int = 4):
        super().__init__(parent)
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self.setContentsMargins(0, 0, 0, 0)
        self._rows: list[QHBoxLayout] = []
        self._current_row: QHBoxLayout | None = None

    def addWidget(self, w: QWidget) -> None:
        if self._current_row is None:
            self._new_row()
        self._current_row.addWidget(w)
        # Add stretcher so items align left
        if self._current_row.count() == 1:
            self._current_row.addStretch()

    def _new_row(self) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(self._h_spacing)
        self.addLayout(row)
        self._rows.append(row)
        self._current_row = row
