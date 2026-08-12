from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from i18n import tr, language_changed
from ui.widgets import make_card

_PEDAL_DISPLAY_MAP = {
    "Auto (Default)": "hybrid",
    "Harmonic":        "legato",
    "Rhythmic":        "rhythmic",
    "None":            "none",
}

_PEDAL_INV_MAP = {v: k for k, v in _PEDAL_DISPLAY_MAP.items()}


class PlaybackTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        sc_layout = QHBoxLayout(scroll_content)
        sc_layout.setContentsMargins(12, 12, 12, 12)
        sc_layout.setSpacing(12)

        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        self._file_group = self._create_file_group()
        left_col.addWidget(self._file_group)
        self._playback_group = self._create_playback_group()
        left_col.addWidget(self._playback_group, 1)

        right_col = QVBoxLayout()
        right_col.setSpacing(10)
        self._humanization_group = self._create_humanization_group()
        right_col.addWidget(self._humanization_group, 1)

        sc_layout.addLayout(left_col, 1)
        sc_layout.addLayout(right_col, 1)

        scroll.setWidget(scroll_content)
        outer.addWidget(scroll)

    # ── Card builders ──────────────────────────────────────────────────

    def _create_file_group(self):
        self._file_card, self._file_content = make_card("")
        self._file_title = QLabel()
        self._file_title.setProperty("role", "section")
        self._file_content.insertWidget(0, self._file_title)

        self._file_path_label = QLabel()
        self._file_path_label.setObjectName("file_path_label")
        self._file_path_label.setWordWrap(True)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)
        self._browse_button = QPushButton()
        self._browse_button.setToolTip("")
        self._load_saved_btn = QPushButton()
        self._load_saved_btn.setToolTip("")
        btn_layout.addWidget(self._browse_button)
        btn_layout.addWidget(self._load_saved_btn)

        self._file_content.addWidget(self._file_path_label)
        self._file_content.addLayout(btn_layout)
        return self._file_card

    def _create_playback_group(self):
        self._pb_card, self._pb_content = make_card("")
        self._pb_title = QLabel()
        self._pb_title.setProperty("role", "section")
        self._pb_content.insertWidget(0, self._pb_title)

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnMinimumWidth(1, 8)
        grid.setColumnStretch(2, 1)

        self._tempo_label = QLabel()
        self.tempo_slider, self.tempo_spinbox = self._make_slider_spinbox(
            10.0, 200.0, 100.0, "%", factor=10.0, decimals=1
        )
        self.tempo_spinbox.setFixedWidth(80)
        self.tempo_slider.setToolTip("")
        self.tempo_spinbox.setToolTip("")
        grid.addWidget(self._tempo_label, 0, 0)
        grid.addWidget(self.tempo_slider, 0, 2)
        grid.addWidget(self.tempo_spinbox, 0, 3)

        self._pedal_label = QLabel()
        self.pedal_style_combo = QComboBox()
        self._rebuild_pedal_combo()
        self.pedal_style_combo.setToolTip("")
        grid.addWidget(self._pedal_label, 1, 0)
        grid.addWidget(self.pedal_style_combo, 1, 2, 1, 2)

        self._transpose_label = QLabel()
        self.transpose_spinbox = QSpinBox()
        self.transpose_spinbox.setRange(-24, 24)
        self.transpose_spinbox.setValue(0)
        self.transpose_spinbox.setSuffix("")
        self.transpose_spinbox.setFixedWidth(80)
        self.transpose_spinbox.setToolTip("")
        grid.addWidget(self._transpose_label, 2, 0)
        grid.addWidget(self.transpose_spinbox, 2, 2, 1, 2)

        self._use_88_key_check = QCheckBox()
        self._use_88_key_check.setToolTip("")
        self._countdown_check = QCheckBox()
        self._countdown_check.setToolTip("")
        self._debug_check = QCheckBox()
        self._debug_check.setToolTip("")
        self._pb_content.addLayout(grid)
        self._pb_content.addWidget(self._use_88_key_check)
        self._pb_content.addWidget(self._countdown_check)
        self._pb_content.addWidget(self._debug_check)
        self._pb_content.addStretch()
        return self._pb_card

    def _create_humanization_group(self):
        self._hum_card, self._hum_content = make_card("")
        self._hum_title = QLabel()
        self._hum_title.setProperty("role", "section")
        self._hum_content.insertWidget(0, self._hum_title)

        self._select_all_humanization_check = QCheckBox()
        self._select_all_humanization_check.setToolTip("")

        self.all_humanization_checks = {}
        self.all_humanization_spinboxes = {}
        self.all_humanization_sliders = {}

        self._simulate_hands_check = QCheckBox()
        self._simulate_hands_check.setToolTip("")
        self._enable_chord_roll_check = QCheckBox()
        self._enable_chord_roll_check.setToolTip("")

        self.all_humanization_checks['simulate_hands'] = self._simulate_hands_check
        self.all_humanization_checks['enable_chord_roll'] = self._enable_chord_roll_check

        self._hum_content.addWidget(self._select_all_humanization_check)
        self._hum_content.addWidget(self._simulate_hands_check)
        self._hum_content.addWidget(self._enable_chord_roll_check)

        h_sep = QFrame()
        h_sep.setObjectName("h_sep")
        h_sep.setFrameShape(QFrame.Shape.HLine)
        self._hum_content.addWidget(h_sep)

        self._detailed_layout = QGridLayout()
        self._detailed_layout.setSpacing(6)
        self._detailed_layout.setColumnStretch(2, 1)
        self._detailed_layout.setColumnMinimumWidth(1, 4)

        self._human_rows = []
        self._add_human_row(0, "vary_timing",       0,  0.1, 0.01, " s",
                            factor=10000.0)
        self._add_human_row(1, "vary_articulation", 50, 100,   95, "%",
                            factor=100.0, decimals=1)
        self._add_human_row(2, "hand_drift",         0, 100,   25, "%",
                            factor=100.0, decimals=1)
        self._add_human_row(3, "mistake_chance",     0,  10,    0, "%",
                            factor=100.0, decimals=1)
        self._add_human_row(4, "tempo_sway",         0, 0.1,   0, " s",
                            factor=10000.0)

        self._invert_sway_check = QCheckBox()
        self._invert_sway_check.setToolTip("")
        self.all_humanization_checks['invert_tempo_sway'] = self._invert_sway_check
        self.all_humanization_checks['tempo_sway'].toggled.connect(
            self._invert_sway_check.setEnabled
        )
        self._detailed_layout.addWidget(self._invert_sway_check, 5, 0)

        self._hum_content.addLayout(self._detailed_layout)
        self._hum_content.addStretch()

        self.all_humanization_checks['vary_velocity'] = QCheckBox()
        self._select_all_humanization_check.toggled.connect(self._toggle_all)
        for check in self.all_humanization_checks.values():
            if check.text():
                check.toggled.connect(self._update_select_all_state)

        return self._hum_card

    def _add_human_row(self, row_idx, key, min_val, max_val, def_val,
                       suffix, factor=1.0, decimals=3):
        check = QCheckBox("")
        slider, spinbox = self._make_slider_spinbox(
            min_val, max_val, def_val, suffix, factor=factor, decimals=decimals
        )
        spinbox.setFixedWidth(80)
        check.toggled.connect(slider.setEnabled)
        check.toggled.connect(spinbox.setEnabled)
        self._detailed_layout.addWidget(check,   row_idx, 0)
        self._detailed_layout.addWidget(slider,  row_idx, 2)
        self._detailed_layout.addWidget(spinbox, row_idx, 3)
        self.all_humanization_checks[key]   = check
        self.all_humanization_sliders[key]  = slider
        self.all_humanization_spinboxes[key] = spinbox
        self._human_rows.append((key, check, slider, spinbox))

    def _rebuild_pedal_combo(self):
        self.pedal_style_combo.blockSignals(True)
        self.pedal_style_combo.clear()
        pedal_items = [
            (tr("Auto (Default)"), "Auto (Default)"),
            (tr("Harmonic"), "Harmonic"),
            (tr("Rhythmic"), "Rhythmic"),
            (tr("None"), "None"),
        ]
        for display, eng_key in pedal_items:
            self.pedal_style_combo.addItem(display, eng_key)
        self.pedal_style_combo.blockSignals(False)

    # ── Widget factory ─────────────────────────────────────────────────

    @staticmethod
    def _make_slider_spinbox(min_val, max_val, default_val,
                             text_suffix="", factor=10000.0, decimals=4):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(int(min_val * factor), int(max_val * factor))
        spinbox = QDoubleSpinBox()
        spinbox.setDecimals(decimals)
        spinbox.setRange(0.0, 9999.9999)
        spinbox.setSingleStep(1.0 / factor)
        spinbox.setSuffix(text_suffix)
        slider.setValue(int(default_val * factor))
        spinbox.setValue(default_val)
        slider.valueChanged.connect(lambda v: spinbox.setValue(v / factor))
        spinbox.valueChanged.connect(lambda v: slider.setValue(int(v * factor)))
        return slider, spinbox

    # ── Humanization helpers ───────────────────────────────────────────

    def _toggle_all(self, checked: bool) -> None:
        for check in self.all_humanization_checks.values():
            if check.text():
                check.setChecked(checked)

    def _update_select_all_state(self) -> None:
        checks = [c for c in self.all_humanization_checks.values() if c.text()]
        self._select_all_humanization_check.blockSignals(True)
        self._select_all_humanization_check.setChecked(all(c.isChecked() for c in checks))
        self._select_all_humanization_check.blockSignals(False)

    # ── ReTranslation ──────────────────────────────────────────────────

    def _retranslate(self, lang_code: str = "") -> None:
        self._file_title.setText(tr("MIDI File"))
        self._file_path_label.setText(tr("No file selected."))
        self._browse_button.setText(tr("Browse…"))
        self._browse_button.setToolTip(tr("Open a MIDI file to play"))
        self._load_saved_btn.setText(tr("Load Save"))
        self._load_saved_btn.setToolTip(tr("Load a previously saved humanized performance"))

        self._pb_title.setText(tr("Playback"))
        self._tempo_label.setText(tr("Tempo"))
        tip = tr("Playback speed as a percentage of the original tempo")
        self.tempo_slider.setToolTip(tip)
        self.tempo_spinbox.setToolTip(tip)

        self._pedal_label.setText(tr("Pedal"))
        self._rebuild_pedal_combo()
        self.pedal_style_combo.setToolTip(
            tr("Auto (Default): AI-driven pedal using a hybrid of rhythmic and harmonic analysis\n"
               "Harmonic: Hold pedal through harmonic regions, releasing at chord/bass changes\n"
               "Rhythmic: Release pedal on beat boundaries only\n"
               "None: No sustain pedal"))

        self._transpose_label.setText(tr("Transpose"))
        self.transpose_spinbox.setSuffix(tr(" st"))
        self.transpose_spinbox.setToolTip(
            tr("Shift all notes up or down by the given number of semitones"))

        self._use_88_key_check.setText(tr("88-Key Layout"))
        self._use_88_key_check.setToolTip(
            tr("Map notes to the full 88-key piano layout instead of a compressed keyboard layout"))
        self._countdown_check.setText(tr("Countdown"))
        self._countdown_check.setToolTip(
            tr("Show a 3-second countdown before playback begins"))
        self._debug_check.setText(tr("Debug Output"))
        self._debug_check.setToolTip(
            tr("Print verbose event logs to the Debug tab during playback"))

        self._hum_title.setText(tr("Humanization"))
        self._select_all_humanization_check.setText(tr("All"))
        self._select_all_humanization_check.setToolTip(
            tr("Enable or disable all humanization options at once"))
        self._simulate_hands_check.setText(tr("Simulate Hands"))
        self._simulate_hands_check.setToolTip(
            tr("Assign notes to left/right hand and limit simultaneous finger usage "
               "to simulate realistic hand behavior"))
        self._enable_chord_roll_check.setText(tr("Chord Roll"))
        self._enable_chord_roll_check.setToolTip(
            tr("Slightly stagger the notes within each chord to simulate the natural "
               "roll of fingers across the keys"))

        self._invert_sway_check.setText(tr("Invert Sway"))
        self._invert_sway_check.setToolTip(tr("Invert the phase of the tempo sway curve"))

        self._rebuild_human_rows()

    def _rebuild_human_rows(self) -> None:
        for key, check, slider, spinbox in self._human_rows:
            if key == "vary_timing":
                check.setText(tr("Vary Timing"))
                tip = tr("Add random timing offsets to note events (in seconds)")
            elif key == "vary_articulation":
                check.setText(tr("Vary Articulation"))
                tip = tr("Randomize note hold duration — lower values create a more staccato feel")
            elif key == "hand_drift":
                check.setText(tr("Hand Drift"))
                tip = tr("Simulate gradual timing drift between the left and right hands")
            elif key == "mistake_chance":
                check.setText(tr("Mistakes"))
                tip = tr("Randomly skip notes to simulate human errors")
            elif key == "tempo_sway":
                check.setText(tr("Tempo Sway"))
                tip = tr("Apply a sinusoidal tempo variation across the song for a more expressive feel")
            else:
                check.setText(key)
                tip = ""
            check.setToolTip(tip)
            slider.setToolTip(tip)
            spinbox.setToolTip(tip)

    _ROW_SOURCE = {
        "vary_timing":       ("Vary Timing",       "Add random timing offsets to note events (in seconds)"),
        "vary_articulation": ("Vary Articulation", "Randomize note hold duration — lower values create a more staccato feel"),
        "hand_drift":        ("Hand Drift",        "Simulate gradual timing drift between the left and right hands"),
        "mistake_chance":    ("Mistakes",          "Randomly skip notes to simulate human errors"),
        "tempo_sway":        ("Tempo Sway",        "Apply a sinusoidal tempo variation across the song for a more expressive feel"),
    }

    # ── Public API ─────────────────────────────────────────────────────

    def update_file_label(self, text: str, tooltip: str = "") -> None:
        self._file_path_label.setText(text)
        self._file_path_label.setToolTip(tooltip)

    def set_groups_enabled(self, enabled: bool, skip_playback_humanization: bool = False) -> None:
        self._file_group.setEnabled(enabled)
        if not skip_playback_humanization:
            self._playback_group.setEnabled(enabled)
            self._humanization_group.setEnabled(enabled)

    def update_enabled_states(self) -> None:
        for key, check in self.all_humanization_checks.items():
            if not check.text():
                continue
            checked = check.isChecked()
            if key in self.all_humanization_sliders:
                self.all_humanization_sliders[key].setEnabled(checked)
            if key in self.all_humanization_spinboxes:
                self.all_humanization_spinboxes[key].setEnabled(checked)
        self._invert_sway_check.setEnabled(
            self.all_humanization_checks['tempo_sway'].isChecked()
        )

    def reset_to_default(self) -> None:
        self.tempo_spinbox.setValue(100)
        self.transpose_spinbox.setValue(0)
        self.pedal_style_combo.setCurrentIndex(0)
        self._use_88_key_check.setChecked(False)
        self._countdown_check.setChecked(True)
        self._debug_check.setChecked(False)
        self.all_humanization_spinboxes['vary_timing'].setValue(0.010)
        self.all_humanization_spinboxes['vary_articulation'].setValue(95.0)
        self.all_humanization_spinboxes['hand_drift'].setValue(25.0)
        self.all_humanization_spinboxes['mistake_chance'].setValue(0.5)
        self.all_humanization_spinboxes['tempo_sway'].setValue(0.015)
        for check in self.all_humanization_checks.values():
            if check.text():
                check.setChecked(False)
        self.update_enabled_states()

    def load_config(self, config: dict) -> None:
        self.tempo_spinbox.setValue(config.get('tempo', 100.0))
        self.transpose_spinbox.setValue(config.get('transpose', 0))
        internal = config.get('pedal_style', 'hybrid')
        display_eng = _PEDAL_INV_MAP.get(internal) or internal
        if display_eng not in _PEDAL_DISPLAY_MAP:
            display_eng = "Auto (Default)"
        idx = self.pedal_style_combo.findData(display_eng)
        if idx >= 0:
            self.pedal_style_combo.setCurrentIndex(idx)
        self._use_88_key_check.setChecked(config.get('use_88_key_layout', False))
        self._countdown_check.setChecked(config.get('countdown', True))
        self._debug_check.setChecked(config.get('debug_mode', False))
        self._select_all_humanization_check.setChecked(config.get('select_all_humanization', False))
        self._simulate_hands_check.setChecked(config.get('simulate_hands', False))
        self._enable_chord_roll_check.setChecked(config.get('enable_chord_roll', False))
        self.all_humanization_checks['vary_timing'].setChecked(config.get('enable_vary_timing', False))
        self.all_humanization_spinboxes['vary_timing'].setValue(config.get('value_timing_variance', 0.010))
        self.all_humanization_checks['vary_articulation'].setChecked(config.get('enable_vary_articulation', False))
        self.all_humanization_spinboxes['vary_articulation'].setValue(config.get('value_articulation', 95.0))
        self.all_humanization_checks['hand_drift'].setChecked(config.get('enable_hand_drift', False))
        self.all_humanization_spinboxes['hand_drift'].setValue(config.get('value_hand_drift_decay', 25.0))
        self.all_humanization_checks['mistake_chance'].setChecked(config.get('enable_mistakes', False))
        self.all_humanization_spinboxes['mistake_chance'].setValue(config.get('value_mistake_chance', 0.5))
        self.all_humanization_checks['tempo_sway'].setChecked(config.get('enable_tempo_sway', False))
        self.all_humanization_spinboxes['tempo_sway'].setValue(config.get('value_tempo_sway_intensity', 0.015))
        self.all_humanization_checks['invert_tempo_sway'].setChecked(config.get('invert_tempo_sway', False))
        self.update_enabled_states()

    def gather_playback_config(self) -> dict:
        internal = _PEDAL_DISPLAY_MAP.get(self.pedal_style_combo.currentData(), 'hybrid')
        return {
            'midi_file':             self._file_path_label.toolTip(),
            'tempo':                 self.tempo_spinbox.value(),
            'transpose':             self.transpose_spinbox.value(),
            'countdown':             self._countdown_check.isChecked(),
            'use_88_key_layout':     self._use_88_key_check.isChecked(),
            'pedal_style':           internal,
            'debug_mode':            self._debug_check.isChecked(),
            'simulate_hands':        self._simulate_hands_check.isChecked(),
            'vary_velocity':         False,
            'enable_chord_roll':     self._enable_chord_roll_check.isChecked(),
            'vary_timing':           self.all_humanization_checks['vary_timing'].isChecked(),
            'timing_variance':       self.all_humanization_spinboxes['vary_timing'].value(),
            'vary_articulation':     self.all_humanization_checks['vary_articulation'].isChecked(),
            'articulation':          self.all_humanization_spinboxes['vary_articulation'].value() / 100.0,
            'enable_drift_correction': self.all_humanization_checks['hand_drift'].isChecked(),
            'drift_decay_factor':    self.all_humanization_spinboxes['hand_drift'].value() / 100.0,
            'enable_mistakes':       self.all_humanization_checks['mistake_chance'].isChecked(),
            'mistake_chance':        self.all_humanization_spinboxes['mistake_chance'].value(),
            'enable_tempo_sway':     self.all_humanization_checks['tempo_sway'].isChecked(),
            'tempo_sway_intensity':  self.all_humanization_spinboxes['tempo_sway'].value(),
            'invert_tempo_sway':     self._invert_sway_check.isChecked(),
        }

    def gather_app_config(self) -> dict:
        internal = _PEDAL_DISPLAY_MAP.get(self.pedal_style_combo.currentData(), 'hybrid')
        return {
            'tempo':                   self.tempo_spinbox.value(),
            'transpose':               self.transpose_spinbox.value(),
            'pedal_style':             internal,
            'use_88_key_layout':       self._use_88_key_check.isChecked(),
            'countdown':               self._countdown_check.isChecked(),
            'debug_mode':              self._debug_check.isChecked(),
            'select_all_humanization': self._select_all_humanization_check.isChecked(),
            'simulate_hands':          self._simulate_hands_check.isChecked(),
            'enable_chord_roll':       self._enable_chord_roll_check.isChecked(),
            'enable_vary_timing':      self.all_humanization_checks['vary_timing'].isChecked(),
            'value_timing_variance':   self.all_humanization_spinboxes['vary_timing'].value(),
            'enable_vary_articulation': self.all_humanization_checks['vary_articulation'].isChecked(),
            'value_articulation':      self.all_humanization_spinboxes['vary_articulation'].value(),
            'enable_hand_drift':       self.all_humanization_checks['hand_drift'].isChecked(),
            'value_hand_drift_decay':  self.all_humanization_spinboxes['hand_drift'].value(),
            'enable_mistakes':         self.all_humanization_checks['mistake_chance'].isChecked(),
            'value_mistake_chance':    self.all_humanization_spinboxes['mistake_chance'].value(),
            'enable_tempo_sway':       self.all_humanization_checks['tempo_sway'].isChecked(),
            'value_tempo_sway_intensity': self.all_humanization_spinboxes['tempo_sway'].value(),
            'invert_tempo_sway':       self._invert_sway_check.isChecked(),
        }

    # ── Compatibility shims (old attribute names) ──────────────────────

    @property
    def browse_button(self):
        return self._browse_button

    @property
    def load_saved_btn(self):
        return self._load_saved_btn

    @property
    def file_path_label(self):
        return self._file_path_label

    @property
    def playback_group(self):
        return self._pb_card

    @property
    def humanization_group(self):
        return self._hum_card

    @property
    def use_88_key_check(self):
        return self._use_88_key_check

    @property
    def select_all_humanization_check(self):
        return self._select_all_humanization_check