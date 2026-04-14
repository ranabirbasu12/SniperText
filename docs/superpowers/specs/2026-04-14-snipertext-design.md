# SniperText — Design Specification

**Date:** 2026-04-14
**Status:** Approved
**Author:** Brainstorming session (Claude Code + user)

## Overview

SniperText is a lightweight Windows system tray application that captures text from any screen region using OCR. The user presses a keyboard shortcut, drags a rectangle over the area containing text, and the extracted text is instantly copied to the clipboard.

Inspired by [TextSniper](https://textsniper.app/) (macOS), SniperText brings the same core experience to Windows.

## Target Environment

- **OS:** Windows 10/11
- **Hardware:** Lenovo ThinkPad X1 (no dedicated GPU — CPU-only processing)
- **Distribution:** Single .exe via PyInstaller (no installation required)

## Scope — v1

**In scope:**
- Screen region capture via transparent fullscreen overlay
- OCR text extraction using Tesseract (CPU-only)
- Copy extracted text to clipboard
- System tray app with menu
- Settings window (hotkey, OCR engine, notifications, startup toggle)
- Configurable global keyboard shortcut (default: Ctrl+Shift+T)
- Swappable OCR engine architecture

**Out of scope (future versions):**
- QR code / barcode recognition
- Multi-language OCR
- Text-to-speech
- Translation
- Multi-monitor overlay support (v1: primary monitor only)

## Decisions & Rationale

| Decision | Choice | Why |
|----------|--------|-----|
| Language | Python | Fast iteration, cross-platform development, user familiarity |
| UI framework | PySide6 (Qt) | LGPL license (no GPL concerns), handles tray + overlay + settings in one framework, mature ecosystem |
| OCR engine | Tesseract via pytesseract | Open source, CPU-only, works on Mac (dev) and Windows (prod), lightweight |
| OCR architecture | Swappable via abstract base class | Future-proofs for Windows.Media.Ocr or RapidOCR without rewriting existing code |
| Screen capture | mss library | Fast, cross-platform, no dependencies on platform-specific APIs |
| Global hotkey | pynput | Cross-platform keyboard listener, works from background/tray apps |
| Distribution | PyInstaller single .exe | No admin privileges needed, no Python installation required on target machine |
| Development | Mac (develop & test) → Windows (final build & deploy) | User's primary machine is Mac; target machine is company Windows laptop |

## Architecture

### Project Structure

```
SniperText/
├── src/
│   ├── main.py              # Entry point, app lifecycle
│   ├── tray.py              # System tray icon + menu
│   ├── overlay.py           # Fullscreen transparent capture overlay
│   ├── capture.py           # Screenshot capture (mss)
│   ├── ocr/
│   │   ├── base.py          # OCR engine interface (abstract base class)
│   │   ├── tesseract.py     # Tesseract implementation
│   │   └── __init__.py
│   ├── hotkey.py            # Global hotkey registration (pynput)
│   ├── settings.py          # Settings window UI
│   └── config.py            # Config persistence (JSON file)
├── assets/
│   └── icon.png             # Tray icon
├── requirements.txt
├── build.py                 # PyInstaller build script
└── README.md
```

### Data Flow

```
User presses Ctrl+Shift+T
        │
        ▼
  hotkey.py detects keypress
        │
        ▼
  overlay.py shows fullscreen transparent overlay
  (screen dimmed ~30%, crosshair cursor)
        │
        ▼
  User drags rectangle over text
  (selected area shown clearly, outside stays dimmed)
        │
        ▼
  overlay.py captures coordinates, closes overlay
        │
        ▼
  capture.py takes screenshot of selected region (mss)
        │
        ▼
  ocr/tesseract.py extracts text from image (pytesseract)
        │
        ▼
  Extracted text → QApplication.clipboard()
        │
        ▼
  System tray notification: "Text copied to clipboard"
```

### Component Details

#### 1. Entry Point (`main.py`)

- Creates `QApplication` (with no main window — tray-only app)
- Initializes config, OCR engine, hotkey listener, and tray
- Runs the Qt event loop
- Handles clean shutdown (deregisters hotkey, saves config)

#### 2. System Tray (`tray.py`)

- `QSystemTrayIcon` with a context menu:
  - **Capture Text** — triggers the overlay (same as hotkey)
  - **Settings...** — opens the settings dialog
  - **About** — shows version info
  - **Quit** — exits the app
- Displays balloon notifications after successful capture

#### 3. Capture Overlay (`overlay.py`)

- A `QWidget` configured as:
  - Fullscreen, frameless (`Qt.FramelessWindowHint`)
  - Always on top (`Qt.WindowStaysOnTopHint`)
  - Semi-transparent background (~30% black tint)
  - Crosshair cursor (`Qt.CrossCursor`)
- Mouse event handling:
  - `mousePressEvent` — records start position
  - `mouseMoveEvent` — draws selection rectangle (clear area inside, dimmed outside)
  - `mouseReleaseEvent` — captures coordinates, closes overlay
- `keyPressEvent` — Escape cancels and closes
- `paintEvent` — uses `QPainter` to render the dimmed overlay and selection rectangle
- Visual feedback:
  - 2px blue border around selection rectangle
  - Area inside selection is clear (no tint)
  - Area outside selection stays dimmed
- Edge cases:
  - Zero-size selection (click without drag) → ignored, overlay stays open
  - Drag off-screen → coordinates clamped to screen bounds
  - Multi-monitor → primary monitor only for v1

#### 4. Screen Capture (`capture.py`)

- Uses `mss` to capture a screenshot of the selected region
- Takes pixel coordinates from the overlay
- Returns a `PIL.Image` for OCR processing
- Handles DPI scaling (important on high-DPI displays like ThinkPad X1)

#### 5. OCR Engine Interface (`ocr/base.py`)

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

#### 6. Tesseract Implementation (`ocr/tesseract.py`)

- Implements `OCREngine` using `pytesseract.image_to_string()`
- Configures Tesseract binary path (bundled in .exe or system-installed)
- Pre-processes image for better accuracy:
  - Convert to grayscale
  - Apply slight sharpening
- Returns cleaned text (strip whitespace, normalize line endings)

#### 7. Future OCR Engines (not in v1, but the architecture supports them)

- `WindowsOCREngine` — uses `Windows.Media.Ocr` via `winocr` package
- `RapidOCREngine` — lightweight deep learning OCR, CPU-friendly

#### 8. Global Hotkey (`hotkey.py`)

- Uses `pynput.keyboard.GlobalHotKeys` to listen for the configured shortcut
- Default: Ctrl+Shift+T
- Runs in a background thread
- Signals the main Qt thread (via `QMetaObject.invokeMethod` or Qt signals) to show the overlay
- Supports re-registration when the user changes the shortcut in settings

#### 9. Settings Window (`settings.py`)

- `QDialog` with the following controls:
  - **Hotkey:** Displays current shortcut, button to record a new one (captures next key combo)
  - **OCR Engine:** `QComboBox` dropdown listing available engines
  - **Notifications:** `QCheckBox` toggle for "text copied" balloon
  - **Start on login:** `QCheckBox` to add/remove from Windows startup (writes to `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` registry key)
- OK/Cancel buttons to apply or discard changes

#### 10. Configuration (`config.py`)

- Reads/writes a JSON file at `~/.snipertext/config.json` (on Windows: `C:\Users\<username>\.snipertext\config.json`)
- Default values hardcoded in the app:
  ```json
  {
    "hotkey": "ctrl+shift+t",
    "ocr_engine": "tesseract",
    "notifications": true,
    "start_on_login": false
  }
  ```
- Config file is created on first run with defaults
- Settings window reads from and writes to this config

## Dependencies

```
PySide6>=6.6       # UI framework (tray, overlay, settings, clipboard)
pytesseract>=0.3   # Tesseract OCR wrapper
Pillow>=10.0       # Image processing
mss>=9.0           # Screen capture
pynput>=1.7        # Global hotkey listener
```

**Bundled with .exe:**
- Tesseract OCR binary (Windows build, included via PyInstaller `--add-binary`)

## Build & Distribution

- **Build tool:** PyInstaller
- **Output:** Single .exe (`--onefile` mode)
- **Tesseract binary:** Bundled via `--add-binary` flag pointing to Windows Tesseract installation
- **Build script:** `build.py` automates PyInstaller invocation with correct flags
- **Expected .exe size:** ~80-120MB
- **No admin privileges required** to run the .exe

## Development Strategy

1. **Develop on Mac:** All core logic (overlay, OCR pipeline, settings UI, config) is cross-platform via PySide6 + Tesseract. Develop and test the full capture → OCR → clipboard flow on macOS.
2. **Transfer to Windows:** Clone/copy the repo to the ThinkPad X1.
3. **Windows testing:** Run directly with Python to verify overlay rendering, hotkey behavior, and Tesseract path resolution.
4. **Build .exe:** Run PyInstaller on Windows to produce the final distributable.

## Handoff Notes

This project is designed to be picked up by a fresh Claude Code instance on a Windows machine. Key things to know:

- All design decisions and rationale are in this document
- The OCR engine is swappable — `ocr/base.py` defines the interface, `ocr/tesseract.py` is the v1 implementation
- PySide6 (not PyQt6) was chosen specifically for LGPL licensing
- Target hardware has no GPU — everything must be CPU-only
- The overlay is the most complex UI piece — it's a transparent fullscreen QWidget with QPainter rendering
- High-DPI scaling on ThinkPad X1 needs attention in `capture.py`
