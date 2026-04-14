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
