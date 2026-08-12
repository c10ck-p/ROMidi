from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from i18n import tr, language_changed

_LICENSE_TEXTS: dict[str, str] = {
    "ROMidi": """\
ROMidi — A community fork of HuMidi

Based on HuMidi by smyGitt (https://github.com/smyGitt/HuMidi-Roblox-Piano-Autoplayer)

This is a modified fork focused on UI polish, i18n support, and theme
customization. All original code is licensed under the MIT License.

Original Copyright (c) 2026 smyGitt
""",

    "HuMidi": """\
MIT License

Copyright (c) 2026 smyGitt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",

    "PedalAI Dataset": """\
The following datasets were used to train the BiLSTM AI pedal timing
model bundled with HuMidi.

────────────────
POP909        
────────────────
A piano MIDI dataset of 909 popular songs with performance annotations.

Citation:
  Wang, Z., Chen, K., Jiang, J., Zhang, Y., Xu, M., Dai, S., Xia, G.,
  & Fazekas, G. (2020). POP909: A Pop-song Dataset for Music Arrangement
  Generation. Proceedings of ISMIR 2020.

License : MIT
URL     : https://github.com/music-x-lab/POP909-Dataset

────────────────
GiantMIDI-Piano
────────────────
A large-scale MIDI dataset of classical piano music transcribed from
audio recordings.

Citation:
  Kong, Q., Li, B., Chen, J., & Wang, Y. (2020). GiantMIDI-Piano: A
  large-scale MIDI dataset for classical piano music. arXiv:2010.07061.

License : Creative Commons Attribution 4.0 International (CC BY 4.0)

  You are free to share and adapt the material for any purpose, provided
  appropriate credit is given.

URL     : https://github.com/bytedance/GiantMIDI-Piano
""",

    "Third-Party Libraries": """\
PyQt6
  License : GPL v3 / Commercial (Riverbank Computing)
  URL     : https://riverbankcomputing.com/software/pyqt/

mido
  License : MIT
  URL     : https://github.com/mido/mido

pynput
  License : LGPL v3
  URL     : https://github.com/moses-palmer/pynput

onnxruntime
  License : MIT
  URL     : https://github.com/microsoft/onnxruntime

numpy
  License : BSD 3-Clause
  URL     : https://numpy.org/
""",
}


class LicenseTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._retranslate()
        language_changed().connect(self._retranslate)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self._header = QLabel()
        self._header.setProperty("role", "title")
        layout.addWidget(self._header)

        selector_row = QHBoxLayout()
        selector_row.setSpacing(8)
        self._sel_lbl = QLabel()
        self._sel_lbl.setProperty("role", "muted")
        self._sel_lbl.setFixedWidth(34)
        self._combo = QComboBox()
        for name in _LICENSE_TEXTS:
            self._combo.addItem(tr(name), name)
        self._combo.currentIndexChanged.connect(self._on_changed)
        selector_row.addWidget(self._sel_lbl)
        selector_row.addWidget(self._combo, 1)
        layout.addLayout(selector_row)

        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setFont(QFont("Courier New", 9))
        self._text.setPlainText(_LICENSE_TEXTS.get(self._combo.currentData(), ""))
        layout.addWidget(self._text)

    def _retranslate(self, lang_code: str = "") -> None:
        self._header.setText(tr("Licenses & Credits"))
        self._sel_lbl.setText(tr("View:"))
        for i, name in enumerate(_LICENSE_TEXTS):
            self._combo.setItemText(i, tr(name))

    def _on_changed(self, index: int) -> None:
        key = self._combo.itemData(index)
        self._text.setPlainText(_LICENSE_TEXTS.get(key, ""))