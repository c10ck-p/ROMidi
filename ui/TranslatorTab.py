from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from i18n import tr, language_changed
from core.translator import FormatRegistry


class TranslatorTab(QWidget):
    play_sheet_requested = Signal(str, str, int, bool)
    export_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._retranslate()
        language_changed().connect(self._retranslate)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        fmt_row = QHBoxLayout()
        self._fmt_label = QLabel()
        self._fmt_label.setProperty("role", "section")
        self.format_combo = QComboBox()
        self.format_combo.addItems(FormatRegistry.names())
        self.format_combo.setToolTip("")
        fmt_row.addWidget(self._fmt_label)
        fmt_row.addWidget(self.format_combo, 1)
        layout.addLayout(fmt_row)

        self.sub_tabs = QTabWidget()
        self._import_tab_widget = self._build_import_tab()
        self._export_tab_widget = self._build_export_tab()
        self.sub_tabs.addTab(self._import_tab_widget, "")
        self.sub_tabs.addTab(self._export_tab_widget, "")
        layout.addWidget(self.sub_tabs)

    # ── Import tab ────────────────────────────────────────────────────

    def _build_import_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._import_hint = QLabel()
        self._import_hint.setProperty("role", "muted")
        layout.addWidget(self._import_hint)

        self.import_text = QTextEdit()
        self.import_text.setFont(QFont("Courier New", 9))
        self.import_text.setPlaceholderText(
            "e.g.\ne e e [6t] e\ne y 9 y t [wy] t\ne w [6e] e e t"
        )
        layout.addWidget(self.import_text)

        options_row = QHBoxLayout()
        options_row.setSpacing(12)
        self._bpm_label = QLabel()
        self._bpm_label.setProperty("role", "muted")
        self.bpm_spinbox = QSpinBox()
        self.bpm_spinbox.setRange(20, 400)
        self.bpm_spinbox.setValue(120)
        self.bpm_spinbox.setFixedWidth(70)
        self.bpm_spinbox.setToolTip("")
        self._humanize_check = QCheckBox()
        self._humanize_check.setToolTip("")
        options_row.addWidget(self._bpm_label)
        options_row.addWidget(self.bpm_spinbox)
        options_row.addWidget(self._humanize_check)
        options_row.addStretch()
        layout.addLayout(options_row)

        self._import_play_btn = QPushButton()
        self._import_play_btn.setToolTip("")
        self._import_play_btn.clicked.connect(self._on_play_clicked)
        layout.addWidget(self._import_play_btn)

        return tab

    # ── Export tab ────────────────────────────────────────────────────

    def _build_export_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._export_status_label = QLabel()
        self._export_status_label.setProperty("role", "muted")
        self._export_status_label.setStyleSheet("font-style: italic;")
        layout.addWidget(self._export_status_label)

        self._export_generate_btn = QPushButton()
        self._export_generate_btn.setToolTip("")
        self._export_generate_btn.clicked.connect(self._on_export_clicked)
        layout.addWidget(self._export_generate_btn)

        sep = QFrame()
        sep.setObjectName("h_sep")
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        self._out_label = QLabel()
        self._out_label.setProperty("role", "muted")
        layout.addWidget(self._out_label)

        self.export_text = QTextEdit()
        self.export_text.setReadOnly(True)
        self.export_text.setFont(QFont("Courier New", 9))
        self.export_text.setPlaceholderText("")
        layout.addWidget(self.export_text)

        self._copy_btn = QPushButton()
        self._copy_btn.setToolTip("")
        self._copy_btn.clicked.connect(self._on_copy_clicked)
        layout.addWidget(self._copy_btn)

        return tab

    def _retranslate(self, lang_code: str = "") -> None:
        self._fmt_label.setText(tr("Format"))
        self.format_combo.setToolTip(tr("Select the Roblox piano sheet format"))
        self.sub_tabs.setTabText(0, tr("Import"))
        self.sub_tabs.setTabText(1, tr("Export"))

        self._import_hint.setText(tr("Paste sheet text:"))
        self._bpm_label.setText(tr("BPM"))
        self.bpm_spinbox.setToolTip(tr("Tempo used to calculate note durations from the sheet"))
        self._humanize_check.setText(tr("Humanize"))
        self._humanize_check.setToolTip(
            tr("Apply current humanization settings during playback.\n"
               "When unchecked, the sheet plays back exactly as written."))
        self._import_play_btn.setText(tr("▶  Play Sheet"))
        self._import_play_btn.setToolTip(
            tr("Convert the pasted sheet to keystrokes and begin playback"))

        self._export_status_label.setText(
            tr("Load a MIDI file on the Playback tab, then click Generate."))
        self._export_generate_btn.setText(tr("Generate Sheet"))
        self._export_generate_btn.setToolTip(
            tr("Convert the currently loaded MIDI notes to sheet text in the selected format"))
        self._out_label.setText(tr("Output"))
        self.export_text.setPlaceholderText(tr("Generated sheet will appear here..."))
        self._copy_btn.setText(tr("Copy to Clipboard"))
        self._copy_btn.setToolTip(tr("Copy the generated sheet to the clipboard"))

    # ── Slots ─────────────────────────────────────────────────────────

    def _on_play_clicked(self):
        text = self.import_text.toPlainText().strip()
        if not text:
            return
        self.play_sheet_requested.emit(
            text,
            self.format_combo.currentText(),
            self.bpm_spinbox.value(),
            self._humanize_check.isChecked(),
        )

    def _on_export_clicked(self):
        self.export_requested.emit(self.format_combo.currentText())

    def _on_copy_clicked(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.export_text.toPlainText())

    # ── Public API ────────────────────────────────────────────────────

    def set_export_text(self, text: str):
        self.export_text.setPlainText(text)
        note_count = sum(
            1 for line in text.splitlines() if line.strip() and not line.startswith('#')
        )
        self._export_status_label.setText(
            tr("Generated %1 line(s).").arg(note_count)
        )
        self._export_status_label.setStyleSheet("")
        self._export_status_label.setProperty("role", "success")
        self._export_status_label.style().unpolish(self._export_status_label)
        self._export_status_label.style().polish(self._export_status_label)

    def humanize_check(self):
        return self._humanize_check.isChecked()