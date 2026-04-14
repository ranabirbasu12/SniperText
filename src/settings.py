import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QCheckBox, QPushButton, QLineEdit,
    QDialogButtonBox, QGroupBox,
)

from src.config import Config
from src.ocr import ENGINE_REGISTRY


class HotkeyEdit(QLineEdit):
    """A line edit that captures keyboard shortcuts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Click 'Record' then press your shortcut")
        self._recording = False

    def start_recording(self):
        self._recording = True
        self.setText("Press your shortcut...")
        self.setFocus()

    def keyPressEvent(self, event):
        if not self._recording:
            return super().keyPressEvent(event)

        key = event.key()
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return  # Wait for the actual key

        modifiers = event.modifiers()
        parts = []
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append("ctrl")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append("shift")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append("alt")

        key_name = event.text().lower() if event.text() else ""
        if not key_name or not key_name.isprintable():
            key_enum = Qt.Key(key)
            key_name = key_enum.name.decode() if hasattr(key_enum.name, 'decode') else str(key_enum.name)
            key_name = key_name.replace("Key_", "").lower()

        if key_name:
            parts.append(key_name)

        self.setText("+".join(parts))
        self._recording = False


class SettingsDialog(QDialog):
    """Settings dialog for SniperText."""

    settings_changed = Signal()

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self._config = config
        self.setWindowTitle("SniperText Settings")
        self.setMinimumWidth(400)
        self._build_ui()
        self._load_from_config()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- Hotkey group ---
        hotkey_group = QGroupBox("Keyboard Shortcut")
        hotkey_layout = QHBoxLayout()
        self._hotkey_edit = HotkeyEdit()
        self._record_btn = QPushButton("Record")
        self._record_btn.clicked.connect(self._hotkey_edit.start_recording)
        hotkey_layout.addWidget(self._hotkey_edit)
        hotkey_layout.addWidget(self._record_btn)
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)

        # --- OCR Engine group ---
        engine_group = QGroupBox("OCR Engine")
        engine_layout = QFormLayout()
        self._engine_combo = QComboBox()
        for engine_name in ENGINE_REGISTRY:
            self._engine_combo.addItem(engine_name.title(), engine_name)
        engine_layout.addRow("Engine:", self._engine_combo)
        engine_group.setLayout(engine_layout)
        layout.addWidget(engine_group)

        # --- General group ---
        general_group = QGroupBox("General")
        general_layout = QVBoxLayout()
        self._notifications_cb = QCheckBox("Show notification after capture")
        general_layout.addWidget(self._notifications_cb)
        self._startup_cb = QCheckBox("Start on login")
        general_layout.addWidget(self._startup_cb)
        if sys.platform != "win32":
            self._startup_cb.setEnabled(False)
            self._startup_cb.setToolTip("Only available on Windows")
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # --- Buttons ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._apply_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_from_config(self):
        self._hotkey_edit.setText(self._config.hotkey)
        idx = self._engine_combo.findData(self._config.ocr_engine)
        if idx >= 0:
            self._engine_combo.setCurrentIndex(idx)
        self._notifications_cb.setChecked(self._config.notifications)
        self._startup_cb.setChecked(self._config.start_on_login)

    def _apply_and_accept(self):
        hotkey_text = self._hotkey_edit.text()
        if hotkey_text and "Press your" not in hotkey_text:
            self._config.hotkey = hotkey_text
        self._config.ocr_engine = self._engine_combo.currentData()
        self._config.notifications = self._notifications_cb.isChecked()
        self._config.start_on_login = self._startup_cb.isChecked()
        self._config.save()
        self.settings_changed.emit()
        self.accept()
