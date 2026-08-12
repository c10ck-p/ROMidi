from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from i18n import tr, load_language, get_available_languages, language_changed
from ui.theme import ThemeManager
from ui.widgets import make_card


class SettingsTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_hotkey = ""
        self._saved_lang = "follow_system"
        self._setup_ui()
        self._retranslate()
        language_changed().connect(self._retranslate)

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_content = QWidget()
        sc_layout = QVBoxLayout(scroll_content)
        sc_layout.setContentsMargins(12, 12, 12, 12)
        sc_layout.setSpacing(12)

        # ── Save Path card (full width) ────────────────────────────────
        self._save_card, self._save_content = make_card("")
        self._save_title = QLabel()
        self._save_title.setProperty("role", "section")
        self._save_content.insertWidget(0, self._save_title)

        save_row = QHBoxLayout()
        save_row.setSpacing(8)
        self.save_path_input = QLineEdit()
        self.save_path_input.setReadOnly(True)
        self.save_path_input.setToolTip("")
        self.save_browse_btn = QPushButton()
        self.save_browse_btn.setToolTip("")
        save_row.addWidget(self.save_path_input)
        save_row.addWidget(self.save_browse_btn)
        self._save_content.addLayout(save_row)
        sc_layout.addWidget(self._save_card)

        # ── Two-column body ────────────────────────────────────────────
        body = QHBoxLayout()
        body.setSpacing(12)

        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        # Hotkey card
        self._hk_card, self._hk_content = make_card("")
        self._hk_title = QLabel()
        self._hk_title.setProperty("role", "section")
        self._hk_content.insertWidget(0, self._hk_title)

        hk_row = QHBoxLayout()
        hk_row.setSpacing(8)
        self._hk_label = QLabel()
        self.hk_btn = QPushButton()
        self.hk_btn.setToolTip("")
        hk_row.addWidget(self._hk_label, 1)
        hk_row.addWidget(self.hk_btn)
        self._hk_content.addLayout(hk_row)
        left_col.addWidget(self._hk_card)

        # Overlay card
        self._ov_card, self._ov_content = make_card("")
        self._ov_title = QLabel()
        self._ov_title.setProperty("role", "section")
        self._ov_content.insertWidget(0, self._ov_title)

        ov_grid = QGridLayout()
        ov_grid.setSpacing(8)
        self._always_top_check = QCheckBox()
        self._always_top_check.setToolTip("")
        self._opacity_label = QLabel()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setToolTip("")
        ov_grid.addWidget(self._always_top_check, 0, 0, 1, 2)
        ov_grid.addWidget(self._opacity_label, 1, 0)
        ov_grid.addWidget(self.opacity_slider, 1, 1)
        self._ov_content.addLayout(ov_grid)
        left_col.addWidget(self._ov_card)

        self._check_update_btn = QPushButton()
        self._check_update_btn.setToolTip("")
        left_col.addWidget(self._check_update_btn)
        left_col.addStretch()

        # Visualizer card
        self._vis_card, self._vis_content = make_card("")
        self._vis_title = QLabel()
        self._vis_title.setProperty("role", "section")
        self._vis_content.insertWidget(0, self._vis_title)

        self._timeline_vis_check = QCheckBox()
        self._timeline_vis_check.setChecked(True)
        self._timeline_vis_check.setToolTip("")
        self._piano_vis_check = QCheckBox()
        self._piano_vis_check.setChecked(True)
        self._piano_vis_check.setToolTip("")
        self._vis_content.addWidget(self._timeline_vis_check)
        self._vis_content.addWidget(self._piano_vis_check)
        right_col.addWidget(self._vis_card)

        # AI Model card (hidden — feature under development)
        self._ai_card, self._ai_content = make_card("")
        self._ai_title = QLabel()
        self._ai_title.setProperty("role", "section")
        self._ai_content.insertWidget(0, self._ai_title)

        self._use_ai_pedal_check = QCheckBox()
        self._use_ai_pedal_check.setChecked(False)
        self._use_ai_pedal_check.setEnabled(False)
        self._use_ai_pedal_check.setToolTip("")
        self._ai_wip_label = QLabel()
        self._ai_wip_label.setEnabled(False)
        self._ai_content.addWidget(self._use_ai_pedal_check)
        self._ai_content.addWidget(self._ai_wip_label)
        self._ai_card.setVisible(False)

        # Theme card
        self._theme_card, self._theme_content = make_card("")
        self._theme_title = QLabel()
        self._theme_title.setProperty("role", "section")
        self._theme_content.insertWidget(0, self._theme_title)

        theme_row = QHBoxLayout()
        theme_row.setSpacing(8)
        self.theme_combo = QComboBox()
        self.theme_combo.setToolTip("")
        self._populate_theme_combo()
        self._theme_customize_btn = QPushButton()
        self._theme_customize_btn.setToolTip("")
        theme_row.addWidget(self.theme_combo, 1)
        theme_row.addWidget(self._theme_customize_btn)
        self._theme_content.addLayout(theme_row)
        right_col.addWidget(self._theme_card)

        # Language card
        self._lang_card, self._lang_content = make_card("")
        self._lang_title = QLabel()
        self._lang_title.setProperty("role", "section")
        self._lang_content.insertWidget(0, self._lang_title)

        lang_row = QHBoxLayout()
        lang_row.setSpacing(8)
        self.lang_combo = QComboBox()
        self._populate_lang_combo()
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_row.addWidget(self.lang_combo, 1)
        self._lang_content.addLayout(lang_row)
        right_col.addWidget(self._lang_card)

        right_col.addStretch()

        body.addLayout(left_col, 1)
        body.addLayout(right_col, 1)
        sc_layout.addLayout(body)

        scroll.setWidget(scroll_content)
        outer.addWidget(scroll)

    def _populate_theme_combo(self) -> None:
        active = ThemeManager.get_active_name()
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        for name in ThemeManager.all_themes():
            self.theme_combo.addItem(tr(name), name)
        idx = self.theme_combo.findData(active)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.blockSignals(False)

    def _populate_lang_combo(self) -> None:
        self.lang_combo.blockSignals(True)
        self.lang_combo.clear()
        for code, name in get_available_languages():
            self.lang_combo.addItem(name, code)
        current = self._saved_lang or 'follow_system'
        idx = self.lang_combo.findData(current)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        elif current == 'follow_system':
            self.lang_combo.setCurrentIndex(0)
        self.lang_combo.blockSignals(False)

    def _on_language_changed(self, index: int) -> None:
        code = self.lang_combo.itemData(index)
        self._saved_lang = code
        if code == 'follow_system':
            load_language('follow_system')
            self._retranslate_combo_labels()
        else:
            load_language(code)

    def _retranslate_combo_labels(self) -> None:
        self.lang_combo.blockSignals(True)
        current_data = self.lang_combo.currentData()
        self.lang_combo.clear()
        for code, name in get_available_languages():
            self.lang_combo.addItem(name, code)
        idx = self.lang_combo.findData(current_data)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        elif current_data is None:
            self.lang_combo.setCurrentIndex(0)
        self.lang_combo.blockSignals(False)

    def _retranslate(self, lang_code: str = "") -> None:
        self._retranslate_combo_labels()
        self._save_title.setText(tr("Save Path"))
        self.save_path_input.setToolTip(tr("Directory where humanized performance saves are stored"))
        self.save_browse_btn.setText(tr("Browse"))
        self.save_browse_btn.setToolTip(tr("Choose where to save humanized performance files"))

        self._hk_title.setText(tr("Hotkey"))
        self._refresh_hotkey_label()
        self.hk_btn.setText(tr("Change"))
        self.hk_btn.setToolTip(tr("Click to bind a new hotkey for toggling playback"))

        self._ov_title.setText(tr("Overlay"))
        self._always_top_check.setText(tr("Always on Top"))
        self._always_top_check.setToolTip(tr("Keep this window above all other windows"))
        self._opacity_label.setText(tr("Opacity"))
        self.opacity_slider.setToolTip(tr("Adjust window transparency (20-100%)"))

        self._check_update_btn.setText(tr("Check for updates"))
        self._check_update_btn.setToolTip(tr("Check GitHub for a newer version of ROMidi"))

        self._vis_title.setText(tr("Visualizer"))
        self._timeline_vis_check.setText(tr("Timeline"))
        self._timeline_vis_check.setToolTip(
            tr("Show the piano-roll timeline in the Visualizer tab "
               "(disable for a simple seek slider)"))
        self._piano_vis_check.setText(tr("Piano Keys"))
        self._piano_vis_check.setToolTip(tr("Show the piano key visualizer in the Visualizer tab"))

        self._ai_title.setText(tr("AI Model"))
        self._use_ai_pedal_check.setText(tr("Enable AI Pedal"))
        self._use_ai_pedal_check.setToolTip(tr("Sorry, still in development!"))
        self._ai_wip_label.setText(tr("Sorry, still in development!"))

        self._theme_title.setText(tr("Theme"))
        self.theme_combo.setToolTip(tr("Switch the application colour theme"))
        self._theme_customize_btn.setText(tr("Customize..."))
        self._theme_customize_btn.setToolTip(
            tr("Open the theme editor to create or modify colour presets"))

        self._populate_theme_combo()

        self._lang_title.setText(tr("Language"))

    def _refresh_hotkey_label(self) -> None:
        key_str = self._current_hotkey or ""
        if key_str:
            self._hk_label.setText(tr("Hotkey: %1").arg(key_str))
        else:
            self._hk_label.setText(tr("Hotkey: "))

    # ── Public API ─────────────────────────────────────────────────────

    def refresh_theme_combo(self) -> None:
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        self._populate_theme_combo()
        self.theme_combo.blockSignals(False)

    def load_config(self, config: dict, save_dir: str) -> None:
        self._use_ai_pedal_check.setChecked(config.get('use_ai_pedal', False))
        self._always_top_check.setChecked(config.get('always_on_top', False))
        self.opacity_slider.setValue(config.get('opacity', 100))
        self._timeline_vis_check.setChecked(config.get('show_timeline_visualizer', True))
        self._piano_vis_check.setChecked(config.get('show_piano_visualizer', True))
        self.save_path_input.setText(save_dir)
        saved_lang = config.get('language', 'follow_system')
        self._saved_lang = saved_lang
        load_language(saved_lang)
        self._retranslate_combo_labels()
        idx = self.lang_combo.findData(saved_lang)
        if idx >= 0:
            self.lang_combo.blockSignals(True)
            self.lang_combo.setCurrentIndex(idx)
            self.lang_combo.blockSignals(False)

    def gather_config(self) -> dict:
        return {
            'use_ai_pedal':              self._use_ai_pedal_check.isChecked(),
            'always_on_top':             self._always_top_check.isChecked(),
            'opacity':                   self.opacity_slider.value(),
            'show_timeline_visualizer':  self._timeline_vis_check.isChecked(),
            'show_piano_visualizer':     self._piano_vis_check.isChecked(),
            'language':                  self._saved_lang or 'follow_system',
        }

    def set_hotkey_label(self, key_str: str) -> None:
        self._current_hotkey = key_str
        self._refresh_hotkey_label()

    # ── Compatibility shims (old attribute names) ──────────────────────

    @property
    def timeline_vis_check(self):
        return self._timeline_vis_check

    @property
    def piano_vis_check(self):
        return self._piano_vis_check

    @property
    def use_ai_pedal_check(self):
        return self._use_ai_pedal_check

    @property
    def always_top_check(self):
        return self._always_top_check

    @property
    def theme_customize_btn(self):
        return self._theme_customize_btn

    @property
    def hk_label(self):
        return self._hk_label

    @property
    def check_update_btn(self):
        return self._check_update_btn