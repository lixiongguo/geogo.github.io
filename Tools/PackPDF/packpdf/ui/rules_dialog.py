"""公式检查依据与结果弹窗。"""

from __future__ import annotations

import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import TYPE_CHECKING

from packpdf.math_check import CHECK_RULES, CheckRule, MathCheckResult

if TYPE_CHECKING:
    pass


class MathCheckReportDialog(tk.Toplevel):
    """展示检查依据（规则）与可选的检查结果。"""

    def __init__(
        self,
        master: tk.Misc,
        *,
        result: MathCheckResult | None = None,
        title: str = '公式检查依据',
    ) -> None:
        super().__init__(master)
        self.title(title)
        self.geometry('720x560')
        self.minsize(560, 420)
        self.transient(master)
        self.grab_set()

        violated = result.violated_rule_ids if result else set()

        header = ttk.Frame(self, padding=10)
        header.pack(fill=tk.X)
        ttk.Label(
            header,
            text='检查依据（Markdown 公式编辑规范）',
            font=('', 11, 'bold'),
        ).pack(anchor='w')
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
        ttk.Label(header, text=sub, foreground='#555').pack(anchor='w', pady=(4, 0))

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 6))

        rules_tab = ttk.Frame(notebook, padding=4)
        notebook.add(rules_tab, text='检查依据')
        self._fill_rules(rules_tab, violated)

        if result and result.files:
            result_tab = ttk.Frame(notebook, padding=4)
            notebook.add(result_tab, text='问题明细')
            self._fill_results(result_tab, result)
            notebook.select(result_tab)

        ttk.Button(self, text='关闭', command=self.destroy).pack(pady=(0, 10))

    def _fill_rules(self, parent: ttk.Frame, violated: set[str]) -> None:
        canvas = tk.Canvas(parent, highlightthickness=0)
        scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=inner, anchor='nw')
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event: tk.Event) -> None:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

        canvas.bind_all('<MouseWheel>', _on_mousewheel)
        self.bind('<Destroy>', lambda e: canvas.unbind_all('<MouseWheel>'))

        for rule in CHECK_RULES:
            hit = rule.id in violated
            block = ttk.LabelFrame(
                inner,
                text=rule.title + ('  ← 本次触发' if hit else ''),
                padding=8,
            )
            block.pack(fill=tk.X, pady=6, padx=4)
            if hit:
                style = ttk.Style()
                style.configure('Hit.TLabelframe.Label', foreground='#c17900')
                block.configure(style='Hit.TLabelframe')

            ttk.Label(block, text=rule.description, wraplength=640).pack(anchor='w')
            row = ttk.Frame(block)
            row.pack(fill=tk.X, pady=(6, 0))
            ttk.Label(row, text='错误示例：', foreground='#c62828').grid(row=0, column=0, sticky='nw')
            ttk.Label(row, text=rule.wrong, font=('Consolas', 9), wraplength=560).grid(
                row=0, column=1, sticky='w', padx=(4, 0)
            )
            ttk.Label(row, text='正确示例：', foreground='#2e7d32').grid(row=1, column=0, sticky='nw', pady=(4, 0))
            ttk.Label(row, text=rule.correct, font=('Consolas', 9), wraplength=560).grid(
                row=1, column=1, sticky='w', padx=(4, 0), pady=(4, 0)
            )
            ttk.Label(block, text=f'原因：{rule.reason}', foreground='#666', wraplength=640).pack(
                anchor='w', pady=(6, 0)
            )

    def _fill_results(self, parent: ttk.Frame, result: MathCheckResult) -> None:
        text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            font=('Consolas', 10),
            state=tk.DISABLED,
        )
        text.pack(fill=tk.BOTH, expand=True)
        text.configure(state=tk.NORMAL)
        text.tag_configure('file', foreground='#1565c0', font=('Consolas', 10, 'bold'))
        text.tag_configure('issue', foreground='#c17900')
        text.tag_configure('rule', foreground='#666')

        for fr in result.files:
            text.insert(tk.END, f'{fr.path}\n', 'file')
            for issue in fr.issues:
                text.insert(tk.END, f'  {issue.format_short()}\n', 'issue')
                text.insert(
                    tk.END,
                    f'    → {issue.rule.description}\n',
                    'rule',
                )
            text.insert(tk.END, '\n')
        text.configure(state=tk.DISABLED)


def show_check_rules(master: tk.Misc) -> None:
    MathCheckReportDialog(master, result=None, title='公式检查依据')


def show_check_report(master: tk.Misc, result: MathCheckResult) -> None:
    title = '公式检查结果' if result.files_with_issues else '公式检查通过'
    MathCheckReportDialog(master, result=result, title=title)
