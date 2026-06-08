#!/usr/bin/env python3
"""文档整理工具 — PDF 打包、文档格式检查（PyQt5 UI）。"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PyQt5.QtCore import QThread, QTimer, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from packpdf.config import AppConfig, default_project_root, load_config, save_config
from packpdf.core import MergeResult, merge_chapters_to_pdf
from packpdf.deps import check_deps, format_deps_report, format_deps_summary
from packpdf.math_check import MathCheckResult, check_paths
from packpdf.math_fix import MathFixResult, fix_files
from packpdf.oss import OssScanResult, scan_pack_chapters, upload_and_replace
from packpdf.paths import (
    document_title_for_chapters,
    list_markdown_subdirs,
    output_pdf_for_chapters,
    pdf_output_dir,
    subdir_path,
)
from packpdf.ui.chapter_list import ChapterList
from packpdf.ui.docs_dialog import show_docs_dialog
from packpdf.ui.log_panel import LogLevel, LogPanel
from packpdf.ui.oss_settings_dialog import oss_credentials, show_oss_settings
from packpdf.ui.report_dialog import show_check_report, show_fix_report


# ── Worker Threads ──────────────────────────────────────

class _PdfWorker(QThread):
    log_signal = pyqtSignal(str, str)
    done_signal = pyqtSignal(object)

    def __init__(
        self,
        chapters: list[tuple[str, str]],
        output: str,
        title: str,
        single_chapter: bool,
        extra_path: list[str] | None = None,
    ) -> None:
        super().__init__()
        self._chapters = chapters
        self._output = output
        self._title = title
        self._single = single_chapter
        self._extra_path = extra_path

    def run(self) -> None:
        try:
            result = merge_chapters_to_pdf(
                self._chapters,
                self._output,
                self._title,
                single_chapter=self._single,
                extra_path=self._extra_path,
                on_log=lambda m: self.log_signal.emit(m, 'info'),
            )
        except Exception as exc:
            result = MergeResult(
                success=False,
                output_pdf=self._output,
                error=f'生成失败: {exc}',
            )
        self.done_signal.emit(result)


class _OssScanWorker(QThread):
    done_signal = pyqtSignal(object)

    def __init__(
        self,
        project_root: Path,
        chapter_names: list[str],
        imgs_subdir: str,
    ) -> None:
        super().__init__()
        self._root = project_root
        self._chapters = chapter_names
        self._imgs_subdir = imgs_subdir

    def run(self) -> None:
        result = scan_pack_chapters(
            self._root,
            self._chapters,
            imgs_subdir=self._imgs_subdir,
        )
        self.done_signal.emit(result)


class _OssWorker(QThread):
    log_signal = pyqtSignal(str, str)
    done_signal = pyqtSignal(object)

    def __init__(self, project_path: Path, ak: str, sk: str) -> None:
        super().__init__()
        self._path = project_path
        self._ak = ak
        self._sk = sk

    def run(self) -> None:
        result = upload_and_replace(
            self._path, self._ak, self._sk,
            dry_run=False,
            on_log=lambda m, l: self.log_signal.emit(m, l),
        )
        self.done_signal.emit(result)


class _MathWorker(QThread):
    log_signal = pyqtSignal(str, str)
    done_signal = pyqtSignal(object)

    def __init__(self, paths: list[str]) -> None:
        super().__init__()
        self._paths = paths

    def run(self) -> None:
        self.done_signal.emit(check_paths(self._paths))


class _MathFixWorker(QThread):
    done_signal = pyqtSignal(object)

    def __init__(self, file_paths: list[str]) -> None:
        super().__init__()
        self._paths = file_paths

    def run(self) -> None:
        self.done_signal.emit(fix_files(self._paths))


class _DepsWorker(QThread):
    done_signal = pyqtSignal(object)

    def __init__(self, extra_path: list[str] | None = None) -> None:
        super().__init__()
        self._extra = extra_path

    def run(self) -> None:
        self.done_signal.emit(check_deps(self._extra))


# ── Main Window ────────────────────────────────────────

class DocToolsApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('文档整理工具 — PackPDF')
        self.resize(820, 720)
        self.cfg = load_config()
        if self.cfg.window_geometry:
            try:
                w, h = map(int, self.cfg.window_geometry.lower().replace('x', ' ').split())
                self.resize(w, h)
            except Exception:
                pass

        self._busy = False
        self._worker: QThread | None = None
        self._deps_worker: QThread | None = None
        self._math_fix_available = False
        self._last_math_base = ''
        self._last_math_result: MathCheckResult | None = None

        self._build_toolbar()
        self._build_ui()
        self._ensure_project_root()
        self._load_fields()
        self._refresh_subdirs()
        self._refresh_deps(quiet=True)

    # ── UI ──────────────────────────────────────────────

    def _build_toolbar(self) -> None:
        toolbar = QToolBar('工具栏', self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addAction('查看文档', self._show_docs)
        toolbar.addSeparator()
        toolbar.addAction('检测依赖(pandoc/xelatex)', lambda: self._refresh_deps())
        toolbar.addAction('打开输出目录', self._open_pdf_output_dir)
        toolbar.addAction('图床设置', self._show_oss_settings)

    def _show_docs(self) -> None:
        show_docs_dialog(self)

    def _show_oss_settings(self) -> None:
        show_oss_settings(self, self.cfg)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(6)

        # Project root bar
        self._proj_group = QGroupBox('项目根目录')
        proj_layout = QHBoxLayout(self._proj_group)
        self._ent_project = QLineEdit()
        self._ent_project.setReadOnly(True)
        proj_layout.addWidget(self._ent_project)
        self._cb_change_root = QCheckBox('修改根目录')
        self._cb_change_root.stateChanged.connect(self._on_change_root_toggle)
        proj_layout.addWidget(self._cb_change_root)
        root_layout.addWidget(self._proj_group)

        # Splitter: tabs on top (1/3), log on bottom (2/3)
        self._splitter = QSplitter(Qt.Vertical)
        root_layout.addWidget(self._splitter, 1)

        self._work_widget = QWidget()
        self._build_work_tab(self._work_widget)
        self._splitter.addWidget(self._work_widget)

        log_group = QGroupBox('运行日志')
        log_inner = QVBoxLayout(log_group)
        log_inner.setContentsMargins(4, 4, 4, 4)
        self._log = LogPanel()
        log_inner.addWidget(self._log)
        self._splitter.addWidget(log_group)

        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 8)
        QTimer.singleShot(0, self._apply_splitter_ratio)

    def _build_work_tab(self, tab: QWidget) -> None:
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # ── PDF 打包 ──
        chapter_row = QHBoxLayout()
        self._chapter_list = ChapterList(on_change=self._on_chapters_changed)
        chapter_row.addWidget(self._chapter_list, 1)
        layout.addLayout(chapter_row)

        title_row = QHBoxLayout()
        title_row.addWidget(QLabel('文档标题'))
        self._ent_title = QLineEdit()
        self._ent_title.setReadOnly(True)
        title_row.addWidget(self._ent_title)
        layout.addLayout(title_row)

        out_row = QHBoxLayout()
        out_row.addWidget(QLabel('输出 PDF'))
        self._ent_output = QLineEdit()
        self._ent_output.setReadOnly(True)
        out_row.addWidget(self._ent_output)
        layout.addLayout(out_row)

        btn_row = QHBoxLayout()
      
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # ── 公式检查 + 图床检查（同一行）──
        check_group = QGroupBox('文档格式检查（已选章节）')
        check_layout = QHBoxLayout(check_group)
        check_layout.setSpacing(8)

        self._btn_math = QPushButton('公式检查')
        self._btn_math.clicked.connect(self._start_math_check)
        check_layout.addWidget(self._btn_math)
        self._btn_math_fix = QPushButton('自动修复')
        self._btn_math_fix.setEnabled(False)
        self._btn_math_fix.clicked.connect(self._start_math_fix)
        check_layout.addWidget(self._btn_math_fix)

        check_layout.addSpacing(16)

        self._btn_oss_scan = QPushButton('图片检查')
        self._btn_oss_scan.clicked.connect(self._scan_oss)
        check_layout.addWidget(self._btn_oss_scan)
        self._btn_oss_run = QPushButton('上传并替换')
        self._btn_oss_run.clicked.connect(self._start_oss)
        check_layout.addWidget(self._btn_oss_run)

        check_layout.addStretch()
        layout.addWidget(check_group)

        # ── 生成 PDF（主操作）──
        self._btn_pdf = QPushButton('▶  生成 PDF')
        self._btn_pdf.setMinimumHeight(52)
        self._btn_pdf.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._btn_pdf.setCursor(Qt.PointingHandCursor)
        self._btn_pdf.clicked.connect(self._start_pdf)
        self._btn_pdf.setStyleSheet(
            'QPushButton {'
            '  background-color: #1565c0;'
            '  color: #ffffff;'
            '  font-size: 18px;'
            '  font-weight: bold;'
            '  border: 2px solid #0d47a1;'
            '  border-radius: 8px;'
            '  padding: 12px 20px;'
            '}'
            'QPushButton:hover {'
            '  background-color: #1976d2;'
            '  border-color: #1565c0;'
            '}'
            'QPushButton:pressed {'
            '  background-color: #0d47a1;'
            '}'
            'QPushButton:disabled {'
            '  background-color: #424242;'
            '  color: #9e9e9e;'
            '  border-color: #616161;'
            '}'
        )
        layout.addWidget(self._btn_pdf)

        layout.addStretch()

    # ── Config & Paths ──────────────────────────────────

    def _ensure_project_root(self) -> None:
        root = self.cfg.project_root.strip()
        if root and os.path.isdir(root):
            return
        path = QFileDialog.getExistingDirectory(
            self,
            '首次使用：请选择项目根目录',
            root or default_project_root(),
        )
        if path:
            self.cfg.project_root = path
            save_config(self.cfg)
        else:
            fallback = default_project_root()
            if os.path.isdir(fallback):
                self.cfg.project_root = fallback

    def _load_fields(self) -> None:
        self._ent_project.setText(self.cfg.project_root or default_project_root())

    def _save_fields(self) -> None:
        self.cfg.project_root = self._ent_project.text().strip()
        selected = self._chapter_list.get_selected()
        if selected:
            self.cfg.selected_chapters = selected
            self.cfg.last_markdown_subdir = selected[0]
        self.cfg.window_geometry = f'{self.width()}x{self.height()}'
        save_config(self.cfg)

    def _selected_chapter_paths(self) -> list[Path]:
        root = self._project_path()
        return [subdir_path(root, name) for name in self._chapter_list.get_selected()]

    def _pdf_single_chapter_mode(self) -> bool:
        return len(self._chapter_list.get_selected()) <= 1

    def _apply_splitter_ratio(self) -> None:
        """日志区占窗口中央区域高度的 6/7。"""
        central = self.centralWidget()
        if not central:
            return
        total = central.height()
        splitter_h = self._splitter.height()
        if total <= 0 or splitter_h <= 0:
            return
        log_h = total * 6 // 7
        tabs_h = splitter_h - log_h
        if tabs_h < 64:
            tabs_h = 64
            log_h = max(splitter_h - tabs_h, 200)
        self._splitter.setSizes([tabs_h, log_h])

    def showEvent(self, event) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self._apply_splitter_ratio)

    def _project_path(self) -> Path:
        p = self._ent_project.text().strip() or default_project_root()
        return Path(p).resolve()

    def _refresh_subdirs(self) -> None:
        root = self._project_path()
        names = list_markdown_subdirs(root)

        if not names:
            self._chapter_list.set_chapters([], set())
            self._ent_title.setText('')
            self._ent_output.setText('')
            self._log.warn(f'根目录下未找到含 .md 的一层子目录: {root}')
            return

        saved = set(self.cfg.selected_chapters) & set(names)
        if not saved and self.cfg.last_markdown_subdir in names:
            saved = {self.cfg.last_markdown_subdir}
        if not saved:
            saved = set(names)
        self._chapter_list.set_chapters(names, saved)
        self._on_chapters_changed()

    def _on_chapters_changed(self) -> None:
        selected = self._chapter_list.get_selected()
        root = self._project_path()
        if not selected:
            self._ent_title.setText('')
            self._ent_output.setText('')
            return
        self._ent_title.setText(document_title_for_chapters(root, selected))
        out = output_pdf_for_chapters(root, selected)
        pdf_output_dir(root)
        self._ent_output.setText(str(out))

    def _on_change_root_toggle(self) -> None:
        if not self._cb_change_root.isChecked():
            return
        self._cb_change_root.setChecked(False)
        initial = self._ent_project.text() or default_project_root()
        path = QFileDialog.getExistingDirectory(self, '选择新的项目根目录', initial)
        if not path:
            return
        self._ent_project.setText(path)
        self.cfg.project_root = path
        save_config(self.cfg)
        self._log.info(f'根目录已更新: {path}')
        self._refresh_subdirs()

    # ── Task Control ────────────────────────────────────

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        for btn in (self._btn_pdf, self._btn_oss_scan, self._btn_oss_run, self._btn_math):
            btn.setEnabled(not busy)
        self._btn_math_fix.setEnabled(not busy and self._math_fix_available)

    def _update_math_fix_button(self, result: MathCheckResult | None, base: str = '') -> None:
        self._last_math_result = result
        self._last_math_base = base
        self._math_fix_available = bool(result and result.files_with_issues > 0)
        self._btn_math_fix.setEnabled(not self._busy and self._math_fix_available)

    def _start_worker(self, worker: QThread, on_done) -> None:
        if self._busy:
            return
        self._save_fields()
        self._set_busy(True)
        self._worker = worker

        def log_handler(msg: str, level: str = 'info') -> None:
            lvl = LogLevel.INFO
            if level == 'error':
                lvl = LogLevel.ERROR
            elif level == 'warn':
                lvl = LogLevel.WARN
            self._log.append(msg, lvl)

        if hasattr(worker, 'log_signal'):
            worker.log_signal.connect(log_handler)

        def cleanup(result: object) -> None:
            self._set_busy(False)
            self._worker = None
            on_done(result)

        worker.done_signal.connect(cleanup)
        worker.start()

    # ── PDF ─────────────────────────────────────────────

    def _refresh_deps(self, quiet: bool = False) -> None:
        if not quiet:
            self._log.info('—— 检测依赖 ——')

        if self._deps_worker and self._deps_worker.isRunning():
            if not quiet:
                self._log.warn('依赖检测正在进行中…')
            return

        self._deps_worker = _DepsWorker(self.cfg.extra_path or None)

        def on_done(status) -> None:
            if not quiet:
                ok = all(s.found for s in status.values())
                self._log.info(format_deps_summary(status))
                report = format_deps_report(status)
                for line in report.splitlines():
                    lvl = 'error' if '[缺失]' in line else 'info'
                    self._log.append(line, LogLevel.ERROR if lvl == 'error' else LogLevel.INFO)
                if ok:
                    self._log.info('依赖检测通过')
                else:
                    self._log.warn('存在缺失依赖，请安装后重试')

        self._deps_worker.done_signal.connect(on_done)
        self._deps_worker.start()

    def _start_pdf(self) -> None:
        selected = self._chapter_list.get_selected()
        if not selected:
            QMessageBox.warning(self, '提示', '请至少勾选一个章节')
            return

        root = self._project_path()
        chapters = [(str(subdir_path(root, name)), name) for name in selected]
        title = document_title_for_chapters(root, selected)
        output = str(output_pdf_for_chapters(root, selected))

        self._log.info('—— 开始生成 PDF ——')
        self._log.info(f'已选 {len(selected)} 章: {", ".join(selected)}')
        self._log.info(f'输出: {output}')

        def on_done(r) -> None:
            if r and r.success:
                self._ent_output.setText(r.output_pdf)
                self._log.info(f'PDF 已生成: {r.output_pdf} ({r.pages} 页, {r.size_kb:.1f} KB)')
                QMessageBox.information(self, '完成', f'已生成 PDF\n\n{r.output_pdf}\n{r.pages} 页')
            else:
                err = (r.error if r else '') or '未知错误'
                self._log.error(err)
                QMessageBox.critical(self, '失败', err)

        w = _PdfWorker(
            chapters, output, title,
            single_chapter=self._pdf_single_chapter_mode(),
            extra_path=self.cfg.extra_path or None,
        )
        self._start_worker(w, on_done)

    # ── OSS ─────────────────────────────────────────────

    def _log_oss_scan_result(self, result: OssScanResult, root: Path) -> None:
        """图床扫描：红=文档，黄=本地图片 URL，白=规则/状态说明。"""
        chapters = '、'.join(result.chapter_names)
        self._log.info(f'扫描章节: {chapters}')
        self._log.info(f'图片目录: {result.imgs_dir}')

        if result.refs == 0:
            self._log.info('未发现本地图片 URL，文档中的图片均为 OSS/远程地址')
            self._log.info('—— 扫描结束 ——')
            return

        self._log.warn(
            f'发现 {result.unique} 张唯一本地图片，共 {result.refs} 处引用'
        )

        for md, items in result.refs_by_document():
            try:
                rel = str(md.relative_to(root))
            except ValueError:
                rel = str(md)
            self._log.error(f'文档: {rel}（{len(items)} 处）')
            if rel != str(md):
                self._log.error(f'      {md}')

            for i, (fn, path_str) in enumerate(items, 1):
                exists = (result.imgs_dir / fn).exists()
                status = '本地 imgs/ 存在' if exists else '本地 imgs/ 缺失'
                self._log.warn(f'  [{i}] {path_str}')
                self._log.info(f'      文件: {fn} · {status}')

        if result.missing:
            self._log.warn(f'imgs/ 目录缺失 {len(result.missing)} 张图片:')
            for fn in result.missing:
                self._log.warn(f'  - {fn}')

        self._log.info('[预览] 未上传、未修改任何文件')
        self._log.info('—— 扫描结束 ——')

    def _scan_oss(self) -> None:
        selected = self._chapter_list.get_selected()
        if not selected:
            QMessageBox.warning(
                self,
                '提示',
                '请勾选要打包的章节',
            )
            return

        root = self._project_path()
        self._log.info(f'—— 扫描本地图片 URL（待打包文档）——')

        def on_done(r) -> None:
            if r:
                self._log_oss_scan_result(r, root)

        w = _OssScanWorker(root, selected, self.cfg.imgs_subdir)
        self._start_worker(w, on_done)

    def _start_oss(self) -> None:
        ak, sk = oss_credentials(self.cfg)
        if not ak or not sk:
            QMessageBox.warning(self, '提示', '请先在工具栏「图床设置」中填写 OSS AccessKey')
            return
        reply = QMessageBox.question(
            self,
            '确认',
            '将上传图片到 OSS 并修改 _posts/ 下的 .md 文件，是否继续？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self._log.info('—— 开始上传并替换 ——')

        def on_done(r) -> None:
            if r and r.success:
                QMessageBox.information(self, '完成', f'上传 {r.uploaded} 张，替换 {r.replaced} 处')
            elif r and r.error:
                self._log.error(r.error)
                QMessageBox.critical(self, '失败', r.error)
            elif r and r.failed:
                QMessageBox.warning(self, '部分失败', f'{len(r.failed)} 张上传失败，详见日志')

        w = _OssWorker(self._project_path(), ak, sk)
        self._start_worker(w, on_done)

    # ── Math Check ──────────────────────────────────────

    def _log_math_check_result(self, result: MathCheckResult, base: str) -> None:
        """公式检查结果：红=文档，黄=问题公式，白=触犯规则。"""
        self._log.info(f'共扫描 {result.total_files} 个文件')
        if result.files_with_issues == 0:
            self._log.info('全部通过，未发现问题')
            return

        self._log.warn(
            f'发现 {result.files_with_issues} 个文件有问题，共 {result.total_issues} 处'
        )
        for fr in result.files:
            rel = fr.rel_path(base)
            self._log.error(f'文档: {rel}（{len(fr.issues)} 处）')
            if rel != fr.path:
                self._log.error(f'      {fr.path}')

            for i, issue in enumerate(fr.issues, 1):
                loc = f'第 {issue.line} 行' if issue.line else '文件末尾'
                self._log.info(f'  [{i}] {loc}')
                self._log.info(f'      违反: {issue.rule.title}')
                self._log.info(f'      问题: {issue.detail}')
                self._log.info(f'      说明: {issue.rule.description}')
                snippet = issue.snippet_text()
                if snippet:
                    self._log.warn(f'      公式: {snippet}')

        self._log.info('—— 检查结束 ——')

    def _start_math_check(self) -> None:
        selected = self._chapter_list.get_selected()
        if not selected:
            QMessageBox.warning(self, '提示', '请至少勾选一个章节')
            return

        paths = [str(p) for p in self._selected_chapter_paths()]
        base = str(self._project_path())
        self._log.info(f'—— 检查公式规范: {", ".join(selected)} ——')
        self._update_math_fix_button(None)

        def on_done(r) -> None:
            if not r:
                self._update_math_fix_button(None)
                return
            self._log_math_check_result(r, base)
            self._update_math_fix_button(r, base)
            show_check_report(self, r, base)

        w = _MathWorker(paths)
        self._start_worker(w, on_done)

    def _log_math_fix_result(self, result: MathFixResult, base: str) -> None:
        if result.error:
            self._log.error(f'自动修复失败: {result.error}')
            return

        self._log.info(
            f'自动修复完成: {result.fixed_files} 个文件已修改，'
            f'{result.unchanged_files} 个无变化'
        )
        root_path = Path(base)
        for path, changes in result.details:
            try:
                rel = str(Path(path).relative_to(root_path))
            except ValueError:
                rel = path
            self._log.error(f'文档: {rel}')
            for change in changes:
                self._log.info(f'  · {change}')
        if result.fixed_files == 0:
            self._log.warn('未能自动修复的问题（如 $$ 未配对）请手动修改')
        self._log.info('—— 自动修复结束 ——')

    def _start_math_fix(self) -> None:
        if not self._last_math_result or not self._last_math_result.files:
            QMessageBox.information(self, '提示', '请先执行公式检查并发现问题')
            return

        base = self._last_math_base or str(self._project_path())
        file_count = self._last_math_result.files_with_issues
        issue_count = self._last_math_result.total_issues
        reply = QMessageBox.question(
            self,
            '确认自动修复',
            f'将尝试修复 {file_count} 个文件中的公式规范问题（共 {issue_count} 处）。\n'
            f'会直接改写 .md 文件，是否继续？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        paths = [fr.path for fr in self._last_math_result.files]
        self._log.info(f'—— 自动修复公式: {len(paths)} 个文件 ——')

        def on_fix_done(r: MathFixResult) -> None:
            if not r:
                return
            self._log_math_fix_result(r, base)
            show_fix_report(self, r, base)

            def on_recheck(check: MathCheckResult | None) -> None:
                if check:
                    self._log_math_check_result(check, base)
                    show_check_report(self, check, base)
                self._update_math_fix_button(check, base)

            self._log.info('—— 重新检查 ——')
            paths = [str(p) for p in self._selected_chapter_paths()]
            recheck = _MathWorker(paths)
            self._start_worker(recheck, on_recheck)

        w = _MathFixWorker(paths)
        self._start_worker(w, on_fix_done)

    # ── Misc ────────────────────────────────────────────

    def _open_pdf_output_dir(self) -> None:
        self._open_path(str(pdf_output_dir(self._project_path())))

    def _open_output(self) -> None:
        path = self._ent_output.text().strip()
        if path and os.path.exists(path):
            self._open_path(path)
        else:
            QMessageBox.information(self, '提示', '输出文件尚不存在')

    @staticmethod
    def _open_path(path: str) -> None:
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.run(['open', path], check=False)
        else:
            subprocess.run(['xdg-open', path], check=False)

    def closeEvent(self, event) -> None:
        self._save_fields()
        for w in (self._worker, self._deps_worker):
            if w is not None and w.isRunning():
                w.quit()
                w.wait(2000)
        super().closeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    # Dark-ish style
    app.setStyle('Fusion')
    window = DocToolsApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
