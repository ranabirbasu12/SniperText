# SniperText Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows system tray OCR app that captures text from any screen region via keyboard shortcut and copies it to the clipboard.

**Architecture:** PySide6 handles all UI (system tray, fullscreen capture overlay, settings dialog). Tesseract OCR extracts text from captured screen regions via a swappable engine interface. pynput listens for global hotkeys. mss captures screenshots. Config persists as JSON. PyInstaller bundles everything into a single .exe.

**Tech Stack:** Python 3.11+, PySide6, pytesseract, Pillow, mss, pynput, PyInstaller

**Design Spec:** `docs/superpowers/specs/2026-04-14-snipertext-design.md`

---

## File Map

| File | Responsibility |
|------|---------------|
| `src/config.py` | Load/save JSON config, provide defaults |
| `src/ocr/__init__.py` | OCR package init, engine registry |
| `src/ocr/base.py` | Abstract OCR engine interface |
| `src/ocr/tesseract.py` | Tesseract OCR implementation with preprocessing |
| `src/capture.py` | Screenshot capture of a screen region via mss |
| `src/overlay.py` | Fullscreen transparent overlay for region selection |
| `src/hotkey.py` | Global hotkey listener via pynput |
| `src/tray.py` | System tray icon and context menu |
| `src/settings.py` | Settings dialog (hotkey, engine, notifications, startup) |
| `src/main.py` | Entry point, wires all components together |
| `tests/test_config.py` | Config tests |
| `tests/test_ocr.py` | OCR engine interface and Tesseract tests |
| `tests/test_capture.py` | Screen capture tests |
| `tests/test_overlay.py` | Overlay coordinate/edge-case tests |
| `tests/test_hotkey.py` | Hotkey parsing tests |
| `requirements.txt` | Python dependencies |
| `requirements-dev.txt` | Dev/test dependencies |
| `assets/icon.png` | System tray icon |
| `build.py` | PyInstaller build script |

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `src/__init__.py`
- Create: `src/ocr/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `assets/icon.png`

- [ ] **Step 1: Create requirements.txt**

```
PySide6>=6.6
pytesseract>=0.3
Pillow>=10.0
mss>=9.0
pynput>=1.7
```

- [ ] **Step 2: Create requirements-dev.txt**

```
-r requirements.txt
pytest>=8.0
pytest-qt>=4.3
```

- [ ] **Step 3: Create package init files**

`src/__init__.py` — empty file.

`src/ocr/__init__.py`:

```python
from src.ocr.base import OCREngine

__all__ = ["OCREngine"]
```

`tests/__init__.py` — empty file.

- [ ] **Step 4: Create test conftest**

`tests/conftest.py`:

```python
import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent))
```

- [ ] **Step 5: Create a placeholder tray icon**

Generate a simple 64x64 PNG icon for the system tray. Use Pillow to create a minimal crosshair icon programmatically:

```python
# Run this once to generate assets/icon.png
from PIL import Image, ImageDraw

img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
# Blue circle with white crosshair
draw.ellipse([8, 8, 56, 56], fill=(41, 128, 185, 230))
draw.line([32, 14, 32, 50], fill="white", width=2)
draw.line([14, 32, 50, 32], fill="white", width=2)
img.save("assets/icon.png")
```

- [ ] **Step 6: Install dependencies and verify**

Run: `pip install -r requirements-dev.txt`
Expected: All packages install successfully.

Run: `python -c "import PySide6; import pytesseract; import mss; import pynput; print('OK')"`
Expected: `OK`

- [ ] **Step 7: Commit**

```bash
git add requirements.txt requirements-dev.txt src/__init__.py src/ocr/__init__.py tests/__init__.py tests/conftest.py assets/icon.png
git commit -m "chore: project setup with dependencies and package structure"
```

---

### Task 2: Configuration Module

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing tests for config**

`tests/test_config.py`:

```python
import json
from pathlib import Path

from src.config import Config


