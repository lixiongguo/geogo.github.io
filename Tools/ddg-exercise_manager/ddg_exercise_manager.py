#!/usr/bin/env python3
"""DDG Exercise Manager — 浏览和打开离散微分几何练习项目"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

from PyQt5.QtCore import Qt, QSize, QProcess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QListWidgetItem,
    QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QSplitter, QMessageBox, QCheckBox, QFileDialog
)
from PyQt5.QtGui import QFont, QColor, QPalette, QTextCursor

# ── 路径配置 ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # .../lixiongguo.github.io/
PROJECTS_DIR = PROJECT_ROOT / "cpp" / "ddg-exercises" / "projects"
HISTORY_FILE = SCRIPT_DIR / "history.json"
EIGEN_PATH = PROJECT_ROOT / "cpp" / "deps" / "eigen-3.4.0"

# ── 项目元数据 ────────────────────────────────────────────
PROJECTS_META = {
    "simplicial-complex-operators": {
        "name": "HW0 — 组合曲面",
        "subtitle": "单纯复形算子",
        "desc": (
            "课程入门作业。实现单纯复形的基本算子：\n"
            "  • assignElementIndices — 元素索引分配\n"
            "  • buildVertexEdgeAdjacencyMatrix — 顶点-边邻接\n"
            "  • buildEdgeFaceAdjacencyMatrix — 边-面邻接\n"
            "  • star / closure / link / boundary — 拓扑算子\n\n"
            "默认网格: small_disk.obj"
        ),
        "keywords": "simplicial complex, star, closure, link, boundary"
    },
    "discrete-exterior-calculus": {
        "name": "HW1 — 外微积分",
        "subtitle": "离散外微积分 (DEC)",
        "desc": (
            "实现离散外微积分核心算子：\n"
            "  • cotan 权重 & 重心对偶面积\n"
            "  • Hodge 星算子 (0/1/2-形式)\n"
            "  • 外导数 (0-形式 & 1-形式)\n\n"
            "构建对偶网格，可随机生成 k-形式并可视化 d 和 * 算子。\n"
            "仅支持平面网格 (Z=0)。\n"
            "默认网格: hexagon.obj"
        ),
        "keywords": "Hodge star, exterior derivative, discrete exterior calculus"
    },
    "discrete-curvatures-and-normals": {
        "name": "HW2 — 曲率研究",
        "subtitle": "离散曲率与顶点法线",
        "desc": (
            "实现多种顶点法线加权方式和曲率着色：\n"
            "  • 顶点法线: 角度加权 / 球内切 / 面积加权 / 高斯曲率 / 平均曲率\n"
            "  • 角度缺陷 (angle defect) & 总角度缺陷\n"
            "  • 标量平均曲率 & 外心对偶面积\n"
            "  • 主曲率 (principal curvatures)\n\n"
            "默认网格: bunny.obj"
        ),
        "keywords": "normal, curvature, angle defect, principal curvature"
    },
    "geometric-flow": {
        "name": "HW3a — 几何流",
        "subtitle": "平均曲率流 (MCF)",
        "desc": (
            "实现网格上的平均曲率流和平滑平均曲率流：\n"
            "  • Laplace 矩阵 & 质量矩阵\n"
            "  • buildFlowOperator — 构建流算子\n"
            "  • integrate — 时间积分\n\n"
            "可调节 timestep 并逐步应用流。\n"
            "默认网格: bunny.obj"
        ),
        "keywords": "mean curvature flow, Laplace-Beltrami, mesh smoothing"
    },
    "poisson-problem": {
        "name": "HW3b — 泊松问题",
        "subtitle": "曲面标量泊松方程",
        "desc": (
            "在曲面上求解标量泊松问题：\n"
            "  • Laplace 矩阵 & 质量矩阵\n"
            "  • ScalarPoissonProblem 构造与求解\n\n"
            "点选顶点设密度值，求解后以颜色图显示。\n"
            "默认网格: bunny.obj"
        ),
        "keywords": "Poisson, Laplace, PDE on surfaces"
    },
    "parameterization": {
        "name": "HW4 — 共形参数化",
        "subtitle": "谱共形参数化 (SCP)",
        "desc": (
            "实现谱共形参数化 (Spectral Conformal Parameterization):\n"
            "  • complexLaplaceMatrix — 复数拉普拉斯矩阵\n"
            "  • buildConformalEnergy / flatten\n"
            "  • solveInversePowerMethod — 逆幂法求解\n\n"
            "支持棋盘格纹理/共形误差/面积缩放着色。\n"
            "要求网格至少有一个边界环。\n"
            "默认网格: face.obj"
        ),
        "keywords": "conformal parameterization, spectral, eigenvalues"
    },
    "geodesic-distance": {
        "name": "HW5 — 测地距离",
        "subtitle": "热方法 (Heat Method)",
        "desc": (
            "使用热方法计算曲面上的测地距离：\n"
            "  • computeVectorField — 梯度场\n"
            "  • computeDivergence — 散度\n"
            "  • compute — 泊松求解\n\n"
            "点选源顶点 → Solve → 距离颜色图 + 等值线。\n"
            "默认网格: bunny.obj"
        ),
        "keywords": "geodesic, heat method, distance"
    },
    "vector-field-decomposition": {
        "name": "HW6a — 向量场分解",
        "subtitle": "Hodge 分解",
        "desc": (
            "实现向量场的 Hodge 分解：\n"
            "  • Tree-Cotree — 生成树/余树/生成元\n"
            "  • HarmonicBases — 调和基\n"
            "  • HodgeDecomposition — 精确/余精确/调和分量\n\n"
            "仅支持无边界的闭合网格。\n"
            "默认网格: bunny.obj"
        ),
        "keywords": "Hodge decomposition, tree-cotree, harmonic basis"
    },
    "direction-field-design": {
        "name": "HW6b — 方向场设计",
        "subtitle": "平凡联络 (Trivial Connections)",
        "desc": (
            "实现平凡联络用于方向场设计：\n"
            "  • buildPeriodMatrix — 周期矩阵\n"
            "  • computeConnections — 联络计算\n\n"
            "点选顶点设奇点指数 → Compute → 方向场可视化。\n"
            "仅支持拓扑球面。\n"
            "默认网格: bunny.obj"
        ),
        "keywords": "direction field, trivial connection, singularity"
    },
}

# ── 样式表 ────────────────────────────────────────────────
STYLE = """
QMainWindow {
    background-color: #1a1d2e;
}
QListWidget {
    background-color: #141829;
    color: #d8def7;
    border: 1px solid #2a3a5c;
    border-radius: 8px;
    font-size: 13px;
    outline: none;
}
QListWidget::item {
    padding: 10px 14px;
    border-bottom: 1px solid #1e2a42;
}
QListWidget::item:selected {
    background-color: #2c3e6b;
    color: #ffffff;
}
QListWidget::item:hover {
    background-color: #1e2e4f;
}
QTextEdit {
    background-color: #0d1220;
    color: #bcc8e8;
    border: 1px solid #2a3a5c;
    border-radius: 8px;
    padding: 12px;
    font-size: 13px;
    line-height: 1.6;
}
QPushButton {
    background-color: #2d4a8c;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #3a5dad;
}
QPushButton:pressed {
    background-color: #1f3570;
}
QPushButton:disabled {
    background-color: #1a2644;
    color: #5a6d9c;
}
QPushButton#secondary {
    background-color: #1e2a45;
    color: #8ca0d4;
}
QPushButton#secondary:hover {
    background-color: #2a3c60;
}
QLabel {
    color: #8ca0d4;
    font-size: 12px;
}
QCheckBox {
    color: #8ca0d4;
    font-size: 12px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
}
QSplitter::handle {
    background-color: #2a3a5c;
    width: 2px;
}
"""


class DDGExerciseManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DDG Exercise Manager — 离散微分几何练习")
        self.setMinimumSize(900, 600)
        self.resize(1000, 680)

        self._projects_dir = Path(PROJECTS_DIR)
        self._history = self._load_history()
        self._current_project = None
        self._recent_first = True

        self._init_ui()
        self._populate_list()
        self._restore_selection()

    # ── UI 构建 ─────────────────────────────────────────
    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        # 标题
        title = QLabel("⚙️ DDG Exercise Manager")
        title.setStyleSheet("font-size:18px; font-weight:bold; color:#e0e6ff; padding:4px 0;")
        root.addWidget(title)

        # 复选框
        chk_row = QHBoxLayout()
        chk_row.setContentsMargins(0, 0, 0, 0)
        self._recent_cb = QCheckBox("最近打开置顶")
        self._recent_cb.setChecked(True)
        self._recent_cb.toggled.connect(lambda v: self._sort_list())
        chk_row.addWidget(self._recent_cb)
        chk_row.addStretch()
        root.addLayout(chk_row)

        # 主分割器
        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter, 1)

        # — 左侧: 项目列表 —
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 8, 0)
        ll.setSpacing(8)

        search_label = QLabel("📂 项目列表 (9 个作业)")
        search_label.setStyleSheet("font-weight:bold; color:#a0b0e0;")
        ll.addWidget(search_label)

        self._list = QListWidget()
        self._list.currentItemChanged.connect(self._on_select)
        ll.addWidget(self._list)
        splitter.addWidget(left)

        # — 右侧: 详情 + 操作 —
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(8, 0, 0, 0)
        rl.setSpacing(10)

        info_label = QLabel("📄 项目详情")
        info_label.setStyleSheet("font-weight:bold; color:#a0b0e0;")
        rl.addWidget(info_label)

        self._detail = QTextEdit()
        self._detail.setReadOnly(True)
        rl.addWidget(self._detail, 1)

        # 按钮行 1
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._open_btn = QPushButton("▶  运行项目")
        self._open_btn.clicked.connect(self._run_project)
        btn_row.addWidget(self._open_btn)

        self._compile_btn = QPushButton("🔨 编译")
        self._compile_btn.clicked.connect(lambda: self._start_build(rebuild=False))
        btn_row.addWidget(self._compile_btn)

        self._rebuild_btn = QPushButton("🔄 重编译")
        self._rebuild_btn.setObjectName("secondary")
        self._rebuild_btn.clicked.connect(lambda: self._start_build(rebuild=True))
        btn_row.addWidget(self._rebuild_btn)

        btn_row.addStretch()

        self._folder_btn = QPushButton("📁 打开文件夹")
        self._folder_btn.setObjectName("secondary")
        self._folder_btn.clicked.connect(self._open_folder)
        btn_row.addWidget(self._folder_btn)

        self._readme_btn = QPushButton("📖 README")
        self._readme_btn.setObjectName("secondary")
        self._readme_btn.clicked.connect(self._open_readme)
        btn_row.addWidget(self._readme_btn)

        rl.addLayout(btn_row)

        # 构建输出 (初始隐藏)
        self._build_label = QLabel("📋 构建输出")
        self._build_label.setStyleSheet("font-weight:bold; color:#a0b0e0; margin-top:6px;")
        self._build_label.setVisible(False)
        rl.addWidget(self._build_label)

        self._build_output = QTextEdit()
        self._build_output.setReadOnly(True)
        self._build_output.setMaximumHeight(180)
        self._build_output.setStyleSheet("""
            QTextEdit {
                background-color: #0a0e18;
                color: #98c0d8;
                border: 1px solid #2a3a5c;
                border-radius: 6px;
                padding: 6px;
                font-family: 'Menlo', 'Consolas', monospace;
                font-size: 11px;
                line-height: 1.3;
            }
        """)
        self._build_output.setVisible(False)
        rl.addWidget(self._build_output)

        # QProcess (复用)
        self._build_proc = None

        # 状态标签
        self._status = QLabel("就绪 — 选择一个项目以开始")
        self._status.setStyleSheet("color:#5a7d9c; font-size:11px; padding:2px 0;")
        rl.addWidget(self._status)

        splitter.addWidget(right)
        splitter.setSizes([350, 650])

    # ── 列表填充 ────────────────────────────────────────
    def _populate_list(self):
        self._list.clear()
        for key, meta in PROJECTS_META.items():
            item = QListWidgetItem(f"{meta['name']}\n{meta['subtitle']}")
            item.setData(Qt.UserRole, key)
            item.setSizeHint(QSize(0, 52))
            self._list.addItem(item)

    def _sort_list(self):
        """将最近打开的项目置顶"""
        if not self._recent_cb.isChecked() or not self._history:
            return

        # 收集当前项目顺序
        keys = [self._list.item(i).data(Qt.UserRole) for i in range(self._list.count())]
        recent = set(self._history)

        # 排序: 最近的在前
        keys.sort(key=lambda k: (k not in recent, -self._history.index(k) if k in self._history else 0))
        for i, key in enumerate(keys):
            for j in range(self._list.count()):
                if self._list.item(j).data(Qt.UserRole) == key:
                    item = self._list.takeItem(j)
                    self._list.insertItem(i, item)
                    break

    def _restore_selection(self):
        if self._history and self._list.count() > 0:
            # 选择最近打开的项目
            last = self._history[0]
            for i in range(self._list.count()):
                if self._list.item(i).data(Qt.UserRole) == last:
                    self._list.setCurrentRow(i)
                    return
        self._list.setCurrentRow(0)

    # ── 交互 ────────────────────────────────────────────
    def _on_select(self, current, _previous):
        if not current:
            self._current_project = None
            self._detail.clear()
            self._open_btn.setEnabled(False)
            self._folder_btn.setEnabled(False)
            self._readme_btn.setEnabled(False)
            self._compile_btn.setEnabled(False)
            self._rebuild_btn.setEnabled(False)
            self._status.setText("")
            return

        key = current.data(Qt.UserRole)
        self._current_project = key
        meta = PROJECTS_META.get(key, {})

        detail_text = f"""<h2 style="color:#d8def7;margin:0 0 8px;">{meta.get('name','')}</h2>
