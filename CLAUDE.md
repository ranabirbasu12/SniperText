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
