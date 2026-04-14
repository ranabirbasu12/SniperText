from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication


class SystemTray(QSystemTrayIcon):
    """System tray icon with context menu for SniperText."""

    def __init__(self, icon_path: str, parent=None):
        icon = QIcon(icon_path)
        super().__init__(icon, parent)
        self.setToolTip("SniperText - OCR Screen Capture")
        self._build_menu()

    def _build_menu(self):
        menu = QMenu()

        self._capture_action = QAction("Capture Text", menu)
        menu.addAction(self._capture_action)

        menu.addSeparator()

        self._settings_action = QAction("Settings...", menu)
        menu.addAction(self._settings_action)

        self._about_action = QAction("About", menu)
        menu.addAction(self._about_action)

        menu.addSeparator()

        self._quit_action = QAction("Quit", menu)
        self._quit_action.triggered.connect(QApplication.quit)
        menu.addAction(self._quit_action)

        self.setContextMenu(menu)

    @property
    def capture_action(self) -> QAction:
        return self._capture_action

    @property
    def settings_action(self) -> QAction:
        return self._settings_action

    @property
    def about_action(self) -> QAction:
        return self._about_action

    def show_notification(self, title: str, message: str, duration_ms: int = 2000):
        """Show a system tray balloon notification."""
        self.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, duration_ms)