def test_default_values():
    """Config should have sensible defaults without a config file."""
    config = Config.__new__(Config)
    config._data = {}
    config._path = Path("/nonexistent/config.json")
    assert config.hotkey == "ctrl+shift+t"
    assert config.ocr_engine == "tesseract"
    assert config.notifications is True
    assert config.start_on_login is False


def test_load_from_file(tmp_path):
    """Config should load values from a JSON file."""
    config_file = tmp_path / ".snipertext" / "config.json"
    config_file.parent.mkdir(parents=True)
    config_file.write_text(json.dumps({
        "hotkey": "ctrl+alt+s",
        "ocr_engine": "tesseract",
        "notifications": False,
        "start_on_login": True,
    }))
    config = Config(config_dir=tmp_path / ".snipertext")
    assert config.hotkey == "ctrl+alt+s"
    assert config.notifications is False
    assert config.start_on_login is True


def test_save_to_file(tmp_path):
    """Config.save() should persist current values to disk."""
    config_dir = tmp_path / ".snipertext"
    config = Config(config_dir=config_dir)
    config.hotkey = "ctrl+shift+x"
    config.save()

    raw = json.loads((config_dir / "config.json").read_text())
    assert raw["hotkey"] == "ctrl+shift+x"


def test_creates_config_dir_if_missing(tmp_path):
    """Config should create its directory on save if it doesn't exist."""
    config_dir = tmp_path / ".snipertext"
    assert not config_dir.exists()
    config = Config(config_dir=config_dir)
    config.save()
    assert config_dir.exists()
    assert (config_dir / "config.json").exists()


def test_malformed_json_falls_back_to_defaults(tmp_path):
    """Config should use defaults if the config file contains invalid JSON."""
    config_dir = tmp_path / ".snipertext"
    config_dir.mkdir(parents=True)
    (config_dir / "config.json").write_text("NOT JSON{{{")
    config = Config(config_dir=config_dir)
    assert config.hotkey == "ctrl+shift+t"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.config'`

- [ ] **Step 3: Implement config module**

`src/config.py`:

```python
import json
from pathlib import Path

DEFAULTS = {
    "hotkey": "ctrl+shift+t",
    "ocr_engine": "tesseract",
    "notifications": True,
    "start_on_login": False,
}


class Config:
    def __init__(self, config_dir: Path | None = None):
        if config_dir is None:
            config_dir = Path.home() / ".snipertext"
        self._path = config_dir / "config.json"
        self._data: dict = {}
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._data = {}
        else:
            self._data = {}

    def save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "hotkey": self.hotkey,
            "ocr_engine": self.ocr_engine,
            "notifications": self.notifications,
            "start_on_login": self.start_on_login,
        }
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @property
    def hotkey(self) -> str:
        return self._data.get("hotkey", DEFAULTS["hotkey"])

    @hotkey.setter
    def hotkey(self, value: str):
        self._data["hotkey"] = value

    @property
    def ocr_engine(self) -> str:
        return self._data.get("ocr_engine", DEFAULTS["ocr_engine"])

    @ocr_engine.setter
    def ocr_engine(self, value: str):
        self._data["ocr_engine"] = value

    @property
    def notifications(self) -> bool:
        return self._data.get("notifications", DEFAULTS["notifications"])

    @notifications.setter
    def notifications(self, value: bool):
        self._data["notifications"] = value

    @property
    def start_on_login(self) -> bool:
        return self._data.get("start_on_login", DEFAULTS["start_on_login"])

    @start_on_login.setter
    def start_on_login(self, value: bool):
        self._data["start_on_login"] = value
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_config.py -v`
Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add config module with JSON persistence and defaults"
```

---

### Task 3: OCR Engine Interface and Tesseract Implementation

**Files:**
- Create: `src/ocr/base.py`
- Create: `src/ocr/tesseract.py`
- Modify: `src/ocr/__init__.py`
- Create: `tests/test_ocr.py`

- [ ] **Step 1: Write failing tests for OCR**

`tests/test_ocr.py`:

```python
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw, ImageFont

from src.ocr.base import OCREngine
from src.ocr.tesseract import TesseractEngine


