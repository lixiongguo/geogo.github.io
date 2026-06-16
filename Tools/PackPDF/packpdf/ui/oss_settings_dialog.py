"""图床 OSS 密钥设置对话框。"""

from __future__ import annotations

import csv
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from packpdf.config import AppConfig, save_config

# AccessKey.csv 路径（与 oss_upload.sh 一致）
_CSV_PATH = Path(__file__).resolve().parent.parent.parent / 'docs' / 'AccessKey.csv'


def _read_oss_keys_from_csv() -> tuple[str, str]:
    """从 docs/AccessKey.csv 读取 OSS 密钥。返回 (ak, sk) 或 ('', '')。"""
    if not _CSV_PATH.exists():
        return '', ''
    try:
        with open(_CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) >= 2 and len(rows[1]) >= 2:
                return rows[1][0].strip(), rows[1][1].strip()
    except Exception:
        pass
    return '', ''


class OssSettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None, cfg: AppConfig) -> None:
        super().__init__(parent)
        self.setWindowTitle('图床设置')
        self.setMinimumWidth(520)
        self._cfg = cfg

        csv_ak, csv_sk = _read_oss_keys_from_csv()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        layout.addWidget(
            QLabel('阿里云 OSS AccessKey，用于上传 imgs/ 图片并替换 Markdown 中的本地路径。')
        )

        if csv_ak and csv_sk:
            self._csv_label = QLabel(
                f'✅ 已从 docs/AccessKey.csv 检测到密钥，可直接使用。'
            )
            self._csv_label.setStyleSheet('color: #4caf50;')
            layout.addWidget(self._csv_label)

            csv_row = QHBoxLayout()
            self._btn_load_csv = QPushButton('从 CSV 填入')
            self._btn_load_csv.clicked.connect(lambda: self._fill_from_csv(csv_ak, csv_sk))
            csv_row.addWidget(self._btn_load_csv)
            csv_row.addStretch()
            layout.addLayout(csv_row)
        else:
            self._csv_label = QLabel('')
            layout.addWidget(self._csv_label)

        form = QFormLayout()
        self._ent_ak = QLineEdit(
            cfg.oss_access_key_id or os.environ.get('OSS_ACCESS_KEY_ID', '')
        )
        form.addRow('AccessKey ID', self._ent_ak)

        self._ent_sk = QLineEdit(
            cfg.oss_access_key_secret or os.environ.get('OSS_ACCESS_KEY_SECRET', '')
        )
        self._ent_sk.setEchoMode(QLineEdit.Password)
        form.addRow('AccessKey Secret', self._ent_sk)
        layout.addLayout(form)

        self._cb_remember = QCheckBox('记住密钥到本地 config.json（勿提交 git）')
        self._cb_remember.setChecked(cfg.remember_oss_keys)
        layout.addWidget(self._cb_remember)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(buttons)
        layout.addLayout(row)

    def _fill_from_csv(self, ak: str, sk: str) -> None:
        self._ent_ak.setText(ak)
        self._ent_sk.setText(sk)

    def _on_accept(self) -> None:
        self._cfg.remember_oss_keys = self._cb_remember.isChecked()
        self._cfg.oss_access_key_id = self._ent_ak.text().strip()
        self._cfg.oss_access_key_secret = self._ent_sk.text().strip()
        save_config(self._cfg)
        self.accept()


def show_oss_settings(parent: QWidget | None, cfg: AppConfig) -> bool:
    dlg = OssSettingsDialog(parent, cfg)
    return dlg.exec_() == QDialog.Accepted


def oss_credentials(cfg: AppConfig) -> tuple[str, str]:
    """从配置 → 环境变量 → docs/AccessKey.csv 依次读取 OSS 密钥。"""
    ak = (cfg.oss_access_key_id or os.environ.get('OSS_ACCESS_KEY_ID', '')).strip()
    sk = (cfg.oss_access_key_secret or os.environ.get('OSS_ACCESS_KEY_SECRET', '')).strip()
    if not ak or not sk:
        ak, sk = _read_oss_keys_from_csv()
    return ak, sk
