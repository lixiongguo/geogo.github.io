"""章节目录复选框列表（横向排列，自动换行）。"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable


class ChapterCheckList(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        *,
        on_change: Callable[[], None] | None = None,
        height: int = 72,
    ) -> None:
        super().__init__(master)
        self._on_change = on_change
        self._order: list[str] = []
        self._vars: dict[str, tk.BooleanVar] = {}
        self._buttons: list[ttk.Checkbutton] = []
        self._padx = 10
        self._pady = 4

        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(toolbar, text='全选', command=self.select_all, width=8).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(toolbar, text='全不选', command=self.select_none, width=8).pack(side=tk.LEFT)

        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(container, height=height, highlightthickness=0)
        scroll = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self._canvas.yview)
        self._inner = ttk.Frame(self._canvas)
        self._inner.bind('<Configure>', self._on_inner_configure)
        self._canvas_window = self._canvas.create_window((0, 0), window=self._inner, anchor='nw')
        self._canvas.configure(yscrollcommand=scroll.set)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.bind('<Configure>', self._on_canvas_configure)

        def _wheel(event: tk.Event) -> None:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

        self._canvas.bind('<Enter>', lambda e: self._canvas.bind_all('<MouseWheel>', _wheel))
        self._canvas.bind('<Leave>', lambda e: self._canvas.unbind_all('<MouseWheel>'))

    def _on_inner_configure(self, _event: tk.Event | None = None) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self._canvas.itemconfigure(self._canvas_window, width=event.width)
        self._reflow(event.width)

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()

    def _reflow(self, width: int | None = None) -> None:
        if not self._buttons:
            return
        if width is None:
            width = self._canvas.winfo_width()
        if width <= 1:
            width = 640

        for btn in self._buttons:
            btn.grid_forget()

        col = row = 0
        x_used = 0
        for btn in self._buttons:
            btn.update_idletasks()
            w = btn.winfo_reqwidth() + self._padx
            if x_used + w > width and col > 0:
                row += 1
                col = 0
                x_used = 0
            btn.grid(row=row, column=col, sticky='w', padx=(0, self._padx), pady=(0, self._pady))
            x_used += w
            col += 1

        self._inner.update_idletasks()
        self._on_inner_configure()

    def set_chapters(self, names: list[str], selected: set[str] | None = None) -> None:
        for w in self._inner.winfo_children():
            w.destroy()
        self._vars.clear()
        self._buttons.clear()
        self._order = list(names)
        sel = selected or set(names)

        for name in names:
            var = tk.BooleanVar(value=name in sel)
            var.trace_add('write', lambda *_a: self._notify())
            self._vars[name] = var
            btn = ttk.Checkbutton(self._inner, text=name, variable=var)
            self._buttons.append(btn)

        self.after_idle(lambda: self._reflow())

    def get_selected(self) -> list[str]:
        return [n for n in self._order if self._vars.get(n) and self._vars[n].get()]

    def select_all(self) -> None:
        for var in self._vars.values():
            var.set(True)

    def select_none(self) -> None:
        for var in self._vars.values():
            var.set(False)

    def selected_set(self) -> set[str]:
        return set(self.get_selected())
