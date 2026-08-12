"""
i18n module - loads .ts XML translation files directly, no lrelease/.qm needed.

Usage:
    from i18n import tr, load_language, get_available_languages

    load_language('zh_CN')          # loads i18n/zh_CN.ts
    tr("Playback")                  # returns "播放" or original text
    tr("Hello %1, you have %2 items", name, count)
    tr("Hello %1").arg(name)        # Qt-compatible chaining
"""

import os
import sys
import xml.etree.ElementTree as ET
from PyQt6.QtCore import QObject, pyqtSignal, QLocale

_TRANSLATIONS: dict[str, str] = {}
_CURRENT_LANG: str = 'en'

_I18N_DIR = os.path.dirname(os.path.abspath(__file__))


class _TranslatorNotifier(QObject):
    language_changed = pyqtSignal(str)

_notifier = _TranslatorNotifier()


class _TrStr(str):
    """String with .arg() method for Qt-compatible chaining."""
    def arg(self, *args) -> '_TrStr':
        result = str.__new__(_TrStr, self)
        for i, arg in enumerate(args):
            result = result.replace(f'%{i + 1}', str(arg))
        return _TrStr(result)


def tr(source: str, *args) -> _TrStr:
    """Translate a string. Supports two call styles:
        tr("Playback")
        tr("Hello %1", name)
        tr("Hello %1").arg(name)
    """
    translated = _TRANSLATIONS.get(source.strip(), source)
    result = _TrStr(translated)
    if args:
        for i, arg in enumerate(args):
            result = result.replace(f'%{i + 1}', str(arg))
    return result


def get_current_language() -> str:
    return _CURRENT_LANG


def get_available_languages() -> list[tuple[str, str]]:
    """Returns [(lang_code, display_name), ...] including English."""
    langs = [('follow_system', 'Follow System')]
    langs.append(('en', 'English'))
    display_map = {
        'zh_CN': 'Simplified Chinese',
        'zh_TW': 'Traditional Chinese',
        'ja':    'Japanese',
        'ko':    'Korean',
    }
    for fname in sorted(os.listdir(_I18N_DIR)):
        if fname.endswith('.ts'):
            code = fname[:-3]
            name = display_map.get(code, code)
            langs.append((code, name))
    return langs


def detect_system_language() -> str:
    """Detects system language, returns load_language-compatible code ('en' on failure)."""
    try:
        locale = QLocale()
        code = locale.name()
        mapping = {
            'zh_CN': 'zh_CN',
            'zh_TW': 'zh_TW',
            'zh_HK': 'zh_TW',
            'ja_JP': 'ja',
            'ko_KR': 'ko',
        }
        if code in mapping:
            return mapping[code]
        lang = code.split('_')[0]
        if lang == 'zh':
            if locale == QLocale.Language.ChineseTraditional:
                return 'zh_TW'
            return 'zh_CN'
        if lang == 'ja':
            return 'ja'
        if lang == 'ko':
            return 'ko'
    except Exception:
        pass
    return 'en'


def load_language(lang_code: str) -> bool:
    """Loads a .ts file. Pass 'en' or empty string to switch back to English.
    Pass 'follow_system' to auto-detect system language."""
    global _TRANSLATIONS, _CURRENT_LANG

    if lang_code == 'follow_system':
        lang_code = detect_system_language()

    if not lang_code or lang_code == 'en':
        _TRANSLATIONS = {}
        _CURRENT_LANG = 'en'
        _notifier.language_changed.emit('en')
        return True

    ts_path = os.path.join(_I18N_DIR, f'{lang_code}.ts')
    if not os.path.exists(ts_path):
        _TRANSLATIONS = {}
        _CURRENT_LANG = 'en'
        _notifier.language_changed.emit('en')
        return True

    try:
        tree = ET.parse(ts_path)
        root = tree.getroot()
    except Exception:
        return False

    translations: dict[str, str] = {}
    for msg in root.iter('message'):
        source = (msg.findtext('source') or '').strip()
        translation = (msg.findtext('translation') or '').strip()
        if source and translation:
            translations[source] = translation

    _TRANSLATIONS = translations
    _CURRENT_LANG = lang_code
    _notifier.language_changed.emit(lang_code)
    return True


def language_changed():
    """Returns the language-changed signal for UI connections."""
    return _notifier.language_changed