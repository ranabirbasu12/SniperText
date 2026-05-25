import sys
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image

from src.ocr.base import OCREngine


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only engine")
class TestWindowsOCREngine:
    def test_implements_interface(self):
        from src.ocr.winocr_engine import WindowsOCREngine
        assert issubclass(WindowsOCREngine, OCREngine)

    def test_engine_name(self):
        from src.ocr.winocr_engine import WindowsOCREngine
        engine = WindowsOCREngine()
        assert engine.name() == "Windows OCR"

    @patch("src.ocr.winocr_engine.recognize_pil_sync")
    def test_extract_text(self, mock_recognize):
        from src.ocr.winocr_engine import WindowsOCREngine
        mock_recognize.return_value = {
            "lines": [{"text": "  Hello World  "}, {"text": "Second Line"}],
        }
        engine = WindowsOCREngine()

        img = Image.new("RGB", (100, 30), "white")
        result = engine.extract_text(img)

        assert result == "Hello World\nSecond Line"
        mock_recognize.assert_called_once()

    @patch("src.ocr.winocr_engine.recognize_pil_sync")
    def test_empty_result(self, mock_recognize):
        from src.ocr.winocr_engine import WindowsOCREngine
        mock_recognize.return_value = {"lines": []}
        engine = WindowsOCREngine()

        img = Image.new("RGB", (100, 30), "white")
        result = engine.extract_text(img)

        assert result == ""

    def test_registered_in_engine_registry(self):
        from src.ocr import ENGINE_REGISTRY
        assert "winocr" in ENGINE_REGISTRY