def test_ocr_engine_is_abstract():
    """OCREngine cannot be instantiated directly."""
    try:
        OCREngine()
        assert False, "Should have raised TypeError"
    except TypeError:
        pass


def test_tesseract_engine_implements_interface():
    """TesseractEngine should be a subclass of OCREngine."""
    assert issubclass(TesseractEngine, OCREngine)


def test_tesseract_engine_name():
    """TesseractEngine.name() should return 'Tesseract'."""
    engine = TesseractEngine()
    assert engine.name() == "Tesseract"


@patch("src.ocr.tesseract.pytesseract")
def test_tesseract_extract_text(mock_pytesseract):
    """TesseractEngine should call pytesseract and return cleaned text."""
    mock_pytesseract.image_to_string.return_value = "  Hello World  \n\n"
    engine = TesseractEngine()

    img = Image.new("RGB", (100, 30), "white")
    result = engine.extract_text(img)

    assert result == "Hello World"
    mock_pytesseract.image_to_string.assert_called_once()


@patch("src.ocr.tesseract.pytesseract")
def test_tesseract_preprocesses_image(mock_pytesseract):
    """TesseractEngine should convert image to grayscale before OCR."""
    mock_pytesseract.image_to_string.return_value = "test"
    engine = TesseractEngine()

    img = Image.new("RGB", (100, 30), "red")
    engine.extract_text(img)

    # The image passed to pytesseract should be grayscale (mode "L")
    call_args = mock_pytesseract.image_to_string.call_args
    processed_img = call_args[0][0]
    assert processed_img.mode == "L"


@patch("src.ocr.tesseract.pytesseract")
def test_tesseract_empty_result(mock_pytesseract):
    """TesseractEngine should return empty string for blank images."""
    mock_pytesseract.image_to_string.return_value = "   \n  \n  "
    engine = TesseractEngine()

    img = Image.new("RGB", (100, 30), "white")
    result = engine.extract_text(img)

    assert result == ""
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_ocr.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.ocr.base'`

- [ ] **Step 3: Implement OCR engine base class**

`src/ocr/base.py`:

```python
from abc import ABC, abstractmethod
from PIL import Image


class OCREngine(ABC):
    @abstractmethod
    def extract_text(self, image: Image.Image) -> str:
        """Takes a PIL Image, returns extracted text string."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Returns human-readable engine name for settings UI."""
        pass
```

- [ ] **Step 4: Implement Tesseract engine**

`src/ocr/tesseract.py`:

```python
import pytesseract
from PIL import Image, ImageFilter

from src.ocr.base import OCREngine


class TesseractEngine(OCREngine):
    def extract_text(self, image: Image.Image) -> str:
        processed = self._preprocess(image)
        raw_text = pytesseract.image_to_string(processed)
        return self._clean_text(raw_text)

    def name(self) -> str:
        return "Tesseract"

    def _preprocess(self, image: Image.Image) -> Image.Image:
        grayscale = image.convert("L")
        sharpened = grayscale.filter(ImageFilter.SHARPEN)
        return sharpened

    def _clean_text(self, text: str) -> str:
        lines = text.strip().splitlines()
        cleaned_lines = [line.rstrip() for line in lines]
        result = "\n".join(cleaned_lines).strip()
        return result
```

- [ ] **Step 5: Update OCR package init**

`src/ocr/__init__.py`:

```python
from src.ocr.base import OCREngine
from src.ocr.tesseract import TesseractEngine

ENGINE_REGISTRY: dict[str, type[OCREngine]] = {
    "tesseract": TesseractEngine,
}


def get_engine(name: str) -> OCREngine:
    """Instantiate an OCR engine by its config name."""
    engine_cls = ENGINE_REGISTRY.get(name)
    if engine_cls is None:
        raise ValueError(f"Unknown OCR engine: {name!r}. Available: {list(ENGINE_REGISTRY)}")
    return engine_cls()


__all__ = ["OCREngine", "TesseractEngine", "get_engine", "ENGINE_REGISTRY"]
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python -m pytest tests/test_ocr.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add src/ocr/base.py src/ocr/tesseract.py src/ocr/__init__.py tests/test_ocr.py
git commit -m "feat: add swappable OCR engine interface with Tesseract implementation"
```

