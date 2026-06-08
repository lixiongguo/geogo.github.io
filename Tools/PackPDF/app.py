#!/usr/bin/env python3
"""文档整理工具 — PDF 打包、图床上传、公式检查（PyQt5 UI）。"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PyQt5.QtCore import QThread, pyqtSignal, Qt
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
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from packpdf.config import AppConfig, default_project_root, load_config, save_config
from packpdf.core import merge_chapters_to_pdf
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
from packpdf.ui.chapter_list import ChapterList
from packpdf.ui.rules_dialog import show_check_report, show_check_rules
from packpdf.ui.log_panel import LogLevel, LogPanel


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
        result = merge_chapters_to_pdf(
            self._chapters,
            self._output,
            self._title,
            single_chapter=self._single,
            extra_path=self._extra_path,
            on_log=lambda m: self.log_signal.emit(m, 'info'),
        )
        self.done_signal.emit(result)


class _OssScanWorker(QThread):
    log_signal = pyqtSignal(str, str)
    done_signal = pyqtSignal()

    def __init__(self, project_path: Path, ak: str, sk: str) -> None:
        super().__init__()
        self._path = project_path
        self._ak = ak
        self._sk = sk

    def run(self) -> None:
        summary = scan_summary(self._path)
        self.log_signal.emit(
            f'唯一图片: {summary["unique"]} 张，引用: {summary["refs"]} 处', 'info'
        )
        if summary.get('missing'):
            self.log_signal.emit(
                f'本地缺失 {len(summary["missing"])} 张:', 'warn'
            )
            for fn in summary['missing'][:30]:
                self.log_signal.emit(f'  - {fn}', 'warn')
            if len(summary['missing']) > 30:
                self.log_signal.emit(
                    f'  ... 还有 {len(summary["missing"]) - 30} 张', 'warn'
                )
        upload_and_replace(
            self._path, self._ak, self._sk,
            dry_run=True,
            on_log=lambda m, l: self.log_signal.emit(m, l),
        )
        self.done_signal.emit()


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

    def __init__(self, root: str, recursive: bool) -> None:
        super().__init__()
        self._root = root
        self._recursive = recursive

    def run(self) -> None:
        result = check_directory(self._root, recursive=self._recursive)
        self.done_signal.emit(result)


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
        self.setWindowTitle('文档整理工具 — PDF / 图床 / 公式')
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

        self._build_ui()
        self._ensure_project_root()
        self._load_fields()
        self._refresh_subdirs()
        self._refresh_deps(quiet=True)

    # ── UI ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(6)

        # Project root bar
        proj_group = QGroupBox('项目根目录')
        proj_layout = QHBoxLayout(proj_group)
        self._ent_project = QLineEdit()
        self._ent_project.setReadOnly(True)
        proj_layout.addWidget(self._ent_project)
        self._cb_change_root = QCheckBox('修改根目录')
        self._cb_change_root.stateChanged.connect(self._on_change_root_toggle)
        proj_layout.addWidget(self._cb_change_root)
        root_layout.addWidget(proj_group)

        # Splitter: tabs on top, log on bottom
        splitter = QSplitter(Qt.Vertical)
        root_layout.addWidget(splitter)

        self._tabs = QTabWidget()
        self._build_pdf_tab()
        self._build_oss_tab()
        self._build_math_tab()
        splitter.addWidget(self._tabs)

        log_group = QGroupBox('运行日志')
        log_inner = QVBoxLayout(log_group)
        log_inner.setContentsMargins(4, 4, 4, 4)
        self._log = LogPanel(height=10)
        log_inner.addWidget(self._log)
        splitter.addWidget(log_group)

        splitter.setSizes([500, 180])

    def _build_pdf_tab(self) -> None:
        tab = QWidget()
        self._tabs.addTab(tab, 'PDF 打包')
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Chapter selection
        row_header = QHBoxLayout()
        row_header.addWidget(QLabel('选择章节'))
        row_header.addStretch()
        btn_refresh = QPushButton('刷新列表')
        btn_refresh.clicked.connect(self._refresh_subdirs)
        row_header.addWidget(btn_refresh)
        layout.addLayout(row_header)

        self._chapter_list = ChapterList(on_change=self._on_chapters_changed, height=60)
        layout.addWidget(self._chapter_list)

        # Title
        title_row = QHBoxLayout()
        title_row.addWidget(QLabel('文档标题'))
        self._ent_title = QLineEdit()
        self._ent_title.setReadOnly(True)
        title_row.addWidget(self._ent_title)
        layout.addLayout(title_row)

        # Output PDF
        out_row = QHBoxLayout()
        out_row.addWidget(QLabel('输出 PDF'))
        self._ent_output = QLineEdit()
        self._ent_output.setReadOnly(True)
        out_row.addWidget(self._ent_output)
        layout.addLayout(out_row)

        # Options
        self._cb_single = QCheckBox('单章模式（章内文章不加「第 N 章」前缀；多章时各章以目录名分节）')
        self._cb_single.setChecked(True)
        layout.addWidget(self._cb_single)

        # Buttons
        btn_row = QHBoxLayout()
        self._btn_pdf = QPushButton('生成 PDF')
        self._btn_pdf.clicked.connect(self._start_pdf)
        btn_row.addWidget(self._btn_pdf)
        btn_deps = QPushButton('检测 pandoc/xelatex')
        btn_deps.clicked.connect(self._refresh_deps)
        btn_row.addWidget(btn_deps)
        btn_open_dir = QPushButton('打开 PDF_output')
        btn_open_dir.clicked.connect(self._open_pdf_output_dir)
        btn_row.addWidget(btn_open_dir)
        btn_open = QPushButton('打开输出 PDF')
        btn_open.clicked.connect(self._open_output)
        btn_row.addWidget(btn_open)
        btn_help = QPushButton('📖 帮助说明')
        btn_help.clicked.connect(self._show_pdf_help)
        btn_row.addWidget(btn_help)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        hint = QLabel('勾选要打包的章节；多章合并为一个 PDF，输出至根目录/PDF_output/')
        hint.setStyleSheet('color: #888;')
        layout.addWidget(hint)

        self._lbl_deps = QLabel('')
        layout.addWidget(self._lbl_deps)

    def _build_oss_tab(self) -> None:
        tab = QWidget()
        self._tabs.addTab(tab, '图床上传')
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        layout.addWidget(
            QLabel('说明：扫描 _posts/ 中引用 imgs/ 的本地图片，上传阿里云 OSS 并替换路径。')
        )

        # AK
        ak_row = QHBoxLayout()
        ak_row.addWidget(QLabel('AccessKey ID'))
        self._ent_ak = QLineEdit()
        self._ent_ak.setText(os.environ.get('OSS_ACCESS_KEY_ID', ''))
        ak_row.addWidget(self._ent_ak)
        layout.addLayout(ak_row)

        # SK
        sk_row = QHBoxLayout()
        sk_row.addWidget(QLabel('AccessKey Secret'))
        self._ent_sk = QLineEdit()
        self._ent_sk.setEchoMode(QLineEdit.Password)
        self._ent_sk.setText(os.environ.get('OSS_ACCESS_KEY_SECRET', ''))
        sk_row.addWidget(self._ent_sk)
        layout.addLayout(sk_row)

        self._cb_remember_oss = QCheckBox('记住密钥到本地 config.json（勿提交 git）')
        layout.addWidget(self._cb_remember_oss)

        btn_row = QHBoxLayout()
        self._btn_oss_scan = QPushButton('扫描预览')
        self._btn_oss_scan.clicked.connect(self._scan_oss)
        btn_row.addWidget(self._btn_oss_scan)
        self._btn_oss_run = QPushButton('上传并替换')
        self._btn_oss_run.clicked.connect(self._start_oss)
        btn_row.addWidget(self._btn_oss_run)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addStretch()

    def _build_math_tab(self) -> None:
        tab = QWidget()
        self._tabs.addTab(tab, '公式检查')
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel('检查目录'))
        self._ent_check_dir = QLineEdit()
        dir_row.addWidget(self._ent_check_dir)
        btn_browse = QPushButton('浏览…')
        btn_browse.clicked.connect(self._pick_check_dir)
        dir_row.addWidget(btn_browse)
        layout.addLayout(dir_row)

        self._cb_recursive = QCheckBox('递归子目录')
        self._cb_recursive.setChecked(True)
        layout.addWidget(self._cb_recursive)

        btn_row = QHBoxLayout()
        self._btn_math = QPushButton('开始检查')
        self._btn_math.clicked.connect(self._start_math_check)
        btn_row.addWidget(self._btn_math)
        btn_rules = QPushButton('查看检查依据')
        btn_rules.clicked.connect(lambda: show_check_rules(self))
        btn_row.addWidget(btn_rules)
        btn_row.addStretch()
        layout.addLayout(btn_row)
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
        self._cb_single.setChecked(self.cfg.single_chapter)
        self._ent_check_dir.setText(
            self.cfg.check_dir or os.path.join(self._ent_project.text(), '_posts')
        )
        if self.cfg.oss_access_key_id:
            self._ent_ak.setText(self.cfg.oss_access_key_id)
        if self.cfg.oss_access_key_secret:
            self._ent_sk.setText(self.cfg.oss_access_key_secret)
        self._cb_remember_oss.setChecked(self.cfg.remember_oss_keys)

    def _save_fields(self) -> None:
        self.cfg.project_root = self._ent_project.text().strip()
        selected = self._chapter_list.get_selected()
        if selected:
            self.cfg.selected_chapters = selected
            self.cfg.last_markdown_subdir = selected[0]
        self.cfg.single_chapter = self._cb_single.isChecked()
        self.cfg.check_dir = self._ent_check_dir.text().strip()
        self.cfg.remember_oss_keys = self._cb_remember_oss.isChecked()
        if self.cfg.remember_oss_keys:
            self.cfg.oss_access_key_id = self._ent_ak.text().strip()
            self.cfg.oss_access_key_secret = self._ent_sk.text().strip()
        self.cfg.window_geometry = f'{self.width()}x{self.height()}'
        save_config(self.cfg)

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
        if len(selected) == 1:
            self._ent_check_dir.setText(str(subdir_path(root, selected[0])))

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
        self._log.info('—— 检测依赖 ——')

        if self._deps_worker and self._deps_worker.isRunning():
            self._log.warn('依赖检测正在进行中…')
            return

        self._deps_worker = _DepsWorker(self.cfg.extra_path or None)

        def on_done(status) -> None:
            report = format_deps_report(status)
            ok = all(s.found for s in status.values())
            self._lbl_deps.setText(report.replace('\n', '  |  '))
            self._lbl_deps.setStyleSheet(f'color: {"#080" if ok else "#a00"};')
            if not quiet:
                for line in report.splitlines():
                    lvl = 'error' if '[缺失]' in line else 'info'
                    self._log.append(line, LogLevel.ERROR if lvl == 'error' else LogLevel.INFO)

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
            single_chapter=self._cb_single.isChecked(),
            extra_path=self.cfg.extra_path or None,
        )
        self._start_worker(w, on_done)

    def _show_pdf_help(self) -> None:
        msg = QMessageBox(self)
        msg.setWindowTitle('PDF 打包说明')
        msg.setIcon(QMessageBox.Information)
        msg.setText(
            '<h3>📦 依赖安装</h3>'
            '<p><b>macOS：</b></p>'
            '<pre>brew install pandoc\nbrew install --cask mactex    # 完整版（~4GB）\n# 或\nbrew install --cask basictex  # 精简版（~100MB）</pre>'
            '<p><b>Windows：</b></p>'
            '<pre>winget install Pandoc.Pandoc\nwinget install MiKTeX.MiKTeX\n# 或手动下载安装包</pre>'
            '<p>安装后重启终端，点击「检测 pandoc/xelatex」确认两项均显示 [OK]。</p>'
            '<hr>'
            '<h3>⚙️ 打包流程</h3>'
            '<ol>'
            '<li><b>选择章节</b> — 勾选 _posts/ 下的子目录（每个目录即为一章）</li>'
            '<li><b>拼接 Markdown</b> — 将章节内所有 .md 文件按文件名排序拼接，合并为单个临时 .md</li>'
            '<li><b>下载远程图片</b> — 将 远程引用的图片下载到本地临时目录</li>'
            '<li><b>pandoc 转换</b> — <code>pandoc input.md -o output.tex --standalone</code> 生成 LaTeX 中间文件</li>'
            '<li><b>xelatex 编译</b> — <code>xelatex output.tex</code> 编译两次，生成最终 PDF（支持中文）</li>'
            '<li><b>合并页面</b> — 使用 PyPDF2 合并多个 PDF 为单一文件</li>'
            '</ol>'
            '<hr>'
            '<h3>💡 提示</h3>'
            '<ul>'
            '<li>单章模式下各文章不加「第 N 章」前缀；多章时自动分节</li>'
            '<li>输出目录为 <code>项目根目录/PDF_output/</code></li>'
            '<li>章节内 .md 文件建议按日期命名以便排序</li>'
            '</ul>'
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    # ── OSS ─────────────────────────────────────────────

    def _scan_oss(self) -> None:
        self._log.info('—— 扫描本地图片引用 ——')
        ak = self._ent_ak.text().strip()
        sk = self._ent_sk.text().strip()
        w = _OssScanWorker(self._project_path(), ak, sk)
        self._start_worker(w, lambda _r: None)

    def _start_oss(self) -> None:
        ak = self._ent_ak.text().strip()
        sk = self._ent_sk.text().strip()
        if not ak or not sk:
            QMessageBox.warning(self, '提示', '请填写 OSS AccessKey')
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

    def _pick_check_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            '选择要检查的目录',
            self._ent_check_dir.text() or self._ent_project.text(),
        )
        if path:
            self._ent_check_dir.setText(path)

    def _start_math_check(self) -> None:
        root = self._ent_check_dir.text().strip()
        if not root or not os.path.isdir(root):
            QMessageBox.warning(self, '提示', '请选择有效的检查目录')
            return

        self._log.info(f'—— 检查公式规范: {root} ——')

        def on_done(r) -> None:
            if not r:
                return
            if r.files_with_issues == 0:
                self._log.info(f'全部通过 ({r.total_files} 个文件)')
            else:
                self._log.warn(f'{r.files_with_issues}/{r.total_files} 个文件有问题，共 {r.total_issues} 处')
                for fr in r.files:
                    self._log.warn(f'{fr.path} ({len(fr.issues)} 处)')
                    for issue in fr.issues:
                        self._log.warn(f'  {issue.format_log()}')
            show_check_report(self, r)

        w = _MathWorker(root, recursive=self._cb_recursive.isChecked())
        self._start_worker(w, on_done)

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
