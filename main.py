#!/usr/bin/env python3
import bisect
import ctypes
import os
import sys
import warnings

warnings.filterwarnings("ignore", message="sipPyTypeDict.*", category=DeprecationWarning)

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QDialog, QFileDialog, QMainWindow, QMessageBox

from controllers.PlaybackController import PlaybackController
from core.core import KeyMapper, MidiParser, TempoMap
from core.translator import FormatRegistry
from managers.ConfigManager import ConfigManager
from managers.HotkeyManager import HotkeyManager
from i18n import tr
from managers.UpdateManager import DownloadWorker, UpdateChecker
from ui.LoadSaveDialog import LoadSaveDialog
from ui.MainWindowUI import MainWindowUI
from ui.TrackSelectionDialog import TrackSelectionDialog
from ui.theme import ThemeManager

APP_VERSION = "1.0"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"ROMidi v{APP_VERSION}")
        self.setMinimumWidth(820)
        self.setMinimumHeight(550)
        self.resize(self.minimumWidth(), self.minimumHeight())

        # Set specific Icon base execution path (Required for OS Contexts)
        base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._enable_dark_title_bar()
        
        # Instantiate Domains
        self.config_manager = ConfigManager()
        self.ui = MainWindowUI(self)
        self.playback_controller = PlaybackController()
        self.hotkey_manager = HotkeyManager()
        
        # Global Application States
        self.loaded_save_data = None
        self.loaded_save_filename = None
        self.selected_tracks_info = None
        self.current_notes = []
        self._note_start_times = []
        self.total_song_duration_sec = 1.0
        self._max_note_duration = 0.0
        self.current_pedal_intervals = []

        self._preview_alias = "humidi_preview"
        self._preview_playing = False

        self._bind_signals()

        # Load initialization data
        loaded_cfg = self.config_manager.load()
        if loaded_cfg:
            self.ui.load_config_to_ui(loaded_cfg, self.config_manager.save_dir)
            key_str = self.hotkey_manager._format_key_string(self.hotkey_manager.current_key)
            self.ui.settings_tab.set_hotkey_label(key_str)
        else:
            self.ui.reset_controls_to_default()

        self._update_checker = UpdateChecker(APP_VERSION)
        self._update_checker.update_available.connect(self._on_update_available)
        self._update_checker.start()

    def _bind_signals(self):
        # UI controls bound strictly to Execution/Router logic
        self.ui.play_button.clicked.connect(self.handle_play)
        self.ui.stop_button.clicked.connect(self.handle_stop)
        self.ui.preview_button.clicked.connect(self._toggle_preview)
        self.ui.save_button.clicked.connect(self.handle_save)
        self.ui.reset_button.clicked.connect(self.ui.reset_controls_to_default)
        self.ui.playback_tab.browse_button.clicked.connect(self.select_file)
        self.ui.playback_tab.load_saved_btn.clicked.connect(self.open_load_dialog)
        self.ui.settings_tab.save_browse_btn.clicked.connect(self._browse_save_dir)
        self.ui._collapsed_load_btn.clicked.connect(self.select_file)
        self.ui._collapsed_load_saved_btn.clicked.connect(self.open_load_dialog)
        self.ui._collapsed_save_btn.clicked.connect(self.handle_save)
        self.ui.settings_tab.hk_btn.clicked.connect(self._change_hotkey)
        self.ui.settings_tab.check_update_btn.clicked.connect(self._manual_check_update)

        # View manipulations bound to Window behavior
        self.ui.collapse_btn.clicked.connect(self._sync_play_button)
        self.ui.settings_tab.always_top_check.toggled.connect(self._toggle_always_on_top)
        self.ui._collapsed_always_on_top_check.toggled.connect(self._toggle_always_on_top)
        self.ui.settings_tab.opacity_slider.valueChanged.connect(self._change_opacity)

        # Settings-tab persistence — save immediately on change so closing without playing doesn't lose them
        self.ui.settings_tab.always_top_check.toggled.connect(self._save_config)
        self.ui.settings_tab.opacity_slider.valueChanged.connect(self._save_config)
        self.ui.settings_tab.timeline_vis_check.toggled.connect(self._save_config)
        self.ui.settings_tab.piano_vis_check.toggled.connect(self._save_config)
        self.ui.settings_tab.use_ai_pedal_check.toggled.connect(self._save_config)
        self.ui.settings_tab.lang_combo.currentIndexChanged.connect(self._save_config)

        # Translator tab
        self.ui.translator_tab.play_sheet_requested.connect(self._on_play_sheet)
        self.ui.translator_tab.export_requested.connect(self._on_export_sheet)

        # Timeline logic bridging
        self.ui.timeline_widget.seek_requested.connect(self._on_timeline_seek)
        self.ui.timeline_widget.scrub_position_changed.connect(self._on_visual_scrub)

        # External IO bridging
        self.hotkey_manager.toggle_requested.connect(self.toggle_playback_state)
        self.hotkey_manager.bound_updated.connect(self._on_hotkey_bound)

        # System Logic bridging to the View representations
        self.playback_controller.status_updated.connect(self.ui.log_output.append)
        self.playback_controller.progress_updated.connect(self.update_progress)
        self.playback_controller.playback_finished.connect(self.on_playback_finished)
        self.playback_controller.visualizer_updated.connect(lambda p: self.ui.piano_widget.set_active_pitches(p))
        self.playback_controller.pedal_updated.connect(self.ui.piano_widget.set_pedal_active)
        self.playback_controller.auto_paused.connect(self._on_auto_paused)
        self.playback_controller.error_occurred.connect(self.show_error_dialog)
        self.playback_controller.timeline_data_ready.connect(self._on_timeline_data_ready)
        self.playback_controller.pedal_data_ready.connect(self._on_pedal_data_ready)
        self.playback_controller.save_successful.connect(self._on_save_successful)
        self.playback_controller.save_failed.connect(self._on_save_failed)

    # --- MIDI Preview (system synth) ---
    def _toggle_preview(self, checked=None, force_stop: bool = False) -> None:
        if force_stop:
            self._stop_preview()
        elif self._preview_playing:
            self._stop_preview()
        else:
            self._start_preview()

    def _start_preview(self) -> None:
        if sys.platform != "win32":
            return
        filepath = self.ui.playback_tab.file_path_label.toolTip()
        if not filepath or not os.path.exists(filepath):
            return
        self._stop_preview()
        try:
            ctypes.windll.winmm.mciSendStringW(
                f'open "{filepath}" type sequencer alias {self._preview_alias}',
                None, 0, None
            )
            ctypes.windll.winmm.mciSendStringW(
                f'play {self._preview_alias}',
                None, 0, None
            )
            self._preview_playing = True
            self.ui.preview_button.setCheckable(True)
            self.ui.preview_button.setChecked(True)
            self.ui.preview_button.setToolTip(tr("Click to stop previewing"))
            self.ui.play_button.setEnabled(False)
            self.ui.stop_button.setEnabled(False)
        except Exception:
            self._stop_preview()

    def _stop_preview(self) -> None:
        if sys.platform != "win32":
            return
        try:
            ctypes.windll.winmm.mciSendStringW(
                f'close {self._preview_alias}',
                None, 0, None
            )
        except Exception:
            pass
        self._preview_playing = False
        self.ui.preview_button.setChecked(False)
        self.ui.preview_button.setToolTip(
            tr("Audition the loaded MIDI file with the system synthesizer"))
        self.ui.play_button.setEnabled(True)
        self.ui.stop_button.setEnabled(
            self.playback_controller.is_playing() or self.playback_controller.is_paused()
        )

    # --- Windows Specific GUI Modifications ---
    def _toggle_always_on_top(self, checked):
        if sys.platform == 'win32':
            handle = self.windowHandle()
            flags = self.windowFlags()
            if checked:
                handle.setFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
            else:
                handle.setFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
            self.update()
        else:
            flags = self.windowFlags()
            if checked: self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
            else: self.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
            self.show()
        self.ui.settings_tab.always_top_check.blockSignals(True)
        self.ui.settings_tab.always_top_check.setChecked(checked)
        self.ui.settings_tab.always_top_check.blockSignals(False)
        self.ui._collapsed_always_on_top_check.blockSignals(True)
        self.ui._collapsed_always_on_top_check.setChecked(checked)
        self.ui._collapsed_always_on_top_check.blockSignals(False)

    def _change_opacity(self, value):
        self.setWindowOpacity(value / 100.0)

    # --- Standard Execution Behaviors ---
    def _save_config(self):
        config_data = self.ui.gather_app_config()
        self.config_manager.save(config_data)

    def _browse_save_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Save Directory", self.config_manager.save_dir)
        if path:
            self.config_manager.set_save_dir(path)
            self.ui.settings_tab.save_path_input.setText(path)
            self._save_config()

    def _change_hotkey(self):
        QMessageBox.information(self, tr("Bind Key"), tr("Press the key you want to bind now."))
        self.ui.settings_tab.hk_btn.setText(tr("Listening..."))
        self.ui.settings_tab.hk_btn.setEnabled(False)
        self.hotkey_manager.start_binding()

    def _on_hotkey_bound(self, key_str):
        self.ui.settings_tab.set_hotkey_label(key_str)
        self.ui.settings_tab.hk_btn.setText(tr("Change"))
        self.ui.settings_tab.hk_btn.setEnabled(True)
        self._sync_play_button()

    def _sync_play_button(self):
        """Single authoritative update for the play button, derived from current playback state."""
        key_str = self.hotkey_manager._format_key_string(self.hotkey_manager.current_key)
        if self.ui._is_collapsed:
            if self.playback_controller.is_paused():
                self.ui.play_button.setText("\uE768")
                self.ui.play_button.setToolTip(tr("Resume (%1)").arg(key_str))
            elif self.playback_controller.is_playing():
                self.ui.play_button.setText("\uE769")
                self.ui.play_button.setToolTip(tr("Pause (%1)").arg(key_str))
            else:
                self.ui.play_button.setText("\uE768")
                self.ui.play_button.setToolTip(tr("Play (%1)").arg(key_str))
        else:
            if self.playback_controller.is_paused():
                self.ui.play_button.setText(tr("▶  Resume (%1)").arg(key_str))
            elif self.playback_controller.is_playing():
                self.ui.play_button.setText(tr("⏸  Pause (%1)").arg(key_str))
            else:
                self.ui.play_button.setText(tr("▶  Play (%1)").arg(key_str))
            self.ui.play_button.setToolTip(tr("Start, pause, or resume playback"))

    def toggle_playback_state(self):
        if not self.playback_controller.is_paused():
            self.ui.piano_widget.clear()

        if self.playback_controller.is_playing() or self.playback_controller.is_paused():
            self.playback_controller.toggle_pause()
            self._sync_play_button()
            if not self.playback_controller.is_paused():
                current_t = self.ui.timeline_widget.current_time
                self._on_visual_scrub(current_t)
        elif self.ui.play_button.isEnabled():
            self.handle_play()

    def _on_auto_paused(self):
        self._sync_play_button()
        self.ui.piano_widget.clear()
        self.ui.stop_button.setEnabled(True)

    def _on_timeline_seek(self, time):
        self.ui.log_output.append(f"Seeking to {time:.2f}s...")
        self.playback_controller.seek(time)
    
    def _on_visual_scrub(self, time):
        active_pitches = set()
        lo = bisect.bisect_left(self._note_start_times, time - self._max_note_duration)
        hi = bisect.bisect_right(self._note_start_times, time)
        for note in self.current_notes[lo:hi]:
            if note.end_time > time:
                active_pitches.add(note.pitch)
        self.ui.piano_widget.set_active_pitches(list(active_pitches))
        pedal_down = any(s <= time < e for s, e in self.current_pedal_intervals)
        self.ui.piano_widget.set_pedal_active(pedal_down)
        self.ui.update_time_label(time, self.total_song_duration_sec)

    def _on_timeline_data_ready(self, notes, total_dur, tempo_map):
        self.current_notes = notes
        self._note_start_times = [n.start_time for n in notes]
        self._max_note_duration = max((n.duration for n in notes), default=0.0)
        self.total_song_duration_sec = total_dur
        self.ui.timeline_widget.set_data(notes, total_dur, tempo_map)
        self.ui.reset_timeline_position()

    def _on_pedal_data_ready(self, intervals: list):
        self.current_pedal_intervals = intervals
        self.ui.timeline_widget.set_pedal_intervals(intervals)

    def update_progress(self, current_time):
        self.ui.update_progress(current_time, self.total_song_duration_sec)

    # --- Loading & File State Dialogs ---
    def select_file(self):
        if self.playback_controller.is_playing() or self.playback_controller.is_paused(): return
        filepath, _ = QFileDialog.getOpenFileName(self, "Select MIDI File", "", "MIDI Files (*.mid *.midi)")
        if filepath:
            self.loaded_save_data = None
            self.loaded_save_filename = None
            self.ui.playback_tab.playback_group.setEnabled(True)
            self.ui.playback_tab.humanization_group.setEnabled(True)
            self.ui.update_file_label(os.path.basename(filepath), filepath)
            self.ui.log_output.append(f"Selected file: {filepath}")
            self.ui.preview_button.setEnabled(True)
            self._toggle_preview(force_stop=True)
            self._parse_and_select_tracks(filepath)
            
    def open_load_dialog(self):
        dialog = LoadSaveDialog(self.config_manager.save_dir, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_file, data = dialog.get_selected_data()
            if selected_file and data:
                self.loaded_save_data = data
                self.loaded_save_filename = os.path.basename(selected_file)
                
                self.ui.update_file_label(self.loaded_save_filename, selected_file)
                self.ui.playback_tab.playback_group.setEnabled(False)
                self.ui.playback_tab.humanization_group.setEnabled(False)
                self.ui._set_save_enabled(False)
                self.ui.play_button.setEnabled(True)
                self.ui.scrubber_slider.setEnabled(True)
                self.ui.preview_button.setEnabled(True)
                self._toggle_preview(force_stop=True)
                self.ui.log_output.append(f"Loaded save file: {self.loaded_save_filename}")

    def _parse_and_select_tracks(self, filepath):
        self.ui.log_output.append("Parsing MIDI structure...")
        try:
            tracks, tempo_map = MidiParser.parse_structure(filepath, 1.0, None)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to parse MIDI:\n{e}")
            return
            
        dialog = TrackSelectionDialog(tracks, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_tracks_info = dialog.get_selection()
            self.parsed_tempo_map = tempo_map 
            self.ui.log_output.append(f"Tracks selected: {len(self.selected_tracks_info)}")
            self.ui.play_button.setEnabled(True)
            self.ui.scrubber_slider.setEnabled(True)
            self.ui._set_save_enabled(True)
        else:
            self.ui.log_output.append("Track selection cancelled.")
            self.selected_tracks_info = None
            self.ui.play_button.setEnabled(False)
            self.ui.scrubber_slider.setEnabled(False)
            self.ui._set_save_enabled(False)

    # --- Translator ---
    def _on_play_sheet(self, text: str, format_name: str, bpm: int, humanize: bool):
        if self.playback_controller.is_playing() or self.playback_controller.is_paused():
            return

        fmt = FormatRegistry.get(format_name)
        if not fmt:
            QMessageBox.critical(self, "Unknown Format", f"No handler found for format: {format_name}")
            return

        use_88 = self.ui.playback_tab.use_88_key_check.isChecked()
        key_mapper = KeyMapper(use_88_key_layout=use_88)

        try:
            notes = fmt.parse(text, float(bpm), key_mapper)
        except Exception as e:
            QMessageBox.critical(self, "Parse Error", f"Failed to parse sheet:\n{e}")
            return

        if not notes:
            QMessageBox.warning(self, "No Notes", "No playable notes were found in the pasted sheet.")
            return

        tempo_us = int(60_000_000 / bpm)
        tempo_map = TempoMap([(0, tempo_us)], [])

        if humanize:
            config = self.ui.gather_playback_config()
        else:
            config = {
                'use_88_key_layout': use_88, 'debug_mode': False, 'countdown': False,
                'pedal_style': 'none', 'simulate_hands': False, 'vary_velocity': False,
                'enable_chord_roll': False, 'vary_timing': False, 'timing_variance': 0.01,
                'vary_articulation': False, 'articulation': 0.95,
                'enable_drift_correction': False, 'drift_decay_factor': 0.25,
                'enable_mistakes': False, 'mistake_chance': 0.0,
                'enable_tempo_sway': False, 'tempo_sway_intensity': 0.0,
                'invert_tempo_sway': False, 'use_ai_pedal': False,
            }

        self.ui.log_output.append(f"Importing sheet: {len(notes)} notes at {bpm} BPM ({format_name})")
        self.playback_controller.play_from_notes(config, notes, tempo_map)
        self.ui.set_controls_enabled(False)
        self.ui.play_button.setEnabled(True)
        self.ui.stop_button.setEnabled(True)
        self.ui.scrubber_slider.setEnabled(True)
        self._sync_play_button()
        if self.ui._nav_btns[1].isEnabled():
            self.ui.tabs.setCurrentIndex(1)  # Switch to Visualizer

    def _on_export_sheet(self, format_name: str):
        if not self.current_notes:
            QMessageBox.warning(self, "No MIDI Loaded",
                                "Load and prepare a MIDI file on the Playback tab first.")
            return

        fmt = FormatRegistry.get(format_name)
        if not fmt:
            QMessageBox.critical(self, "Unknown Format", f"No handler found for format: {format_name}")
            return

        use_88 = self.ui.playback_tab.use_88_key_check.isChecked()
        key_mapper = KeyMapper(use_88_key_layout=use_88)
        tempo_map = getattr(self, 'parsed_tempo_map', TempoMap([(0, 500000)], []))

        try:
            text = fmt.serialize(self.current_notes, key_mapper, tempo_map)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to generate sheet:\n{e}")
            return

        self.ui.translator_tab.set_export_text(text)
        self.ui.log_output.append(f"Sheet exported: {format_name} ({len(text.splitlines())} lines)")

    def show_error_dialog(self, error_message: str):
        self.ui.log_output.append("ERROR: Playback thread terminated unexpectedly due to an execution failure.")
        QMessageBox.critical(self, "Hardware/Execution Failure", error_message)

    # --- Core Executions ---
    def handle_save(self):
        config = self.ui.gather_playback_config()
        if not self.selected_tracks_info:
            QMessageBox.warning(self, "No Tracks", "Please select a MIDI file and choose tracks first.")
            return
            
        self._save_config()
        original_filename = os.path.basename(self.ui.playback_tab.file_path_label.toolTip())
        self.playback_controller.save(config, self.selected_tracks_info, self.config_manager.save_dir, original_filename)

    def _on_save_successful(self, filepath: str, message: str):
        QMessageBox.information(self, "Save Successful", f"{message}\n{filepath}")

    def _on_save_failed(self, error_message: str):
        QMessageBox.critical(self, "Save Error", error_message)

    def handle_play(self):
        if self.playback_controller.is_playing() or self.playback_controller.is_paused(): 
            self.toggle_playback_state()
            return

        self._stop_preview()
            
        if self.loaded_save_data:
            self.playback_controller.play_from_save(self.loaded_save_data)
        else:
            config = self.ui.gather_playback_config()
            if not self.selected_tracks_info:
                QMessageBox.warning(self, "No Tracks", "Please select a MIDI file and choose tracks first.")
                return
            self.playback_controller.play(config, self.selected_tracks_info)
            
        self.ui.set_controls_enabled(False, bool(self.loaded_save_data))
        self.ui.play_button.setEnabled(True)
        self.ui.stop_button.setEnabled(True)
        self._sync_play_button()
        if self.ui._nav_btns[1].isEnabled():
            self.ui.tabs.setCurrentIndex(1)

    def handle_stop(self):
        self._stop_preview()
        self.playback_controller.stop()

    def on_playback_finished(self):
        self.ui.log_output.append("Playback process finished.\n" + "="*50 + "\n")
        self.ui.set_controls_enabled(True, bool(self.loaded_save_data))
        self.ui.stop_button.setEnabled(False)
        self._sync_play_button()
        self.ui.piano_widget.set_pedal_active(False)

    # --- Update ---
    def _manual_check_update(self):
        btn = self.ui.settings_tab.check_update_btn
        btn.setEnabled(False)
        btn.setText("Checking...")
        self._manual_checker = UpdateChecker(APP_VERSION, force=True)
        self._manual_checker.update_available.connect(self._on_update_available)
        self._manual_checker.update_available.connect(lambda *_: self._reset_update_btn())
        self._manual_checker.no_update.connect(self._on_no_update)
        self._manual_checker.check_failed.connect(self._on_check_failed)
        self._manual_checker.start()

    def _reset_update_btn(self):
        btn = self.ui.settings_tab.check_update_btn
        btn.setEnabled(True)
        btn.setText(tr("Check for updates"))

    def _on_no_update(self):
        self._reset_update_btn()
        QMessageBox.information(self, "Up to Date",
            f"ROMidi v{APP_VERSION} is the latest version.")

    def _on_check_failed(self):
        self._reset_update_btn()
        QMessageBox.warning(self, "Update Check Failed",
            "Could not reach GitHub.\nPlease check your internet connection.")

    def _on_update_available(self, latest_tag: str, download_url: str):
        reply = QMessageBox.question(
            self, "Update Available",
            f"Update available to {latest_tag}. Would you like to update?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._download_worker = DownloadWorker(download_url)
        self._download_worker.finished.connect(self._on_download_finished)
        self._download_worker.failed.connect(self._on_download_failed)
        self._download_worker.start()
        self.ui.log_output.append(f"Downloading update {latest_tag}...")

    def _on_download_finished(self, _tmp_path: str):
        self._save_config()
        self.playback_controller.shutdown()
        QApplication.quit()

    def _on_download_failed(self, error: str):
        QMessageBox.warning(self, "Update Failed",
            f"Could not download update:\n{error}\n\nPlease update manually from GitHub.")

    def closeEvent(self, event):
        self._update_checker.quit()
        self._save_config()
        self._stop_preview()
        self.playback_controller.shutdown()
        event.accept()

    def _enable_dark_title_bar(self):
        if sys.platform != "win32":
            return
        QTimer.singleShot(0, lambda: self._apply_title_bar_theme(ThemeManager.get_active()))

    def _apply_title_bar_theme(self, theme):
        if sys.platform != "win32":
            return
        try:
            hwnd = ctypes.wintypes.HWND(int(self.winId()))
            bg = getattr(theme, 'bg_primary', '#1c1c2e')
            r, g, b = self._hex_to_rgb_static(bg)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            is_dark = luminance < 0.5

            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(1 if is_dark else 0)),
                ctypes.sizeof(ctypes.c_int),
            )

            cr = _DwmColorization()
            cr.Color = 0x02000000 | (b << 16) | (g << 8) | r
            cr.IsEnabled = 1
            DWMWA_COLORIZATION_ATTRIBUTE = 33
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_COLORIZATION_ATTRIBUTE,
                ctypes.byref(cr),
                ctypes.sizeof(cr),
            )
        except Exception:
            pass

    @staticmethod
    def _hex_to_rgb_static(h: str):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


class _DwmColorization(ctypes.Structure):
    _fields_ = [
        ("Color", ctypes.c_uint),
        ("IsEnabled", ctypes.c_int),
    ]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())