---

### Task 4: Screen Capture Module

**Files:**
- Create: `src/capture.py`
- Create: `tests/test_capture.py`

- [ ] **Step 1: Write failing tests for capture**

`tests/test_capture.py`:

```python
from unittest.mock import patch, MagicMock
from PIL import Image

from src.capture import capture_region


@patch("src.capture.mss")
def test_capture_region_returns_pil_image(mock_mss_module):
    """capture_region should return a PIL Image of the selected area."""
    mock_sct = MagicMock()
    mock_mss_module.mss.return_value.__enter__ = MagicMock(return_value=mock_sct)
    mock_mss_module.mss.return_value.__exit__ = MagicMock(return_value=False)

    fake_img = Image.new("RGB", (100, 50), "red")
    mock_grab = MagicMock()
    mock_grab.rgb = fake_img.tobytes()
    mock_grab.size = (100, 50)
    mock_sct.grab.return_value = mock_grab

    result = capture_region(10, 20, 110, 70)

    assert isinstance(result, Image.Image)
    assert result.size == (100, 50)
    mock_sct.grab.assert_called_once_with({"left": 10, "top": 20, "width": 100, "height": 50})


@patch("src.capture.mss")
def test_capture_region_clamps_negative_coords(mock_mss_module):
    """Negative coordinates should be clamped to 0."""
    mock_sct = MagicMock()
    mock_mss_module.mss.return_value.__enter__ = MagicMock(return_value=mock_sct)
    mock_mss_module.mss.return_value.__exit__ = MagicMock(return_value=False)

    fake_img = Image.new("RGB", (50, 50), "blue")
    mock_grab = MagicMock()
    mock_grab.rgb = fake_img.tobytes()
    mock_grab.size = (50, 50)
    mock_sct.grab.return_value = mock_grab

    capture_region(-10, -20, 40, 30)

    call_args = mock_sct.grab.call_args[0][0]
    assert call_args["left"] == 0
    assert call_args["top"] == 0


def test_capture_region_swaps_inverted_coords():
    """If user drags right-to-left or bottom-to-top, coords should be normalized."""
    from src.capture import _normalize_coords

    left, top, right, bottom = _normalize_coords(200, 300, 100, 150)
    assert left == 100
    assert top == 150
    assert right == 200
    assert bottom == 300
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_capture.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.capture'`

- [ ] **Step 3: Implement capture module**

`src/capture.py`:

```python
import mss
from PIL import Image


def _normalize_coords(x1: int, y1: int, x2: int, y2: int) -> tuple[int, int, int, int]:
    """Ensure left < right and top < bottom, clamp negatives to 0."""
    left = max(0, min(x1, x2))
    top = max(0, min(y1, y2))
    right = max(x1, x2)
    bottom = max(y1, y2)
    return left, top, right, bottom


def capture_region(x1: int, y1: int, x2: int, y2: int) -> Image.Image:
    """Capture a screenshot of the specified screen region.

    Args:
        x1, y1: Top-left corner (or any corner - coordinates are normalized).
        x2, y2: Bottom-right corner (or any corner).

    Returns:
        PIL Image of the captured region.
    """
    left, top, right, bottom = _normalize_coords(x1, y1, x2, y2)
    width = right - left
    height = bottom - top

    monitor = {"left": left, "top": top, "width": width, "height": height}

    with mss.mss() as sct:
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

    return img
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_capture.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/capture.py tests/test_capture.py
git commit -m "feat: add screen capture module with coordinate normalization"
```

---

### Task 5: Capture Overlay

**Files:**
- Create: `src/overlay.py`
- Create: `tests/test_overlay.py`

- [ ] **Step 1: Write failing tests for overlay logic**

`tests/test_overlay.py`:

