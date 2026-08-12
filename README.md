# ROMidi

**English** | [简体中文](README.zh_CN.md) | [繁體中文](README.zh_TW.md)

A community fork of [HuMidi](https://github.com/smyGitt/HuMidi-Roblox-Piano-Autoplayer) — a MIDI-to-keyboard autoplayer for Roblox piano games with humanization, automatic pedal timing, and 88-key support.

ROMidi focuses on UI polish, internationalization, and theme customization while preserving all original functionality.

---

## What's new in ROMidi vs HuMidi

| Feature | Description |
|---------|-------------|
| **Multi-Language Support** | Built-in i18n with Simplified Chinese and Traditional Chinese translations |
| **Follow System Language** | Automatically detects the OS language on first launch |
| **Improved Themes** | Enhanced QSS-based theme engine with better color synchronization |
| **Preview Fix** | Fixed the preview toggle so stopping and restarting works correctly |
| **Bug Fixes** | Translation lookup normalization and other refinements |

---

## Screenshots

<img width="326" height="396" alt="ROMidi Playback tab" src="https://github.com/user-attachments/assets/c9d39ad9-0517-4ea6-acb3-da312868aaed" />
<img width="326" height="396" alt="ROMidi Visualizer tab" src="https://github.com/user-attachments/assets/dfe54071-70ba-4c80-b2a8-3c866f3f7cb1" />
<img width="326" height="396" alt="ROMidi Settings tab" src="https://github.com/user-attachments/assets/17b5eac5-b194-4d77-af0e-f1d1c17e463a" />

## Quick Start

### Run from source

```bash
# Install dependencies
pip install -r requirements.txt

# Launch
python main.py
```

### Build an executable

```bash
pyinstaller --noconsole --onefile --icon=icon.ico --add-data "icon.ico;." main.py
```

The app accepts `.mid` files. Works best with piano-only MIDI, but mixed instruments are also supported.

## Dependencies

| Package | Purpose |
|---------|---------|
| [PyQt6](https://riverbankcomputing.com/software/pyqt/) | GUI framework |
| [mido](https://github.com/mido/mido) | MIDI file parsing |
| [numpy](https://numpy.org/) | Audio/numeric processing |
| [onnxruntime](https://github.com/microsoft/onnxruntime) | AI pedal timing inference |
| [pynput](https://github.com/moses-palmer/pynput) | Keyboard/mouse simulation |

See `requirements.txt` for exact version constraints.

## License

This project is licensed under the MIT License — see the [HuMidi](./ui/LicenseTab.py) license entry for the full text of the original software.

Original work Copyright (c) 2026 smyGitt — [HuMidi on GitHub](https://github.com/smyGitt/HuMidi-Roblox-Piano-Autoplayer)