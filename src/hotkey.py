import threading
from pynput import keyboard
from PySide6.QtCore import QObject, Signal

MODIFIER_KEYS = {"ctrl", "shift", "alt", "cmd", "win"}


def parse_hotkey_string(hotkey_str: str) -> dict:
    """Parse a hotkey string like 'ctrl+shift+t' into components.

    Returns:
        {"modifiers": {"ctrl", "shift"}, "char": "t"}
    """
    parts = [p.strip().lower() for p in hotkey_str.split("+")]
    modifiers = set()
    char = ""
    for part in parts:
        if part in MODIFIER_KEYS:
            modifiers.add(part)
        else:
            char = part
    return {"modifiers": modifiers, "char": char}


def _pynput_hotkey_string(hotkey_str: str) -> str:
    """Convert our hotkey format to pynput's expected format.

    pynput expects: '<ctrl>+<shift>+t'
    """
    parsed = parse_hotkey_string(hotkey_str)
    parts = []
    for mod in sorted(parsed["modifiers"]):
        parts.append(f"<{mod}>")
    parts.append(parsed["char"])
    return "+".join(parts)


class HotkeyListener(QObject):
    """Listens for a global keyboard shortcut in a background thread."""

    triggered = Signal()

    def __init__(self, hotkey_str: str, parent=None):
        super().__init__(parent)
        self._hotkey_str = hotkey_str
        self._listener: keyboard.GlobalHotKeys | None = None

    def start(self):
        """Start listening for the configured hotkey."""
        self.stop()
        pynput_str = _pynput_hotkey_string(self._hotkey_str)
        self._listener = keyboard.GlobalHotKeys({
            pynput_str: self._on_hotkey,
        })
        self._listener.daemon = True
        self._listener.start()

    def stop(self):
        """Stop the hotkey listener."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def update_hotkey(self, hotkey_str: str):
        """Change the hotkey and restart the listener."""
        self._hotkey_str = hotkey_str
        self.start()

    def _on_hotkey(self):
        """Called from pynput's thread - emit signal to Qt's main thread."""
        self.triggered.emit()