<h3 style="color:#8ca0d4;margin:0 0 12px;">{meta.get('subtitle','')}</h3>
<p style="color:#bcc8e8;line-height:1.7;white-space:pre-wrap;">{meta.get('desc','无描述')}</p>
<hr style="border-color:#2a3a5c;">
<p style="color:#7a8db5;font-size:11px;">📁 路径: <code>{self._projects_dir / key}</code></p>
<p style="color:#7a8db5;font-size:11px;">🏷 关键词: {meta.get('keywords','')}</p>"""

        bin_path = self._find_binary(key)
        if bin_path:
            detail_text += f'<p style="color:#52d681;font-size:11px;">✅ 可执行文件: {bin_path}</p>'
        else:
            detail_text += '<p style="color:#ffd38a;font-size:11px;">⚠ 未找到编译产物 (需要先 cmake && make)</p>'

        self._detail.setHtml(detail_text)
        self._open_btn.setEnabled(True)
        self._folder_btn.setEnabled(True)
        self._readme_btn.setEnabled(True)
        self._compile_btn.setEnabled(True)
        self._rebuild_btn.setEnabled(True)
        self._status.setText(f"选中: {meta.get('name','')}")

    def _find_binary(self, key):
        """查找 build 目录中的可执行文件"""
        build_dir = self._projects_dir / key / "build"
        if not build_dir.is_dir():
            return None
        for f in sorted(build_dir.glob("**/*"), key=lambda p: p.stat().st_mtime, reverse=True):
            if f.is_file() and os.access(f, os.X_OK) and not f.suffix and not f.name.endswith(".d"):
                # 过滤掉 .o, .a, cmake 文件等
                name = f.name
                if name in ("main",) or name.startswith("main") or name.startswith("test"):
                    return str(f)
        return None

    def _run_project(self):
        if not self._current_project:
            return
        bin_path = self._find_binary(self._current_project)
        if bin_path:
            self._add_history()
            # 从 build/ 目录启动 (不是 build/bin/)：
            # 二进制在 build/bin/main，但 ../../../input/ 需要从 build/ 解析
            bin_abs = Path(bin_path).resolve()
            build_dir = bin_abs.parent.parent  # build/bin/ → build/
            rel_bin = "./bin/" + bin_abs.name
            subprocess.Popen([rel_bin], cwd=str(build_dir))
            self._status.setText(f"正在运行: {bin_abs.name}  (cwd={build_dir})")
        else:
            QMessageBox.information(
                self, "未找到可执行文件",
                f"项目 {self._current_project} 尚未编译。\n\n"
                f"请先在该项目目录下执行:\n"
                f"  cd {self._projects_dir / self._current_project}\n"
                f"  mkdir build && cd build && cmake .. && make\n\n"
                f"然后再试。"
            )

    def _open_folder(self):
        if not self._current_project:
            return
        self._add_history()
        path = str(self._projects_dir / self._current_project)
        if sys.platform == "darwin":
            subprocess.Popen(["open", path])
        elif sys.platform == "win32":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])
        self._status.setText(f"已在文件管理器中打开: {path}")

    def _open_readme(self):
        if not self._current_project:
            return
        readme = self._projects_dir / self._current_project / "README.md"
        if readme.is_file():
            if sys.platform == "darwin":
                subprocess.Popen(["open", str(readme)])
            elif sys.platform == "win32":
                os.startfile(str(readme))
            else:
                subprocess.Popen(["xdg-open", str(readme)])
            self._status.setText(f"已打开 README: {readme.name}")
        else:
            QMessageBox.warning(self, "缺少 README", f"该项目没有 README.md 文件。")

    # ── 编译 ────────────────────────────────────────────
    def _start_build(self, rebuild=False):
        if not self._current_project:
            return
        key = self._current_project
        proj_dir = self._projects_dir / key
        build_dir = proj_dir / "build"

        # 重编译: 删除 build 目录
        if rebuild and build_dir.is_dir():
            shutil.rmtree(build_dir)
            self._build_output.append("[rebuild] 已删除 build/ 目录\n")

        build_dir.mkdir(exist_ok=True)

        # 显示输出面板
        self._build_label.setVisible(True)
        self._build_output.setVisible(True)
        self._build_output.clear()
        self._build_output.append(f"═══ {'重编译' if rebuild else '编译'} {key} ═══\n")
        self._build_output.append(f"📁 {build_dir}\n")

        self._compile_btn.setEnabled(False)
        self._rebuild_btn.setEnabled(False)
        self._status.setText(f"正在{'重' if rebuild else ''}编译: {key} ...")

        # 终止之前的进程
        if self._build_proc and self._build_proc.state() != QProcess.NotRunning:
            self._build_proc.kill()

        self._build_proc = QProcess(self)
        self._build_proc.setWorkingDirectory(str(build_dir))
        self._build_proc.readyReadStandardOutput.connect(self._on_build_stdout)
        self._build_proc.readyReadStandardError.connect(self._on_build_stderr)
        self._build_proc.finished.connect(self._on_build_finished)

        # 执行 cmake .. (使用本地 Eigen, 跳过 geometry-central 版本检查)
        self._build_step = 0
        self._build_ok = True

        # 生成 hook 脚本: 预先创建 Eigen3::Eigen target, geometry-central 检测到后跳过 EigenChecker
        hook_path = SCRIPT_DIR / "eigen_hook_active.cmake"
        hook_path.write_text(
            f"if(NOT TARGET Eigen3::Eigen)\n"
            f"  add_library(Eigen3::Eigen INTERFACE IMPORTED)\n"
            f"  set_target_properties(Eigen3::Eigen PROPERTIES\n"
            f"    INTERFACE_INCLUDE_DIRECTORIES \"{EIGEN_PATH}\"\n"
            f"  )\n"
            f"endif()\n"
        )

        cmake_args = ["..",
            f"-DCMAKE_PROJECT_INCLUDE={hook_path}",
            "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",  # polyscope 兼容 CMake 4.x
            f"-DCMAKE_CXX_FLAGS=-I{EIGEN_PATH}",    # 本地 Eigen 优先于 /usr/local/include
        ]
        self._build_output.append(f"$ cmake .. -DCMAKE_PROJECT_INCLUDE={hook_path}\n")
        self._build_proc.start("cmake", cmake_args)

    def _on_build_stdout(self):
        data = self._build_proc.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self._build_output.insertPlainText(data)
        self._build_output.moveCursor(QTextCursor.End)

    def _on_build_stderr(self):
        data = self._build_proc.readAllStandardError().data().decode("utf-8", errors="replace")
        self._build_output.insertPlainText(data)
        self._build_output.moveCursor(QTextCursor.End)

    def _on_build_finished(self, exit_code, _exit_status):
        if exit_code != 0:
            self._build_output.append(f"\n❌ 步骤失败 (exit={exit_code})\n")
            self._build_ok = False
            self._finish_build()
            return

        self._build_step += 1

        if self._build_step == 1:
            # cmake 成功 → make
            self._build_output.append("\n$ make -j$(nproc)\n")
            self._build_proc.start("make", ["-j" + str(os.cpu_count() or 4)])
        else:
            # make 成功
            self._build_output.append("\n✅ 编译成功!\n")
            self._finish_build()
            # 刷新详情 (显示二进制路径)
            key = self._current_project
            self._on_select(self._list.currentItem(), None)

    def _finish_build(self):
        self._compile_btn.setEnabled(True)
        self._rebuild_btn.setEnabled(True)
        key = self._current_project
        self._status.setText(f"{'✅' if self._build_ok else '❌'} {'重' if self._build_step==0 else ''}编译{'完成' if self._build_ok else '失败'}: {key}")
        if self._build_ok:
            self._add_history()

    # ── 历史记录 ────────────────────────────────────────
    def _add_history(self):
        if not self._current_project:
            return
        if self._current_project in self._history:
            self._history.remove(self._current_project)
        self._history.insert(0, self._current_project)
        if len(self._history) > 9:
            self._history = self._history[:9]
        self._save_history()
        self._sort_list()

    def _load_history(self):
        if HISTORY_FILE.is_file():
            try:
                with open(HISTORY_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def _save_history(self):
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(self._history, f, indent=2)
        except IOError:
            pass


# ── 入口 ─────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    app.setApplicationName("DDG Exercise Manager")

    # macOS 暗色模式适配
    if sys.platform == "darwin":
        try:
            app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        except AttributeError:
            pass

    window = DDGExerciseManager()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
