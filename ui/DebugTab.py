from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from i18n import tr, language_changed


class DebugTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._retranslate()
        language_changed().connect(self._retranslate)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Courier New", 9))
        layout.addWidget(self.log_output)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        self._log_clear_btn = QPushButton()
        self._log_clear_btn.setToolTip("")
        self._log_copy_btn = QPushButton()
        self._log_copy_btn.setToolTip("")
        self._log_clear_btn.clicked.connect(self.log_output.clear)
        self._log_copy_btn.clicked.connect(self._copy_to_clipboard)
        btn_row.addWidget(self._log_clear_btn)
        btn_row.addWidget(self._log_copy_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _retranslate(self, lang_code: str = "") -> None:
        self._log_clear_btn.setText(tr("Clear"))
        self._log_clear_btn.setToolTip(tr("Clear all log entries"))
        self._log_copy_btn.setText(tr("Copy Log"))
        self._log_copy_btn.setToolTip(tr("Copy the full log to clipboard"))

    def _copy_to_clipboard(self) -> None:
        QApplication.clipboard().setText(self.log_output.toPlainText())