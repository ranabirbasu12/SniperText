from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QCursor
from PySide6.QtWidgets import QWidget, QApplication


class CaptureOverlay(QWidget):
    """Fullscreen transparent overlay for selecting a screen region."""

    region_selected = Signal(int, int, int, int)  # x1, y1, x2, y2
    capture_cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._start_pos: tuple[int, int] | None = None
        self._end_pos: tuple[int, int] | None = None
        self._dragging = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

    @property
    def selection_rect(self) -> QRect | None:
        """Returns the current selection as a QRect, or None."""
        if self._start_pos is None or self._end_pos is None:
            return None
        if not self._is_valid_selection():
            return None
        x1, y1 = self._start_pos
        x2, y2 = self._end_pos
        return QRect(QPoint(min(x1, x2), min(y1, y2)),
                     QPoint(max(x1, x2), max(y1, y2)))

    def _is_valid_selection(self) -> bool:
        """A selection must be at least 5px in both dimensions."""
        if self._start_pos is None or self._end_pos is None:
            return False
        dx = abs(self._end_pos[0] - self._start_pos[0])
        dy = abs(self._end_pos[1] - self._start_pos[1])
        return dx >= 5 and dy >= 5

    def activate(self):
        """Show the overlay on the screen where the cursor currently is."""
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos)
        if screen is None:
            screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        self.setGeometry(geometry)
        self._start_pos = None
        self._end_pos = None
        self._dragging = False
        self.showFullScreen()
        self.activateWindow()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw semi-transparent overlay over entire screen
        overlay_color = QColor(0, 0, 0, 77)  # ~30% opacity black

        if self.selection_rect:
            # Draw dimmed area with a clear cutout for the selection
            region = self.rect()
            painter.fillRect(region, overlay_color)
            # Clear the selection area
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.selection_rect, Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            # Draw selection border
            pen = QPen(QColor(41, 128, 185), 2)  # Blue, 2px
            painter.setPen(pen)
            painter.drawRect(self.selection_rect)
        else:
            painter.fillRect(self.rect(), overlay_color)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            self._start_pos = (pos.x(), pos.y())
            self._end_pos = (pos.x(), pos.y())
            self._dragging = True
            self.update()

    def mouseMoveEvent(self, event):
        if self._dragging:
            pos = event.position().toPoint()
            self._end_pos = (pos.x(), pos.y())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            pos = event.position().toPoint()
            self._end_pos = (pos.x(), pos.y())

            if self._is_valid_selection():
                x1, y1 = self._start_pos
                x2, y2 = self._end_pos
                # Map widget-local coords to physical pixel coords for mss.
                # Qt gives logical coords; mss needs physical pixels.
                # Scale local offsets by the screen's DPR, then add
                # the physical origin of the screen (logical origin * DPR).
                screen = self.screen()
                dpr = screen.devicePixelRatio() if screen else 1.0
                geo = self.geometry()
                ox = int(geo.x() * dpr)
                oy = int(geo.y() * dpr)
                gx1 = ox + int(min(x1, x2) * dpr)
                gy1 = oy + int(min(y1, y2) * dpr)
                gx2 = ox + int(max(x1, x2) * dpr)
                gy2 = oy + int(max(y1, y2) * dpr)
                self.hide()
                self.region_selected.emit(gx1, gy1, gx2, gy2)
            # else: stay open, let user try again

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            self.capture_cancelled.emit()