```python
"""Tests for overlay coordinate logic. UI rendering is tested manually."""
from src.overlay import CaptureOverlay


def test_selection_rect_none_before_drag(qtbot):
    """Before any mouse interaction, selection_rect should be None."""
    overlay = CaptureOverlay()
    qtbot.addWidget(overlay)
    assert overlay.selection_rect is None


def test_zero_size_selection_is_ignored(qtbot):
    """A click without drag should not produce a selection."""
    overlay = CaptureOverlay()
    qtbot.addWidget(overlay)
    overlay._start_pos = (100, 100)
    overlay._end_pos = (100, 100)
    assert overlay._is_valid_selection() is False


def test_valid_selection(qtbot):
    """A proper drag should be considered valid."""
    overlay = CaptureOverlay()
    qtbot.addWidget(overlay)
    overlay._start_pos = (100, 100)
    overlay._end_pos = (200, 250)
    assert overlay._is_valid_selection() is True


def test_small_selection_is_ignored(qtbot):
    """A drag smaller than 5px in either dimension should be ignored."""
    overlay = CaptureOverlay()
    qtbot.addWidget(overlay)
    overlay._start_pos = (100, 100)
    overlay._end_pos = (103, 102)
    assert overlay._is_valid_selection() is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_overlay.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.overlay'`

- [ ] **Step 3: Implement overlay**

`src/overlay.py`:

```python
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
        """Show the overlay fullscreen on the primary monitor."""
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
                # Map to global screen coordinates
                geo = self.geometry()
                gx1 = geo.x() + min(x1, x2)
                gy1 = geo.y() + min(y1, y2)
                gx2 = geo.x() + max(x1, x2)
                gy2 = geo.y() + max(y1, y2)
                self.hide()
                self.region_selected.emit(gx1, gy1, gx2, gy2)
            # else: stay open, let user try again

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            self.capture_cancelled.emit()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_overlay.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/overlay.py tests/test_overlay.py
git commit -m "feat: add fullscreen capture overlay with region selection"
```

---

### Task 6: Global Hotkey Listener

**Files:**
- Create: `src/hotkey.py`
- Create: `tests/test_hotkey.py`

- [ ] **Step 1: Write failing tests for hotkey parsing**

`tests/test_hotkey.py`:

```python
from src.hotkey import parse_hotkey_string


def test_parse_ctrl_shift_t():
    """Standard hotkey string should parse into components."""
    combo = parse_hotkey_string("ctrl+shift+t")
    assert combo["char"] == "t"
    assert combo["modifiers"] == {"ctrl", "shift"}


def test_parse_ctrl_alt_s():
    """Alternate combo with alt."""
    combo = parse_hotkey_string("ctrl+alt+s")
    assert combo["char"] == "s"
    assert combo["modifiers"] == {"ctrl", "alt"}


def test_parse_single_key():
    """A single key with no modifiers."""
    combo = parse_hotkey_string("f1")
    assert combo["char"] == "f1"
    assert combo["modifiers"] == set()


def test_parse_case_insensitive():
    """Parsing should be case-insensitive."""
    combo = parse_hotkey_string("Ctrl+Shift+T")
    assert combo["char"] == "t"
    assert combo["modifiers"] == {"ctrl", "shift"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_hotkey.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.hotkey'`

- [ ] **Step 3: Implement hotkey module**

`src/hotkey.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_hotkey.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/hotkey.py tests/test_hotkey.py
git commit -m "feat: add global hotkey listener with configurable shortcuts"
```

---

### Task 7: System Tray

**Files:**
- Create: `src/tray.py`

- [ ] **Step 1: Implement tray module**

`src/tray.py`:

```python
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
```

- [ ] **Step 2: Verify import works**

Run: `python -c "from src.tray import SystemTray; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/tray.py
git commit -m "feat: add system tray icon with context menu"
```

---

### Task 8: Settings Window

**Files:**
- Create: `src/settings.py`

- [ ] **Step 1: Implement settings dialog**

`src/settings.py`:

```python
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
```

- [ ] **Step 2: Verify import works**

Run: `python -c "from src.settings import SettingsDialog; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/settings.py
git commit -m "feat: add settings dialog with hotkey recording and engine selection"
```

---

### Task 9: Main Entry Point

**Files:**
- Create: `src/main.py`

- [ ] **Step 1: Implement main.py**

`src/main.py`:

