from PyQt6.QtCore import QObject, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from i18n import tr, language_changed
from ui.DebugTab import DebugTab
from ui.LicenseTab import LicenseTab
from ui.PlaybackTab import PlaybackTab
from ui.SettingsTab import SettingsTab
from ui.theme import ThemeManager, generate_stylesheet
from ui.TranslatorTab import TranslatorTab
from ui.VisualizerTab import VisualizerTab
from ui.widgets import NavButton


def _make_mdl2_icon(glyph: str, color: QColor, pixel_size: int = 14) -> QIcon:
    pix = QPixmap(pixel_size, pixel_size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    f = QFont("Segoe MDL2 Assets")
    f.setPixelSize(pixel_size)
    p.setFont(f)
    p.setPen(color)
    p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, glyph)
    p.end()
    return QIcon(pix)


class ElidingLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._full_text = text
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        if text:
            self._update_elided()

    def setText(self, text):
        self._full_text = text
        self._update_elided()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elided()

    def _update_elided(self):
        width = self.contentsRect().width()
        if width <= 0:
            return
        elided = self.fontMetrics().elidedText(
            self._full_text, Qt.TextElideMode.ElideRight, width
        )
        super().setText(elided)


class MainWindowUI(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        self._retranslate()
        language_changed().connect(self._retranslate)

    def setup_ui(self):
        main_widget = QWidget()
        main_widget.setObjectName("main_widget")
        self.main_window.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._is_collapsed = False

        # ── Collapsed mini strip ───────────────────────────────────────
        self._collapsed_strip = QFrame()
        self._collapsed_strip.setObjectName("collapsed_strip")
        self._collapsed_strip.setVisible(False)
        cs_layout = QVBoxLayout(self._collapsed_strip)
        cs_layout.setContentsMargins(12, 6, 12, 6)
        cs_layout.setSpacing(4)

        self._collapsed_file_label = ElidingLabel("")
        self._collapsed_file_label.setObjectName("file_path_label")
        cs_layout.addWidget(self._collapsed_file_label)

        self._collapsed_humanize_check = QCheckBox()
        self._collapsed_humanize_check.setToolTip("")
        cs_layout.addWidget(self._collapsed_humanize_check)

        self._collapsed_load_btn = QPushButton("")
        self._collapsed_load_btn.setObjectName("cs_load_btn")
        self._collapsed_load_btn.setIconSize(QSize(16, 16))
        self._collapsed_load_btn.setToolTip("")
        self._collapsed_load_saved_btn = QPushButton("")
        self._collapsed_load_saved_btn.setObjectName("cs_load_saved_btn")
        self._collapsed_load_saved_btn.setIconSize(QSize(16, 16))
        self._collapsed_load_saved_btn.setToolTip("")

        self._collapsed_save_btn = QPushButton("\uE74E")
        self._collapsed_save_btn.setObjectName("cs_save_btn")
        self._collapsed_save_btn.setToolTip("")
        self._collapsed_save_btn.setEnabled(False)

        cs_row3 = QHBoxLayout()
        cs_row3.setSpacing(5)
        cs_row3.addWidget(self._collapsed_load_btn, 1)
        cs_row3.addWidget(self._collapsed_load_saved_btn, 1)
        cs_layout.addLayout(cs_row3)

        self._cs_scrubber_row = QWidget()
        self._cs_scrubber_layout = QVBoxLayout(self._cs_scrubber_row)
        self._cs_scrubber_layout.setContentsMargins(0, 0, 0, 0)
        self._cs_scrubber_layout.setSpacing(2)
        cs_layout.addWidget(self._cs_scrubber_row)

        self._cs_playback_row = QWidget()
        self._cs_playback_layout = QHBoxLayout(self._cs_playback_row)
        self._cs_playback_layout.setContentsMargins(0, 0, 0, 0)
        self._cs_playback_layout.setSpacing(5)
        cs_layout.addWidget(self._cs_playback_row)

        self._cs_expand_row = QWidget()
        self._cs_expand_layout = QHBoxLayout(self._cs_expand_row)
        self._cs_expand_layout.setContentsMargins(0, 0, 0, 0)
        self._cs_expand_layout.setSpacing(0)
        cs_layout.addWidget(self._cs_expand_row)

        self._cs_layout = cs_layout
        main_layout.addWidget(self._collapsed_strip)

        # ── Body: sidebar + page stack ─────────────────────────────────
        self._body = QWidget()
        body_layout = QHBoxLayout(self._body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(120)
        sidebar.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        sidebar_vbox = QVBoxLayout(sidebar)
        sidebar_vbox.setContentsMargins(0, 0, 0, 0)
        sidebar_vbox.setSpacing(0)

        self.tabs = QStackedWidget()
        self.tabs.currentChanged.connect(self._on_page_changed)

        _NAV_ITEMS = [
            ("\uE768", "Playback"),
            ("\uE8D6", "Visualizer"),
            ("\uE8B1", "Translator"),
            ("\uE713", "Settings"),
            ("\uEBE8", "Debug"),
            ("\uE946", "License"),
        ]
        self._nav_btns: list[NavButton] = []
        for i, (icon, label) in enumerate(_NAV_ITEMS):
            btn = NavButton(icon, "")
            btn.clicked.connect(lambda idx=i: self._switch_page(idx))
            sidebar_vbox.addWidget(btn)
            self._nav_btns.append(btn)

        sidebar_vbox.addStretch()
        body_layout.addWidget(sidebar)
        body_layout.addWidget(self.tabs, 1)
        main_layout.addWidget(self._body, 1)

        # ── Pages ──────────────────────────────────────────────────────
        self.playback_tab   = PlaybackTab()
        self.visualizer_tab = VisualizerTab()
        self.translator_tab = TranslatorTab()
        self.settings_tab   = SettingsTab()
        self.debug_tab      = DebugTab()
        self.license_tab    = LicenseTab()

        self.tabs.addWidget(self.playback_tab)    # 0
        self.tabs.addWidget(self.visualizer_tab)  # 1
        self.tabs.addWidget(self.translator_tab)  # 2
        self.tabs.addWidget(self.settings_tab)    # 3
        self.tabs.addWidget(self.debug_tab)       # 4
        self.tabs.addWidget(self.license_tab)     # 5

        # ── Convenience aliases ────────────────────────────────────────
        self.log_output      = self.debug_tab.log_output
        self.timeline_widget = self.visualizer_tab.timeline_widget
        self.piano_widget    = self.visualizer_tab.piano_widget
        self.scroll_area     = self.visualizer_tab.scroll_area

        # ── Transport bar ─────────────────────────────────────────────
        transport_bar = QFrame()
        transport_bar.setObjectName("transport_bar")
        transport_layout = QVBoxLayout(transport_bar)
        transport_layout.setContentsMargins(16, 10, 16, 10)
        transport_layout.setSpacing(6)

        self.scrubber_slider = QSlider(Qt.Orientation.Horizontal)
        self.scrubber_slider.setObjectName("scrubber_slider")
        self.scrubber_slider.setRange(0, 10000)
        self.scrubber_slider.sliderPressed.connect(self._on_scrubber_pressed)
        self.scrubber_slider.sliderMoved.connect(self._on_scrubber_moved)
        self.scrubber_slider.sliderReleased.connect(self._on_scrubber_released)
        self._scrubber_dragging = False
        transport_layout.addWidget(self.scrubber_slider)

        self._btn_row_widget = QWidget()
        btn_row = QHBoxLayout(self._btn_row_widget)
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(5)

        self._play_button = QPushButton()
        self._play_button.setObjectName("play_button")
        self._play_button.setToolTip("")

        self._stop_button = QPushButton()
        self._stop_button.setObjectName("stop_button")
        self._stop_button.setToolTip("")

        self._preview_button = QPushButton()
        self._preview_button.setObjectName("preview_button")
        self._preview_button.setToolTip("")

        self._time_label = QLabel()
        self._time_label.setObjectName("time_label")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._save_button = QPushButton()
        self._save_button.setObjectName("save_button")
        self._save_button.setToolTip("")

        self._reset_button = QPushButton()
        self._reset_button.setObjectName("reset_button")
        self._reset_button.setToolTip("")

        btn_row.addWidget(self._play_button)
        btn_row.addWidget(self._stop_button)
        btn_row.addWidget(self._preview_button)
        btn_row.addStretch()
        btn_row.addWidget(self._time_label)
        btn_row.addStretch()
        btn_row.addWidget(self._save_button)
        btn_row.addWidget(self._reset_button)

        self._collapse_btn = QPushButton()
        self._collapse_btn.setObjectName("collapse_btn")
        self._collapse_btn.setToolTip("")
        self._collapse_btn.clicked.connect(self._toggle_collapsed)
        btn_row.addWidget(self._collapse_btn)

        transport_layout.addWidget(self._btn_row_widget)
        main_layout.addWidget(transport_bar)
        self._transport_bar = transport_bar
        self._transport_layout = transport_layout

        self._play_button.setEnabled(False)
        self._stop_button.setEnabled(False)
        self._preview_button.setEnabled(False)
        self._save_button.setEnabled(False)
        self.scrubber_slider.setEnabled(False)

        # ── Cross-cutting connections ──────────────────────────────────
        self.settings_tab.timeline_vis_check.toggled.connect(self._on_timeline_toggle)
        self.settings_tab.piano_vis_check.toggled.connect(self._on_piano_toggle)
        self.settings_tab.theme_combo.currentIndexChanged.connect(self._on_theme_index_changed)
        self.settings_tab.theme_customize_btn.clicked.connect(self._open_theme_dialog)

        self._collapsed_humanize_check.toggled.connect(self._on_collapsed_humanize_toggled)
        self.playback_tab.select_all_humanization_check.toggled.connect(
            self._sync_collapsed_humanize
        )

        self._switch_page(0)
        self.apply_theme(ThemeManager.get_active_name())

    # ── ReTranslation ─────────────────────────────────────────────────

    def _retranslate(self, lang_code: str = "") -> None:
        self._collapsed_file_label.setText(tr("No file selected."))
        self._collapsed_humanize_check.setText(tr("Humanize"))
        self._collapsed_humanize_check.setToolTip(
            tr("Enable or disable all humanization at once"))
        self._collapsed_load_btn.setToolTip(tr("Open a MIDI file for playback"))
        self._collapsed_load_saved_btn.setToolTip(tr("Load a saved playback"))
        self._collapsed_save_btn.setToolTip(tr("Save the current playback"))

        nav_labels = [
            tr("Playback"),
            tr("Visualizer"),
            tr("Translator"),
            tr("Settings"),
            tr("Debug"),
            tr("License"),
        ]
        for btn, label in zip(self._nav_btns, nav_labels):
            btn._text_lbl.setText(label)

        self._play_button.setText(tr("▶  Play"))
        self._play_button.setToolTip(tr("Start, pause, or resume playback"))
        self._stop_button.setText(tr("■  Stop"))
        self._stop_button.setToolTip(tr("Stop playback and reset to the beginning"))
        self._preview_button.setText(tr("🔊  Preview"))
        self._preview_button.setToolTip(tr("Audition the loaded MIDI file with the system synthesizer"))
        self._time_label.setText(tr("00:00 / 00:00"))
        self._save_button.setText(tr("Save"))
        self._save_button.setToolTip(
            tr("Save the current humanized performance to a file for later replay"))
        self._reset_button.setText(tr("Reset"))
        self._reset_button.setToolTip(tr("Reset all settings to their default values"))
        self._collapse_btn.setText(tr("▲  Collapse"))
        self._collapse_btn.setToolTip(tr("Collapse to mini mode"))

        if self._is_collapsed:
            self._collapse_btn.setText(tr("▼  Expand"))
            self._collapse_btn.setToolTip(tr("Restore full window"))
        else:
            self._collapse_btn.setText(tr("▲  Collapse"))
            self._collapse_btn.setToolTip(tr("Collapse to mini mode"))

    # ── Navigation ─────────────────────────────────────────────────────

    def _switch_page(self, index: int) -> None:
        self.tabs.setCurrentIndex(index)

    def _on_page_changed(self, index: int) -> None:
        for i, btn in enumerate(self._nav_btns):
            btn.set_active(i == index)

    # ── Theme ──────────────────────────────────────────────────────────

    def _on_theme_index_changed(self, index: int) -> None:
        name = self.settings_tab.theme_combo.itemData(index)
        if name:
            self.apply_theme(name)

    def apply_theme(self, name: str) -> None:
        themes = ThemeManager.all_themes()
        theme = themes.get(name)
        if theme is None:
            return
        ThemeManager.set_active_name(name)
        self.main_window.setStyleSheet(generate_stylesheet(theme))
        self.main_window._apply_title_bar_theme(theme)
        _c = QColor(theme.text_primary)
        _px = self._collapsed_load_btn.fontMetrics().height()
        self._collapsed_load_btn.setIconSize(QSize(_px, _px))
        self._collapsed_load_btn.setIcon(_make_mdl2_icon("\uE8D6", _c, _px))
        self._collapsed_load_saved_btn.setIconSize(QSize(_px, _px))
        self._collapsed_load_saved_btn.setIcon(_make_mdl2_icon("\uEC50", _c, _px))
        self.timeline_widget.left_hand_color.setNamedColor(theme.accent)
        self.timeline_widget.left_hand_color.setAlpha(210)
        self.timeline_widget.right_hand_color.setNamedColor(theme.accent_play)
        self.timeline_widget.right_hand_color.setAlpha(210)
        self.timeline_widget.bg_color.setNamedColor(theme.bg_primary)
        pedal_q = QColor(theme.pedal_color)
        pedal_q.setAlpha(180)
        self.timeline_widget.pedal_color = pedal_q
        self.timeline_widget.cached_background = None
        self.timeline_widget.update()
        piano_pedal_q = QColor(theme.pedal_color)
        self.piano_widget.pedal_color = piano_pedal_q
        self.piano_widget.update()

    def _open_theme_dialog(self) -> None:
        from ui.ThemeDialog import ThemeDialog
        dlg = ThemeDialog(self.main_window, self.main_window)
        dlg.theme_applied.connect(self._on_theme_dialog_accepted)
        dlg.exec()

    def _on_theme_dialog_accepted(self, name: str) -> None:
        self.settings_tab.refresh_theme_combo()
        self.apply_theme(name)

    # ── Visualizer helpers ─────────────────────────────────────────────

    def _on_timeline_toggle(self, checked: bool) -> None:
        self.scroll_area.setVisible(checked)
        self._update_visualizer_availability()

    def _on_piano_toggle(self, checked: bool) -> None:
        self.piano_widget.setVisible(checked)
        self.timeline_widget.set_show_pedal(checked)
        self._update_visualizer_availability()

    def _update_visualizer_availability(self) -> None:
        both_off = (not self.settings_tab.timeline_vis_check.isChecked() and
                    not self.settings_tab.piano_vis_check.isChecked())
        self._nav_btns[1].setEnabled(not both_off)
        if both_off and self.tabs.currentIndex() == 1:
            self._switch_page(0)

    def update_progress(self, current_time, total_duration):
        if self.scroll_area.isVisible() and not self.timeline_widget.is_dragging:
            self.timeline_widget.set_position(current_time)
            if total_duration > 0:
                ratio = current_time / total_duration
                cursor_x = ratio * self.timeline_widget.width()
                target_scroll = cursor_x - (self.scroll_area.width() / 2)
                self.scroll_area.horizontalScrollBar().setValue(int(target_scroll))

        if not self._scrubber_dragging and not self.timeline_widget.is_dragging:
            self.scrubber_slider.blockSignals(True)
            if total_duration > 0:
                self.scrubber_slider.setValue(int(current_time / total_duration * 10000))
            self.scrubber_slider.blockSignals(False)

        self.update_time_label(current_time, total_duration)

    def reset_timeline_position(self) -> None:
        self.timeline_widget.current_time = 0.0
        self.scrubber_slider.blockSignals(True)
        self.scrubber_slider.setValue(0)
        self.scrubber_slider.blockSignals(False)

    def update_time_label(self, current, total) -> None:
        def fmt(s):
            m, sec = int(s // 60), int(s % 60)
            return f"{m:02d}:{sec:02d}"
        self._time_label.setText(f"{fmt(current)} / {fmt(total)}")

    # ── Scrubber ───────────────────────────────────────────────────────

    def _on_scrubber_pressed(self):
        self._scrubber_dragging = True

    def _on_scrubber_moved(self, value):
        if self.timeline_widget.total_duration > 0:
            t = (value / 10000.0) * self.timeline_widget.total_duration
            self.timeline_widget.current_time = t
            self.timeline_widget.scrub_position_changed.emit(t)
            self.update_time_label(t, self.timeline_widget.total_duration)

    def _on_scrubber_released(self):
        self._scrubber_dragging = False
        self.timeline_widget.seek_requested.emit(self.timeline_widget.current_time)

    # ── Collapse ───────────────────────────────────────────────────────

    def _toggle_collapsed(self) -> None:
        self._is_collapsed = not self._is_collapsed
        if self._is_collapsed:
            self._expanded_size = self.main_window.size()
            self._body.setVisible(False)
            self._collapsed_strip.setVisible(True)
            self._collapse_btn.setText(tr("▼  Expand"))
            self._collapse_btn.setToolTip(tr("Restore full window"))
            self._collapse_btn.setMinimumWidth(0)
            self._collapse_btn.setMaximumWidth(16777215)
            self._collapse_btn.setProperty("strip_mode", True)
            self._collapse_btn.style().unpolish(self._collapse_btn)
            self._collapse_btn.style().polish(self._collapse_btn)
            self._cs_scrubber_layout.addWidget(self.scrubber_slider)
            self._cs_scrubber_layout.addWidget(self._time_label)
            self._cs_playback_layout.addWidget(self._play_button, 1)
            self._cs_playback_layout.addWidget(self._stop_button, 1)
            self._cs_playback_layout.addWidget(self._preview_button, 1)
            self._cs_expand_layout.addWidget(self._collapse_btn)
            for btn, glyph in [
                (self._play_button, "\uE768"),
                (self._stop_button, "\uE71A"),
                (self._preview_button, "\uF0C7"),
            ]:
                btn.setMinimumWidth(0)
                btn.setMaximumWidth(16777215)
                btn.setText(glyph)
                btn.setProperty("icon_mode", True)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            self._save_button.setVisible(False)
            self._reset_button.setVisible(False)
            self._transport_bar.setVisible(False)
            self.main_window.setMinimumWidth(0)
            self.main_window.setMinimumHeight(0)
            self.main_window.adjustSize()
            self.main_window.resize(250, 250)
        else:
            self._body.setVisible(True)
            self._collapsed_strip.setVisible(False)
            self._collapse_btn.setText(tr("▲  Collapse"))
            self._collapse_btn.setToolTip(tr("Collapse to mini mode"))
            self._collapse_btn.setProperty("strip_mode", False)
            self._collapse_btn.style().unpolish(self._collapse_btn)
            self._collapse_btn.style().polish(self._collapse_btn)
            self._transport_layout.insertWidget(0, self.scrubber_slider)
            btn_row_layout = self._btn_row_widget.layout()
            btn_row_layout.insertWidget(0, self._play_button)
            btn_row_layout.insertWidget(1, self._stop_button)
            btn_row_layout.insertWidget(2, self._preview_button)
            btn_row_layout.insertWidget(4, self._time_label)
            btn_row_layout.addWidget(self._collapse_btn)
            for btn in (self._play_button, self._stop_button, self._preview_button):
                btn.setMinimumWidth(0)
                btn.setMaximumWidth(16777215)
                btn.setProperty("icon_mode", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            self._stop_button.setText(tr("■  Stop"))
            self._preview_button.setText(tr("🔊  Preview"))
            self._save_button.setVisible(True)
            self._save_button.setText(tr("Save"))
            self._reset_button.setVisible(True)
            self._reset_button.setText(tr("Reset"))
            self._transport_bar.setVisible(True)
            self.main_window.setMinimumWidth(820)
            self.main_window.setMinimumHeight(485)
            self.main_window.resize(self._expanded_size)

    # ── Collapsed-strip humanize sync ──────────────────────────────────

    def _on_collapsed_humanize_toggled(self, checked: bool) -> None:
        sel = self.playback_tab.select_all_humanization_check
        sel.blockSignals(True)
        sel.setChecked(checked)
        sel.blockSignals(False)
        self.playback_tab._toggle_all(checked)

    def _sync_collapsed_humanize(self, checked: bool) -> None:
        self._collapsed_humanize_check.blockSignals(True)
        self._collapsed_humanize_check.setChecked(checked)
        self._collapsed_humanize_check.blockSignals(False)

    # ── Public API ─────────────────────────────────────────────────────

    def update_file_label(self, text: str, tooltip: str = "") -> None:
        self.playback_tab.update_file_label(text, tooltip)
        self._collapsed_file_label.setText(text)

    def set_controls_enabled(self, enabled: bool, ignore_if_loaded: bool = False) -> None:
        self.playback_tab.set_groups_enabled(
            enabled,
            skip_playback_humanization=(ignore_if_loaded and enabled)
        )

    def _set_save_enabled(self, val: bool) -> None:
        self._save_button.setEnabled(val)
        self._collapsed_save_btn.setEnabled(val)

    def reset_controls_to_default(self) -> None:
        self.playback_tab.reset_to_default()
        self.settings_tab.use_ai_pedal_check.setChecked(False)

    def load_config_to_ui(self, config: dict, save_dir: str) -> None:
        self.playback_tab.load_config(config)
        self.settings_tab.load_config(config, save_dir)

    def gather_playback_config(self) -> dict:
        cfg = self.playback_tab.gather_playback_config()
        cfg['use_ai_pedal'] = self.settings_tab.use_ai_pedal_check.isChecked()
        return cfg

    def gather_app_config(self) -> dict:
        return self.settings_tab.gather_config()

    def update_enabled_states(self) -> None:
        self.playback_tab.update_enabled_states()

    # ── Compatibility shims (old attribute names) ──────────────────────

    @property
    def play_button(self):
        return self._play_button

    @property
    def stop_button(self):
        return self._stop_button

    @property
    def preview_button(self):
        return self._preview_button

    @property
    def save_button(self):
        return self._save_button

    @property
    def reset_button(self):
        return self._reset_button

    @property
    def collapse_btn(self):
        return self._collapse_btn