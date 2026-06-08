#!/usr/bin/env python3
"""文档整理工具 — PDF 打包、图床上传、公式检查。"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from packpdf.config import AppConfig, default_project_root, load_config, save_config
from packpdf.core import merge_chapters_to_pdf, merge_to_pdf
from packpdf.deps import check_deps, format_deps_report
from packpdf.math_check import check_directory
from packpdf.oss import scan_summary, upload_and_replace
from packpdf.paths import (
    document_title_for_chapters,
    list_markdown_subdirs,
    output_pdf_for_chapters,
    pdf_output_dir,
    subdir_path,
)
from packpdf.ui.chapter_list import ChapterCheckList
from packpdf.ui.rules_dialog import show_check_report, show_check_rules
from packpdf.ui.log_panel import LogLevel, LogPanel

PAD = {'padx': 8, 'pady': 4}


class DocToolsApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('文档整理工具 — PDF / 图床 / 公式')
        self.minsize(760, 600)
        self.cfg = load_config()
        if self.cfg.window_geometry:
            self.geometry(self.cfg.window_geometry)

        self._busy = False
        self._build_ui()
        self._ensure_project_root()
        self._load_fields()
        self._refresh_subdirs()
        self._refresh_deps(quiet=True)
        self.protocol('WM_DELETE_WINDOW', self._on_close)

    # ── UI ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=8)
        root.pack(fill=tk.BOTH, expand=True)

        proj = ttk.LabelFrame(root, text='项目根目录', padding=6)
        proj.pack(fill=tk.X, pady=(0, 6))
        self.var_project = tk.StringVar()
        self.ent_project = ttk.Entry(proj, textvariable=self.var_project, state='readonly')
        self.ent_project.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.var_change_root = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            proj,
            text='修改根目录',
            variable=self.var_change_root,
            command=self._on_change_root_toggle,
        ).pack(side=tk.LEFT)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._build_pdf_tab()
        self._build_oss_tab()
        self._build_math_tab()

        log_frame = ttk.LabelFrame(root, text='运行日志', padding=4)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        self.log = LogPanel(log_frame, height=12)
        self.log.pack(fill=tk.BOTH, expand=True)

    def _build_pdf_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text='PDF 打包')

        ttk.Label(tab, text='选择章节').grid(row=0, column=0, sticky='nw', **PAD)
        chapter_frame = ttk.Frame(tab)
        chapter_frame.grid(row=0, column=1, columnspan=2, sticky='nsew', **PAD)
        self.chapter_list = ChapterCheckList(chapter_frame, on_change=self._on_chapters_changed, height=72)
        self.chapter_list.pack(fill=tk.BOTH, expand=True)
        ttk.Button(tab, text='刷新列表', command=self._refresh_subdirs).grid(row=0, column=3, sticky='n', **PAD)

        ttk.Label(tab, text='文档标题').grid(row=1, column=0, sticky='w', **PAD)
        self.var_title = tk.StringVar()
        self.ent_title = ttk.Entry(tab, textvariable=self.var_title, state='readonly')
        self.ent_title.grid(row=1, column=1, columnspan=3, sticky='ew', **PAD)

        ttk.Label(tab, text='输出 PDF').grid(row=2, column=0, sticky='w', **PAD)
        self.var_output = tk.StringVar()
        self.ent_output = ttk.Entry(tab, textvariable=self.var_output, state='readonly')
        self.ent_output.grid(row=2, column=1, columnspan=3, sticky='ew', **PAD)

        self.var_single = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab,
            text='单章模式（章内文章不加「第 N 章」前缀；多章时各章以目录名分节）',
            variable=self.var_single,
        ).grid(row=3, column=0, columnspan=4, sticky='w', **PAD)

        row = ttk.Frame(tab)
        row.grid(row=4, column=0, columnspan=4, sticky='w', **PAD)
        self.btn_pdf = ttk.Button(row, text='生成 PDF', command=self._start_pdf)
        self.btn_pdf.pack(side=tk.LEFT)
        ttk.Button(row, text='检测 pandoc/xelatex', command=self._refresh_deps).pack(side=tk.LEFT, padx=6)
        ttk.Button(row, text='打开 PDF_output', command=self._open_pdf_output_dir).pack(side=tk.LEFT)
        ttk.Button(row, text='打开输出 PDF', command=self._open_output).pack(side=tk.LEFT, padx=6)

        ttk.Label(
            tab,
            text='勾选要打包的章节；多章合并为一个 PDF，输出至根目录/PDF_output/',
            foreground='#666',
        ).grid(row=5, column=0, columnspan=4, sticky='w', **PAD)

        self.lbl_deps = ttk.Label(tab, text='', foreground='#555')
        self.lbl_deps.grid(row=6, column=0, columnspan=4, sticky='w', **PAD)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)

    def _build_oss_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text='图床上传')

        ttk.Label(tab, text='说明：扫描 _posts/ 中引用 imgs/ 的本地图片，上传阿里云 OSS 并替换路径。').grid(
            row=0, column=0, columnspan=3, sticky='w', **PAD
        )

        ttk.Label(tab, text='AccessKey ID').grid(row=1, column=0, sticky='w', **PAD)
        self.var_ak = tk.StringVar(value=os.environ.get('OSS_ACCESS_KEY_ID', ''))
        ttk.Entry(tab, textvariable=self.var_ak, show='').grid(row=1, column=1, sticky='ew', **PAD)

        ttk.Label(tab, text='AccessKey Secret').grid(row=2, column=0, sticky='w', **PAD)
        self.var_sk = tk.StringVar(value=os.environ.get('OSS_ACCESS_KEY_SECRET', ''))
        ttk.Entry(tab, textvariable=self.var_sk, show='*').grid(row=2, column=1, sticky='ew', **PAD)

        self.var_remember_oss = tk.BooleanVar(value=False)
        ttk.Checkbutton(tab, text='记住密钥到本地 config.json（勿提交 git）', variable=self.var_remember_oss).grid(
            row=3, column=0, columnspan=3, sticky='w', **PAD
        )

        row = ttk.Frame(tab)
        row.grid(row=4, column=0, columnspan=3, sticky='w', **PAD)
        self.btn_oss_scan = ttk.Button(row, text='扫描预览', command=self._scan_oss)
        self.btn_oss_scan.pack(side=tk.LEFT)
        self.btn_oss_run = ttk.Button(row, text='上传并替换', command=self._start_oss)
        self.btn_oss_run.pack(side=tk.LEFT, padx=6)
        tab.columnconfigure(1, weight=1)

    def _build_math_tab(self) -> None:
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text='公式检查')

        ttk.Label(tab, text='检查目录').grid(row=0, column=0, sticky='w', **PAD)
        self.var_check_dir = tk.StringVar()
        ttk.Entry(tab, textvariable=self.var_check_dir).grid(row=0, column=1, sticky='ew', **PAD)
        ttk.Button(tab, text='浏览…', command=self._pick_check_dir).grid(row=0, column=2, **PAD)

        self.var_recursive = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text='递归子目录', variable=self.var_recursive).grid(
            row=1, column=0, columnspan=3, sticky='w', **PAD
        )

        row = ttk.Frame(tab)
        row.grid(row=2, column=0, columnspan=3, sticky='w', **PAD)
        self.btn_math = ttk.Button(row, text='开始检查', command=self._start_math_check)
        self.btn_math.pack(side=tk.LEFT)
        ttk.Button(row, text='查看检查依据', command=self._show_math_rules).pack(side=tk.LEFT, padx=6)
        tab.columnconfigure(1, weight=1)

    # ── 配置与路径 ────────────────────────────────────────

    def _ensure_project_root(self) -> None:
        root = self.cfg.project_root.strip()
        if root and os.path.isdir(root):
            return
        path = filedialog.askdirectory(
            title='首次使用：请选择项目根目录',
            initialdir=root or default_project_root(),
        )
        if path:
            self.cfg.project_root = path
            save_config(self.cfg)
        else:
            fallback = default_project_root()
            if os.path.isdir(fallback):
                self.cfg.project_root = fallback

    def _load_fields(self) -> None:
        self.var_project.set(self.cfg.project_root or default_project_root())
        self.var_single.set(self.cfg.single_chapter)
        self.var_check_dir.set(self.cfg.check_dir or os.path.join(self.var_project.get(), '_posts'))
        if self.cfg.oss_access_key_id:
            self.var_ak.set(self.cfg.oss_access_key_id)
        if self.cfg.oss_access_key_secret:
            self.var_sk.set(self.cfg.oss_access_key_secret)
        self.var_remember_oss.set(self.cfg.remember_oss_keys)

    def _save_fields(self) -> None:
        self.cfg.project_root = self.var_project.get().strip()
        selected = self.chapter_list.get_selected()
        if selected:
            self.cfg.selected_chapters = selected
            self.cfg.last_markdown_subdir = selected[0]
        self.cfg.single_chapter = self.var_single.get()
        self.cfg.check_dir = self.var_check_dir.get().strip()
        self.cfg.remember_oss_keys = self.var_remember_oss.get()
        if self.cfg.remember_oss_keys:
            self.cfg.oss_access_key_id = self.var_ak.get().strip()
            self.cfg.oss_access_key_secret = self.var_sk.get().strip()
        self.cfg.window_geometry = self.geometry()
        save_config(self.cfg)

    def _project_path(self) -> Path:
        p = self.var_project.get().strip() or default_project_root()
        return Path(p).resolve()

    def _refresh_subdirs(self) -> None:
        root = self._project_path()
        names = list_markdown_subdirs(root)

        if not names:
            self.chapter_list.set_chapters([], set())
            self.var_title.set('')
            self.var_output.set('')
            self.log.warn(f'根目录下未找到含 .md 的一层子目录: {root}')
            return

        saved = set(self.cfg.selected_chapters) & set(names)
        if not saved and self.cfg.last_markdown_subdir in names:
            saved = {self.cfg.last_markdown_subdir}
        if not saved:
            saved = set(names)
        self.chapter_list.set_chapters(names, saved)
        self._on_chapters_changed()

    def _on_chapters_changed(self) -> None:
        selected = self.chapter_list.get_selected()
        root = self._project_path()
        if not selected:
            self.var_title.set('')
            self.var_output.set('')
            return
        self.var_title.set(document_title_for_chapters(root, selected))
        out = output_pdf_for_chapters(root, selected)
        pdf_output_dir(root)
        self.var_output.set(str(out))
        if len(selected) == 1:
            self.var_check_dir.set(str(subdir_path(root, selected[0])))

    def _on_change_root_toggle(self) -> None:
        if not self.var_change_root.get():
            return
        initial = self.var_project.get() or default_project_root()
        path = filedialog.askdirectory(title='选择新的项目根目录', initialdir=initial)
        self.var_change_root.set(False)
        if not path:
            return
        self.var_project.set(path)
        self.cfg.project_root = path
        save_config(self.cfg)
        self.log.info(f'根目录已更新: {path}')
        self._refresh_subdirs()

    # ── 日志桥接 ────────────────────────────────────────

    def _log_cb(self, msg: str, level: str = 'info') -> None:
        lvl = LogLevel.INFO
        if level == 'error':
            lvl = LogLevel.ERROR
        elif level == 'warn':
            lvl = LogLevel.WARN
        self.after(0, lambda: self.log.append(msg, lvl))

    def _core_log(self, msg: str) -> None:
        self._log_cb(msg, 'info')

    # ── 文件选择 ────────────────────────────────────────

    def _pick_check_dir(self) -> None:
        path = filedialog.askdirectory(
            title='选择要检查的目录',
            initialdir=self.var_check_dir.get() or self.var_project.get(),
        )
        if path:
            self.var_check_dir.set(path)

    # ── 任务控制 ────────────────────────────────────────

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = tk.DISABLED if busy else tk.NORMAL
        for btn in (self.btn_pdf, self.btn_oss_scan, self.btn_oss_run, self.btn_math):
            btn.configure(state=state)

    def _run_async(self, worker, on_done) -> None:
        if self._busy:
            return
        self._save_fields()
        self._set_busy(True)

        def wrap() -> None:
            try:
                worker()
            finally:
                self.after(0, on_done)

        threading.Thread(target=wrap, daemon=True).start()

    # ── PDF ─────────────────────────────────────────────

    def _refresh_deps(self, quiet: bool = False) -> None:
        status = check_deps(self.cfg.extra_path or None)
        report = format_deps_report(status)
        ok = all(s.found for s in status.values())
        self.lbl_deps.configure(text=report.replace('\n', '  |  '), foreground='#080' if ok else '#a00')
        if not quiet:
            for line in report.splitlines():
                lvl = 'error' if '[缺失]' in line else 'info'
                self._log_cb(line, lvl)

    def _start_pdf(self) -> None:
        selected = self.chapter_list.get_selected()
        if not selected:
            messagebox.showwarning('提示', '请至少勾选一个章节')
            return

        root = self._project_path()
        chapters = [(str(subdir_path(root, name)), name) for name in selected]
        title = document_title_for_chapters(root, selected)
        output = str(output_pdf_for_chapters(root, selected))

        self.log.info('—— 开始生成 PDF ——')
        self.log.info(f'已选 {len(selected)} 章: {", ".join(selected)}')
        self.log.info(f'输出: {output}')
        result_holder: dict = {}

        def worker() -> None:
            result_holder['r'] = merge_chapters_to_pdf(
                chapters,
                output,
                title,
                single_chapter=self.var_single.get(),
                extra_path=self.cfg.extra_path or None,
                on_log=self._core_log,
            )

        def done() -> None:
            self._set_busy(False)
            r = result_holder.get('r')
            if r and r.success:
                self.var_output.set(r.output_pdf)
                self.log.info(f'PDF 已生成: {r.output_pdf} ({r.pages} 页, {r.size_kb:.1f} KB)')
                messagebox.showinfo('完成', f'已生成 PDF\n\n{r.output_pdf}\n{r.pages} 页')
            else:
                err = (r.error if r else '') or '未知错误'
                self.log.error(err)
                messagebox.showerror('失败', err)

        self._run_async(worker, done)

    # ── OSS ─────────────────────────────────────────────

    def _scan_oss(self) -> None:
        self.log.info('—— 扫描本地图片引用 ——')

        def worker() -> None:
            summary = scan_summary(self._project_path())
            self._log_cb(f'唯一图片: {summary["unique"]} 张，引用: {summary["refs"]} 处', 'info')
            if summary['missing']:
                self._log_cb(f'本地缺失 {len(summary["missing"])} 张:', 'warn')
                for fn in summary['missing'][:30]:
                    self._log_cb(f'  - {fn}', 'warn')
                if len(summary['missing']) > 30:
                    self._log_cb(f'  ... 还有 {len(summary["missing"]) - 30} 张', 'warn')
            upload_and_replace(
                self._project_path(),
                access_key_id=self.var_ak.get().strip(),
                access_key_secret=self.var_sk.get().strip(),
                dry_run=True,
                on_log=self._log_cb,
            )

        self._run_async(worker, lambda: self._set_busy(False))

    def _start_oss(self) -> None:
        if not self.var_ak.get().strip() or not self.var_sk.get().strip():
            messagebox.showwarning('提示', '请填写 OSS AccessKey')
            return
        if not messagebox.askyesno('确认', '将上传图片到 OSS 并修改 _posts/ 下的 .md 文件，是否继续？'):
            return

        self.log.info('—— 开始上传并替换 ——')
        result_holder: dict = {}

        def worker() -> None:
            result_holder['r'] = upload_and_replace(
                self._project_path(),
                access_key_id=self.var_ak.get().strip(),
                access_key_secret=self.var_sk.get().strip(),
                dry_run=False,
                on_log=self._log_cb,
            )

        def done() -> None:
            self._set_busy(False)
            r = result_holder.get('r')
            if r and r.success:
                messagebox.showinfo('完成', f'上传 {r.uploaded} 张，替换 {r.replaced} 处')
            elif r and r.error:
                self.log.error(r.error)
                messagebox.showerror('失败', r.error)
            elif r and r.failed:
                messagebox.showwarning('部分失败', f'{len(r.failed)} 张上传失败，详见日志')

        self._run_async(worker, done)

    # ── 公式检查 ────────────────────────────────────────

    def _show_math_rules(self) -> None:
        show_check_rules(self)

    def _start_math_check(self) -> None:
        root = self.var_check_dir.get().strip()
        if not root or not os.path.isdir(root):
            messagebox.showwarning('提示', '请选择有效的检查目录')
            return

        self.log.info(f'—— 检查公式规范: {root} ——')
        result_holder: dict = {}

        def worker() -> None:
            result_holder['r'] = check_directory(root, recursive=self.var_recursive.get())

        def done() -> None:
            self._set_busy(False)
            r = result_holder.get('r')
            if not r:
                return
            if r.files_with_issues == 0:
                self.log.info(f'全部通过 ({r.total_files} 个文件)')
            else:
                self.log.warn(f'{r.files_with_issues}/{r.total_files} 个文件有问题，共 {r.total_issues} 处')
                for fr in r.files:
                    self.log.warn(f'{fr.path} ({len(fr.issues)} 处)')
                    for issue in fr.issues:
                        self.log.warn(f'  {issue.format_log()}')
            show_check_report(self, r)

        self._run_async(worker, done)

    # ── 杂项 ────────────────────────────────────────────

    def _open_pdf_output_dir(self) -> None:
        path = pdf_output_dir(self._project_path())
        self._open_path(str(path))

    def _open_output(self) -> None:
        path = self.var_output.get().strip()
        if path and os.path.exists(path):
            self._open_path(path)
        else:
            messagebox.showinfo('提示', '输出文件尚不存在')

    @staticmethod
    def _open_path(path: str) -> None:
        if sys.platform == 'win32':
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == 'darwin':
            subprocess.run(['open', path], check=False)
        else:
            subprocess.run(['xdg-open', path], check=False)

    def _on_close(self) -> None:
        self._save_fields()
        self.destroy()


def main() -> None:
    app = DocToolsApp()
    app.mainloop()


if __name__ == '__main__':
    main()
