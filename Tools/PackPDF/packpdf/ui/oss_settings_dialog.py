"""图床 OSS 密钥设置对话框。"""

from __future__ import annotations

import os

from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from packpdf.config import AppConfig, save_config


class OssSettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None, cfg: AppConfig) -> None:
        super().__init__(parent)
        self.setWindowTitle('图床设置')
        self.setMinimumWidth(480)
        self._cfg = cfg

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        layout.addWidget(
            QLabel('阿里云 OSS AccessKey，用于上传 imgs/ 图片并替换 Markdown 中的本地路径。')
        )

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
    """从配置或环境变量读取 OSS 密钥。"""
    ak = (cfg.oss_access_key_id or os.environ.get('OSS_ACCESS_KEY_ID', '')).strip()
    sk = (cfg.oss_access_key_secret or os.environ.get('OSS_ACCESS_KEY_SECRET', '')).strip()
    return ak, sk
