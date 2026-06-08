"""章节目录复选框列表（横向流式排列，宽度不足自动换行）。"""

from __future__ import annotations

from typing import Callable

from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
    QLayout,
    QLayoutItem,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QWidgetItem,
)


class FlowLayout(QLayout):
    """横向排列子控件，空间不足时自动换行。"""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        h_spacing: int = 10,
        v_spacing: int = 4,
        margin: int = 2,
    ) -> None:
        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item: QLayoutItem) -> None:
        self._items.append(item)

    def addWidget(self, widget: QWidget) -> None:
        self.addItem(QWidgetItem(widget))

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int) -> QLayoutItem | None:
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int) -> QLayoutItem | None:
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self) -> Qt.Orientations:
        return Qt.Orientations()

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize(0, 0)
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect: QRect, *, test_only: bool) -> int:
        margins = self.contentsMargins()
        effective = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())

        x = effective.x()
        y = effective.y()
        line_height = 0

        for item in self._items:
            hint = item.sizeHint()
            next_x = x + hint.width() + self._h_spacing
            if next_x - self._h_spacing > effective.right() and line_height > 0:
                x = effective.x()
                y += line_height + self._v_spacing
                next_x = x + hint.width() + self._h_spacing
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))

            x = next_x
            line_height = max(line_height, hint.height())

        return y + line_height - rect.y() + margins.bottom()


class ChapterList(QWidget):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        on_change: Callable[[], None] | None = None,
        max_height: int = 56,
    ) -> None:
        super().__init__(parent)
        self._on_change = on_change
        self._order: list[str] = []
        self._checkboxes: dict[str, QCheckBox] = {}

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setMaximumHeight(max_height)
        self._scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._flow_host = QWidget()
        self._flow_layout = FlowLayout(self._flow_host, h_spacing=12, v_spacing=4, margin=2)
        self._scroll.setWidget(self._flow_host)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._scroll)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMaximumHeight(max_height)

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()

    def _clear_flow(self) -> None:
        while self._flow_layout.count():
            item = self._flow_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._checkboxes.clear()

    def set_chapters(self, names: list[str], selected: set[str] | None = None) -> None:
        self._clear_flow()
        self._order = list(names)
        sel = selected or set(names)

        for name in names:
            cb = QCheckBox(name, self._flow_host)
            cb.setChecked(name in sel)
            cb.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
            cb.stateChanged.connect(lambda _state, _n=name: self._notify())
            self._checkboxes[name] = cb
            self._flow_layout.addWidget(cb)

        self._flow_host.adjustSize()
        self._flow_host.updateGeometry()

    def get_selected(self) -> list[str]:
        return [n for n in self._order if self._checkboxes.get(n) and self._checkboxes[n].isChecked()]

    def selected_set(self) -> set[str]:
        return set(self.get_selected())
