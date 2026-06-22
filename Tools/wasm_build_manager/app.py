#!/usr/bin/env python3
"""WASM Build Manager — visualize packages, sources, and trigger builds."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

from PyQt5.QtCore import QProcess, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from manifest_loader import BUILD_SCRIPT, MANIFEST_PATH, OUTPUT_DIR, REPO_ROOT, load_manifest
from package_model import PackageInfo, build_package_model, source_overlap

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def fmt_kb(n: int | None) -> str:
    if n is None:
        return "—"
    return f"{n / 1024:.1f} KB"


class WasmBuildManager(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WASM Build Manager")
        self.resize(1280, 800)
        self._packages: list[PackageInfo] = []
        self._overlap: dict[str, list[str]] = {}
        self._process: QProcess | None = None
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        toolbar = QHBoxLayout()
        self.status_label = QLabel("emsdk: checking…")
        btn_refresh = QPushButton("刷新")
        btn_build_sel = QPushButton("构建选中包")
        btn_build_page = QPushButton("构建全部 compat")
        btn_open_out = QPushButton("打开输出目录")
        btn_refresh.clicked.connect(self.refresh)
        btn_build_sel.clicked.connect(self.build_selected)
        btn_build_page.clicked.connect(lambda: self.run_build("page"))
        btn_open_out.clicked.connect(self.open_output_dir)
        for w in (btn_refresh, btn_build_sel, btn_build_page, btn_open_out):
            toolbar.addWidget(w)
        toolbar.addStretch()
        toolbar.addWidget(self.status_label)
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Horizontal)
        self.pkg_tree = QTreeWidget()
        self.pkg_tree.setHeaderLabels(["包", "体积", "状态"])
        self.pkg_tree.setMinimumWidth(240)
        self.pkg_tree.currentItemChanged.connect(self.on_pkg_selected)
        splitter.addWidget(self.pkg_tree)

        center = QVBoxLayout()
        center_w = QWidget()
        center_w.setLayout(center)
        self.detail_title = QLabel("选择左侧包查看详情")
        self.detail_title.setWordWrap(True)
        self.detail_meta = QLabel("")
        self.detail_meta.setWordWrap(True)
        self.src_tree = QTreeWidget()
        self.src_tree.setHeaderLabels(["源文件", "共享"])
        self.exports_list = QTreeWidget()
        self.exports_list.setHeaderLabels(["导出符号"])
        center.addWidget(self.detail_title)
        center.addWidget(self.detail_meta)
        center.addWidget(QLabel("源文件"))
        center.addWidget(self.src_tree, 2)
        center.addWidget(QLabel("导出符号 / 页面引用"))
        center.addWidget(self.exports_list, 1)
        splitter.addWidget(center_w)

        self.page_tree = QTreeWidget()
        self.page_tree.setHeaderLabels(["页面 / 重叠分析"])
        self.page_tree.setMinimumWidth(260)
        splitter.addWidget(self.page_tree)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Consolas", 10))
        self.log.setMaximumHeight(200)
        layout.addWidget(self.log)

        self._check_emsdk()

    def _check_emsdk(self) -> None:
        import platform
        ext = ".bat" if platform.system() == "Windows" else ""
        emsdk = REPO_ROOT / "cpp" / "emsdk" / "upstream" / "emscripten" / f"em++{ext}"
        if emsdk.exists():
            self.status_label.setText("emsdk: OK")
            self.status_label.setStyleSheet("color: #52d681")
        else:
            self.status_label.setText("emsdk: 未安装 — 运行 cpp/emsdk install latest")
            self.status_label.setStyleSheet("color: #ff5252")

    def refresh(self) -> None:
        try:
            manifest = load_manifest()
        except Exception as e:
            QMessageBox.critical(self, "Manifest 错误", str(e))
            return
        self._packages = build_package_model(manifest)
        self._overlap = source_overlap(self._packages)
        self.pkg_tree.clear()
        groups: dict[str, QTreeWidgetItem] = {}
        for pkg in self._packages:
            g = groups.setdefault(pkg.kind, QTreeWidgetItem([pkg.kind]))
            if g.parent() is None:
                self.pkg_tree.addTopLevelItem(g)
            size = fmt_kb(pkg.wasm_size)
            status = "✓" if pkg.built else "✗"
            item = QTreeWidgetItem([pkg.name, size, status])
            item.setData(0, Qt.UserRole, pkg.name)
            g.addChild(item)
        self.pkg_tree.expandAll()
        self.page_tree.clear()
        for page, cfg in (manifest.get("pages") or {}).items():
            pitem = QTreeWidgetItem([page])
            self.page_tree.addTopLevelItem(pitem)
            for ref in cfg.get("packages") or []:
                QTreeWidgetItem(pitem, [f"{ref['name']}  ({ref.get('load', 'eager')})"])
        ov = QTreeWidgetItem(["— 源文件重叠 —"])
        self.page_tree.addTopLevelItem(ov)
        for src, names in sorted(self._overlap.items(), key=lambda x: -len(x[1]))[:20]:
            QTreeWidgetItem(ov, [f"{Path(src).name}: {', '.join(names)}"])
        self.page_tree.expandAll()
        cur = self.pkg_tree.currentItem()
        if cur:
            self.on_pkg_selected(cur, None)

    def _pkg_by_name(self, name: str) -> PackageInfo | None:
        for p in self._packages:
            if p.name == name:
                return p
        return None

    def on_pkg_selected(self, current: QTreeWidgetItem | None, _prev) -> None:
        if not current:
            return
        name = current.data(0, Qt.UserRole)
        if not name:
            return
        pkg = self._pkg_by_name(name)
        if not pkg:
            return
        self.detail_title.setText(f"<b>{pkg.name}</b>  ({pkg.export_name})")
        pages = ", ".join(f"{p} [{m}]" for p, m in pkg.pages) or "—"
        self.detail_meta.setText(
            f"类型: {pkg.kind}  |  make: {pkg.make_target}\n"
            f"方法: {', '.join(pkg.methods) or '—'}\n"
            f"体积: wasm {fmt_kb(pkg.wasm_size)}  js {fmt_kb(pkg.js_size)}  |  页面: {pages}"
        )
        self.src_tree.clear()
        for src in pkg.sources:
            shared = self._overlap.get(src, [])
            tag = f"{len(shared)} 包" if len(shared) > 1 else ""
            QTreeWidgetItem(self.src_tree, [src, tag])
        self.exports_list.clear()
        for ex in pkg.exports:
            QTreeWidgetItem(self.exports_list, [ex])

    def open_output_dir(self) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        os.startfile(str(OUTPUT_DIR))

    def build_selected(self) -> None:
        item = self.pkg_tree.currentItem()
        if not item:
            return
        name = item.data(0, Qt.UserRole)
        if not name:
            QMessageBox.information(self, "提示", "请选择一个具体包（非分组行）")
            return
        self.run_build(name)

    def run_build(self, target: str) -> None:
        if self._process and self._process.state() != QProcess.NotRunning:
            QMessageBox.warning(self, "构建中", "请等待当前构建完成")
            return
        if not BUILD_SCRIPT.exists():
            QMessageBox.critical(self, "错误", f"未找到 {BUILD_SCRIPT}")
            return
        self.log.clear()
        if platform.system() == "Windows":
            cmd = "powershell"
            args = ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(BUILD_SCRIPT), "-Target", target]
            self.log.append(f"> powershell -File build_wasm.ps1 -Target {target}\n")
        else:
            cmd = "bash"
            args = [str(BUILD_SCRIPT), target]
            self.log.append(f"> bash build_wasm.sh {target}\n")
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._read_log)
        self._process.finished.connect(self._build_finished)
        self._process.start(cmd, args, cwd=str(REPO_ROOT / "cpp"))

    def _read_log(self) -> None:
        if not self._process:
            return
        data = bytes(self._process.readAllStandardOutput()).decode("utf-8", errors="replace")
        self.log.moveCursor(self.log.textCursor().End)
        self.log.insertPlainText(data)

    def _build_finished(self, code: int, _status) -> None:
        self.log.append(f"\n[exit {code}]\n")
        self.refresh()
        if code != 0:
            QMessageBox.warning(self, "构建失败", f"退出码 {code}，见日志")


def main() -> None:
    app = QApplication(sys.argv)
    win = WasmBuildManager()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