```python
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
```

- [ ] **Step 2: Verify import works**

Run: `python -c "from src.main import SniperTextApp; print('OK')"`
Expected: `OK` (may show Qt warning on headless systems)

- [ ] **Step 3: Commit**

```bash
git add src/main.py
git commit -m "feat: add main entry point wiring all components together"
```

---

### Task 10: PyInstaller Build Script

**Files:**
- Create: `build.py`

- [ ] **Step 1: Implement build script**

`build.py`:

```python
"""PyInstaller build script for SniperText.

Run on Windows after installing dependencies:
    pip install -r requirements.txt pyinstaller
    python build.py
"""
import os
import shutil
import sys
from pathlib import Path
from subprocess import run as run_cmd


def find_tesseract() -> str | None:
    """Try to find the Tesseract binary on the system."""
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in common_paths:
        if os.path.isfile(path):
            return path
    return shutil.which("tesseract")


def build():
    project_root = Path(__file__).parent
    main_script = project_root / "src" / "main.py"
    icon_path = project_root / "assets" / "icon.png"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "SniperText",
        f"--add-data={icon_path}{os.pathsep}assets",
    ]

    tesseract_path = find_tesseract()
    if tesseract_path:
        tesseract_dir = str(Path(tesseract_path).parent)
        cmd.append(f"--add-binary={tesseract_dir}{os.pathsep}tesseract")
        print(f"Bundling Tesseract from: {tesseract_dir}")
    else:
        print("WARNING: Tesseract not found on this system.")
        print("The .exe will require Tesseract installed separately.")

    cmd.append(str(main_script))

    print(f"Running PyInstaller...")
    run_cmd(cmd, check=True)
    print("\nBuild complete! Output: dist/SniperText.exe")


if __name__ == "__main__":
    build()
```

- [ ] **Step 2: Verify syntax**

Run: `python -c "import ast; ast.parse(open('build.py').read()); print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add build.py
git commit -m "feat: add PyInstaller build script with Tesseract auto-detection"
```

---

### Task 11: CLAUDE.md for Handoff

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Write CLAUDE.md**

`CLAUDE.md`:

```markdown
# SniperText

## What is this?

A Windows system tray OCR app. Press Ctrl+Shift+T, drag a rectangle over text on screen, and the text is extracted via OCR and copied to the clipboard. Inspired by TextSniper (macOS).

## Tech Stack

- Python 3.11+
- PySide6 (LGPL license, chosen over PyQt6 to avoid GPL)
- pytesseract + Tesseract OCR binary
- mss (screen capture)
- pynput (global hotkeys)
- PyInstaller (single .exe distribution)

## Project Structure

- `src/main.py` - entry point, wires everything together
- `src/config.py` - JSON config at ~/.snipertext/config.json
- `src/overlay.py` - fullscreen transparent capture overlay (the core UX)
- `src/capture.py` - screenshot capture via mss
- `src/ocr/base.py` - abstract OCR engine interface
- `src/ocr/tesseract.py` - Tesseract implementation
- `src/hotkey.py` - global hotkey listener via pynput
- `src/tray.py` - system tray icon and menu
- `src/settings.py` - settings dialog
- `build.py` - PyInstaller build script
- `docs/superpowers/specs/` - design specification

## Running

```bash
pip install -r requirements.txt
python -m src.main
```

## Testing

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

## Building .exe (Windows only)

```bash
pip install pyinstaller
python build.py
```

Requires Tesseract OCR installed on the build machine. Download from the UB-Mannheim Tesseract GitHub wiki. Install to default path (C:\Program Files\Tesseract-OCR\). build.py will auto-detect and bundle it.

## Key Design Decisions

- OCR engine is swappable: add new engines in `src/ocr/` implementing `OCREngine` base class
- Target hardware: ThinkPad X1, no GPU, everything is CPU-only
- Config lives at ~/.snipertext/config.json
- App runs as system tray icon (no main window, no dock presence)
- Full design spec at `docs/superpowers/specs/2026-04-14-snipertext-design.md`
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md for cross-session and cross-machine handoff"
```
