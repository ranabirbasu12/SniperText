import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from src.config import Config
from src.ocr import get_engine
from src.capture import capture_region
from src.overlay import CaptureOverlay
from src.hotkey import HotkeyListener
from src.tray import SystemTray
from src.settings import SettingsDialog


def get_asset_path(filename: str) -> str:
    """Resolve asset path, works both in dev and PyInstaller bundle."""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent / "assets"
    return str(base / filename)


class SniperTextApp:
    """Main application controller wiring all components together."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.config = Config()
        self.ocr_engine = get_engine(self.config.ocr_engine)

        # Overlay
        self.overlay = CaptureOverlay()
        self.overlay.region_selected.connect(self._on_region_selected)

        # System tray
        self.tray = SystemTray(get_asset_path("icon.png"))
        self.tray.capture_action.triggered.connect(self._start_capture)
        self.tray.settings_action.triggered.connect(self._show_settings)
        self.tray.about_action.triggered.connect(self._show_about)
        self.tray.show()

        # Global hotkey
        self.hotkey_listener = HotkeyListener(self.config.hotkey)
        self.hotkey_listener.triggered.connect(self._start_capture)
        self.hotkey_listener.start()

    def _start_capture(self):
        """Show the capture overlay after a small delay."""
        QTimer.singleShot(150, self.overlay.activate)

    def _on_region_selected(self, x1: int, y1: int, x2: int, y2: int):
        """Called when the user finishes selecting a region."""
        try:
            image = capture_region(x1, y1, x2, y2)
            text = self.ocr_engine.extract_text(image)

            if text:
                clipboard = self.app.clipboard()
                clipboard.setText(text)
                if self.config.notifications:
                    preview = text[:50] + "..." if len(text) > 50 else text
                    self.tray.show_notification("SniperText", f"Copied: {preview}")
            else:
                if self.config.notifications:
                    self.tray.show_notification("SniperText", "No text detected in selection.")
        except Exception as e:
            self.tray.show_notification("SniperText Error", str(e))

    def _show_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self.config)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec()

    def _apply_settings(self):
        """Re-apply settings after they change."""
        self.ocr_engine = get_engine(self.config.ocr_engine)
        self.hotkey_listener.update_hotkey(self.config.hotkey)

    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            None,
            "About SniperText",
            "SniperText v1.0.0\n\n"
            "Screen capture OCR tool.\n"
            "Select a region and extract text to clipboard.\n\n"
            f"OCR Engine: {self.ocr_engine.name()}"
        )

    def run(self) -> int:
        """Start the application event loop."""
        return self.app.exec()


def main():
    app = SniperTextApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
